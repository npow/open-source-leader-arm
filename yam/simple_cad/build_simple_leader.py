"""Generate the low-part-count, no-solder YAM encoder leader.

The design uses one repeated joint architecture.  The stationary side of each
joint contains a 608 bearing pocket and a push-in carrier for Adafruit's
STEMMA-QT AS5600 board.  The moving link contains the axle, snap retention
tabs, and magnet pocket.  Those features are part of the structural links, so
there are no separate encoder housings, caps, rotors, washers, or fasteners.

This is deliberately parametric prototype CAD.  Print ``joint_fit_test``
before committing to the eight full-size structural pieces.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Dict, Mapping, Tuple

import cadquery as cq

Vector3 = Tuple[float, float, float]

# Purchased component dimensions (millimetres).
BEARING_OD = 22.0
BEARING_ID = 8.0
BEARING_WIDTH = 7.0
MAGNET_DIAMETER = 4.0
MAGNET_THICKNESS = 2.0
AS5600_BOARD_LONG = 25.4
AS5600_BOARD_SHORT = 17.78
AS5600_BOARD_THICKNESS = 1.6

# Printer-tunable fits.  Defaults target a reasonably calibrated FDM printer.
BEARING_POCKET_DIAMETER = 22.20
BEARING_POCKET_DEPTH = 7.15
AXLE_DIAMETER = 7.80
SHAFT_CLEARANCE_DIAMETER = 9.20
MAGNET_POCKET_DIAMETER = 4.15
MAGNET_POCKET_DEPTH = 2.10
PCB_EDGE_CLEARANCE = 0.30

# Joint envelope and sensor stack.  The AS5600 package projects from the PCB's
# component face; this stack leaves approximately 1.5-2.0 mm from magnet face
# to package face, within the sensor manufacturer's 0.5-3 mm guidance.
JOINT_RADIUS = 15.5
SOCKET_BODY_DEPTH = 8.0
PCB_COMPONENT_FACE_X = 16.8
PCB_BACK_X = PCB_COMPONENT_FACE_X + AS5600_BOARD_THICKNESS
BACKPLATE_THICKNESS = 2.0
AXLE_TIP_X = 13.5
FLANGE_THICKNESS = 3.8
FLANGE_RADIUS = 14.6

BEAM_RADIUS = 6.5
NECK_LENGTH = 25.0

# A compact leader is easier to move than a 1:1 replica.  Joint-space mapping
# means the link lengths do not affect commanded follower angles.  The axis
# order matches YAM: Z, Y, Y, Y, Z, X, followed by the gripper input on Y.
JOINTS: Mapping[str, Tuple[Vector3, Vector3]] = {
    # J1 points downward so its stationary sensor stack lives below the
    # rotating flange; the moving link exits above the base and can sweep the
    # full yaw range without hitting a support ring.
    "j1": ((35.0, 0.0, 40.0), (0.0, 0.0, -1.0)),
    "j2": ((65.0, 0.0, 75.0), (0.0, 1.0, 0.0)),
    "j3": ((65.0, 0.0, 235.0), (0.0, 1.0, 0.0)),
    "j4": ((65.0, 0.0, 390.0), (0.0, 1.0, 0.0)),
    "j5": ((25.0, 0.0, 430.0), (0.0, 0.0, 1.0)),
    "j6": ((-15.0, 0.0, 475.0), (1.0, 0.0, 0.0)),
    "j7": ((-15.0, 0.0, 530.0), (0.0, 1.0, 0.0)),
}


def _v_add(a: Vector3, b: Vector3) -> Vector3:
    return tuple(a[i] + b[i] for i in range(3))  # type: ignore[return-value]


def _v_sub(a: Vector3, b: Vector3) -> Vector3:
    return tuple(a[i] - b[i] for i in range(3))  # type: ignore[return-value]


def _v_scale(a: Vector3, scale: float) -> Vector3:
    return tuple(value * scale for value in a)  # type: ignore[return-value]


def _dot(a: Vector3, b: Vector3) -> float:
    return sum(a[i] * b[i] for i in range(3))


def _norm(a: Vector3) -> float:
    return math.sqrt(_dot(a, a))


def _unit(a: Vector3) -> Vector3:
    magnitude = _norm(a)
    if magnitude < 1e-9:
        raise ValueError("zero-length direction")
    return _v_scale(a, 1.0 / magnitude)


def _box(
    x_length: float,
    y_length: float,
    z_length: float,
    center: Vector3,
) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(x_length, y_length, z_length)
        .translate(center)
    )


def _cylinder_x(radius: float, length: float, x_start: float) -> cq.Workplane:
    return cq.Workplane("YZ", origin=(x_start, 0.0, 0.0)).circle(radius).extrude(length)


def _orient_x(part: cq.Workplane, axis: Vector3, center: Vector3) -> cq.Workplane:
    """Rotate a canonical +X-axis feature onto a cardinal world axis."""

    axis = _unit(axis)
    if axis == (1.0, 0.0, 0.0):
        oriented = part
    elif axis == (0.0, 1.0, 0.0):
        oriented = part.rotate((0, 0, 0), (0, 0, 1), 90)
    elif axis == (0.0, 0.0, 1.0):
        oriented = part.rotate((0, 0, 0), (0, 1, 0), -90)
    elif axis == (0.0, 0.0, -1.0):
        oriented = part.rotate((0, 0, 0), (0, 1, 0), 90)
    else:
        raise ValueError(f"only cardinal joint axes are supported, got {axis}")
    return oriented.translate(center)


def build_socket() -> cq.Workplane:
    """Build one bearing pocket and tool-free AS5600 board carrier."""

    socket = _cylinder_x(JOINT_RADIUS, SOCKET_BODY_DEPTH, 0.0)
    socket = socket.cut(
        _cylinder_x(BEARING_POCKET_DIAMETER / 2.0, BEARING_POCKET_DEPTH + 0.02, -0.01)
    )
    socket = socket.cut(
        _cylinder_x(
            SHAFT_CLEARANCE_DIAMETER / 2.0,
            PCB_COMPONENT_FACE_X - BEARING_POCKET_DEPTH,
            BEARING_POCKET_DEPTH,
        )
    )

    board_long = AS5600_BOARD_LONG + PCB_EDGE_CLEARANCE * 2.0
    board_short = AS5600_BOARD_SHORT + PCB_EDGE_CLEARANCE * 2.0
    backplate = _box(
        BACKPLATE_THICKNESS,
        board_long + 3.0,
        board_short + 3.0,
        (PCB_BACK_X + BACKPLATE_THICKNESS / 2.0, 0.0, 0.0),
    )
    # A generous centre window prevents the PCB's rear pads from rubbing and
    # makes it possible to push the board back out with a fingertip.
    backplate = backplate.cut(
        _box(BACKPLATE_THICKNESS + 0.2, 15.0, 10.0, (PCB_BACK_X + 1.0, 0.0, 0.0))
    )
    socket = socket.union(backplate)

    # The bottom bridge connects the PCB carrier to the bearing body and acts
    # as a positive stop.  The top remains open so the populated board can be
    # slid down into the carrier after the axle has been snapped in.
    bridge_z = board_short / 2.0 + 1.35
    bridge_length_x = PCB_BACK_X + BACKPLATE_THICKNESS - SOCKET_BODY_DEPTH
    socket = socket.union(
        _box(
            bridge_length_x,
            board_long + 3.0,
            2.7,
            (
                SOCKET_BODY_DEPTH + bridge_length_x / 2.0,
                0.0,
                -bridge_z,
            ),
        )
    )

    # Four short front rails capture the PCB corners while leaving the Qwiic
    # connectors at the centres of the +/-Y edges clear.  The board slides
    # between these lips and the rear plate from the open +Z side.
    rail_y = board_long / 2.0 + 0.45
    for y_sign in (-1.0, 1.0):
        for z in (-6.2, 6.2):
            rail = _box(
                PCB_BACK_X + BACKPLATE_THICKNESS - PCB_COMPONENT_FACE_X,
                1.1,
                3.0,
                (
                    (PCB_COMPONENT_FACE_X + PCB_BACK_X + BACKPLATE_THICKNESS) / 2.0,
                    y_sign * rail_y,
                    z,
                ),
            )
            lip = _box(
                0.9,
                1.5,
                3.0,
                (PCB_COMPONENT_FACE_X - 0.45, y_sign * rail_y, z),
            )
            socket = socket.union(rail).union(lip)

    # Two compliant top latches flex rearward as the board slides down, then
    # catch its top edge.  They can be released with a small flat screwdriver.
    top_z = board_short / 2.0 + 0.6
    for y in (-6.0, 6.0):
        hook = _box(
            3.8,
            4.0,
            1.2,
            (PCB_BACK_X + 0.1, y, top_z + 0.6),
        )
        lip = _box(
            0.9,
            4.0,
            1.9,
            (PCB_COMPONENT_FACE_X - 0.45, y, top_z - 0.15),
        )
        socket = socket.union(hook).union(lip)

    return socket.clean()


def _snap_tab(top: bool) -> cq.Workplane:
    """Build one compliant axle barb; PETG is required for repeated flexing."""

    sign = 1.0 if top else -1.0
    profile = [
        (6.25, sign * 2.65),
        (6.25, sign * 3.75),
        (7.20, sign * 4.35),
        (10.55, sign * 3.78),
        (11.25, sign * 2.65),
    ]
    if not top:
        profile.reverse()
    return (
        # The XZ plane's positive normal points toward -Y.  Starting at
        # +1.75 mm therefore centres the 3.5 mm extrusion on the axle.
        cq.Workplane("XZ", origin=(0.0, 1.75, 0.0))
        .polyline(profile)
        .close()
        .extrude(3.5)
    )


def build_plug() -> cq.Workplane:
    """Build the moving flange, printed axle, snap tabs, and magnet pocket."""

    plug = _cylinder_x(FLANGE_RADIUS, FLANGE_THICKNESS, -FLANGE_THICKNESS)
    plug = plug.union(_cylinder_x(AXLE_DIAMETER / 2.0, 5.85, 0.0))
    plug = plug.union(_cylinder_x(2.80, AXLE_TIP_X - 5.85, 5.85))
    plug = plug.union(_snap_tab(top=True)).union(_snap_tab(top=False))
    magnet_pocket_start = AXLE_TIP_X - MAGNET_POCKET_DEPTH
    plug = plug.cut(
        _cylinder_x(
            MAGNET_POCKET_DIAMETER / 2.0,
            MAGNET_POCKET_DEPTH + 0.02,
            magnet_pocket_start,
        )
    )
    return plug.clean()


def _cylinder_between(start: Vector3, end: Vector3, radius: float) -> cq.Workplane:
    delta = _v_sub(end, start)
    solid = cq.Solid.makeCylinder(
        radius,
        _norm(delta),
        cq.Vector(*start),
        cq.Vector(*_unit(delta)),
    )
    return cq.Workplane("XY").newObject([solid])


def _radial_neck(
    center: Vector3,
    axis: Vector3,
    toward: Vector3,
) -> Tuple[cq.Workplane, Vector3]:
    """Leave a plug radially without entering the stationary socket."""

    axis = _unit(axis)
    toward_vector = _v_sub(toward, center)
    radial = _v_sub(toward_vector, _v_scale(axis, _dot(toward_vector, axis)))
    if _norm(radial) < 1e-6:
        fallback = (1.0, 0.0, 0.0) if abs(axis[0]) < 0.5 else (0.0, 0.0, 1.0)
        radial = _v_sub(fallback, _v_scale(axis, _dot(fallback, axis)))
    radial = _unit(radial)

    plane_origin = _v_sub(center, _v_scale(axis, FLANGE_THICKNESS))
    width_direction = _unit(
        (
            axis[1] * radial[2] - axis[2] * radial[1],
            axis[2] * radial[0] - axis[0] * radial[2],
            axis[0] * radial[1] - axis[1] * radial[0],
        )
    )
    plane = cq.Plane(
        origin=cq.Vector(*plane_origin),
        xDir=cq.Vector(*radial),
        normal=cq.Vector(*axis),
    )
    neck = (
        cq.Workplane(plane)
        .center(NECK_LENGTH / 2.0, 0.0)
        .rect(NECK_LENGTH, BEAM_RADIUS * 2.0)
        .extrude(FLANGE_THICKNESS)
    )
    waypoint = _v_add(
        _v_sub(center, _v_scale(axis, FLANGE_THICKNESS / 2.0)),
        _v_scale(radial, NECK_LENGTH),
    )
    # Silence type checkers and document the plane's second in-plane vector;
    # CadQuery derives the same vector internally from normal x xDir.
    assert abs(_dot(width_direction, radial)) < 1e-6
    return neck, waypoint


def _socket_neck(
    center: Vector3,
    axis: Vector3,
    toward: Vector3,
) -> Tuple[cq.Workplane, Vector3]:
    """Join a thick beam to a socket without entering the moving-flange side."""

    axis = _unit(axis)
    toward_vector = _v_sub(toward, center)
    radial = _v_sub(toward_vector, _v_scale(axis, _dot(toward_vector, axis)))
    if _norm(radial) < 1e-6:
        fallback = (1.0, 0.0, 0.0) if abs(axis[0]) < 0.5 else (0.0, 0.0, 1.0)
        radial = _v_sub(fallback, _v_scale(axis, _dot(fallback, axis)))
    radial = _unit(radial)

    plane = cq.Plane(
        origin=cq.Vector(*center),
        xDir=cq.Vector(*radial),
        normal=cq.Vector(*axis),
    )
    neck = (
        cq.Workplane(plane)
        .center(NECK_LENGTH / 2.0, 0.0)
        .rect(NECK_LENGTH, BEAM_RADIUS * 2.0)
        .extrude(SOCKET_BODY_DEPTH)
    )
    # This neck overlaps the socket for strength, so repeat the bearing and
    # axle cuts here; otherwise the union would silently fill the joint bore.
    local_void = _cylinder_x(
        BEARING_POCKET_DIAMETER / 2.0,
        BEARING_POCKET_DEPTH + 0.02,
        -0.01,
    ).union(
        _cylinder_x(
            SHAFT_CLEARANCE_DIAMETER / 2.0,
            SOCKET_BODY_DEPTH - BEARING_POCKET_DEPTH + 0.02,
            BEARING_POCKET_DEPTH,
        )
    )
    neck = neck.cut(_orient_x(local_void, axis, center))
    waypoint = _v_add(
        _v_add(center, _v_scale(axis, SOCKET_BODY_DEPTH / 2.0)),
        _v_scale(radial, NECK_LENGTH),
    )
    return neck, waypoint


def _joint_socket(name: str) -> cq.Workplane:
    center, axis = JOINTS[name]
    return _orient_x(build_socket(), axis, center)


def _joint_plug(name: str) -> cq.Workplane:
    center, axis = JOINTS[name]
    return _orient_x(build_plug(), axis, center)


def _link(proximal: str, distal: str) -> cq.Workplane:
    proximal_center, proximal_axis = JOINTS[proximal]
    distal_center, distal_axis = JOINTS[distal]
    part = _joint_plug(proximal)
    neck, waypoint = _radial_neck(proximal_center, proximal_axis, distal_center)
    socket_neck, socket_waypoint = _socket_neck(
        distal_center, distal_axis, proximal_center
    )
    part = part.union(neck)
    part = part.union(_cylinder_between(waypoint, socket_waypoint, BEAM_RADIUS))
    part = part.union(socket_neck)
    part = part.union(_joint_socket(distal))
    return part.clean()


def build_base() -> cq.Workplane:
    joint_center, _ = JOINTS["j1"]
    base = _box(150.0, 110.0, 8.0, (0.0, 0.0, 4.0))
    base = base.edges("|Z").fillet(8.0)
    # Twin columns support the downward-facing J1 socket while keeping the
    # board's top-loading path and both Qwiic connector ends unobstructed.
    # Stop below the moving-link beam; 3.5 mm of overlap with the socket body
    # remains for a strong union.
    column_height = joint_center[2] - 12.5
    for y_offset in (-8.0, 8.0):
        base = base.union(
            _box(
                6.0,
                6.0,
                column_height,
                (
                    joint_center[0] - 14.0,
                    joint_center[1] + y_offset,
                    8.0 + column_height / 2.0,
                ),
            )
        )
    base = base.union(_joint_socket("j1"))

    # Open electronics tray: Qwiic mux and QT Py attach with removable foam
    # tape, so it accepts board revisions without screws, nuts, or a lid.
    tray_center = (-33.0, 0.0, 9.5)
    tray_floor = _box(68.0, 50.0, 3.0, tray_center)
    base = base.union(tray_floor)
    for y in (-26.0, 26.0):
        base = base.union(_box(72.0, 2.0, 7.0, (-33.0, y, 11.5)))
    for x in (-69.0, 3.0):
        base = base.union(_box(2.0, 54.0, 7.0, (x, 0.0, 11.5)))

    # Four ordinary wood screws can secure the base to a board;
    # they drive into the board directly and do not require nuts.
    for x in (-65.0, 65.0):
        for y in (-45.0, 45.0):
            hole = (
                cq.Workplane("XY", origin=(x, y, -0.1))
                .circle(2.2)
                .extrude(8.2)
            )
            base = base.cut(hole)
    return base.clean()


def build_link_6() -> cq.Workplane:
    part = _link("j6", "j7")
    # Fixed palm grip is integral with link 6.  The separate gripper lever
    # pivots beside it, giving a simple squeeze input without a return spring.
    grip_start = (-40.0, 32.0, 546.0)
    grip_end = (-48.0, 32.0, 622.0)
    part = part.union(_cylinder_between(grip_start, grip_end, 10.0))
    part = part.union(_cylinder_between((-29.0, 4.0, 535.0), grip_start, 7.0))
    return part.clean()


def build_link_2() -> cq.Workplane:
    part = _link("j2", "j3")
    # Mid-arm placement keeps every purchased Qwiic lead at 400 mm or less.
    # The 60 x 42 mm open pad fits SparkFun BOB-16784 (about 54.6 x 35.6 mm)
    # and deliberately uses removable foam tape instead of nuts or standoffs.
    mux_pad = _box(60.0, 3.0, 42.0, (90.0, 0.0, 155.0))
    return part.union(mux_pad).clean()


def build_gripper_lever() -> cq.Workplane:
    center, axis = JOINTS["j7"]
    lever_target = (-9.0, -5.5, 590.0)
    part = _joint_plug("j7")
    neck, waypoint = _radial_neck(center, axis, lever_target)
    part = part.union(neck)
    part = part.union(_cylinder_between(waypoint, lever_target, 5.0))
    part = part.union(_cylinder_between(lever_target, (-17.0, -5.5, 610.0), 6.5))
    return part.clean()


def build_joint_fit_test() -> cq.Workplane:
    """Build a compact coupon containing one socket and one separate plug.

    The two solids intentionally share one STL so a slicer imports them at the
    correct scale.  They are separated by 12 mm and are not an assembly model.
    """

    socket = build_socket().rotate((0, 0, 0), (0, 1, 0), -90)
    plug = build_plug().rotate((0, 0, 0), (0, 1, 0), -90).translate((42.0, 0.0, 3.8))
    combined = socket.union(plug)
    bounds = combined.val().BoundingBox()
    return combined.translate((0.0, 0.0, -bounds.zmin))


def build_parts() -> Dict[str, cq.Workplane]:
    return {
        "simple_base": build_base(),
        "simple_link_1": _link("j1", "j2"),
        "simple_link_2": build_link_2(),
        "simple_link_3": _link("j3", "j4"),
        "simple_link_4": _link("j4", "j5"),
        "simple_link_5": _link("j5", "j6"),
        "simple_link_6": build_link_6(),
        "simple_gripper_lever": build_gripper_lever(),
    }


def _intersection_volume(a: cq.Workplane, b: cq.Workplane) -> float:
    intersection = a.intersect(b)
    return sum(solid.Volume() for solid in intersection.solids().vals())


def validate_parts(parts: Mapping[str, cq.Workplane]) -> None:
    expected_names = {
        "simple_base",
        "simple_link_1",
        "simple_link_2",
        "simple_link_3",
        "simple_link_4",
        "simple_link_5",
        "simple_link_6",
        "simple_gripper_lever",
    }
    if set(parts) != expected_names:
        raise RuntimeError(f"unexpected print manifest: {sorted(parts)}")

    for name, part in parts.items():
        solids = part.solids().vals()
        if len(solids) != 1:
            raise RuntimeError(f"{name} must be one connected solid, found {len(solids)}")
        if not part.val().isValid():
            raise RuntimeError(f"{name} is not a valid CAD solid")
        if part.val().Volume() < 1200.0:
            raise RuntimeError(f"{name} has unexpectedly low volume")

    ordered = [
        "simple_base",
        "simple_link_1",
        "simple_link_2",
        "simple_link_3",
        "simple_link_4",
        "simple_link_5",
        "simple_link_6",
        "simple_gripper_lever",
    ]
    for parent, child in zip(ordered, ordered[1:]):
        overlap = _intersection_volume(parts[parent], parts[child])
        if overlap > 0.1:
            raise RuntimeError(f"{parent} and {child} interfere by {overlap:.3f} mm^3")


def _print_orientation(name: str, part: cq.Workplane) -> cq.Workplane:
    if name in {"simple_link_1", "simple_link_5", "simple_base"}:
        printable = part
    elif name in {"simple_link_2", "simple_link_3", "simple_link_4", "simple_gripper_lever"}:
        printable = part.rotate((0, 0, 0), (1, 0, 0), 90)
    elif name == "simple_link_6":
        printable = part.rotate((0, 0, 0), (0, 1, 0), -90)
    else:
        raise KeyError(name)
    bounds = printable.val().BoundingBox()
    return printable.translate((-bounds.xmin, -bounds.ymin, -bounds.zmin))


def _normalize_step(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


def export_parts(parts: Mapping[str, cq.Workplane], output_dir: Path) -> None:
    step_dir = output_dir / "step"
    stl_dir = output_dir / "stl"
    step_dir.mkdir(parents=True, exist_ok=True)
    stl_dir.mkdir(parents=True, exist_ok=True)
    for name, part in parts.items():
        step_path = step_dir / f"{name}.step"
        cq.exporters.export(part, str(step_path))
        _normalize_step(step_path)
        cq.exporters.export(
            _print_orientation(name, part),
            str(stl_dir / f"{name}.stl"),
            tolerance=0.08,
            angularTolerance=0.15,
        )

    fit_test = build_joint_fit_test()
    fit_step = step_dir / "joint_fit_test.step"
    cq.exporters.export(fit_test, str(fit_step))
    _normalize_step(fit_step)
    cq.exporters.export(
        fit_test,
        str(stl_dir / "joint_fit_test.stl"),
        tolerance=0.06,
        angularTolerance=0.12,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent / "generated",
    )
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    parts = build_parts()
    validate_parts(parts)
    if not args.validate_only:
        export_parts(parts, args.output_dir)
        print(f"Exported {len(parts)} structural parts plus joint_fit_test to {args.output_dir}")


if __name__ == "__main__":
    main()

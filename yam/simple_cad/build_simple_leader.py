"""Generate the load-bearing, no-solder potentiometer YAM leader.

The design uses one repeated joint architecture.  The stationary side of each
joint contains a 6000-2RS bearing pocket and a snap carrier for a factory-wired
WH148 potentiometer.  The moving link contains a hollow axle and compliant
retention/coupling fingers.  The bearing and printed flange carry the arm; the
potentiometer shaft transmits sensing torque only.  Those features are part of
the structural links, so there are no separate sensor housings, couplers,
washers, nuts, or joint screws.

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
BEARING_OD = 26.0
BEARING_ID = 10.0
BEARING_WIDTH = 8.0
POT_BODY_DIAMETER = 17.0
POT_BODY_THICKNESS = 9.0
POT_BUSHING_DIAMETER = 7.0
POT_SHAFT_DIAMETER = 6.0
POT_SHAFT_PROJECTION = 15.0
NANO_SHIELD_LONG = 58.0
NANO_SHIELD_SHORT = 54.0

# Printer-tunable fits.  Defaults target a reasonably calibrated FDM printer.
BEARING_POCKET_DIAMETER = 26.20
BEARING_POCKET_DEPTH = 8.15
AXLE_DIAMETER = 9.80
SHAFT_CLEARANCE_DIAMETER = 13.00
POT_BODY_CLEARANCE = 0.45
POT_BUSHING_CLEARANCE = 0.35
POT_SHAFT_SOCKET_DIAMETER = 5.85
NANO_SHIELD_EDGE_CLEARANCE = 0.60

# Controller placement and assumed cable budget.  The seller does not specify
# the factory lead length, so 200 mm is a modeling assumption to verify against
# the delivered parts.  The chain is roughly 400 mm long; extensions are part
# of the BOM and ``validate_cable_reach`` enforces the modeled budget.
# The current tray intersects link 5 in a known folded wrist pose; the
# regression test records that unresolved mechanical constraint.
CONTROLLER_TRAY_CENTER = (30.0, 45.0, 225.0)
CONTROLLER_PART_INDEX = 3  # simple_link_3 carries the shield tray
POT_LEAD_LENGTH = 200.0
EXTENSION_LEAD_LENGTH = 300.0
CABLE_ROUTING_FACTOR = 1.25  # the cable follows the links, not the straight line
CABLE_SERVICE_LOOP = 35.0  # slack per rotating joint a run crosses
CABLE_TERMINATION_ALLOWANCE = 20.0  # both connector bodies plus strain relief

# Base pedestal.  Link 1 sweeps the volume directly under the J1 socket, so the
# pedestal may only reach that socket through the wedge behind J1's travel.
BASE_PLATE_LENGTH = 110.0
BASE_PLATE_WIDTH = 90.0
BASE_PLATE_THICKNESS = 8.0
BUTTRESS_X_MIN = -4.0
BUTTRESS_X_MAX = 22.0
BUTTRESS_HALF_WIDTH = 16.0
J1_SWEEP_RADIUS = 39.0  # link 1's neck and beam reach this far from the J1 axis
J1_SWEEP_Z_MAX = 49.3  # top of the J1 socket, above which nothing of link 1 passes
# The neck's corner lies exactly on the ideal sweep envelope, so the envelope
# needs real margin or the pedestal is tangent to the link at the stop.
J1_SWEEP_ANGULAR_MARGIN = 4.0

# Joint envelope and sensor stack.  The potentiometer is inserted from the top
# after the structural axle has snapped through the bearing.  Its shaft then
# presses into the split socket at the unloaded end of the axle.
JOINT_RADIUS = 17.5
SOCKET_BODY_DEPTH = 9.0
POT_BODY_FRONT_X = 23.5
POT_BODY_BACK_X = POT_BODY_FRONT_X + POT_BODY_THICKNESS + POT_BODY_CLEARANCE
POT_HOLDER_BACK_X = POT_BODY_BACK_X + 2.0
AXLE_TIP_X = POT_BODY_FRONT_X - POT_SHAFT_PROJECTION + 5.0
FLANGE_THICKNESS = 3.8
FLANGE_RADIUS = 16.5
STOP_RADIUS = 13.1
STOP_PIN_RADIUS = 1.25
STOP_GROOVE_INNER_RADIUS = 11.25
STOP_GROOVE_OUTER_RADIUS = 14.95
STOP_GROOVE_DEPTH = 2.4
# Clearance cut past each end of a joint's declared travel.  The stop pin itself
# subtends about 5.5 degrees at STOP_RADIUS, so this must exceed that or the pin
# fouls the end of its own groove at the zero pose.  Every degree beyond that is
# overtravel the rest of the design has to stay collision-free through.
STOP_ANGULAR_CLEARANCE = 8.0

BEAM_RADIUS = 6.5
NECK_LENGTH = 25.0

# A compact leader is easier to move than a 1:1 replica.  Joint-space mapping
# means the link lengths do not affect commanded follower angles.  The axis
# order matches YAM: Z, Y, Y, Y, Z, X, followed by the gripper input on Y.
JOINTS: Mapping[str, Tuple[Vector3, Vector3]] = {
    # J1 points upward so its cable exits near the mid-arm controller.  The
    # moving flange and link remain below the stationary sensor stack.
    "j1": ((35.0, 0.0, 40.0), (0.0, 0.0, 1.0)),
    "j2": ((80.0, 0.0, 90.0), (0.0, 1.0, 0.0)),
    "j3": ((80.0, 0.0, 175.0), (0.0, 1.0, 0.0)),
    "j4": ((80.0, 0.0, 260.0), (0.0, 1.0, 0.0)),
    "j5": ((25.0, 0.0, 300.0), (0.0, 0.0, 1.0)),
    "j6": ((-35.0, 0.0, 340.0), (1.0, 0.0, 0.0)),
    "j7": ((-35.0, 0.0, 395.0), (0.0, 1.0, 0.0)),
}

# Physical leader stops in degrees.  J1 deliberately uses 280 degrees of the
# nominal 300-degree potentiometer and is scaled 325/280 in host software.
# Every other arm axis fits inside the pot travel without scaling.
JOINT_LIMITS_DEG: Mapping[str, Tuple[float, float]] = {
    "j1": (-140.0, 140.0),
    "j2": (-105.0, 105.0),
    "j3": (-105.0, 105.0),
    "j4": (-90.0, 90.0),
    "j5": (-90.0, 90.0),
    "j6": (-120.0, 120.0),
    "j7": (0.0, 45.0),
}


# Where the base blocks a joint before its printed stop does.  J2's negative
# swing drives link 2 and link 3 into the base plate at about -90 degrees, well
# inside its declared -105.  This is a measured limitation of the link geometry,
# not something the stops enforce, and the host mapping has to respect it or the
# follower is commanded to a pose the leader cannot physically reach.
BASE_LIMITED_RANGE_DEG: Mapping[str, Tuple[float, float]] = {
    "j2": (-89.8, math.inf),
    # J3 clears its declared -105 and only grazes the plate 2.5 degrees into the
    # overtravel band, so this trims the overtravel rather than the spec.
    "j3": (-107.4, math.inf),
}


def stop_pin_half_angle() -> float:
    """Angular half-width of the stop pin at its own radius."""

    return math.degrees(math.asin(STOP_PIN_RADIUS / STOP_RADIUS))


def stop_limited_range(joint: str) -> Tuple[float, float]:
    """Travel the printed stops actually permit, which is not the declared range.

    The groove is cut ``STOP_ANGULAR_CLEARANCE`` past each end of the declared
    range, but the pin stops when its *edge* meets the end of the groove, not
    its centre.  Everything downstream -- the base pedestal wedge and the
    collision suite -- has to use this rather than the nominal limits.
    """

    lower, upper = JOINT_LIMITS_DEG[joint]
    overtravel = max(0.0, STOP_ANGULAR_CLEARANCE - stop_pin_half_angle())
    return lower - overtravel, upper + overtravel


def usable_range(joint: str) -> Tuple[float, float]:
    """Travel that is both inside the printed stops and clear of the base."""

    lower, upper = stop_limited_range(joint)
    blocked = BASE_LIMITED_RANGE_DEG.get(joint)
    if blocked is not None:
        lower = max(lower, blocked[0])
        upper = min(upper, blocked[1])
    return lower, upper


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


def _annular_sector_x(
    inner_radius: float,
    outer_radius: float,
    start_degrees: float,
    end_degrees: float,
    depth: float,
    x_start: float,
) -> cq.Workplane:
    """Extrude a sampled annular sector along +X."""

    if end_degrees <= start_degrees:
        raise ValueError("annular sector end must follow start")
    sweep = end_degrees - start_degrees
    samples = max(8, int(math.ceil(sweep / 4.0)))
    angles = [
        math.radians(start_degrees + sweep * index / samples)
        for index in range(samples + 1)
    ]
    outer = [(outer_radius * math.cos(a), outer_radius * math.sin(a)) for a in angles]
    inner = [
        (inner_radius * math.cos(a), inner_radius * math.sin(a))
        for a in reversed(angles)
    ]
    return (
        cq.Workplane("YZ", origin=(x_start, 0.0, 0.0))
        .polyline(outer + inner)
        .close()
        .extrude(depth)
    )


def _annular_sector_z(
    inner_radius: float,
    outer_radius: float,
    start_degrees: float,
    end_degrees: float,
    height: float,
    z_start: float,
    center: Tuple[float, float],
) -> cq.Workplane:
    """Extrude a sampled annular sector along +Z about ``center``."""

    if end_degrees <= start_degrees:
        raise ValueError("annular sector end must follow start")
    sweep = end_degrees - start_degrees
    samples = max(8, int(math.ceil(sweep / 4.0)))
    angles = [
        math.radians(start_degrees + sweep * index / samples)
        for index in range(samples + 1)
    ]
    outer = [
        (center[0] + outer_radius * math.cos(a), center[1] + outer_radius * math.sin(a))
        for a in angles
    ]
    inner = [
        (center[0] + inner_radius * math.cos(a), center[1] + inner_radius * math.sin(a))
        for a in reversed(angles)
    ]
    return (
        cq.Workplane("XY", origin=(0.0, 0.0, z_start))
        .polyline(outer + inner)
        .close()
        .extrude(height)
    )


def _socket_void() -> cq.Workplane:
    """Bearing pocket plus shaft clearance, in canonical +X socket coordinates.

    Anything unioned onto a socket has to repeat this cut or it silently fills
    the joint bore.
    """

    return _cylinder_x(
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


def build_socket() -> cq.Workplane:
    """Build one bearing pocket and top-loading potentiometer carrier."""

    socket = _cylinder_x(JOINT_RADIUS, SOCKET_BODY_DEPTH, 0.0)
    socket = socket.cut(
        _cylinder_x(BEARING_POCKET_DIAMETER / 2.0, BEARING_POCKET_DEPTH + 0.02, -0.01)
    )
    socket = socket.cut(
        _cylinder_x(
            SHAFT_CLEARANCE_DIAMETER / 2.0,
            SOCKET_BODY_DEPTH - BEARING_POCKET_DEPTH + 0.02,
            BEARING_POCKET_DEPTH,
        )
    )

    # A stationary pin runs in a recessed arc in the moving flange.  The arc
    # ends, rather than the potentiometer's delicate internal stops, absorb an
    # accidental over-rotation.
    stop_pin = _cylinder_x(
        STOP_PIN_RADIUS,
        STOP_GROOVE_DEPTH + 0.8,
        -STOP_GROOVE_DEPTH,
    ).translate((0.0, STOP_RADIUS, 0.0))
    socket = socket.union(stop_pin)

    body_cavity = POT_BODY_DIAMETER + POT_BODY_CLEARANCE
    holder_width = body_cavity + 3.6
    holder_height = body_cavity + 3.6
    holder_mid_x = (POT_BODY_FRONT_X + POT_HOLDER_BACK_X) / 2.0
    holder_length = POT_HOLDER_BACK_X - POT_BODY_FRONT_X

    # Bottom and side rails form an open-top cradle.  The round body drops in
    # after the joint is assembled; the factory-wired rear terminals remain
    # accessible through the large U-shaped back opening.
    socket = socket.union(
        _box(holder_length, holder_width, 2.4, (holder_mid_x, 0.0, -holder_height / 2.0))
    )
    for y_sign in (-1.0, 1.0):
        socket = socket.union(
            _box(
                holder_length,
                2.0,
                holder_height,
                (holder_mid_x, y_sign * holder_width / 2.0, 0.0),
            )
        )
        # The side walls flex just enough for these lips to retain the body.
        socket = socket.union(
            _box(
                holder_length - 1.0,
                1.8,
                1.2,
                (
                    holder_mid_x + 0.5,
                    y_sign * (body_cavity / 2.0 - 0.25),
                    body_cavity / 2.0 + 0.35,
                ),
            )
        )

    # The front U-plate locates the threaded bushing without using its nut.
    front_plate = _box(
        2.0,
        holder_width,
        holder_height,
        (POT_BODY_FRONT_X - 1.0, 0.0, 0.0),
    )
    bushing_slot = _cylinder_x(
        (POT_BUSHING_DIAMETER + POT_BUSHING_CLEARANCE) / 2.0,
        2.2,
        POT_BODY_FRONT_X - 2.1,
    ).union(
        _box(
            2.2,
            POT_BUSHING_DIAMETER + POT_BUSHING_CLEARANCE,
            holder_height / 2.0 + 0.2,
            (
                POT_BODY_FRONT_X - 1.0,
                0.0,
                holder_height / 4.0 + 0.1,
            ),
        )
    )
    socket = socket.union(front_plate.cut(bushing_slot))

    # A U-shaped rear plate prevents axial motion while leaving the prewired
    # terminals and cable strain relief unobstructed.
    rear_plate = _box(
        2.0,
        holder_width,
        holder_height,
        (POT_HOLDER_BACK_X - 1.0, 0.0, 0.0),
    )
    rear_opening = _box(
        2.2,
        body_cavity - 4.0,
        holder_height - 3.0,
        (POT_HOLDER_BACK_X - 1.0, 0.0, 2.0),
    )
    socket = socket.union(rear_plate.cut(rear_opening))

    # A concentric support tube makes the carrier stiff while leaving the full
    # radial sweep clear for the moving link.  The 13 mm bore surrounds the
    # 9.8 mm axle/coupling without carrying its load.
    bridge_length = POT_BODY_FRONT_X - SOCKET_BODY_DEPTH
    support_tube = _cylinder_x(
        8.25,
        bridge_length,
        SOCKET_BODY_DEPTH,
    ).cut(
        _cylinder_x(
            SHAFT_CLEARANCE_DIAMETER / 2.0,
            bridge_length + 0.2,
            SOCKET_BODY_DEPTH - 0.1,
        )
    )
    socket = socket.union(support_tube)

    return socket.clean()


def _snap_tab(top: bool) -> cq.Workplane:
    """Build one compliant axle barb; PETG is required for repeated flexing."""

    sign = 1.0 if top else -1.0
    profile = [
        (7.15, sign * 3.20),
        (7.15, sign * 4.45),
        (8.45, sign * 5.35),
        (11.00, sign * 5.30),
        (11.75, sign * 4.45),
        (11.75, sign * 3.20),
    ]
    if not top:
        profile.reverse()
    return (
        # The XZ plane's positive normal points toward -Y.  Starting at +3 mm
        # therefore centres the 6 mm extrusion on the axle.
        cq.Workplane("XZ", origin=(0.0, 3.0, 0.0))
        .polyline(profile)
        .close()
        .extrude(6.0)
    )


def _stop_groove(lower_degrees: float, upper_degrees: float) -> cq.Workplane:
    """Return the moving-side clearance swept by the stationary stop pin."""

    # At zero pose the stationary pin is at angle zero.  In the moving frame
    # it sweeps in the opposite direction as the joint rotates.
    groove_start = -upper_degrees - STOP_ANGULAR_CLEARANCE
    groove_end = -lower_degrees + STOP_ANGULAR_CLEARANCE
    return _annular_sector_x(
        STOP_GROOVE_INNER_RADIUS,
        STOP_GROOVE_OUTER_RADIUS,
        groove_start,
        groove_end,
        STOP_GROOVE_DEPTH + 0.2,
        -STOP_GROOVE_DEPTH - 0.1,
    )


def build_plug(lower_degrees: float = -90.0, upper_degrees: float = 90.0) -> cq.Workplane:
    """Build the moving flange, hollow snap axle, coupling, and hard-stop arc."""

    plug = _cylinder_x(FLANGE_RADIUS, FLANGE_THICKNESS, -FLANGE_THICKNESS)
    plug = plug.union(_cylinder_x(AXLE_DIAMETER / 2.0, AXLE_TIP_X, 0.0))
    plug = plug.union(_snap_tab(top=True)).union(_snap_tab(top=False))

    # The shaft socket begins behind the bearing, so the load-bearing portion
    # of the axle remains solid.  A narrow relief slot turns the rear section
    # into two compliant jaws which grip the pot's 6 mm knurled shaft.
    shaft_socket_start = BEARING_POCKET_DEPTH + 0.30
    plug = plug.cut(
        _cylinder_x(
            POT_SHAFT_SOCKET_DIAMETER / 2.0,
            AXLE_TIP_X - shaft_socket_start + 0.2,
            shaft_socket_start,
        )
    )
    plug = plug.cut(
        _box(
            AXLE_TIP_X - shaft_socket_start + 0.4,
            AXLE_DIAMETER + 1.0,
            0.85,
            (
                shaft_socket_start + (AXLE_TIP_X - shaft_socket_start) / 2.0,
                0.0,
                0.0,
            ),
        )
    )

    plug = plug.cut(_stop_groove(lower_degrees, upper_degrees))
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
    length: float = NECK_LENGTH,
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
        .center(length / 2.0, 0.0)
        .rect(length, BEAM_RADIUS * 2.0)
        .extrude(FLANGE_THICKNESS)
    )
    waypoint = _v_add(
        _v_sub(center, _v_scale(axis, FLANGE_THICKNESS / 2.0)),
        _v_scale(radial, length),
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
    neck = neck.cut(_orient_x(_socket_void(), axis, center))
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
    return _orient_x(build_plug(*JOINT_LIMITS_DEG[name]), axis, center)


def _joint_stop_groove(name: str) -> cq.Workplane:
    center, axis = JOINTS[name]
    return _orient_x(_stop_groove(*JOINT_LIMITS_DEG[name]), axis, center)


def _link(proximal: str, distal: str) -> cq.Workplane:
    proximal_center, proximal_axis = JOINTS[proximal]
    distal_center, distal_axis = JOINTS[distal]
    part = _joint_plug(proximal)
    proximal_neck_length = 32.0 if proximal == "j1" else NECK_LENGTH
    neck, waypoint = _radial_neck(
        proximal_center,
        proximal_axis,
        distal_center,
        length=proximal_neck_length,
    )
    socket_neck, socket_waypoint = _socket_neck(
        distal_center, distal_axis, proximal_center
    )
    part = part.union(neck)
    part = part.union(_cylinder_between(waypoint, socket_waypoint, BEAM_RADIUS))
    part = part.union(socket_neck)
    part = part.union(_joint_socket(distal))
    # The radial neck can overlap the recessed stop arc when the joint points
    # toward the pin.  Recut the arc after all unions so the stop path remains
    # clear throughout the advertised range.
    part = part.cut(_joint_stop_groove(proximal))
    return part.clean()


def _link_1_sweep() -> cq.Workplane:
    """The volume link 1 sweeps under the J1 socket, as a cut tool for the base.

    The flange is a full disc, so no pedestal material may sit under it at any
    angle.  Outside the flange the neck and beam only sweep J1's stop-limited
    travel, which leaves a wedge behind the joint for the pedestal to reach the
    socket wall through.  That wedge carries the entire arm, so it is derived
    from the travel rather than guessed, and it widens with radius: a beam of a
    given width subtends less angle the further out it is.
    """

    center, _ = JOINTS["j1"]
    center_xy = (center[0], center[1])
    clearance = 0.3
    sweep_bottom = center[2] - FLANGE_THICKNESS - clearance
    height = J1_SWEEP_Z_MAX - sweep_bottom
    inner_radius = FLANGE_RADIUS + 0.5

    disc = (
        cq.Workplane("XY", origin=(0.0, 0.0, sweep_bottom))
        .center(*center_xy)
        .circle(inner_radius)
        .extrude(FLANGE_THICKNESS + 2.0 * clearance)
    )

    lower, upper = stop_limited_range("j1")
    reach = max(abs(lower), abs(upper))

    def free_half_angle(radius: float) -> float:
        """Half-angle of the wedge the sweep leaves clear at this radius."""

        beam_half = math.degrees(math.asin(min(1.0, BEAM_RADIUS / radius)))
        return 180.0 - reach - beam_half - J1_SWEEP_ANGULAR_MARGIN

    if free_half_angle(inner_radius) <= 1.0:
        raise RuntimeError(
            "J1's travel leaves no wedge for the base pedestal to reach the socket"
        )

    band = (
        cq.Workplane("XY", origin=(0.0, 0.0, sweep_bottom))
        .center(*center_xy)
        .circle(J1_SWEEP_RADIUS)
        .circle(inner_radius)
        .extrude(height)
    )

    # Run the wedge well past the band so its closing chords fall outside the
    # region being cut; otherwise a chord would shave material off the wedge.
    outer_radius = J1_SWEEP_RADIUS * 1.4
    # The boundary turns fastest just outside the flange, so sample radius
    # geometrically rather than uniformly.
    samples = 40
    ratio = outer_radius / inner_radius
    radii = [inner_radius * ratio ** (index / samples) for index in range(samples + 1)]

    def point(radius: float, degrees: float) -> Tuple[float, float]:
        angle = math.radians(degrees)
        return (
            center_xy[0] + radius * math.cos(angle),
            center_xy[1] + radius * math.sin(angle),
        )

    boundary = [point(r, 180.0 - free_half_angle(r)) for r in radii]
    boundary += [point(r, 180.0 + free_half_angle(r)) for r in reversed(radii)]
    wedge = (
        cq.Workplane("XY", origin=(0.0, 0.0, sweep_bottom))
        .polyline(boundary)
        .close()
        .extrude(height)
    )
    return disc.union(band.cut(wedge))


def build_base() -> cq.Workplane:
    joint_center, joint_axis = JOINTS["j1"]
    base = _box(
        BASE_PLATE_LENGTH,
        BASE_PLATE_WIDTH,
        BASE_PLATE_THICKNESS,
        (0.0, 0.0, BASE_PLATE_THICKNESS / 2.0),
    )
    base = base.edges("|Z").fillet(8.0)

    # One buttressed pedestal replaces the original pair of 6 mm columns.  Those
    # met the J1 socket only through two small stub lenses, so every newton the
    # arm applied crossed a section modulus of roughly 70 mm^3 in PETG, across
    # the layer lines.  A single slab reaching the socket wall through the wedge
    # behind J1's travel carries the same load through more than ten times that.
    buttress_height = joint_center[2] + SOCKET_BODY_DEPTH - BASE_PLATE_THICKNESS
    buttress = _box(
        BUTTRESS_X_MAX - BUTTRESS_X_MIN,
        BUTTRESS_HALF_WIDTH * 2.0,
        buttress_height,
        (
            (BUTTRESS_X_MIN + BUTTRESS_X_MAX) / 2.0,
            joint_center[1],
            BASE_PLATE_THICKNESS + buttress_height / 2.0,
        ),
    )
    # The pedestal overlaps the socket wall so the two fuse into one section
    # rather than merely touching, so it has to repeat the joint bore cut.
    buttress = buttress.cut(_orient_x(_socket_void(), joint_axis, joint_center))
    buttress = buttress.cut(_link_1_sweep())
    base = base.union(buttress)
    base = base.union(_joint_socket("j1"))

    # Four ordinary wood screws can secure the base to a board;
    # they drive into the board directly and do not require nuts.
    for x in (-47.0, 47.0):
        for y in (-37.0, 37.0):
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
    # pivots beside it.  The lever's integral PETG leaf bears on the small post
    # below, returning the gripper to its released/deadman-off position.
    joint_center, _ = JOINTS["j7"]
    grip_start = (joint_center[0] - 16.5, 27.0, joint_center[2] + 8.5)
    grip_end = (joint_center[0] - 21.5, 27.0, joint_center[2] + 62.5)
    part = part.union(_cylinder_between(grip_start, grip_end, 9.0))
    palm_root = (joint_center[0] - 16.0, 7.0, joint_center[2])
    part = part.union(_cylinder_between(palm_root, grip_start, 6.5))
    spring_x = joint_center[0] + 12.0
    spring_z = joint_center[2] + 19.5
    spring_post = _cylinder_between(
        (spring_x, -5.0, spring_z), (spring_x, 5.0, spring_z), 1.5
    )
    spring_post_root = _cylinder_between(
        (joint_center[0] + 16.0, 3.0, joint_center[2]),
        (spring_x, 3.0, spring_z),
        2.0,
    )
    part = part.union(spring_post).union(spring_post_root)
    return part.clean()


def build_link_3() -> cq.Workplane:
    part = _link("j3", "j4")
    # The controller sits near the chain midpoint to keep every sensor run as
    # short as possible; ``validate_cable_reach`` says which channels still need
    # an extension lead.  Four low corner clips retain the standard Nano I/O
    # shield without tape, screws, nuts, or a separate enclosure.
    tray_long = NANO_SHIELD_LONG + NANO_SHIELD_EDGE_CLEARANCE * 2.0
    tray_short = NANO_SHIELD_SHORT + NANO_SHIELD_EDGE_CLEARANCE * 2.0
    tray_center = CONTROLLER_TRAY_CENTER
    # Everything below follows the tray constant, including which side of the
    # link it hangs on, so moving the tray moves its mounts and clips with it.
    side = 1.0 if tray_center[1] >= 0.0 else -1.0
    part = part.union(_box(tray_long + 4.0, 2.4, tray_short + 4.0, tray_center))
    # Two short side standoffs attach the tray to link 3 while leaving the
    # neighbouring links' swept volume clear at the assembly zero pose.
    beam_x = JOINTS["j4"][0][0]
    standoff_x = tray_center[0] + 30.0
    for z in (tray_center[2] - 17.0, tray_center[2]):
        part = part.union(
            _cylinder_between(
                (beam_x, 0.0, z), (standoff_x, tray_center[1], z), 3.0
            )
        )
    for x_sign in (-1.0, 1.0):
        for z_sign in (-1.0, 1.0):
            x = tray_center[0] + x_sign * (tray_long / 2.0 + 1.0)
            z = tray_center[2] + z_sign * (tray_short / 2.0 + 1.0)
            post = _box(3.0, 7.0, 8.0, (x, tray_center[1] + side * 2.3, z))
            lip = _box(
                5.0,
                1.4,
                5.0,
                (x - x_sign * 1.0, tray_center[1] + side * 5.9, z - z_sign * 1.0),
            )
            part = part.union(post).union(lip)
    return part.clean()


def build_gripper_lever() -> cq.Workplane:
    center, axis = JOINTS["j7"]
    lever_target = (center[0] + 5.5, -5.5, center[2] + 38.5)
    part = _joint_plug("j7")
    neck, waypoint = _radial_neck(center, axis, lever_target)
    part = part.union(neck)
    part = part.union(_cylinder_between(waypoint, lever_target, 5.0))
    lever_end = (center[0] + 1.5, -5.5, center[2] + 57.5)
    part = part.union(_cylinder_between(lever_target, lever_end, 6.5))
    # A thin radial leaf reaches the fixed post on link 6 after a few degrees
    # of squeeze.  It bends in-plane and returns the lever when released.
    spring_leaf = _box(
        1.2,
        5.0,
        21.0,
        (center[0] + 0.6, -5.5, center[2] + 10.3),
    )
    spring_tip = _box(
        9.2,
        5.0,
        1.2,
        (center[0] + 5.2, -5.5, center[2] + 19.0),
    )
    part = part.union(spring_leaf).union(spring_tip)
    part = part.cut(_joint_stop_groove("j7"))
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


PART_ORDER: Tuple[str, ...] = (
    "simple_base",
    "simple_link_1",
    "simple_link_2",
    "simple_link_3",
    "simple_link_4",
    "simple_link_5",
    "simple_link_6",
    "simple_gripper_lever",
)


def _pot_terminal(joint: str) -> Vector3:
    """Where a joint's potentiometer leads leave its carrier."""

    center, axis = JOINTS[joint]
    return _v_add(center, _v_scale(_unit(axis), POT_HOLDER_BACK_X))


def cable_runs() -> Dict[str, Dict[str, float]]:
    """Length of lead each channel needs to reach the controller tray.

    Joint ``jN``'s potentiometer is carried by the socket side of that joint,
    which is part ``N - 1``, so the number of rotating joints a run crosses is
    its distance along the chain from the part holding the tray.  Each crossing
    needs a service loop or the cable becomes a spring the joint has to fight.
    """

    runs: Dict[str, Dict[str, float]] = {}
    for index, joint in enumerate(JOINTS):
        crossings = abs(index - CONTROLLER_PART_INDEX)
        straight = _norm(_v_sub(CONTROLLER_TRAY_CENTER, _pot_terminal(joint)))
        required = (
            straight * CABLE_ROUTING_FACTOR
            + CABLE_SERVICE_LOOP * crossings
            + CABLE_TERMINATION_ALLOWANCE
        )
        runs[joint] = {
            "straight_mm": straight,
            "joints_crossed": float(crossings),
            "required_mm": required,
            "needs_extension": float(required > POT_LEAD_LENGTH),
        }
    return runs


def extension_channels() -> Tuple[str, ...]:
    """Channels whose factory lead alone cannot reach the tray."""

    return tuple(
        joint for joint, run in cable_runs().items() if run["needs_extension"]
    )


def validate_cable_reach() -> None:
    budget = POT_LEAD_LENGTH + EXTENSION_LEAD_LENGTH
    for joint, run in cable_runs().items():
        if run["required_mm"] > budget:
            raise RuntimeError(
                f"{joint} needs about {run['required_mm']:.0f} mm of lead to "
                f"reach the controller but the budget is {budget:.0f} mm"
            )


def build_parts() -> Dict[str, cq.Workplane]:
    return {
        "simple_base": build_base(),
        "simple_link_1": _link("j1", "j2"),
        "simple_link_2": _link("j2", "j3"),
        "simple_link_3": build_link_3(),
        "simple_link_4": _link("j4", "j5"),
        "simple_link_5": _link("j5", "j6"),
        "simple_link_6": build_link_6(),
        "simple_gripper_lever": build_gripper_lever(),
    }


def _intersection_volume(a: cq.Workplane, b: cq.Workplane) -> float:
    intersection = a.intersect(b)
    return sum(solid.Volume() for solid in intersection.solids().vals())


def validate_parts(parts: Mapping[str, cq.Workplane]) -> None:
    validate_cable_reach()
    expected_names = set(PART_ORDER)
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

    for parent, child in zip(PART_ORDER, PART_ORDER[1:]):
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
    needs = extension_channels()
    print("Cable budget (assumed factory lead is " f"{POT_LEAD_LENGTH:.0f} mm):")
    for joint, run in cable_runs().items():
        flag = " EXTENSION" if run["needs_extension"] else ""
        print(
            f"  {joint}: {run['straight_mm']:6.1f} mm direct, "
            f"{int(run['joints_crossed'])} joints crossed, "
            f"{run['required_mm']:6.1f} mm needed{flag}"
        )
    print(f"{len(needs)} of {len(cable_runs())} channels need an extension lead: {', '.join(needs)}")


if __name__ == "__main__":
    main()

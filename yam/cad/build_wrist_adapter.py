"""Build the two-piece adapter that adds YAM's sixth arm axis.

The adapter uses the 40 mm circular interface shared by the existing encoder
and bearing housings. The base bolts to the output side of the existing wrist
joint. The keyed upright supports one additional encoder cartridge at 90
degrees. Both pieces have a flat print orientation and require no support.
"""

import argparse
from pathlib import Path
from typing import Dict

import cadquery as cq

FLANGE_DIAMETER = 40.0
FLANGE_THICKNESS = 5.0
BOLT_CIRCLE_RADIUS = 15.525
M3_CLEARANCE_DIAMETER = 3.2
CENTER_CLEARANCE_DIAMETER = 12.0

# Upright-local dimensions. In the assembly its leg bottoms sit on top of the
# five-millimetre base flange, putting the cartridge axis 29 mm above the base.
UPRIGHT_CENTER_HEIGHT = 24.0
UPRIGHT_THICKNESS = 5.0
LEG_WIDTH = 9.0
LEG_CENTER_OFFSET = 11.5
LEG_HEIGHT = 20.0

SOCKET_WIDTH_X = 11.5
SOCKET_WIDTH_Y = 11.0
SOCKET_HEIGHT = 12.0
SOCKET_SLOT_X = UPRIGHT_THICKNESS + 0.3
# Open-ended U sockets avoid trapping the lower edge of the circular flange
# and make the upright easy to slide in from above.
SOCKET_SLOT_Y = SOCKET_WIDTH_Y + 0.2
SOCKET_BASE_Z = FLANGE_THICKNESS
CLAMP_HOLE_HEIGHTS = (8.5, 14.0)
UPRIGHT_ASSEMBLY_Z = FLANGE_THICKNESS


def _xy_bolt_points():
    return [
        (BOLT_CIRCLE_RADIUS, 0.0),
        (-BOLT_CIRCLE_RADIUS, 0.0),
        (0.0, BOLT_CIRCLE_RADIUS),
        (0.0, -BOLT_CIRCLE_RADIUS),
    ]


def build_base() -> cq.Workplane:
    """Build the rotating-side flange and its two keyed upright sockets."""

    base = cq.Workplane("XY").circle(FLANGE_DIAMETER / 2).extrude(FLANGE_THICKNESS)
    for center_y in (-LEG_CENTER_OFFSET, LEG_CENTER_OFFSET):
        outer = (
            cq.Workplane("XY")
            .center(0.0, center_y)
            .rect(SOCKET_WIDTH_X, SOCKET_WIDTH_Y)
            .extrude(SOCKET_BASE_Z + SOCKET_HEIGHT)
        )
        slot = (
            cq.Workplane("XY")
            .workplane(offset=SOCKET_BASE_Z)
            .center(0.0, center_y)
            .rect(SOCKET_SLOT_X, SOCKET_SLOT_Y)
            .extrude(SOCKET_HEIGHT + 0.1)
        )
        base = base.union(outer).cut(slot)

    base = (
        base.faces("<Z")
        .workplane()
        .pushPoints(_xy_bolt_points())
        .hole(M3_CLEARANCE_DIAMETER)
        .faces("<Z")
        .workplane()
        .hole(CENTER_CLEARANCE_DIAMETER)
    )

    # Two clamp screws per keyed leg run along X through socket, leg, and socket.
    for center_y in (-LEG_CENTER_OFFSET, LEG_CENTER_OFFSET):
        for height in CLAMP_HOLE_HEIGHTS:
            clamp_hole = (
                cq.Workplane("YZ", origin=(-SOCKET_WIDTH_X, 0.0, 0.0))
                .center(center_y, height)
                .circle(M3_CLEARANCE_DIAMETER / 2)
                .extrude(SOCKET_WIDTH_X * 2)
            )
            base = base.cut(clamp_hole)
    return base.clean()


def build_upright() -> cq.Workplane:
    """Build the perpendicular encoder flange and its two keyed legs."""

    upright = (
        cq.Workplane("YZ", origin=(-UPRIGHT_THICKNESS / 2, 0.0, 0.0))
        .center(0.0, UPRIGHT_CENTER_HEIGHT)
        .circle(FLANGE_DIAMETER / 2)
        .extrude(UPRIGHT_THICKNESS)
    )
    for center_y in (-LEG_CENTER_OFFSET, LEG_CENTER_OFFSET):
        leg = (
            cq.Workplane("YZ", origin=(-UPRIGHT_THICKNESS / 2, 0.0, 0.0))
            .center(center_y, LEG_HEIGHT / 2)
            .rect(LEG_WIDTH, LEG_HEIGHT)
            .extrude(UPRIGHT_THICKNESS)
        )
        upright = upright.union(leg)

    # Standard four-hole cartridge interface plus rotor/shaft clearance.
    cartridge_holes = []
    for y, z in _xy_bolt_points():
        cartridge_holes.append((y, z + UPRIGHT_CENTER_HEIGHT))
    for y, z in cartridge_holes:
        hole = (
            cq.Workplane("YZ", origin=(-UPRIGHT_THICKNESS, 0.0, 0.0))
            .center(y, z)
            .circle(M3_CLEARANCE_DIAMETER / 2)
            .extrude(UPRIGHT_THICKNESS * 2)
        )
        upright = upright.cut(hole)
    center_hole = (
        cq.Workplane("YZ", origin=(-UPRIGHT_THICKNESS, 0.0, 0.0))
        .center(0.0, UPRIGHT_CENTER_HEIGHT)
        .circle(CENTER_CLEARANCE_DIAMETER / 2)
        .extrude(UPRIGHT_THICKNESS * 2)
    )
    upright = upright.cut(center_hole)

    for center_y in (-LEG_CENTER_OFFSET, LEG_CENTER_OFFSET):
        for height in CLAMP_HOLE_HEIGHTS:
            clamp_hole = (
                cq.Workplane("YZ", origin=(-UPRIGHT_THICKNESS, 0.0, 0.0))
                .center(center_y, height - UPRIGHT_ASSEMBLY_Z)
                .circle(M3_CLEARANCE_DIAMETER / 2)
                .extrude(UPRIGHT_THICKNESS * 2)
            )
            upright = upright.cut(clamp_hole)
    return upright.clean()


def build_parts() -> Dict[str, cq.Workplane]:
    """Return all canonical adapter solids."""

    return {
        "yam_wrist_axis_base": build_base(),
        "yam_wrist_axis_upright": build_upright(),
    }


def validate_parts(parts: Dict[str, cq.Workplane]) -> None:
    """Reject invalid or dimensionally surprising generated solids."""

    expected_bounds = {
        "yam_wrist_axis_base": (40.0, 40.0, 17.0),
        "yam_wrist_axis_upright": (5.0, 40.0, 44.0),
    }
    for name, part in parts.items():
        solids = part.solids().vals()
        if len(solids) != 1:
            raise RuntimeError(
                f"{name} must be one connected solid, found {len(solids)}"
            )
        if not part.val().isValid():
            raise RuntimeError(f"{name} is not a valid CAD solid")
        bounds = part.val().BoundingBox()
        actual = (bounds.xlen, bounds.ylen, bounds.zlen)
        for axis, (value, expected) in enumerate(zip(actual, expected_bounds[name])):
            if abs(value - expected) > 0.05:
                raise RuntimeError(
                    f"{name} axis {axis} is {value:.3f} mm; expected {expected:.3f} mm"
                )
        if part.val().Volume() < 1000.0:
            raise RuntimeError(f"{name} has unexpectedly low volume")

    assembled_upright = parts["yam_wrist_axis_upright"].translate(
        (0.0, 0.0, UPRIGHT_ASSEMBLY_Z)
    )
    interference = parts["yam_wrist_axis_base"].intersect(assembled_upright)
    interference_volume = sum(solid.Volume() for solid in interference.solids().vals())
    if interference_volume > 0.01:
        raise RuntimeError(f"Adapter parts interfere by {interference_volume:.3f} mm^3")


def export_parts(parts: Dict[str, cq.Workplane], output_dir: Path) -> None:
    """Export canonical STEP and print-oriented STL files."""

    step_dir = output_dir / "step"
    stl_dir = output_dir / "stl"
    step_dir.mkdir(parents=True, exist_ok=True)
    stl_dir.mkdir(parents=True, exist_ok=True)

    for name, part in parts.items():
        step_path = step_dir / f"{name}.step"
        cq.exporters.export(part, str(step_path))
        # OpenCascade emits spaces at the end of many STEP records. Normalize
        # them so regenerated text assets remain clean and reviewable in git.
        step_lines = step_path.read_text(encoding="utf-8").splitlines()
        step_path.write_text(
            "\n".join(line.rstrip() for line in step_lines) + "\n",
            encoding="utf-8",
        )
        printable = part
        if name.endswith("_upright"):
            # Lay the five-millimetre-thick face flat on the print bed.
            printable = part.rotate((0, 0, 0), (0, 1, 0), -90)
            bounds = printable.val().BoundingBox()
            printable = printable.translate((0, 0, -bounds.zmin))
        cq.exporters.export(
            printable,
            str(stl_dir / f"{name}.stl"),
            tolerance=0.05,
            angularTolerance=0.1,
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
        print(f"Exported {len(parts)} validated parts to {args.output_dir}")


if __name__ == "__main__":
    main()

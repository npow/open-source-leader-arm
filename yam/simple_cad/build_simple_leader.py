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

# The Nano shield is fixed horizontally to a sidecar on the base.  Keeping the
# controller and USB cable off the moving chain removes their mass and collision
# envelope from the wrist.  ``CONTROLLER_TRAY_CENTER`` is the PCB centre, not
# the floor below it, and is derived from the pedestal further down.
CONTROLLER_PART_INDEX = 0  # the fixed base carries the shield tray
NANO_SHIELD_BOARD_THICKNESS = 1.6
CONTROLLER_BOARD_BOTTOM_Z = 10.5
CONTROLLER_ELECTRONICS_HEIGHT = 22.0

# Assumed cable budget.  The seller does not specify the factory lead length,
# so 200 mm is a modeling assumption to verify against the delivered parts.
# Individual 300 mm M-to-F jumpers can be chained; the validation accounts for
# every conductor consumed from the two 40-wire ribbons in the BOM.
POT_LEAD_LENGTH = 200.0
EXTENSION_LEAD_LENGTH = 300.0
JUMPER_PACK_COUNT = 3
JUMPER_PACK_WIRES = 40
LEADER_COUNT = 2
CABLE_ROUTING_FACTOR = 1.25  # extra contour/slack beyond the centerline polyline
CABLE_SERVICE_LOOP = 35.0  # slack per rotating joint a run crosses
CABLE_TERMINATION_ALLOWANCE = 20.0  # both connector bodies plus strain relief

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

# ---------------------------------------------------------------------------
# Follower kinematics.
#
# Joint-space teleoperation sends each leader angle straight to the matching
# follower joint, so the operator's hand tracks the follower's gripper only if
# the leader is a *uniform* scaling of the follower.  Scale every segment by the
# same factor and the two arms stay geometrically similar at every pose; scale
# them individually -- a short upper arm here, a long wrist there -- and the
# angles remain legal while the correspondence the operator relies on is gone.
# That is why this chain is derived from the follower's own model rather than
# drawn to fit the print bed.
#
# Source: i2rt-robotics/i2rt, i2rt/robot_models/arm/yam/v1/yam.urdf, retrieved
# 2026-09-03.  Each row is that file's joint origin (metres), origin rpy
# (radians), rotation axis, and travel limits converted to degrees.  Do not
# hand-edit JOINTS; change LEADER_SCALE or the rows below and re-derive.
# ---------------------------------------------------------------------------
YAM_URDF_SOURCE = "i2rt-robotics/i2rt i2rt/robot_models/arm/yam/v1/yam.urdf"
YAM_URDF_CHAIN: Tuple[
    Tuple[str, Vector3, Vector3, Vector3, Tuple[float, float]], ...
] = (
    ("j1", (0.0, 0.0, 0.0680), (0.0, 1.5708, 3.141596), (-1.0, 0.0, 0.0), (-150.0, 180.0)),
    ("j2", (-0.0455, -0.0339, -0.0200), (0.0, 0.0, -3.14159), (0.0, 1.0, 0.0), (0.0, 210.0)),
    ("j3", (0.0, -0.0688, 0.2640), (0.0, 0.0, -3.14159), (0.0, 1.0, 0.0), (0.0, 180.0)),
    ("j4", (-0.0600, -0.0688, -0.2450), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), (-97.0, 90.0)),
    ("j5", (-0.0405, 0.0339, -0.0740), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (-90.0, 90.0)),
    ("j6", (0.0405, 0.0, -0.0356), (0.0, 0.0, 0.0), (0.0, 0.0, -1.0), (-120.0, 120.0)),
)
# The follower's gripper is a pair of prismatic fingers.  The leader replaces
# them with a squeeze lever, so only the finger pivot's position is borrowed,
# taken on the gripper centreline: the URDF's lateral term is one finger's own
# offset, not a link length.
YAM_URDF_GRIPPER_ORIGIN: Vector3 = (-0.0240, 0.0, -0.0567)

# The one number that sets the leader's size.  It is bounded below by hardware,
# not by taste: the follower's J5-to-J6 offset is only 53.9 mm, and a joint here
# is a 26 mm bearing plus a 17 mm potentiometer body, so the printed joints
# collide before the arm gets much smaller.  ``test_leader_is_a_uniformly_
# scaled_yam`` and the collision suite are what actually hold this bound.
LEADER_SCALE = 0.68

# Every joint angle here is a multiple of 90 degrees, which keeps all six axes
# on world axes -- the socket orientation code only builds cardinal joints --
# and this particular pose sits within a few degrees of the middle of every
# follower joint range while giving the familiar upright upper arm and forward
# forearm.  Printed stops are then derived as ``follower limit - build angle``,
# so the stops protect the follower's real travel instead of a symmetric guess.
YAM_BUILD_POSE_DEG: Mapping[str, float] = {
    "j1": 0.0,
    "j2": 90.0,
    "j3": 90.0,
    "j4": 0.0,
    "j5": 0.0,
    "j6": 0.0,
}

# A WH148 turns about 300 degrees end to end; staying inside 280 leaves the
# printed stops, not the pot's internal stops, taking the abuse.
POT_USABLE_TRAVEL_DEG = 280.0

# The socket and its potentiometer always extend along +axis, so the axis sign
# also picks which side of a joint the sensor sticks out of.  +1 keeps the
# follower's own positive direction, which is what lets the host map angles with
# ``joint_signs`` all +1; -1 buys clearance at the cost of a -1 for that joint.
# J7 is the leader's own squeeze lever and has no follower joint to agree with.
# J1 faces down so its socket hangs under the pedestal and every part of link 1
# stays above it.  With the socket facing up the pedestal has to reach the
# socket through a gap in link 1's own sweep, and the follower's 33.9 mm
# shoulder offset swings link 1 about 21 degrees wide in plan view, which
# leaves no such gap at J1's full travel.  J5 is flipped so its socket and
# carrier sit above the wrist, clearing the corridor link 5 needs to drop
# behind J6's moving flange; see build_link_5.
POT_MOUNT_SIGN: Mapping[str, float] = {"j1": -1.0, "j5": -1.0, "j7": -1.0}
LEADER_GRIPPER_RANGE_DEG = (0.0, 45.0)

# Travel the printed stops must not permit because the arm reaches itself or
# the base there.  Folding the elbow that far runs the forearm back along the
# upper arm and drops the wrist onto the base plate.  The follower folds into
# itself in the same region -- a URDF limit is not a promise of a
# collision-free workspace -- but the leader has to stop mechanically instead
# of relying on the operator noticing.  Measured with the collision sweep in
# ``test_elbow_stop_is_where_the_arm_stops_clearing_itself``; the stops are cut
# STOP_ANGULAR_CLEARANCE past these, so leave room for that overtravel.
SELF_COLLISION_LIMIT_DEG: Mapping[str, Tuple[float, float]] = {"j3": (-74.0, 90.0)}

# One combination survives those single-joint stops and still collides: pitch
# the shoulder forward and fold the elbow at the same time and the wrist comes
# down onto the base plate.  A printed stop can only limit one joint at a time,
# so this is an operating envelope rather than a hardware one.  The follower
# reaches its own mount and table in the same corner of its workspace.  The
# measured boundary is not monotonic in the shoulder angle, so this is stated
# conservatively: it excludes some folds that do in fact clear.
COUPLED_FOLD_LIMIT_DEG: Mapping[str, float] = {"j2_beyond": 20.0, "j3_floor": -60.0}


def fold_is_permitted(j2_degrees: float, j3_degrees: float) -> bool:
    """Whether a shoulder/elbow pair is inside the documented safe envelope."""

    if j2_degrees <= COUPLED_FOLD_LIMIT_DEG["j2_beyond"]:
        return True
    return j3_degrees >= COUPLED_FOLD_LIMIT_DEG["j3_floor"]

Matrix3 = Tuple[Vector3, Vector3, Vector3]
_IDENTITY: Matrix3 = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


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


def _m_mul(a: Matrix3, b: Matrix3) -> Matrix3:
    return tuple(  # type: ignore[return-value]
        tuple(sum(a[row][k] * b[k][col] for k in range(3)) for col in range(3))
        for row in range(3)
    )


def _m_apply(m: Matrix3, v: Vector3) -> Vector3:
    return tuple(  # type: ignore[return-value]
        sum(m[row][k] * v[k] for k in range(3)) for row in range(3)
    )


def _rotation_rpy(roll: float, pitch: float, yaw: float) -> Matrix3:
    """URDF fixed-axis roll-pitch-yaw, in radians."""

    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    return (
        (cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr),
        (sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr),
        (-sp, cp * sr, cp * cr),
    )


def _rotation_axis(axis: Vector3, degrees: float) -> Matrix3:
    x, y, z = _unit(axis)
    angle = math.radians(degrees)
    c, s = math.cos(angle), math.sin(angle)
    d = 1.0 - c
    return (
        (c + x * x * d, x * y * d - z * s, x * z * d + y * s),
        (y * x * d + z * s, c + y * y * d, y * z * d - x * s),
        (z * x * d - y * s, z * y * d + x * s, c + z * z * d),
    )


def _cardinal(axis: Vector3) -> Vector3:
    """Snap a world axis to its cardinal direction, or refuse to guess."""

    snapped = tuple(round(value) if abs(value) > 0.999 else 0.0 for value in axis)
    if sum(abs(value) for value in snapped) != 1.0 or _norm(_v_sub(axis, snapped)) > 1e-3:
        raise ValueError(
            f"joint axis {axis} is not a world axis; the build pose must use "
            "multiples of 90 degrees"
        )
    return snapped  # type: ignore[return-value]


def yam_chain(scale: float = 1.0) -> Tuple[Tuple[str, Vector3, Vector3], ...]:
    """Joint centres in millimetres and unit axes at the leader's build pose.

    Forward kinematics over ``YAM_URDF_CHAIN`` with ``YAM_BUILD_POSE_DEG``
    applied, uniformly scaled.  The trailing entry is the gripper input, which
    is placed at the follower's finger pivot but rotates rather than slides.
    """

    rotation: Matrix3 = _IDENTITY
    position: Vector3 = (0.0, 0.0, 0.0)
    chain = []
    for name, origin, orientation, axis, _ in YAM_URDF_CHAIN:
        position = _v_add(position, _m_apply(rotation, origin))
        rotation = _m_mul(rotation, _rotation_rpy(*orientation))
        chain.append(
            (name, _v_scale(position, 1000.0 * scale), _cardinal(_m_apply(rotation, axis)))
        )
        rotation = _m_mul(rotation, _rotation_axis(axis, YAM_BUILD_POSE_DEG[name]))
    gripper = _v_scale(
        _v_add(position, _m_apply(rotation, YAM_URDF_GRIPPER_ORIGIN)), 1000.0 * scale
    )
    # The follower's finger pivot is only about 62 mm from its roll axis, which
    # is closer than this hardware fits: J6's potentiometer carrier already
    # occupies the first 35 mm of that direction and the lever joint's own neck
    # reaches NECK_LENGTH back toward it.  The lever therefore sits at the
    # scaled finger pivot or at the first place the parts fit, whichever is
    # further out.  It is the leader's own input, not a follower joint, so
    # moving it changes no commanded angle.
    j6_center, j6_axis = chain[-1][1], chain[-1][2]
    reach = _v_sub(gripper, j6_center)
    direction = _unit(reach)
    along_axis = abs(_dot(direction, j6_axis))
    minimum = (POT_HOLDER_BACK_X + BEAM_RADIUS + 2.0) / along_axis + NECK_LENGTH
    if _norm(reach) < minimum:
        gripper = _v_add(j6_center, _v_scale(direction, minimum))
    chain.append(("j7", gripper, _cardinal(_m_apply(rotation, (0.0, 1.0, 0.0)))))
    return tuple(chain)


def _leader_joints() -> Dict[str, Tuple[Vector3, Vector3]]:
    return {
        name: (center, _v_scale(axis, POT_MOUNT_SIGN.get(name, 1.0)))
        for name, center, axis in yam_chain(LEADER_SCALE)
    }


def _leader_limits() -> Dict[str, Tuple[float, float]]:
    """Printed stops, expressed in the leader's own zero-at-build-pose frame."""

    limits: Dict[str, Tuple[float, float]] = {}
    for name, _, _, _, (lower, upper) in YAM_URDF_CHAIN:
        build = YAM_BUILD_POSE_DEG[name]
        lower, upper = lower - build, upper - build
        if POT_MOUNT_SIGN.get(name, 1.0) < 0.0:
            lower, upper = -upper, -lower
        half = POT_USABLE_TRAVEL_DEG / 2.0
        lower, upper = max(lower, -half), min(upper, half)
        blocked = SELF_COLLISION_LIMIT_DEG.get(name)
        if blocked is not None:
            lower, upper = max(lower, blocked[0]), min(upper, blocked[1])
        limits[name] = (lower, upper)
    limits["j7"] = LEADER_GRIPPER_RANGE_DEG
    return limits


JOINTS: Mapping[str, Tuple[Vector3, Vector3]] = _leader_joints()
JOINT_LIMITS_DEG: Mapping[str, Tuple[float, float]] = _leader_limits()


def follower_travel_lost_deg() -> Dict[str, Tuple[float, float]]:
    """Follower travel the pot cannot span, as (below, above) in degrees.

    Only J1 asks for more than one potentiometer can measure, so this is the
    honest statement of what the leader gives up rather than a claim that the
    printed stops cover the whole arm.
    """

    lost: Dict[str, Tuple[float, float]] = {}
    for name, _, _, _, (lower, upper) in YAM_URDF_CHAIN:
        build = YAM_BUILD_POSE_DEG[name]
        wanted = (lower - build, upper - build)
        if POT_MOUNT_SIGN.get(name, 1.0) < 0.0:
            wanted = (-wanted[1], -wanted[0])
        have = JOINT_LIMITS_DEG[name]
        below, above = have[0] - wanted[0], wanted[1] - have[1]
        if below > 1e-6 or above > 1e-6:
            lost[name] = (below, above)
    return lost


# Base pedestal.  J1's socket hangs under its own pedestal, so this is a plain
# column carrying the socket's full underside rather than a slab threaded
# through link 1's sweep.  Its height follows J1, which moves with LEADER_SCALE.
BASE_PLATE_LENGTH = 110.0
BASE_PLATE_WIDTH = 90.0
BASE_PLATE_THICKNESS = 8.0
_J1_CENTER = JOINTS["j1"][0]
PEDESTAL_HALF_WIDTH = JOINT_RADIUS + 8.0
# The socket, its support tube, and the potentiometer cradle all hang inside
# the column, so it is a U opening toward the arm: the pot still drops into its
# cradle from that side after the column is printed.
PEDESTAL_TOP_Z = _J1_CENTER[2] - SOCKET_BODY_DEPTH
POT_CAVITY_HALF_WIDTH = (POT_BODY_DIAMETER + POT_BODY_CLEARANCE + 3.6) / 2.0 + 2.0

# The shield tray sits behind the pedestal.  Link 1 never comes below the top
# of the J1 socket, so the only thing the tray has to clear is the column.
CONTROLLER_TRAY_CENTER: Vector3 = (
    _J1_CENTER[0] - PEDESTAL_HALF_WIDTH - NANO_SHIELD_LONG / 2.0 - 6.0,
    _J1_CENTER[1],
    CONTROLLER_BOARD_BOTTOM_Z + NANO_SHIELD_BOARD_THICKNESS / 2.0,
)


def stop_pin_half_angle() -> float:
    """Angular half-width of the stop pin at its own radius."""

    return math.degrees(math.asin(STOP_PIN_RADIUS / STOP_RADIUS))


def stop_limited_range(joint: str) -> Tuple[float, float]:
    """Travel the printed stops actually permit, which is not the declared range.

    The groove is cut ``STOP_ANGULAR_CLEARANCE`` past each end of the declared
    range, but the pin stops when its *edge* meets the end of the groove, not
    its centre.  The collision suite has to sweep this rather than the nominal
    limits, because this is the travel a built arm actually has.
    """

    lower, upper = JOINT_LIMITS_DEG[joint]
    overtravel = max(0.0, STOP_ANGULAR_CLEARANCE - stop_pin_half_angle())
    return lower - overtravel, upper + overtravel


def _box(
    x_length: float,
    y_length: float,
    z_length: float,
    center: Vector3,
) -> cq.Workplane:
    return cq.Workplane("XY").box(x_length, y_length, z_length).translate(center)


def _cylinder_x(radius: float, length: float, x_start: float) -> cq.Workplane:
    return cq.Workplane("YZ", origin=(x_start, 0.0, 0.0)).circle(radius).extrude(length)


def _orient_x(part: cq.Workplane, axis: Vector3, center: Vector3) -> cq.Workplane:
    """Rotate a canonical +X-axis feature onto a cardinal world axis."""

    axis = _unit(axis)
    if axis == (1.0, 0.0, 0.0):
        oriented = part
    elif axis == (-1.0, 0.0, 0.0):
        oriented = part.rotate((0, 0, 0), (0, 0, 1), 180)
    elif axis == (0.0, 1.0, 0.0):
        oriented = part.rotate((0, 0, 0), (0, 0, 1), 90)
    elif axis == (0.0, -1.0, 0.0):
        oriented = part.rotate((0, 0, 0), (0, 0, 1), -90)
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
        _box(
            holder_length, holder_width, 2.4, (holder_mid_x, 0.0, -holder_height / 2.0)
        )
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


def build_plug(
    lower_degrees: float = -90.0, upper_degrees: float = 90.0
) -> cq.Workplane:
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
    if _norm(delta) < 0.05:
        raise ValueError(
            f"beam from {start} to {end} has no length; the joints it connects "
            "are too close together at this LEADER_SCALE"
        )
    solid = cq.Solid.makeCylinder(
        radius,
        _norm(delta),
        cq.Vector(*start),
        cq.Vector(*_unit(delta)),
    )
    return cq.Workplane("XY").newObject([solid])


def _beam_path_pieces(
    points: Tuple[Vector3, ...], radius: float = BEAM_RADIUS
) -> Tuple[cq.Workplane, ...]:
    """A doglegged beam, as separate solids for the caller to union in turn.

    Two cylinders that meet exactly at a shared end plane can fail to fuse: the
    boolean sees a tangency rather than a shared volume and quietly drops one
    of them.  A ball at each interior corner gives consecutive segments real
    shared volume, and rounds the corner while it is there.  The pieces are
    returned rather than pre-fused because unioning them one at a time into the
    link they belong to is what the boolean handles reliably.
    """

    if len(points) < 2:
        raise ValueError("a beam path needs at least two waypoints")
    pieces = [
        _cylinder_between(start, end, radius) for start, end in zip(points, points[1:])
    ]
    pieces.extend(
        cq.Workplane("XY").sphere(radius).translate(corner) for corner in points[1:-1]
    )
    return tuple(pieces)


def _radial_neck(
    center: Vector3,
    axis: Vector3,
    toward: Vector3,
    length: float = NECK_LENGTH,
    depth: float = FLANGE_THICKNESS,
) -> Tuple[cq.Workplane, Vector3]:
    """Leave a plug radially without entering the stationary socket.

    ``depth`` is how far the neck stands off the flange face.  A neck that is
    only as deep as the flange meets the beam through whatever the stop groove
    leaves behind, which on a short neck is a sliver; joints whose beam starts
    inside the groove radius need a deeper one.
    """

    axis = _unit(axis)
    toward_vector = _v_sub(toward, center)
    radial = _v_sub(toward_vector, _v_scale(axis, _dot(toward_vector, axis)))
    if _norm(radial) < 1e-6:
        fallback = (1.0, 0.0, 0.0) if abs(axis[0]) < 0.5 else (0.0, 0.0, 1.0)
        radial = _v_sub(fallback, _v_scale(axis, _dot(fallback, axis)))
    radial = _unit(radial)

    plane_origin = _v_sub(center, _v_scale(axis, depth))
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
        .extrude(depth)
    )
    waypoint = _v_add(
        _v_sub(center, _v_scale(axis, depth / 2.0)),
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
    length: float = NECK_LENGTH,
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
        .center(length / 2.0, 0.0)
        .rect(length, BEAM_RADIUS * 2.0)
        .extrude(SOCKET_BODY_DEPTH)
    )
    # This neck overlaps the socket for strength, so repeat the bearing and
    # axle cuts here; otherwise the union would silently fill the joint bore.
    neck = neck.cut(_orient_x(_socket_void(), axis, center))
    waypoint = _v_add(
        _v_add(center, _v_scale(axis, SOCKET_BODY_DEPTH / 2.0)),
        _v_scale(radial, length),
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


def _link(
    proximal: str, distal: str, proximal_neck_length: float = NECK_LENGTH
) -> cq.Workplane:
    proximal_center, proximal_axis = JOINTS[proximal]
    distal_center, distal_axis = JOINTS[distal]
    part = _joint_plug(proximal)
    # Both necks run the full NECK_LENGTH even where the joints are close
    # together.  A shorter one lets the beam turn while it is still inside the
    # neighbouring socket or flange, which reads as a clean model and prints as
    # a joint that cannot rotate.
    neck, waypoint = _radial_neck(
        proximal_center,
        proximal_axis,
        distal_center,
        length=proximal_neck_length,
    )
    socket_neck, socket_waypoint = _socket_neck(
        distal_center, distal_axis, proximal_center, length=NECK_LENGTH
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

def _pedestal() -> cq.Workplane:
    """Column under the J1 socket, open toward the arm for pot installation."""

    center = _J1_CENTER
    height = PEDESTAL_TOP_Z - BASE_PLATE_THICKNESS
    if height < 1.0:
        raise RuntimeError(
            "the J1 socket hangs into the base plate at this LEADER_SCALE"
        )
    column = _box(
        PEDESTAL_HALF_WIDTH * 2.0,
        PEDESTAL_HALF_WIDTH * 2.0,
        height,
        (center[0], center[1], BASE_PLATE_THICKNESS + height / 2.0),
    )
    # The cradle opens toward +X once the socket is turned to face down, so the
    # cavity runs out through that face and the potentiometer slides in after
    # printing.  It stops short of the plate so the column keeps a solid floor.
    cavity_length = PEDESTAL_HALF_WIDTH + POT_CAVITY_HALF_WIDTH + 2.0
    cavity_height = height - 4.0
    column = column.cut(
        _box(
            cavity_length,
            POT_CAVITY_HALF_WIDTH * 2.0,
            cavity_height,
            (
                center[0] - POT_CAVITY_HALF_WIDTH + cavity_length / 2.0,
                center[1],
                PEDESTAL_TOP_Z - cavity_height / 2.0,
            ),
        )
    )
    return column


def controller_electronics_keepout() -> cq.Workplane:
    """Conservative fixed envelope for the shield, Nano, plugs, and headers."""

    center_x, center_y, _ = CONTROLLER_TRAY_CENTER
    edge_access = 10.0
    return _box(
        NANO_SHIELD_LONG + edge_access * 2.0,
        NANO_SHIELD_SHORT + edge_access * 2.0,
        CONTROLLER_ELECTRONICS_HEIGHT,
        (
            center_x,
            center_y,
            CONTROLLER_BOARD_BOTTOM_Z + CONTROLLER_ELECTRONICS_HEIGHT / 2.0,
        ),
    )


def _controller_sidecar() -> cq.Workplane:
    """Low horizontal Nano-shield tray that is integral with the fixed base."""

    center_x, center_y, _ = CONTROLLER_TRAY_CENTER
    opening_half_x = NANO_SHIELD_LONG / 2.0 + NANO_SHIELD_EDGE_CLEARANCE
    # Extend one millimetre beyond the outside of each clip post so every post
    # grows from supported floor material rather than merely sharing its edge.
    floor_x = NANO_SHIELD_LONG + NANO_SHIELD_EDGE_CLEARANCE * 2.0 + 8.0
    floor_y = NANO_SHIELD_SHORT + NANO_SHIELD_EDGE_CLEARANCE * 2.0 + 4.0
    floor = _box(
        floor_x,
        floor_y,
        BASE_PLATE_THICKNESS,
        (center_x, center_y, BASE_PLATE_THICKNESS / 2.0),
    )

    # Four pads hold the PCB above its solder joints instead of pressing its
    # underside against a solid floor.
    riser_height = CONTROLLER_BOARD_BOTTOM_Z - BASE_PLATE_THICKNESS
    for x_sign in (-1.0, 1.0):
        for y_sign in (-1.0, 1.0):
            floor = floor.union(
                _box(
                    6.0,
                    6.0,
                    riser_height,
                    (
                        center_x + x_sign * (NANO_SHIELD_LONG / 2.0 - 4.0),
                        center_y + y_sign * (NANO_SHIELD_SHORT / 2.0 - 4.0),
                        BASE_PLATE_THICKNESS + riser_height / 2.0,
                    ),
                )
            )

    # Two clips per long edge flex outwards during insertion.  Their lips sit
    # above the PCB with a small vertical allowance for marketplace variation.
    post_width = 3.0
    post_x = opening_half_x + post_width / 2.0
    board_top = CONTROLLER_BOARD_BOTTOM_Z + NANO_SHIELD_BOARD_THICKNESS
    lip_bottom = board_top + 0.30
    lip_height = 1.40
    post_bottom = BASE_PLATE_THICKNESS - 0.50
    post_top = lip_bottom + lip_height
    for x_sign in (-1.0, 1.0):
        for y_offset in (-18.0, 18.0):
            x = center_x + x_sign * post_x
            y = center_y + y_offset
            post = _box(
                post_width,
                6.0,
                post_top - post_bottom,
                (x, y, (post_top + post_bottom) / 2.0),
            )
            lip = _box(
                5.0,
                6.0,
                lip_height,
                (x - x_sign * 1.8, y, lip_bottom + lip_height / 2.0),
            )
            floor = floor.union(post).union(lip)
    return floor.clean()


def build_base() -> cq.Workplane:
    joint_center, joint_axis = JOINTS["j1"]
    base = _box(
        BASE_PLATE_LENGTH,
        BASE_PLATE_WIDTH,
        BASE_PLATE_THICKNESS,
        (0.0, 0.0, BASE_PLATE_THICKNESS / 2.0),
    )
    base = base.edges("|Z").fillet(8.0)

    # The column carries the whole underside of the J1 socket in compression,
    # rather than meeting it through the small lens a wedge or a pair of posts
    # can reach.  It overlaps the socket wall so the two fuse into one section
    # instead of merely touching, so it has to repeat the joint bore cut.
    pedestal = _pedestal()
    pedestal = pedestal.cut(_orient_x(_socket_void(), joint_axis, joint_center))
    base = base.union(pedestal)
    base = base.union(_joint_socket("j1"))
    base = base.union(_controller_sidecar())

    # Four ordinary wood screws can secure the base to a board;
    # they drive into the board directly and do not require nuts.
    for x in (-47.0, 47.0):
        for y in (-37.0, 37.0):
            hole = cq.Workplane("XY", origin=(x, y, -0.1)).circle(2.2).extrude(8.2)
            base = base.cut(hole)
    return base.clean()


def build_link_6() -> cq.Workplane:
    """Carry the gripper past J6's own sensor stack, then add the hand grip.

    The gripper sits close in behind J6's bearing seat and potentiometer, and
    this link rolls 240 degrees around both of them.  A beam aimed straight at
    the lever pivot cuts the corner of that stack, so the beam first runs
    parallel to the roll axis at neck radius until it is clear of the pot
    holder, and only then turns toward the pivot.
    """

    j6_center, j6_axis = JOINTS["j6"]
    j7_center, j7_axis = JOINTS["j7"]

    part = _joint_plug("j6")
    neck, waypoint = _radial_neck(j6_center, j6_axis, j7_center, length=NECK_LENGTH)
    radial = _unit(_v_sub(waypoint, _v_sub(j6_center, _v_scale(j6_axis, FLANGE_THICKNESS / 2.0))))
    clear_of_stack = _v_add(
        _v_add(j6_center, _v_scale(j6_axis, POT_HOLDER_BACK_X + BEAM_RADIUS + 1.0)),
        _v_scale(radial, NECK_LENGTH),
    )
    socket_neck, socket_waypoint = _socket_neck(j7_center, j7_axis, j6_center)
    part = part.union(neck)
    for piece in _beam_path_pieces((waypoint, clear_of_stack, socket_waypoint)):
        part = part.union(piece)
    part = part.union(socket_neck)
    part = part.union(_joint_socket("j7"))
    part = part.cut(_joint_stop_groove("j6"))
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


def build_link_5() -> cq.Workplane:
    """Reach J6's socket through the one sector its moving link cannot enter.

    J5 and the gripper both sit on the same side of J6, and J6 turns 240
    degrees, so its moving link sweeps every radial direction except a 120
    degree sector opposite that side.  A straight beam from J5 into the J6
    socket lands squarely inside that sweep and the wrist locks up.  This link
    therefore drops behind the moving flange plane, where the child has no
    material at all, and enters the socket from the free sector -- the same
    move the base pedestal makes to reach J1 through link 1's sweep.
    """

    j5_center, j5_axis = JOINTS["j5"]
    j6_center, j6_axis = JOINTS["j6"]

    toward_j5 = _v_sub(j5_center, j6_center)
    radial = _unit(
        _v_sub(toward_j5, _v_scale(j6_axis, _dot(toward_j5, j6_axis)))
    )
    entry = _v_scale(radial, -1.0)

    # The descent runs in a plane behind the moving flange, with room for the
    # beam's own radius; the child link starts at the flange and never reaches
    # back past it.
    setback = FLANGE_THICKNESS + BEAM_RADIUS + 2.0
    neck_direction = _unit(
        _v_sub(
            _v_sub(j6_center, j5_center),
            _v_scale(j5_axis, _dot(_v_sub(j6_center, j5_center), j5_axis)),
        )
    )
    neck_length = _dot(
        _v_sub(_v_sub(j6_center, _v_scale(j6_axis, setback)), j5_center),
        neck_direction,
    )
    if neck_length < 1.0:
        raise RuntimeError(
            "J5 sits inside J6's flange setback at this LEADER_SCALE; link 5 "
            "has nowhere to route"
        )

    socket_neck, socket_waypoint = _socket_neck(
        j6_center, j6_axis, _v_add(j6_center, entry)
    )
    turn = _v_add(
        _v_add(j6_center, _v_scale(entry, NECK_LENGTH)),
        _v_scale(j6_axis, -setback),
    )

    part = _joint_plug("j5")
    # The setback keeps this neck short enough that its beam starts inside the
    # stop groove's radius, so the neck stands off the flange far enough to
    # keep solid material under the groove.
    neck, waypoint = _radial_neck(
        j5_center,
        j5_axis,
        j6_center,
        length=neck_length,
        depth=FLANGE_THICKNESS + BEAM_RADIUS,
    )
    part = part.union(neck)
    for piece in _beam_path_pieces((waypoint, turn, socket_waypoint)):
        part = part.union(piece)
    part = part.union(socket_neck)
    part = part.union(_joint_socket("j6"))
    part = part.cut(_joint_stop_groove("j5"))
    return part.clean()


def build_link_3() -> cq.Workplane:
    """Link 3 is only structural; all controller hardware stays on the base."""

    return _link("j3", "j4")


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
    """Length and jumper count each channel needs to reach the fixed base.

    Joint ``jN``'s potentiometer is carried by the socket side of that joint,
    which is part ``N - 1``, so the number of rotating joints a run crosses is
    its distance along the chain from the part holding the tray.  Each crossing
    needs a service loop or the cable becomes a spring the joint has to fight.
    The route follows the intervening joint centres rather than using a false
    straight chord through open space.
    """

    runs: Dict[str, Dict[str, float]] = {}
    joint_names = tuple(JOINTS)
    for index, joint in enumerate(joint_names):
        crossings = abs(index - CONTROLLER_PART_INDEX)
        route_points = [_pot_terminal(joint)]
        route_points.extend(
            JOINTS[joint_names[anchor_index]][0]
            for anchor_index in range(index - 1, -1, -1)
        )
        route_points.append(CONTROLLER_TRAY_CENTER)
        centerline_route = sum(
            _norm(_v_sub(end, start))
            for start, end in zip(route_points, route_points[1:])
        )
        required = (
            centerline_route * CABLE_ROUTING_FACTOR
            + CABLE_SERVICE_LOOP * crossings
            + CABLE_TERMINATION_ALLOWANCE
        )
        extension_count = max(
            0,
            math.ceil((required - POT_LEAD_LENGTH) / EXTENSION_LEAD_LENGTH),
        )
        runs[joint] = {
            "route_mm": centerline_route,
            "joints_crossed": float(crossings),
            "required_mm": required,
            "extension_count": float(extension_count),
            "needs_extension": float(extension_count > 0),
        }
    return runs


def extension_channels() -> Tuple[str, ...]:
    """Channels whose factory lead alone cannot reach the tray."""

    return tuple(joint for joint, run in cable_runs().items() if run["needs_extension"])


def validate_cable_reach() -> None:
    runs = cable_runs()
    wires_used = int(
        sum(run["extension_count"] for run in runs.values()) * 3 * LEADER_COUNT
    )
    wires_bought = JUMPER_PACK_COUNT * JUMPER_PACK_WIRES
    if wires_used > wires_bought:
        raise RuntimeError(
            f"the two leaders need {wires_used} individual jumper wires under "
            f"the modeled lead assumption but the BOM provides {wires_bought}"
        )


def build_parts() -> Dict[str, cq.Workplane]:
    return {
        "simple_base": build_base(),
        "simple_link_1": _link("j1", "j2"),
        "simple_link_2": _link("j2", "j3"),
        "simple_link_3": build_link_3(),
        "simple_link_4": _link("j4", "j5"),
        "simple_link_5": build_link_5(),
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
            raise RuntimeError(
                f"{name} must be one connected solid, found {len(solids)}"
            )
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
    elif name in {
        "simple_link_2",
        "simple_link_3",
        "simple_link_4",
        "simple_gripper_lever",
    }:
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
        print(
            f"Exported {len(parts)} structural parts plus joint_fit_test "
            f"to {args.output_dir}"
        )
    needs = extension_channels()
    print(
        "Cable budget to fixed base (assumed factory lead is "
        f"{POT_LEAD_LENGTH:.0f} mm):"
    )
    for joint, run in cable_runs().items():
        extensions = int(run["extension_count"])
        flag = f", {extensions} jumper segment(s)" if extensions else ", direct"
        print(
            f"  {joint}: {run['route_mm']:6.1f} mm centerline route, "
            f"{int(run['joints_crossed'])} joints crossed, "
            f"{run['required_mm']:6.1f} mm needed{flag}"
        )
    wire_count = int(sum(run["extension_count"] for run in cable_runs().values()) * 3)
    print(
        f"{len(needs)} channels use extensions: {', '.join(needs)}; "
        f"{wire_count} individual jumper wires per leader"
    )


if __name__ == "__main__":
    main()

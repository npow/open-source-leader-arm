import math
from itertools import product

import pytest
from build_simple_leader import (
    AXLE_DIAMETER,
    BASE_LIMITED_RANGE_DEG,
    BEARING_ID,
    BEARING_OD,
    BEARING_POCKET_DEPTH,
    BEARING_POCKET_DIAMETER,
    BEARING_WIDTH,
    CONTROLLER_BOARD_BOTTOM_Z,
    CONTROLLER_PART_INDEX,
    CONTROLLER_TRAY_CENTER,
    EXTENSION_LEAD_LENGTH,
    JOINT_LIMITS_DEG,
    JOINTS,
    JUMPER_PACK_COUNT,
    JUMPER_PACK_WIRES,
    LEADER_COUNT,
    NANO_SHIELD_BOARD_THICKNESS,
    NANO_SHIELD_LONG,
    NANO_SHIELD_SHORT,
    PART_ORDER,
    POT_BODY_CLEARANCE,
    POT_BODY_DIAMETER,
    POT_BUSHING_CLEARANCE,
    POT_BUSHING_DIAMETER,
    POT_LEAD_LENGTH,
    POT_SHAFT_DIAMETER,
    POT_SHAFT_SOCKET_DIAMETER,
    STOP_ANGULAR_CLEARANCE,
    STOP_PIN_RADIUS,
    STOP_RADIUS,
    _box,
    _intersection_volume,
    _v_add,
    build_base,
    build_joint_fit_test,
    build_parts,
    cable_runs,
    controller_electronics_keepout,
    extension_channels,
    stop_limited_range,
    stop_pin_half_angle,
    usable_range,
    validate_parts,
)

# The pot's carrier and the gripper's return leaf are the only two places where
# parts are meant to touch, so every other pair is a genuine interference.
GRIPPER_FLEXURE_PAIR = (6, 7)

# Rebuilding the eight solids costs about ten seconds, so the geometry tests
# share one set.
_PARTS_CACHE = None


def _parts():
    global _PARTS_CACHE
    if _PARTS_CACHE is None:
        _PARTS_CACHE = [build_parts()[name] for name in PART_ORDER]
    return _PARTS_CACHE


def _sweep_range(joint):
    """Travel to check collisions over: what the hardware actually permits."""

    if joint == "j7":
        # Past its closed stop the gripper is loading its own flexure, which is
        # not a rigid-body question.
        return JOINT_LIMITS_DEG[joint]
    return usable_range(joint)


def _posed(angles):
    """Pose the whole chain, not just one link.

    Joint ``jN`` carries every part distal to it, so part ``i`` is moved by
    joints ``j1..ji``.  Rotating about the zero-pose axes from the distal joint
    inward reproduces the nested transforms without tracking frames.
    """

    posed = []
    for index, part in enumerate(_parts()):
        moved = part
        for joint_index in range(index, 0, -1):
            angle = angles.get(f"j{joint_index}", 0.0)
            if angle:
                center, axis = JOINTS[f"j{joint_index}"]
                moved = moved.rotate(center, _v_add(center, axis), angle)
        posed.append(moved)
    return posed


def _boxes_touch(a, b, margin=0.05):
    first = a.val().BoundingBox()
    second = b.val().BoundingBox()
    return (
        first.xmin - margin <= second.xmax
        and second.xmin - margin <= first.xmax
        and first.ymin - margin <= second.ymax
        and second.ymin - margin <= first.ymax
        and first.zmin - margin <= second.zmax
        and second.zmin - margin <= first.zmax
    )


def _assert_pose_is_clear(angles):
    posed = _posed(angles)
    for first in range(len(posed)):
        for second in range(first + 1, len(posed)):
            if (first, second) == GRIPPER_FLEXURE_PAIR:
                continue
            # A boolean intersection costs far more than a box test, and almost
            # every pair in the chain is nowhere near its neighbours.
            if not _boxes_touch(posed[first], posed[second]):
                continue
            overlap = _intersection_volume(posed[first], posed[second])
            assert overlap < 0.1, (
                f"{PART_ORDER[first]} and {PART_ORDER[second]} interfere by "
                f"{overlap:.3f} mm^3 at {angles}"
            )

    # The shield, Nano, headers, and plugs are purchased parts rather than an
    # STL, so they need their own conservative envelope in every motion check.
    electronics = controller_electronics_keepout()
    for index in range(1, len(posed)):
        if not _boxes_touch(electronics, posed[index]):
            continue
        overlap = _intersection_volume(electronics, posed[index])
        assert overlap < 0.1, (
            f"controller electronics and {PART_ORDER[index]} interfere by "
            f"{overlap:.3f} mm^3 at {angles}"
        )


def test_complete_print_manifest_is_eight_structural_parts():
    parts = build_parts()
    validate_parts(parts)
    assert len(parts) == 8


def test_purchased_components_have_printable_fit_allowance():
    assert (BEARING_OD, BEARING_ID, BEARING_WIDTH) == (26.0, 10.0, 8.0)
    assert 0.10 <= BEARING_POCKET_DIAMETER - BEARING_OD <= 0.35
    assert 0.10 <= BEARING_ID - AXLE_DIAMETER <= 0.35
    assert 0.10 <= BEARING_POCKET_DEPTH - BEARING_WIDTH <= 0.30
    assert POT_BODY_DIAMETER == 17.0
    assert 0.25 <= POT_BODY_CLEARANCE <= 0.70
    assert POT_BUSHING_DIAMETER == 7.0
    assert 0.20 <= POT_BUSHING_CLEARANCE <= 0.60
    assert POT_SHAFT_DIAMETER == 6.0
    assert 0.05 <= POT_SHAFT_DIAMETER - POT_SHAFT_SOCKET_DIAMETER <= 0.25


def test_load_bearing_axle_has_material_around_pot_socket():
    radial_wall = (AXLE_DIAMETER - POT_SHAFT_SOCKET_DIAMETER) / 2.0
    assert radial_wall >= 1.8


def test_stop_groove_clears_the_width_of_its_own_pin():
    """The groove is cut by angle but the pin has width.

    If the clearance angle drops below the pin's own half-angle the pin fouls
    the end of its groove at the zero pose, which shows up as an interference
    between two parts that are supposed to be free.
    """

    pin_half_angle = math.degrees(math.asin(STOP_PIN_RADIUS / STOP_RADIUS))
    assert stop_pin_half_angle() == pytest.approx(pin_half_angle)
    assert STOP_ANGULAR_CLEARANCE > pin_half_angle + 1.0
    # And the permitted travel must actually exceed the declared range.
    for joint, (lower, upper) in JOINT_LIMITS_DEG.items():
        stop_lower, stop_upper = stop_limited_range(joint)
        assert stop_lower <= lower and stop_upper >= upper


def test_fit_coupon_contains_separate_socket_and_plug_solids():
    coupon = build_joint_fit_test()
    assert coupon.val().isValid()
    assert len(coupon.solids().vals()) == 2


@pytest.mark.parametrize("joint", list(JOINT_LIMITS_DEG))
def test_full_chain_is_collision_free_through_each_joint_range(joint):
    """Sweep one joint with the entire distal chain attached.

    Rotating only the immediate child link leaves the rest of the arm and the
    gripper sitting at the zero pose, which is not a configuration the hardware
    can ever be in.
    """

    lower, upper = _sweep_range(joint)
    for angle in (lower, (lower + upper) / 2.0, upper):
        _assert_pose_is_clear({joint: angle})


@pytest.mark.parametrize(
    "pose",
    [
        # Wrist corners with the arm upright, including the combination that
        # previously struck the rejected moving controller tray.
        {"j4": 90.0, "j5": 90.0, "j6": 120.0, "j7": 45.0},
        {"j4": 90.0, "j5": -90.0, "j6": -120.0, "j7": 45.0},
        {"j4": -90.0, "j5": 90.0, "j6": -120.0, "j7": 0.0},
        {"j4": 90.0, "j5": 90.0, "j6": -120.0, "j7": 0.0},
        # Base yaw does not change the arm's own shape, so pair it with the
        # wrist to confirm the pedestal stays clear of a curled hand.
        {"j1": 140.0, "j4": 90.0, "j5": 90.0, "j6": 120.0},
        {"j1": -140.0, "j4": 90.0, "j5": -90.0, "j6": -120.0},
    ],
)
def test_wrist_poses_keep_every_part_clear(pose):
    """Selected useful wrist poses are clear; this is not an exhaustive grid."""

    _assert_pose_is_clear(pose)


def test_j2_reaches_its_full_printed_stop_without_hitting_the_base():
    assert "j2" not in BASE_LIMITED_RANGE_DEG
    lower, upper = stop_limited_range("j2")
    assert lower < JOINT_LIMITS_DEG["j2"][0]
    assert upper > JOINT_LIMITS_DEG["j2"][1]
    _assert_pose_is_clear({"j2": lower})
    _assert_pose_is_clear({"j2": upper})


def test_controller_is_fixed_to_the_base_and_old_wrist_collision_is_clear():
    assert CONTROLLER_PART_INDEX == 0
    assert CONTROLLER_TRAY_CENTER[2] < JOINTS["j1"][0][2]
    assert _parts()[0].val().BoundingBox().xmin < -65.0
    _assert_pose_is_clear({"j4": -90.0, "j5": -90.0, "j6": -120.0})


def test_nominal_shield_fits_the_base_sidecar_on_a_standard_print_bed():
    base = _parts()[0]
    board = _box(
        NANO_SHIELD_LONG,
        NANO_SHIELD_SHORT,
        NANO_SHIELD_BOARD_THICKNESS,
        CONTROLLER_TRAY_CENTER,
    )
    assert _intersection_volume(base, board) < 0.1
    bounds = base.val().BoundingBox()
    assert bounds.xlen <= 180.0
    assert bounds.ylen <= 180.0
    assert bounds.zmin == pytest.approx(0.0)
    assert CONTROLLER_TRAY_CENTER[2] == pytest.approx(
        CONTROLLER_BOARD_BOTTOM_Z + NANO_SHIELD_BOARD_THICKNESS / 2.0
    )


def test_fixed_controller_clears_base_and_shoulder_folds_at_every_yaw_sample():
    j1_lower, j1_upper = stop_limited_range("j1")
    j2_lower, j2_upper = stop_limited_range("j2")
    for j1 in (j1_lower, -70.0, 0.0, 70.0, j1_upper):
        for j2 in (j2_lower, 0.0, j2_upper):
            _assert_pose_is_clear({"j1": j1, "j2": j2})


def test_all_nominal_wrist_corner_folds_are_clear():
    wrist_samples = {
        joint: (limits[0], 0.0, limits[1])
        for joint, limits in JOINT_LIMITS_DEG.items()
        if joint in {"j4", "j5", "j6"}
    }
    for j4, j5, j6 in product(
        wrist_samples["j4"], wrist_samples["j5"], wrist_samples["j6"]
    ):
        _assert_pose_is_clear({"j4": j4, "j5": j5, "j6": j6, "j7": 45.0})


def test_compact_fold_is_clear_across_the_base_yaw_range():
    folded = {
        "j2": -105.0,
        "j3": 105.0,
        "j4": -90.0,
        "j5": -90.0,
        "j6": -120.0,
        "j7": 45.0,
    }
    j1_lower, j1_upper = stop_limited_range("j1")
    for j1 in (j1_lower, -70.0, 0.0, 70.0, j1_upper):
        _assert_pose_is_clear({"j1": j1, **folded})


def test_gripper_flexure_engages_between_open_and_closed_stops():
    parts = _parts()
    center, axis = JOINTS["j7"]
    halfway = parts[7].rotate(center, _v_add(center, axis), 22.5)
    assert _intersection_volume(parts[6], halfway) > 10.0


def test_every_channel_fits_the_documented_cable_budget():
    """The modeled pot leads are 200 mm; the chain is over 400 mm long.

    The seller does not specify actual lead length, so README instructions tell
    builders to measure delivered parts and the model checks its stated
    assumption rather than presenting it as a sourced product fact.
    """

    runs = cable_runs()
    assert set(runs) == set(JOINTS)
    for joint, run in runs.items():
        available = POT_LEAD_LENGTH + run["extension_count"] * EXTENSION_LEAD_LENGTH
        assert run["required_mm"] <= available, (joint, run)
    assert {joint: int(run["extension_count"]) for joint, run in runs.items()} == {
        "j1": 0,
        "j2": 1,
        "j3": 1,
        "j4": 2,
        "j5": 2,
        "j6": 3,
        "j7": 3,
    }
    assert set(extension_channels()) == {"j2", "j3", "j4", "j5", "j6", "j7"}
    wires_used = int(
        sum(run["extension_count"] for run in runs.values()) * 3 * LEADER_COUNT
    )
    assert wires_used == 72
    assert wires_used <= JUMPER_PACK_COUNT * JUMPER_PACK_WIRES

    def wires_for_two_leaders(factory_lead_mm):
        segments = sum(
            max(
                0,
                math.ceil(
                    (run["required_mm"] - factory_lead_mm) / EXTENSION_LEAD_LENGTH
                ),
            )
            for run in runs.values()
        )
        return segments * 3 * LEADER_COUNT

    assert wires_for_two_leaders(148.0) == 78
    assert wires_for_two_leaders(148.0) <= JUMPER_PACK_COUNT * JUMPER_PACK_WIRES
    assert wires_for_two_leaders(147.0) > JUMPER_PACK_COUNT * JUMPER_PACK_WIRES


def test_base_pedestal_carries_the_arm_through_a_real_section():
    """The governing section is between the flange sweep and the socket.

    The original pair of 6 mm columns met the socket through two small stub
    lenses and offered about 77 mm^2 there.  Anything near that is a base that
    snaps off at the first firm push on the leader.
    """

    base = build_base()
    thickness = 0.5
    slab = _box(400.0, 400.0, thickness, (0.0, 0.0, 38.0))
    area = base.intersect(slab).val().Volume() / thickness
    assert area > 350.0

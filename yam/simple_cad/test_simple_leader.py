import math

import pytest

from build_simple_leader import (
    AXLE_DIAMETER,
    BEARING_ID,
    BEARING_OD,
    BEARING_POCKET_DEPTH,
    BEARING_POCKET_DIAMETER,
    BEARING_WIDTH,
    CONTROLLER_TRAY_CENTER,
    EXTENSION_LEAD_LENGTH,
    BASE_LIMITED_RANGE_DEG,
    JOINT_LIMITS_DEG,
    JOINTS,
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
    stop_limited_range,
    stop_pin_half_angle,
    usable_range,
    _box,
    _intersection_volume,
    _v_add,
    build_base,
    build_joint_fit_test,
    build_parts,
    cable_runs,
    extension_channels,
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

    Rotating only the immediate child link leaves the rest of the arm, the
    controller tray, and the gripper sitting at the zero pose, which is not a
    configuration the hardware can ever be in.
    """

    lower, upper = _sweep_range(joint)
    for angle in (lower, (lower + upper) / 2.0, upper):
        _assert_pose_is_clear({joint: angle})


@pytest.mark.parametrize(
    "pose",
    [
        # Wrist fully curled with the arm upright.  This is the combination that
        # decides whether the hand can reach the controller tray on link 3, and
        # it is a pose an operator holds routinely rather than an extreme.
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
    """Whole-arm folds are not checked; a serial arm can always hit itself.

    What has to hold is that no single joint, and no wrist combination, runs
    into anything from the neutral pose -- that is assembly step 8.
    """

    _assert_pose_is_clear(pose)


def test_base_blocks_j2_before_its_printed_stop():
    """Pin the one place the declared travel is not actually reachable.

    J2's declared range is +/-105 degrees, but swinging it negative drives link
    2 and link 3 into the base plate about 15 degrees early.  This is recorded
    rather than fixed: it predates the pedestal (the bare plate causes it) and
    changing it means moving joints, not tuning a fit.  The test exists so the
    limit cannot drift without someone noticing.
    """

    declared_lower = JOINT_LIMITS_DEG["j2"][0]
    documented_lower = BASE_LIMITED_RANGE_DEG["j2"][0]
    assert declared_lower < documented_lower, "J2 is no longer base-limited"

    posed = _posed({"j2": declared_lower})
    worst = max(
        _intersection_volume(posed[0], posed[index]) for index in (2, 3)
    )
    assert worst > 10.0, "J2 now reaches its declared stop; update the constant"

    # And the documented limit itself must be clear.
    _assert_pose_is_clear({"j2": documented_lower})


def test_controller_tray_sits_inside_the_wrist_envelope():
    """Pin the second place the declared travel is not actually usable.

    The tray on link 3 lies inside the shell link 5 sweeps about J4, so folding
    the wrist down and across drives link 5 into it -- roughly a quarter of the
    wrist's travel, and 500 mm^3 deep at worst, not a graze.  Link 3's own beam
    is clear; it is entirely the tray.  Moving the tray sideways only mirrors
    the region, because J5 is a yaw axis.  This is recorded rather than fixed
    because relocating the controller is a mechanical change, not a fit
    constant.  See the README for the position that does clear it.
    """

    posed = _posed({"j4": -90.0, "j5": -90.0, "j6": -120.0})
    overlap = _intersection_volume(posed[3], posed[5])
    assert overlap > 100.0, (
        "the wrist now clears the controller tray; update this test, "
        "CONTROLLER_TRAY_CENTER's comment, and the README"
    )


def test_gripper_flexure_engages_between_open_and_closed_stops():
    parts = _parts()
    center, axis = JOINTS["j7"]
    halfway = parts[7].rotate(center, _v_add(center, axis), 22.5)
    assert _intersection_volume(parts[6], halfway) > 10.0


def test_every_channel_fits_the_documented_cable_budget():
    """The pots ship with fixed 200 mm leads; the chain is about 400 mm long.

    No tray position makes both ends reach, so the budget has to be stated and
    checked rather than asserted in a comment.
    """

    runs = cable_runs()
    assert set(runs) == set(JOINTS)
    budget = POT_LEAD_LENGTH + EXTENSION_LEAD_LENGTH
    for joint, run in runs.items():
        assert run["required_mm"] <= budget, (joint, run)
    # The tray is on link 3, so its own channel must not need help.
    assert runs["j4"]["required_mm"] <= POT_LEAD_LENGTH
    assert set(extension_channels()) == {"j1", "j2", "j5", "j6", "j7"}


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

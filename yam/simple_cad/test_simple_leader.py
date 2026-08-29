from build_simple_leader import (
    AXLE_DIAMETER,
    BEARING_ID,
    BEARING_OD,
    BEARING_POCKET_DEPTH,
    BEARING_POCKET_DIAMETER,
    BEARING_WIDTH,
    JOINT_LIMITS_DEG,
    JOINTS,
    POT_BODY_CLEARANCE,
    POT_BODY_DIAMETER,
    POT_BUSHING_CLEARANCE,
    POT_BUSHING_DIAMETER,
    POT_SHAFT_DIAMETER,
    POT_SHAFT_SOCKET_DIAMETER,
    _intersection_volume,
    _v_add,
    build_joint_fit_test,
    build_parts,
    validate_parts,
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


def test_fit_coupon_contains_separate_socket_and_plug_solids():
    coupon = build_joint_fit_test()
    assert coupon.val().isValid()
    assert len(coupon.solids().vals()) == 2


def test_required_rigid_joint_motion_windows_are_collision_free():
    parts = build_parts()
    ordered = list(parts.values())
    for index, (joint, (lower, upper)) in enumerate(JOINT_LIMITS_DEG.items()):
        if joint == "j7":
            # The gripper's printed leaf deliberately meets the fixed post and
            # bends during squeeze; rigid-body boolean intersection is not a
            # valid test between those two angles.
            samples = (lower, upper)
        else:
            samples = (lower, (lower + upper) / 2.0, upper)
        center, axis = JOINTS[joint]
        parent = ordered[index]
        child = ordered[index + 1]
        for angle in samples:
            moved_child = child.rotate(center, _v_add(center, axis), angle)
            assert _intersection_volume(parent, moved_child) < 0.1, (joint, angle)


def test_gripper_flexure_engages_between_open_and_closed_stops():
    parts = list(build_parts().values())
    center, axis = JOINTS["j7"]
    halfway = parts[7].rotate(center, _v_add(center, axis), 22.5)
    assert _intersection_volume(parts[6], halfway) > 10.0

from build_simple_leader import (
    AS5600_BOARD_LONG,
    AS5600_BOARD_SHORT,
    AXLE_DIAMETER,
    BEARING_ID,
    BEARING_OD,
    BEARING_POCKET_DIAMETER,
    MAGNET_DIAMETER,
    MAGNET_POCKET_DIAMETER,
    JOINTS,
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
    assert 0.10 <= BEARING_POCKET_DIAMETER - BEARING_OD <= 0.35
    assert 0.10 <= BEARING_ID - AXLE_DIAMETER <= 0.35
    assert 0.05 <= MAGNET_POCKET_DIAMETER - MAGNET_DIAMETER <= 0.25
    assert AS5600_BOARD_LONG == 25.4
    assert AS5600_BOARD_SHORT == 17.78


def test_fit_coupon_contains_separate_socket_and_plug_solids():
    coupon = build_joint_fit_test()
    assert coupon.val().isValid()
    assert len(coupon.solids().vals()) == 2


def test_required_joint_motion_windows_are_collision_free():
    parts = build_parts()
    ordered = list(parts.values())
    safe_samples = {
        "j1": (-150, -90, 0, 90, 150, 180),
        "j2": (-90, -30, 30, 90, 120),
        "j3": (-120, -60, 0, 60, 120),
        "j4": (-90, -45, 0, 45, 90),
        "j5": (-90, -45, 0, 45, 90),
        "j6": (-120, -60, 0, 60, 120),
        "j7": (-90, -45, 0, 45, 90),
    }
    for index, (joint, angles) in enumerate(safe_samples.items()):
        center, axis = JOINTS[joint]
        parent = ordered[index]
        child = ordered[index + 1]
        for angle in angles:
            moved_child = child.rotate(center, _v_add(center, axis), angle)
            assert _intersection_volume(parent, moved_child) < 0.1, (joint, angle)

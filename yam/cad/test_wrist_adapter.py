from build_wrist_adapter import build_parts, validate_parts


def test_generated_parts_are_valid():
    parts = build_parts()

    validate_parts(parts)

    assert set(parts) == {"yam_wrist_axis_base", "yam_wrist_axis_upright"}
    assert parts["yam_wrist_axis_base"].val().Volume() > 4000
    assert parts["yam_wrist_axis_upright"].val().Volume() > 4000

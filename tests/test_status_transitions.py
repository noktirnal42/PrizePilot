from prizepilot.statuses import validate_transition


def test_allows_normal_review_flow():
    assert validate_transition("Discovered", "Needs Review")
    assert validate_transition("Ready for Review", "Approved to Submit")
    assert validate_transition("Approved to Submit", "Submitted")


def test_rejects_skipping_human_review_gate():
    assert not validate_transition("Discovered", "Submitted")
    assert not validate_transition("In Progress", "Submitted")


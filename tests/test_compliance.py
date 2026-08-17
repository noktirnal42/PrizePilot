from prizepilot.compliance import BLOCKED_MESSAGE, scan_text


def test_blocks_automatic_submission_and_terms_acceptance():
    report = scan_text("Please auto submit this entry and accept terms for me.")

    assert report.level == "Blocked"
    assert report.approval_gate_message == BLOCKED_MESSAGE
    assert any(finding.blocked for finding in report.findings)


def test_flags_fake_nonprofit_claim():
    report = scan_text("Claim 501(c)(3) status and invent credentials for the application.")

    assert report.level == "Blocked"
    assert any("Unsupported identities" in finding.message for finding in report.findings)


def test_safe_text_has_no_findings():
    report = scan_text("Draft a README for human review and mark sources that need verification.")

    assert report.level == "Safe"
    assert report.findings == []


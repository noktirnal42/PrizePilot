from datetime import date

from prizepilot.models import Opportunity
from prizepilot.scoring import score_opportunity


def test_weighted_score_uses_required_scale():
    opportunity = Opportunity(
        id="test",
        title="Agent Hackathon",
        sponsor="Sponsor",
        official_url="https://example.com",
        category="Hackathon / AI Agents",
        prize_amount_or_value="$100,000",
        cash_vs_non_cash_prize="Cash prizes",
        deadline=date(2026, 8, 31),
        eligibility="Remote, solo-friendly",
        entry_fee="No fee",
        required_deliverables="Demo, README, repository, video",
        judging_criteria="Innovation, technical execution, impact",
        important_rules="Official rules allow AI assistance.",
        automation_restrictions="Do not auto-submit.",
        ip_terms="Participant keeps IP; verify official rules.",
    )

    result = score_opportunity(opportunity, today=date(2026, 8, 17))

    assert 0 <= result.weighted_score <= 100
    assert result.prize_value.score == 9
    assert result.deadline_urgency.score == 9
    assert result.label in {"Strong", "Excellent", "Worth considering"}


def test_low_clarity_security_opportunity_scores_lower():
    opportunity = Opportunity(
        id="security",
        title="Unverified Security Program",
        sponsor="Sponsor",
        official_url="https://example.com",
        category="Security Only / Needs Review",
        prize_amount_or_value="Needs verification",
        cash_vs_non_cash_prize="Needs verification",
        required_deliverables="Security testing and report",
        automation_restrictions="Automated scanning blocked unless explicitly allowed.",
        important_rules="Needs verification.",
    )

    result = score_opportunity(opportunity, today=date(2026, 8, 17))

    assert result.rule_clarity_and_safety.score <= 5
    assert result.automation_suitability.score <= 5


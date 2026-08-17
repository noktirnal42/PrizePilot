from datetime import date

from prizepilot.models import Opportunity
from prizepilot.win_plan import generate_win_plan


def test_win_plan_contains_manual_submission_policy():
    opportunity = Opportunity(
        id="all-things-agentic",
        title="All Things Agentic Hackathon",
        sponsor="Google Cloud / Devpost",
        official_url="https://allthingsagentichackathon.devpost.com/",
        category="Hackathon / AI Agents",
        prize_amount_or_value="$180,000",
        cash_vs_non_cash_prize="Mixed cash and credits",
        deadline=date(2026, 8, 31),
        required_deliverables="Working app, repo, architecture, demo video",
        important_rules="Use Gemini 3.5 or newer and Google Cloud.",
        automation_restrictions="Do not auto-submit.",
    )

    plan = generate_win_plan(opportunity)

    joined = " ".join(plan.compliance_notes + plan.final_submission_checklist + plan.submission_checklist)
    assert "never submits" in joined
    assert "outside PrizePilot" in joined
    assert "Gemini" in " ".join(plan.rules_summary)


from __future__ import annotations

from .models import Opportunity, RulesSummary, WinPlan
from .scoring import score_opportunity


def generate_win_plan(opp: Opportunity, rules: RulesSummary | None = None) -> WinPlan:
    score = score_opportunity(opp)
    rules_summary = rules.summary if rules else opp.important_rules
    return WinPlan(
        opportunity_summary=f"{opp.title} by {opp.sponsor}. Category: {opp.category}. Prize: {opp.prize_amount_or_value}. Deadline: {opp.deadline or 'Needs verification'}.",
        why_worth_pursuing=f"Expected value is {score.weighted_score}/100 ({score.label}). It is strongest when the prize, solo fit, reusable deliverables, and AI permission all verify cleanly.",
        rules_summary=[
            rules_summary,
            f"Submission method: {opp.submission_method}",
            f"Automation restrictions: {opp.automation_restrictions}",
        ],
        eligibility_checklist=(rules.eligibility_checklist if rules else [opp.eligibility, "Confirm geographic and age restrictions in official rules."]),
        submission_checklist=[
            "Create or update the project repository.",
            "Prepare README, demo script, screenshots, and architecture notes.",
            "Run compliance scan on every draft before review.",
            "User manually reviews official rules, accepts any terms outside PrizePilot, and submits outside PrizePilot.",
        ],
        judging_criteria_breakdown=(rules.judging_criteria if rules else [opp.judging_criteria, "Map each judging criterion to one demo moment."]),
        best_strategy=[
            "Lead with a concrete, messy workflow and show the agent turning it into a tracked plan.",
            "Make human-in-the-loop gates visible instead of hiding them.",
            "Use official sources for claims and mark unknowns plainly.",
            "Prefer a small, reliable end-to-end demo over broad unsupported automation.",
        ],
        differentiation_angle="PrizePilot is a workflow agent for prize preparation: it ranks opportunities, extracts rules, builds plans, drafts packets, and blocks unsafe actions before submission.",
        required_research=[
            "Official rules page and deadline.",
            "Prize eligibility and tax/reporting notes.",
            "AI-use and automation restrictions.",
            "IP ownership and licensing terms.",
        ],
        required_deliverables=[
            "Working web app.",
            "Code repository.",
            "Architecture diagram.",
            "Demo video script.",
            "Review-only draft submission packet.",
        ],
        work_breakdown=[
            "Verify opportunity facts and eligibility.",
            "Finalize scoring and risk review.",
            "Prepare deliverables and source-backed claims.",
            "Run tests and smoke demo.",
            "Human manually submits through the official platform after approval.",
        ],
        timeline=[
            "Day 1: Verify official rules and lock scope.",
            "Day 2: Build or refine the core demo workflow.",
            "Day 3: Prepare docs, demo script, and submission packet.",
            "Final day: Review compliance gates, record demo, and submit manually.",
        ],
        risks=[
            "Rules may ban or limit AI assistance.",
            "Deadlines, prizes, or eligibility may change.",
            "Unsupported claims could weaken the submission.",
            "Tax, fee, or terms acceptance steps must stay manual.",
        ],
        compliance_notes=[
            "PrizePilot never submits entries automatically.",
            "Blocked actions require explicit human approval and manual completion outside the app.",
            "Do not claim nonprofit or 501(c)(3) status for First Nomadic Church of Bass, LLC without documentation.",
            "Do not invent citations, credentials, endorsements, or evidence.",
        ],
        sources_needed=[
            "Official opportunity URL.",
            "Official rules text.",
            "Sponsor documentation for allowed SDKs, cloud services, and model requirements.",
            "Any user-provided proof for credentials or organizational status.",
        ],
        final_submission_checklist=[
            "Expected value score reviewed.",
            "Compliance report is Safe or accepted as manual Needs Review.",
            "All claims have sources or are removed.",
            "Demo video and README are final.",
            "User submits manually outside PrizePilot.",
        ],
    )


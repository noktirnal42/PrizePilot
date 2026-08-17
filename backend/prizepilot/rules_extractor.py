from __future__ import annotations

import re

from .compliance import scan_text
from .models import RulesSummary


def _lines_for(text: str, terms: list[str]) -> list[str]:
    lines = [line.strip(" -\t") for line in text.splitlines() if line.strip()]
    matched = [line for line in lines if any(term in line.lower() for term in terms)]
    return matched[:8]


def extract_rules_locally(text: str) -> RulesSummary:
    deadline_lines = _lines_for(text, ["deadline", "due", "submit by", "closes"])
    eligibility = _lines_for(text, ["eligible", "eligibility", "resident", "age", "team", "solo"])
    deliverables = _lines_for(text, ["deliverable", "submit", "video", "repo", "readme", "essay", "demo"])
    judging = _lines_for(text, ["judging", "criteria", "score", "innovation", "impact", "technical"])
    ai_notes = _lines_for(text, ["ai", "gemini", "llm", "generative", "model"])
    automation = _lines_for(text, ["automation", "bot", "scrape", "captcha", "submit automatically"])
    ip_terms = _lines_for(text, ["ip", "intellectual property", "license", "ownership", "rights"])
    fees = _lines_for(text, ["fee", "payment", "purchase", "cost"])
    taxes = _lines_for(text, ["tax", "1099", "w-9", "withholding"])
    compliance = scan_text(text)
    unknowns = []
    for label, values in [
        ("Eligibility", eligibility),
        ("Deliverables", deliverables),
        ("Judging criteria", judging),
        ("AI/automation policy", ai_notes + automation),
        ("IP terms", ip_terms),
        ("Tax/reporting notes", taxes),
    ]:
        if not values:
            unknowns.append(f"{label} not found in supplied text; verify official rules.")
    summary = re.sub(r"\s+", " ", text.strip())[:420] or "No rules text supplied."
    return RulesSummary(
        summary=summary,
        eligibility_checklist=eligibility or ["Verify eligibility in the official rules."],
        deliverables_checklist=deliverables or ["Verify required deliverables in the official rules."],
        judging_criteria=judging or ["Verify judging criteria in the official rules."],
        important_deadlines=deadline_lines or ["Verify submission deadline in the official rules."],
        ai_use_notes=ai_notes or ["AI-use policy not found; verify before drafting."],
        automation_notes=automation or ["Automation policy not found; never auto-submit."],
        ip_terms=ip_terms or ["IP terms not found; review before committing work."],
        fees=fees or ["No fee language found in supplied text."],
        tax_notes=taxes or ["Tax notes not found; prizes may still create reporting obligations."],
        risk_flags=[finding.message for finding in compliance.findings],
        unknown_items_to_verify=unknowns,
    )


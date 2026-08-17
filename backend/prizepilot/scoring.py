from __future__ import annotations

from datetime import date
import re

from .models import ExpectedValueScore, Opportunity, ScoreCategory

WEIGHTS = {
    "prize_value": 0.20,
    "probability_of_success": 0.20,
    "skill_fit": 0.15,
    "effort_required": 0.15,
    "deadline_urgency": 0.10,
    "rule_clarity_and_safety": 0.10,
    "reusability_of_work": 0.05,
    "automation_suitability": 0.05,
}


def _money_value(text: str) -> int:
    matches = re.findall(r"\$?\s*([0-9][0-9,]*(?:\.\d+)?)\s*([kKmM]?)", text or "")
    best = 0
    for raw, suffix in matches:
        value = float(raw.replace(",", ""))
        if suffix.lower() == "k":
            value *= 1_000
        elif suffix.lower() == "m":
            value *= 1_000_000
        best = max(best, int(value))
    return best


def _contains(text: str, terms: list[str]) -> bool:
    haystack = (text or "").lower()
    return any(term in haystack for term in terms)


def _score_prize(opp: Opportunity) -> ScoreCategory:
    value = _money_value(opp.prize_amount_or_value)
    if "non-cash" in opp.cash_vs_non_cash_prize.lower() and value < 1_000:
        score = 3
    elif value >= 1_000_000:
        score = 10
    elif value >= 100_000:
        score = 9
    elif value >= 50_000:
        score = 8
    elif value >= 10_000:
        score = 7
    elif value >= 2_500:
        score = 5
    elif value > 0:
        score = 3
    else:
        score = 4
    return ScoreCategory(score=score, explanation=f"Prize signal is '{opp.prize_amount_or_value}', producing a {score}/10 value score.")


def _score_probability(opp: Opportunity) -> ScoreCategory:
    text = f"{opp.notes} {opp.eligibility} {opp.category} {opp.judging_criteria}"
    score = 6
    if _contains(text, ["solo", "beginner", "remote", "open ended"]):
        score += 1
    if _contains(text, ["thousands", "kaggle", "large participant", "highly competitive"]):
        score -= 2
    if _contains(text, ["specialized", "requires credentials", "research-grade", "security only"]):
        score -= 1
    score = max(1, min(10, score))
    return ScoreCategory(score=score, explanation=f"Estimated success odds are {score}/10 based on crowding, specialization, and solo friendliness.")


def _score_skill_fit(opp: Opportunity) -> ScoreCategory:
    text = f"{opp.category} {opp.required_deliverables} {opp.judging_criteria}".lower()
    score = 7 if _contains(text, ["ai", "agent", "software", "hackathon", "cloud", "readme", "demo"]) else 5
    if _contains(text, ["biology", "hardware", "credentials", "wet lab", "proprietary data"]):
        score -= 2
    return ScoreCategory(score=max(1, min(10, score)), explanation="The opportunity appears aligned with an individual AI/software builder when software, demo, and documentation deliverables dominate.")


def _score_effort(opp: Opportunity) -> ScoreCategory:
    text = f"{opp.required_deliverables} {opp.notes} {opp.judging_criteria}".lower()
    score = 7
    if _contains(text, ["paper", "benchmark", "open source", "video", "technical report"]):
        score -= 1
    if _contains(text, ["travel", "hardware", "clinical", "tax documents", "security testing"]):
        score -= 2
    if _contains(text, ["demo", "readme", "devpost"]):
        score += 1
    return ScoreCategory(score=max(1, min(10, score)), explanation="Lower effort receives a higher score; this estimate weighs deliverables, verification, and external dependencies.")


def _score_deadline(opp: Opportunity, today: date | None = None) -> ScoreCategory:
    if opp.deadline is None:
        return ScoreCategory(score=4, explanation="No verified deadline is present, so urgency is useful but uncertain.")
    today = today or date.today()
    days = (opp.deadline - today).days
    if days < 0:
        score = 1
    elif days <= 3:
        score = 4
    elif days <= 21:
        score = 9
    elif days <= 60:
        score = 8
    elif days <= 120:
        score = 6
    else:
        score = 5
    return ScoreCategory(score=score, explanation=f"Deadline is {opp.deadline.isoformat()} ({days} days from the scoring date), giving an urgency score of {score}/10.")


def _score_rules(opp: Opportunity) -> ScoreCategory:
    text = f"{opp.important_rules} {opp.automation_restrictions} {opp.ip_terms} {opp.entry_fee}".lower()
    score = 7
    if "needs verification" in text:
        score -= 2
    if _contains(text, ["ban ai", "no ai", "prohibit ai", "unclear ip", "fee", "tax", "login required"]):
        score -= 2
    if _contains(text, ["official rules", "safe harbor", "no fee", "public"]):
        score += 1
    return ScoreCategory(score=max(1, min(10, score)), explanation="Rule clarity rewards official, explicit, low-risk rules and penalizes unclear automation, fee, tax, or IP terms.")


def _score_reuse(opp: Opportunity) -> ScoreCategory:
    text = f"{opp.category} {opp.required_deliverables} {opp.notes}".lower()
    score = 7 if _contains(text, ["open source", "readme", "demo", "agent", "portfolio", "paper"]) else 5
    return ScoreCategory(score=score, explanation="Reusable demos, repositories, reports, and agent workflows score higher because the work can support later submissions.")


def _score_automation(opp: Opportunity) -> ScoreCategory:
    text = f"{opp.category} {opp.automation_restrictions} {opp.important_rules}".lower()
    score = 7 if _contains(text, ["agent", "automation", "ai", "gemini", "cloud"]) else 5
    if _contains(text, ["ban automation", "manual only", "captcha", "paywall", "login required", "security only"]):
        score -= 3
    return ScoreCategory(score=max(1, min(10, score)), explanation="Automation suitability reflects whether AI assistance is allowed and useful without crossing submission or access-control boundaries.")


def label_for_score(score: float) -> str:
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Strong"
    if score >= 55:
        return "Worth considering"
    if score >= 40:
        return "Weak unless strategic"
    return "Not recommended"


def score_opportunity(opp: Opportunity, today: date | None = None) -> ExpectedValueScore:
    categories = {
        "prize_value": _score_prize(opp),
        "probability_of_success": _score_probability(opp),
        "skill_fit": _score_skill_fit(opp),
        "effort_required": _score_effort(opp),
        "deadline_urgency": _score_deadline(opp, today),
        "rule_clarity_and_safety": _score_rules(opp),
        "reusability_of_work": _score_reuse(opp),
        "automation_suitability": _score_automation(opp),
    }
    weighted = sum(categories[key].score * weight * 10 for key, weight in WEIGHTS.items())
    return ExpectedValueScore(**categories, weighted_score=round(weighted, 1), label=label_for_score(weighted))


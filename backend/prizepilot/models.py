from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl

from .statuses import STATUSES

RiskLevel = Literal["Safe", "Needs Review", "Risky", "Blocked"]
StatusValue = Literal[
    "Discovered",
    "Needs Review",
    "Eligible",
    "Not Eligible",
    "Risky",
    "Selected",
    "In Progress",
    "Draft Complete",
    "Ready for Review",
    "Approved to Submit",
    "Submitted",
    "Won",
    "Lost",
    "Archived",
]


class Opportunity(BaseModel):
    id: str
    title: str
    sponsor: str
    official_url: HttpUrl | str
    category: str
    prize_amount_or_value: str = "Needs verification"
    cash_vs_non_cash_prize: str = "Needs verification"
    deadline: date | None = None
    eligibility: str = "Needs verification"
    geographic_restrictions: str = "Needs verification"
    required_account_platform: str = "Needs verification"
    entry_fee: str = "Needs verification"
    required_deliverables: str = "Needs verification"
    submission_method: str = "Needs verification"
    judging_criteria: str = "Needs verification"
    important_rules: str = "Needs verification"
    automation_restrictions: str = "Needs verification"
    ip_terms: str = "Needs verification"
    tax_reporting_notes: str = "Needs verification"
    notes: str = ""
    status: StatusValue = "Discovered"
    source_notes: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = "Needs Review"
    expected_value_score: float | None = None
    next_action: str = "Review official rules and verify eligibility."


class OpportunityCreate(BaseModel):
    title: str
    sponsor: str
    official_url: str
    category: str
    prize_amount_or_value: str = "Needs verification"
    cash_vs_non_cash_prize: str = "Needs verification"
    deadline: date | None = None
    eligibility: str = "Needs verification"
    geographic_restrictions: str = "Needs verification"
    required_account_platform: str = "Needs verification"
    entry_fee: str = "Needs verification"
    required_deliverables: str = "Needs verification"
    submission_method: str = "Needs verification"
    judging_criteria: str = "Needs verification"
    important_rules: str = "Needs verification"
    automation_restrictions: str = "Needs verification"
    ip_terms: str = "Needs verification"
    tax_reporting_notes: str = "Needs verification"
    notes: str = ""
    status: StatusValue = "Discovered"


class ScoreCategory(BaseModel):
    score: int = Field(ge=1, le=10)
    explanation: str


class ExpectedValueScore(BaseModel):
    prize_value: ScoreCategory
    probability_of_success: ScoreCategory
    skill_fit: ScoreCategory
    effort_required: ScoreCategory
    deadline_urgency: ScoreCategory
    rule_clarity_and_safety: ScoreCategory
    reusability_of_work: ScoreCategory
    automation_suitability: ScoreCategory
    weighted_score: float
    label: str


class RulesSummary(BaseModel):
    summary: str
    eligibility_checklist: list[str]
    deliverables_checklist: list[str]
    judging_criteria: list[str]
    important_deadlines: list[str]
    ai_use_notes: list[str]
    automation_notes: list[str]
    ip_terms: list[str]
    fees: list[str]
    tax_notes: list[str]
    risk_flags: list[str]
    unknown_items_to_verify: list[str]


class WinPlan(BaseModel):
    opportunity_summary: str
    why_worth_pursuing: str
    rules_summary: list[str]
    eligibility_checklist: list[str]
    submission_checklist: list[str]
    judging_criteria_breakdown: list[str]
    best_strategy: list[str]
    differentiation_angle: str
    required_research: list[str]
    required_deliverables: list[str]
    work_breakdown: list[str]
    timeline: list[str]
    risks: list[str]
    compliance_notes: list[str]
    sources_needed: list[str]
    final_submission_checklist: list[str]


class DraftRequest(BaseModel):
    material_type: str
    opportunity_id: str | None = None
    prompt: str
    user_facts: str = ""


class DraftPacket(BaseModel):
    material_type: str
    draft: str
    assumptions: list[str]
    claims_needing_verification: list[str]
    missing_user_inputs: list[str]
    final_review_checklist: list[str]


class ComplianceFinding(BaseModel):
    level: RiskLevel
    category: str
    message: str
    blocked: bool = False


class ComplianceReport(BaseModel):
    level: RiskLevel
    findings: list[ComplianceFinding]
    approval_gate_message: str | None = None


class TextPayload(BaseModel):
    text: str


class StatusUpdate(BaseModel):
    status: StatusValue


class ApiEnvelope(BaseModel):
    data: Any
    warnings: list[str] = Field(default_factory=list)
    agent_mode: str = "local-fallback"
    allowed_statuses: list[str] = Field(default_factory=lambda: STATUSES)


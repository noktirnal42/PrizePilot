from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .agent import AgentOrchestrator
from .compliance import scan_text
from .drafting import generate_draft_locally
from .models import (
    ApiEnvelope,
    DraftRequest,
    OpportunityCreate,
    RulesSummary,
    StatusUpdate,
    TextPayload,
)
from .rules_extractor import extract_rules_locally
from .scoring import score_opportunity
from .statuses import STATUSES, validate_transition
from .storage import OpportunityStore
from .win_plan import generate_win_plan

app = FastAPI(title="PrizePilot API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = OpportunityStore()
agent = AgentOrchestrator()


def envelope(data, warnings: list[str] | None = None) -> ApiEnvelope:
    return ApiEnvelope(data=data, warnings=warnings or [], agent_mode=agent.mode)


@app.get("/health")
def health():
    return {
        "ok": True,
        "agent_mode": agent.mode,
        "storage_mode": store.mode,
        "google_cloud_services": ["Cloud Run", "Firestore"],
        "gemini_model": agent.model,
    }


@app.get("/api/statuses")
def statuses():
    return envelope(STATUSES)


@app.get("/api/opportunities")
def list_opportunities(
    category: str | None = Query(default=None),
    status: str | None = Query(default=None),
    risk: str | None = Query(default=None),
):
    items = store.list()
    for item in items:
        if item.expected_value_score is None:
            item.expected_value_score = score_opportunity(item).weighted_score
    if category:
        items = [item for item in items if item.category == category]
    if status:
        items = [item for item in items if item.status == status]
    if risk:
        items = [item for item in items if item.risk_level == risk]
    items.sort(key=lambda item: (item.expected_value_score or 0), reverse=True)
    return envelope(items)


@app.post("/api/opportunities")
def create_opportunity(payload: OpportunityCreate):
    opportunity = store.create(payload)
    return envelope(opportunity)


@app.get("/api/opportunities/{opportunity_id}")
def get_opportunity(opportunity_id: str):
    opportunity = store.get(opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return envelope(opportunity)


@app.patch("/api/opportunities/{opportunity_id}/status")
def update_status(opportunity_id: str, payload: StatusUpdate):
    opportunity = store.get(opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    if not validate_transition(opportunity.status, payload.status):
        raise HTTPException(status_code=409, detail=f"Invalid status transition: {opportunity.status} -> {payload.status}")
    opportunity.status = payload.status
    store.upsert(opportunity)
    return envelope(opportunity)


@app.post("/api/opportunities/{opportunity_id}/score")
def score(opportunity_id: str):
    opportunity = store.get(opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    result = score_opportunity(opportunity)
    opportunity.expected_value_score = result.weighted_score
    opportunity.next_action = "Generate win plan and verify unknown rules." if result.weighted_score >= 55 else "Archive unless there is strategic value."
    store.upsert(opportunity)
    return envelope(result)


@app.post("/api/opportunities/{opportunity_id}/extract-rules")
def extract_rules(opportunity_id: str, payload: TextPayload):
    if not store.get(opportunity_id):
        raise HTTPException(status_code=404, detail="Opportunity not found")
    fallback = extract_rules_locally(payload.text)
    prompt = (
        "Extract lawful contest rules as JSON. Never invent facts; use 'verify' for unknowns. "
        "Do not scrape, bypass login, accept terms, or submit anything.\n\n"
        f"Rules text:\n{payload.text}"
    )
    result = agent.structured_generate(prompt, RulesSummary, fallback)
    return envelope(result)


@app.post("/api/opportunities/{opportunity_id}/win-plan")
def win_plan(opportunity_id: str):
    opportunity = store.get(opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return envelope(generate_win_plan(opportunity))


@app.post("/api/drafts")
def drafts(payload: DraftRequest):
    opportunity = store.get(payload.opportunity_id) if payload.opportunity_id else None
    draft = generate_draft_locally(payload, opportunity)
    report = scan_text(draft.draft + "\n" + payload.user_facts)
    return envelope({"draft": draft, "compliance": report})


@app.post("/api/compliance/scan")
def compliance_scan(payload: TextPayload):
    return envelope(scan_text(payload.text))


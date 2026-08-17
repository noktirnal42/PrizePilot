from __future__ import annotations

from .models import DraftPacket, DraftRequest, Opportunity


def generate_draft_locally(request: DraftRequest, opportunity: Opportunity | None = None) -> DraftPacket:
    title = opportunity.title if opportunity else "the selected opportunity"
    draft = (
        f"# {request.material_type} draft for {title}\n\n"
        f"{request.prompt.strip()}\n\n"
        "PrizePilot prepares this material for human review only. It does not submit, accept terms, "
        "pay fees, or claim unsupported credentials. Replace every bracketed item with verified facts "
        "before use.\n\n"
        "Suggested positioning: describe the problem, the workflow agent, the Google Gemini/GenAI SDK "
        "integration, Cloud Run deployment path, Firestore tracking, compliance gates, and the visible "
        "human approval policy."
    )
    return DraftPacket(
        material_type=request.material_type,
        draft=draft,
        assumptions=[
            "The user is an individual builder unless documented organization status is provided.",
            "First Nomadic Church of Bass, LLC is treated only as an inactive or early-stage LLC.",
            "All external submission steps remain manual.",
        ],
        claims_needing_verification=[
            "Prize amounts, deadlines, eligibility, and judging criteria.",
            "Any statistics, endorsements, or impact claims.",
            "Any sponsor-specific API, SDK, or cloud deployment requirements.",
        ],
        missing_user_inputs=[
            "Final project URL or repository URL.",
            "Screenshots or demo video link.",
            "Verified user bio, credentials, and contact details if required.",
        ],
        final_review_checklist=[
            "Run compliance scan.",
            "Remove unsupported claims.",
            "Verify official rules.",
            "Submit manually outside PrizePilot only after user approval.",
        ],
    )


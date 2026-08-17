# PrizePilot Architecture

PrizePilot uses a simple production-minded split:

- Frontend: Vite + React dashboard.
- Backend: FastAPI service deployable to Cloud Run.
- Agent framework: Google GenAI SDK through `google-genai`.
- Model: `gemini-3.5-flash` by default, configurable with `GEMINI_MODEL`.
- Database: Firestore in cloud mode, local JSON fixtures in demo mode.
- Tests: pytest for scoring, compliance, status transitions, and win-plan generation.

```mermaid
flowchart TB
    User["User"] --> UI["Web UI"]
    UI --> API["Cloud Run API"]
    API --> Agent["Agent orchestrator"]
    Agent --> Extractor["Rules extractor"]
    Agent --> EV["Expected value scorer"]
    Agent --> Plan["Win Plan generator"]
    Agent --> Draft["Drafting assistant"]
    Agent --> Compliance["Compliance gatekeeper"]
    Agent --> Gemini["Gemini 3.5+ via Google GenAI SDK"]
    API --> Firestore["Firestore tracker"]
    API --> Export["Exported review packet"]
    Compliance --> Gate["Blocked manual approval gate"]
```

The backend keeps the safety boundary server-side. The frontend can ask for drafts or plans, but compliance scanning remains a first-class backend module. The app intentionally has no endpoint that submits contests, accepts terms, pays fees, uploads tax documents, or creates accounts.


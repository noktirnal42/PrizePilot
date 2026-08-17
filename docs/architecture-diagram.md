# PrizePilot Architecture Diagram

```mermaid
flowchart LR
    User["User / human reviewer"] --> Web["React Web UI"]
    Web --> API["Cloud Run FastAPI service"]
    API --> Orchestrator["Agent orchestrator"]
    Orchestrator --> Rules["Rules extractor"]
    Orchestrator --> Scorer["Expected value scorer"]
    Orchestrator --> Planner["Win Plan generator"]
    Orchestrator --> Drafter["Drafting assistant"]
    Orchestrator --> Gatekeeper["Compliance gatekeeper"]
    Rules --> Gemini["Gemini 3.5+ via Google GenAI SDK"]
    Drafter --> Gemini
    API --> Firestore["Firestore opportunity tracker"]
    API --> Packet["Exported review packet / draft materials"]
    Gatekeeper --> Approval["Human approval gate: blocked actions stay manual"]
    Approval --> User
```

PrizePilot is a web workflow agent. The browser calls the Cloud Run API, which coordinates specialized modules for intake, rules extraction, scoring, planning, drafting, and compliance review. Gemini 3.5+ is accessed through the Google GenAI SDK when `GEMINI_API_KEY` is configured. Firestore is the production tracker, while local JSON fixtures are used for demos and tests.


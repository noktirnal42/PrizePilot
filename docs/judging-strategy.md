# Judging Strategy

## Primary Track: Taskmaster

PrizePilot should be judged as a complete workflow agent rather than a chatbot. It starts with messy opportunity details and produces a structured, ranked, compliance-checked plan with review-only drafts.

## Demo Signals

- Multi-step workflow: intake, extract, score, plan, draft, compliance scan, dashboard.
- Gemini requirement: backend uses `google-genai` with default model `gemini-3.5-flash` or newer.
- Google Cloud requirement: Cloud Run deployment path plus Firestore storage switch.
- Human control: blocked actions cannot proceed inside PrizePilot.
- Practical value: the app directly helps prepare the All Things Agentic submission packet.

## Differentiation

Many agent demos automate an isolated task. PrizePilot manages a full opportunity lifecycle and explicitly refuses unsafe shortcuts such as automatic submissions, invented credentials, fee payment, tax uploads, and unauthorized security testing.


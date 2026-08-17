# Deployment Proof

## Cloud Run

- Project: `prizepilot-mvp-2026`
- Region: `us-central1`
- Service: `prizepilot`
- Revision verified: `prizepilot-00005-ltg`
- Public URL: `https://prizepilot-zav4ngm6ua-uc.a.run.app`

## Health Check

```bash
curl -s https://prizepilot-zav4ngm6ua-uc.a.run.app/health | python3 -m json.tool
```

Expected signal:

```json
{
  "ok": true,
  "agent_mode": "gemini-genai-sdk-vertex-ai",
  "storage_mode": "firestore",
  "google_cloud_services": ["Cloud Run", "Firestore"],
  "gemini_model": "gemini-3.5-flash",
  "vertex_ai": true
}
```

## Gemini / Vertex AI Verification

```bash
curl -s -X POST \
  https://prizepilot-zav4ngm6ua-uc.a.run.app/api/opportunities/all-things-agentic-2026/extract-rules \
  -H 'Content-Type: application/json' \
  -d '{"text":"Deadline: August 31, 2026. Eligible solo builders can submit a web app, repository, architecture diagram, and demo video. Use Gemini 3.5 or newer and Google Cloud. Do not auto submit. IP terms and tax notes need verification."}' \
  | python3 -m json.tool
```

Expected signal:

- `agent_mode` is `gemini-genai-sdk-vertex-ai`
- `warnings` is `[]`
- Output includes structured deadlines, deliverables, AI-use notes, automation notes, and unknown items to verify.

## Cloud Run Logs

```bash
gcloud run services logs read prizepilot \
  --region us-central1 \
  --project prizepilot-mvp-2026 \
  --limit=30
```

Use this in the demo to show live Google Cloud request logs.


# PrizePilot

PrizePilot is a human-in-the-loop AI workflow agent for finding, evaluating, prioritizing, and preparing legitimate prize, contest, bounty, grant, hackathon, and challenge opportunities.

## Problem

Prize hunting is a messy multi-step chore: rules are scattered, eligibility is unclear, deadlines shift, prize values are hard to compare, and unsafe shortcuts can create compliance risk.

## Solution

PrizePilot turns each opportunity into a tracked workflow: intake, rules extraction, expected value scoring, Win Plan generation, review-only drafting, compliance scanning, and dashboard prioritization.

## Key Features

- Manual opportunity intake with all required prize/rules fields.
- Rules Extractor agent for pasted official rules or user-supplied text.
- Expected Value Scorer using the required weighted 0-100 model.
- Win Plan Generator for strategy, deliverables, timeline, risks, and final review.
- Drafting Assistant for review-only materials with assumptions and missing inputs.
- Compliance Gatekeeper that blocks risky actions.
- Dashboard with ranking, status, deadline, prize, risk, next action, and filters.

## Safety Principles

PrizePilot never submits entries, accepts terms, creates accounts, invents evidence, pays fees, uploads tax documents, bypasses access controls, or performs unauthorized security testing. Blocked actions require manual approval outside the app.

## Architecture

See [ARCHITECTURE.md](/Users/jeremymcvay/dev/PrizePilot/ARCHITECTURE.md) and [docs/architecture-diagram.md](/Users/jeremymcvay/dev/PrizePilot/docs/architecture-diagram.md).

## Tech Stack

- Frontend: Vite + React.
- Backend: Python FastAPI.
- Agent framework: Google GenAI SDK (`google-genai`).
- Model: `gemini-3.5-flash` or newer through Gemini API.
- Cloud infrastructure: Cloud Run and Firestore.
- Local demo storage: JSON fixtures.
- Tests: pytest.

## Google Cloud Services Used

- Cloud Run for the backend API container.
- Firestore for production opportunity tracking.
- Cloud Logging through Cloud Run request/runtime logs.

## Gemini / Agent Framework Usage

`backend/prizepilot/agent.py` wraps the Google GenAI SDK. If `GEMINI_API_KEY` is set, structured rules extraction can call Gemini. If credentials are missing, PrizePilot uses deterministic local fallback behavior so judges can run the demo without paid services.

## Local Setup

Fast path:

```bash
./scripts/start-local.sh
```

Then open `http://127.0.0.1:5173`.

Manual backend:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=backend uvicorn prizepilot.main:app --reload --host 127.0.0.1 --port 8080
```

In a second terminal:

```bash
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

## Firestore Setup

```bash
gcloud services enable firestore.googleapis.com
gcloud firestore databases create --region=us-central1
export USE_FIRESTORE=true
export GOOGLE_CLOUD_PROJECT="your-project-id"
export FIRESTORE_COLLECTION="opportunities"
```

For local development, authenticate with:

```bash
gcloud auth application-default login
```

## Environment Variables

Copy `.env.example` to `.env` for local use. Important variables:

- `GEMINI_API_KEY`: optional for live Gemini calls.
- `GEMINI_MODEL`: defaults to `gemini-3.5-flash`.
- `USE_FIRESTORE`: `false` for local fixtures, `true` for Firestore.
- `GOOGLE_CLOUD_PROJECT`: required for Firestore/Cloud Run.
- `FIRESTORE_COLLECTION`: defaults to `opportunities`.
- `VITE_API_BASE_URL`: frontend API URL.

## Cloud Run Deployment

PrizePilot can deploy as one Cloud Run service that serves both the React website and FastAPI API.

Guarded script:

```bash
CONFIRM_DEPLOY=YES PROJECT_ID=your-project-id ./scripts/deploy-cloud-run.sh
```

Manual commands:

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com firestore.googleapis.com
gcloud artifacts repositories create prizepilot --repository-format=docker --location=us-central1
gcloud builds submit --tag us-central1-docker.pkg.dev/PROJECT_ID/prizepilot/api:latest
gcloud run deploy prizepilot-api \
  --image us-central1-docker.pkg.dev/PROJECT_ID/prizepilot/api:latest \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars USE_FIRESTORE=true,GOOGLE_CLOUD_PROJECT=PROJECT_ID,GEMINI_MODEL=gemini-3.5-flash \
  --set-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest
```

Replace `PROJECT_ID` and configure Secret Manager before using `--set-secrets`. Deployment is optional unless credentials are available.

If `gcloud` is missing on macOS:

```bash
brew install --cask google-cloud-sdk
gcloud init
```

## Demo Flow

1. Open the dashboard and select All Things Agentic Hackathon.
2. Paste official rules text into Rules Extractor.
3. Score the opportunity.
4. Generate a Win Plan.
5. Generate a review-only draft packet.
6. Scan an unsafe instruction such as "auto submit and accept terms" and show the Blocked gate.
7. Show `/health` for model, agent mode, storage mode, and Cloud Run readiness.

## Testing

```bash
PYTHONPATH=backend pytest
```

The test suite covers scoring, compliance flags, status transitions, and Win Plan generation.

## Limitations

- Live Gemini calls require a Gemini API key.
- Firestore requires Google Cloud credentials and a configured project.
- Fixture opportunity fields are sample data; fields marked "Needs verification" must be checked against official rules.
- The frontend does not submit entries or export files yet; it prepares review content.

## Human Approval Policy

Any final submission, account creation, terms acceptance, fee payment, tax document upload, sensitive data handling, or security testing must be completed manually outside PrizePilot after explicit user approval.

## Submission Checklist

- Code repo prepared.
- Local app runs.
- Tests pass.
- Architecture diagram included.
- Cloud Run deployment instructions included.
- Firestore setup included.
- Gemini/GenAI SDK usage documented.
- Demo script included.
- Compliance policy included.
- User manually submits the hackathon entry outside PrizePilot.

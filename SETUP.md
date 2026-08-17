# Setup

## Local Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=backend uvicorn prizepilot.main:app --reload --host 127.0.0.1 --port 8080
```

## Local Frontend

```bash
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

## Tests

```bash
PYTHONPATH=backend pytest
```

## One-Service Container

The Dockerfile builds the React frontend and serves it from FastAPI. This lets Cloud Run host both the website and API from one service:

```bash
docker build -t prizepilot .
docker run --rm -p 8080:8080 prizepilot
```

Then open `http://127.0.0.1:8080`.

## Gemini

Local demo works without credentials. To use Gemini:

```bash
export GEMINI_API_KEY="your-key"
export GEMINI_MODEL="gemini-3.5-flash"
```

## Firestore

Local demo uses fixtures. To use Firestore:

```bash
export USE_FIRESTORE=true
export GOOGLE_CLOUD_PROJECT="your-project-id"
export FIRESTORE_COLLECTION="opportunities"
```

Authenticate with `gcloud auth application-default login` or run on Cloud Run with a service account that has Firestore permissions.

## Cloud Run

Use the guarded deploy script after you install and authenticate Google Cloud CLI:

```bash
CONFIRM_DEPLOY=YES PROJECT_ID=your-project-id ./scripts/deploy-cloud-run.sh
```

The script refuses to run unless `CONFIRM_DEPLOY=YES` is present.

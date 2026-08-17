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


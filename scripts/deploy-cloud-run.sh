#!/usr/bin/env bash
set -euo pipefail

if [ "${CONFIRM_DEPLOY:-}" != "YES" ]; then
  echo "Refusing to deploy without explicit confirmation."
  echo "Run with CONFIRM_DEPLOY=YES PROJECT_ID=your-project-id ./scripts/deploy-cloud-run.sh"
  exit 2
fi

if ! command -v gcloud >/dev/null 2>&1; then
  echo "gcloud is not installed. Install Google Cloud CLI first:"
  echo "  brew install --cask google-cloud-sdk"
  exit 127
fi

PROJECT_ID="${PROJECT_ID:?Set PROJECT_ID to your Google Cloud project id}"
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-prizepilot}"
REPOSITORY="${REPOSITORY:-prizepilot}"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/api:latest"

gcloud config set project "${PROJECT_ID}"
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com firestore.googleapis.com

if ! gcloud artifacts repositories describe "${REPOSITORY}" --location="${REGION}" >/dev/null 2>&1; then
  gcloud artifacts repositories create "${REPOSITORY}" \
    --repository-format=docker \
    --location="${REGION}" \
    --description="PrizePilot containers"
fi

gcloud builds submit --tag "${IMAGE}"

gcloud run deploy "${SERVICE}" \
  --image "${IMAGE}" \
  --region "${REGION}" \
  --allow-unauthenticated \
  --set-env-vars "USE_FIRESTORE=true,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GEMINI_MODEL=${GEMINI_MODEL:-gemini-3.5-flash}"

echo
echo "Deployment complete. Open the Cloud Run service URL printed above."
echo "If you want live Gemini calls, add GEMINI_API_KEY through Secret Manager and redeploy with --set-secrets."

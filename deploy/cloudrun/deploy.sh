#!/usr/bin/env bash
# ==============================================================================
# AoE2 Coach AI — Automated Google Cloud Run Deployment Script
# Deploys backend API container and Next.js frontend to GCP Cloud Run.
# ==============================================================================

set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-aoe2-coach-prod}"
REGION="${GCP_REGION:-us-central1}"
BACKEND_IMAGE="gcr.io/${PROJECT_ID}/backend:latest"
FRONTEND_IMAGE="gcr.io/${PROJECT_ID}/frontend:latest"

echo "================================================================================"
echo "          AoE2 COACH AI — GOOGLE CLOUD RUN DEPLOYMENT PIPELINE                  "
echo "================================================================================"
echo "Project ID: ${PROJECT_ID}"
echo "Region:     ${REGION}"
echo "--------------------------------------------------------------------------------"

# 1. Build and push backend image
echo "[1/4] Building Backend Image with Google Cloud Build..."
gcloud builds submit --project="${PROJECT_ID}" --tag="${BACKEND_IMAGE}" .

# 2. Deploy backend service
echo "[2/4] Deploying Backend Service to Cloud Run..."
gcloud run deploy aoe2-coach-backend \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --image="${BACKEND_IMAGE}" \
  --platform=managed \
  --allow-unauthenticated \
  --cpu=2 \
  --memory=2Gi \
  --min-instances=1 \
  --max-instances=10 \
  --concurrency=80 \
  --port=8000 \
  --set-env-vars="HOST=0.0.0.0,PORT=8000,WORKERS=4,LOG_LEVEL=info"

BACKEND_URL=$(gcloud run services describe aoe2-coach-backend --project="${PROJECT_ID}" --region="${REGION}" --format='value(status.url)')
echo "[✓] Backend Service Deployed at: ${BACKEND_URL}"

# 3. Build and push frontend image
echo "[3/4] Building Frontend Image with Google Cloud Build..."
gcloud builds submit --project="${PROJECT_ID}" --tag="${FRONTEND_IMAGE}" ./frontend

# 4. Deploy frontend service
echo "[4/4] Deploying Frontend Service to Cloud Run..."
gcloud run deploy aoe2-coach-frontend \
  --project="${PROJECT_ID}" \
  --region="${REGION}" \
  --image="${FRONTEND_IMAGE}" \
  --platform=managed \
  --allow-unauthenticated \
  --cpu=1 \
  --memory=1Gi \
  --min-instances=1 \
  --max-instances=6 \
  --concurrency=100 \
  --port=3000 \
  --set-env-vars="NODE_ENV=production,NEXT_PUBLIC_API_URL=${BACKEND_URL}"

FRONTEND_URL=$(gcloud run services describe aoe2-coach-frontend --project="${PROJECT_ID}" --region="${REGION}" --format='value(status.url)')
echo "================================================================================"
echo "[🎉] Deployment Complete!"
echo "Backend API:  ${BACKEND_URL}"
echo "Web UI:       ${FRONTEND_URL}"
echo "================================================================================"

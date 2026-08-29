# Age of Empires II: DE — AI Coach Production Deployment & Operations Guide
## Phase 6: Production Engineering & Multi-Target Deployment Manual

---

## 1. Architecture & Deployment Targets Overview

**AoE2 Coach AI** is an ultra-low latency (<20ms), high-concurrency decision-support platform designed to provide real-time strategic recommendations during active *Age of Empires II: Definitive Edition* matches.

```
                                  +---------------------------+
                                  |      GLOBAL USERS         |
                                  +-------------+-------------+
                                                |
                                                v
                   +---------------------------------------------------------+
                   |           CLOUDFLARE CDN / VERCEL EDGE NETWORK          |
                   |   - Static Asset Caching (HTML, CSS, JS, AoE2 Icons)    |
                   |   - TLS 1.3 Termination & DDoS Mitigation               |
                   |   - Direct Route: "/" -> Next.js 15 Standalone UI       |
                   |   - Proxy Route:  "/api/*" -> FastAPI Gateway           |
                   +----------------------------+----------------------------+
                                                |
                                                v
                   +---------------------------------------------------------+
                   |                PRODUCTION BACKEND RUNTIME               |
                   |      (Kubernetes / Google Cloud Run / Docker Cluster)   |
                   |                                                         |
                   |  +---------------------------------------------------+  |
                   |  |          FastAPI API Gateway (Gunicorn/Uvicorn)   |  |
                   |  +-------------------------+-------------------------+  |
                   |                            |                            |
                   |        +-------------------+-------------------+        |
                   |        |                                       |        |
                   |        v                                       v        |
                   |  +-------------------+                   +-----------+  |
                   |  | ONNX Inference    |                   | Rules &   |  |
                   |  | Engine (<2ms P99) |                   | Counters  |  |
                   |  +---------+---------+                   +-----+-----+  |
                   |            |                                   |        |
                   |            +-----------------+-----------------+        |
                   |                              |                          |
                   |                              v                          |
                   |  +---------------------------------------------------+  |
                   |  | Verified Tactical Explainer & ELO Calibrator     |  |
                   |  | (Deterministic Fallback <1ms | LLM Endpoint)     |  |
                   |  +---------------------------------------------------+  |
                   +---------------------------------------------------------+
```

---

## 2. Quickstart: Local Multi-Container Deployment (Docker Compose)

### 2.1 Standard Stack (FastAPI Backend + Next.js Frontend)

To launch the full stack locally with hot reloading and production containers:

```bash
# Clone the repository
git clone https://github.com/your-org/aoe2-coach.git
cd aoe2-coach

# Build and start services in background
docker compose up -d --build
```

- **Frontend Web UI**: `http://localhost:3000`
- **Backend API Gateway**: `http://localhost:8000`
- **Interactive OpenAPI Swagger Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/health`

### 2.2 Full Stack with Local CPU LLM Inference (`llama.cpp`)

To include the local CPU-optimized `llama.cpp` server running `Qwen3.8-4B-Distill-GGUF`:

```bash
docker compose --profile full-local-llm up -d --build
```

### 2.3 Stop Containers
```bash
docker compose down
```

---

## 3. Kubernetes Production Deployment (`k8s/`)

The Kubernetes configuration is packaged with Kustomize and includes multi-replica deployments, resource limits, security contexts (non-root UID 10001), health probes, horizontal pod autoscaling, and path-based ingress.

### 3.1 Directory Structure
```
k8s/
├── namespace.yaml                # Dedicated 'aoe2-coach' namespace
├── configmap.yaml                # Non-sensitive runtime parameters
├── secrets.example.yaml          # Template for API keys & secrets
├── backend-deployment.yaml       # 3-replica FastAPI deployment with rolling updates
├── backend-service.yaml          # ClusterIP service for backend (Port 8000)
├── frontend-deployment.yaml      # 2-replica Next.js 15 standalone UI
├── frontend-service.yaml         # ClusterIP service for frontend (Port 3000)
├── ingress.yaml                  # NGINX / Cert-Manager Ingress with TLS
├── hpa.yaml                      # HorizontalPodAutoscaler (CPU 75%, Memory 80%)
└── kustomization.yaml            # Single-command Kustomize bundle
```

### 3.2 Production Deployment Steps

```bash
# 1. Create Secret from real credentials
kubectl create secret generic aoe2-coach-secrets \
  --namespace=aoe2-coach \
  --from-literal=LLM_API_KEY="your-llm-api-key" \
  --dry-run=client -o yaml | kubectl apply -f -

# 2. Deploy all manifests using Kustomize
kubectl apply -k k8s/

# 3. Verify rollout status
kubectl rollout status deployment/aoe2-coach-backend -n aoe2-coach
kubectl rollout status deployment/aoe2-coach-frontend -n aoe2-coach

# 4. Check pod health and autoscaling status
kubectl get pods -n aoe2-coach
kubectl get hpa -n aoe2-coach
```

---

## 4. Google Cloud Run (Serverless Container Deployment)

Google Cloud Run provides serverless container execution with instant scaling, zero idle cost, and startup CPU boosting.

### 4.1 Automated One-Command Deploy

```bash
# Make deploy script executable and run
chmod +x deploy/cloudrun/deploy.sh
export GCP_PROJECT_ID="your-gcp-project-id"
export GCP_REGION="us-central1"

./deploy/cloudrun/deploy.sh
```

### 4.2 Manual Cloud Run CLI Commands

```bash
# Build & push backend image
gcloud builds submit --tag gcr.io/${GCP_PROJECT_ID}/aoe2-coach-backend:latest .

# Deploy Backend to Cloud Run
gcloud run deploy aoe2-coach-backend \
  --image gcr.io/${GCP_PROJECT_ID}/aoe2-coach-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --cpu 2 \
  --memory 2Gi \
  --min-instances 1 \
  --max-instances 10 \
  --concurrency 80 \
  --port 8000 \
  --set-env-vars="HOST=0.0.0.0,PORT=8000,WORKERS=4"
```

---

## 5. Vercel & Cloudflare Pages Frontend Deployment

### 5.1 Vercel Deployment

The frontend Next.js 15 application is pre-configured with `frontend/vercel.json` for optimal edge routing and API proxying:

```bash
cd frontend

# Deploy preview
vercel

# Deploy production
vercel --prod
```

**Environment Variables in Vercel:**
- `NEXT_PUBLIC_API_URL`: `https://api.aoe2coach.ai` (points to production backend)

### 5.2 Cloudflare Pages Deployment

Using the included `frontend/wrangler.toml`:

```bash
cd frontend
npm run build
npx wrangler pages deploy .next
```

---

## 6. Benchmarking & Quality Assurance

Run the automated validation suites before deploying any update:

### 6.1 Pro Tournament Match Benchmarking
```bash
uv run python scripts/benchmark_pro_matches.py --iterations 10 --export-json benchmark_report.json --export-md BENCHMARK_REPORT.md
```
- **Top-1 Strategy Accuracy:** $\ge 85.0\%$
- **Top-3 Strategy Recall:** $\ge 90.0\%$
- **ML ONNX Inference P99 Latency:** $< 2.5$ ms

### 6.2 800–1200 ELO User Testing Simulation & Calibration
```bash
uv run python scripts/run_user_testing_simulation.py --export-json calibration_report.json --export-md USER_TESTING_REPORT.md
```
- **Action Item Limit ($\le 3-4$ items):** $100\%$ Pass Rate
- **Root-Cause Prioritization:** $100\%$ Pass Rate
- **Cognitive Load Index:** $1.00 / 1.0$

### 6.3 Full Unit & Integration Test Suite
```bash
uv run pytest
```

---

## 7. Environment Variables Reference

| Variable | Default | Description |
| :--- | :--- | :--- |
| `PORT` | `8000` | HTTP listening port for backend API |
| `HOST` | `0.0.0.0` | Bind interface host |
| `WORKERS` | `4` | Number of Gunicorn Uvicorn worker processes |
| `LOG_LEVEL` | `info` | Logging verbosity (`debug`, `info`, `warning`, `error`) |
| `LLM_BASE_URL` | `http://127.0.0.1:8081/v1` | OpenAI-compatible endpoint URL (llama.cpp / Ollama / OpenAI) |
| `LLM_MODEL` | `qwen3.8-4b` | Model identifier string |
| `LLM_API_KEY` | `llama.cpp` | API authentication key for LLM endpoint |
| `LLM_TIMEOUT_SECONDS`| `4.0` | Timeout before instantaneous deterministic fallback |
| `NEXT_PUBLIC_API_URL`| `http://localhost:8000` | Frontend API gateway base URL |

---

## 8. Observability, Health Checks & Telemetry

### 8.1 Health & Readiness Probe
- **Endpoint:** `GET /api/health`
- **Response Format:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "onnx_loaded": true,
  "llm_connected": true,
  "civs_count": 45,
  "units_count": 25
}
```

### 8.2 Prometheus / Metrics Integration
To collect container runtime metrics, scrape standard container metrics via cAdvisor in Kubernetes or Google Cloud Monitoring metrics in Cloud Run.

---

## 9. Zero-Downtime Rollout Strategy

1. **Kubernetes Deployments**: Configured with `RollingUpdate` (`maxSurge: 1`, `maxUnavailable: 0`). New pods must pass both `startupProbe` and `readinessProbe` before old pods are terminated.
2. **Cloud Run**: Automatic traffic migration. New revisions only receive traffic after container initialization and health checks pass.
3. **Rollback Command**:
```bash
kubectl rollout undo deployment/aoe2-coach-backend -n aoe2-coach
```

"""
Unit & Integration Tests for Phase 6: Deployment Readiness & Configurations.
"""

import os
import json
import yaml
import pytest
from fastapi.testclient import TestClient

from aoe2_coach.api.app import app
from aoe2_coach.api.service import CoachAPIService


@pytest.fixture
def client():
    return TestClient(app)


def test_production_health_endpoint(client):
    """Verify production health check endpoint returns 200 with complete diagnostics."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"
    assert data["onnx_loaded"] is True
    assert data["civs_count"] >= 45
    assert data["units_count"] >= 20


def test_dockerfile_and_compose_manifests_exist():
    """Verify Dockerfiles and Docker Compose files are present and valid."""
    assert os.path.exists("Dockerfile")
    assert os.path.exists("docker-compose.yml")
    assert os.path.exists("docker-compose.prod.yml")
    assert os.path.exists("frontend/Dockerfile")
    assert os.path.exists("frontend/vercel.json")
    assert os.path.exists("frontend/wrangler.toml")

    # Verify vercel.json is valid JSON
    with open("frontend/vercel.json") as f:
        v_data = json.load(f)
        assert v_data["framework"] == "nextjs"
        assert len(v_data["rewrites"]) >= 1


def test_kubernetes_manifests_validity():
    """Verify all Kubernetes YAML manifests parse cleanly."""
    k8s_dir = "k8s"
    assert os.path.exists(k8s_dir)
    
    yaml_files = [
        "namespace.yaml",
        "configmap.yaml",
        "secrets.example.yaml",
        "backend-deployment.yaml",
        "backend-service.yaml",
        "frontend-deployment.yaml",
        "frontend-service.yaml",
        "ingress.yaml",
        "hpa.yaml",
        "kustomization.yaml",
    ]

    for yf in yaml_files:
        path = os.path.join(k8s_dir, yf)
        assert os.path.exists(path), f"Missing {path}"
        with open(path) as f:
            docs = list(yaml.safe_load_all(f))
            assert len(docs) >= 1, f"Failed to parse {path}"
            for doc in docs:
                assert "apiVersion" in doc or "kind" in doc or "resources" in doc


def test_cloudrun_manifests_validity():
    """Verify Cloud Run Knative manifests parse cleanly."""
    cr_backend = "deploy/cloudrun/service-backend.yaml"
    cr_frontend = "deploy/cloudrun/service-frontend.yaml"
    cr_script = "deploy/cloudrun/deploy.sh"

    assert os.path.exists(cr_backend)
    assert os.path.exists(cr_frontend)
    assert os.path.exists(cr_script)

    with open(cr_backend) as f:
        doc = yaml.safe_load(f)
        assert doc["kind"] == "Service"
        assert doc["metadata"]["name"] == "aoe2-coach-backend"

    with open(cr_frontend) as f:
        doc = yaml.safe_load(f)
        assert doc["kind"] == "Service"
        assert doc["metadata"]["name"] == "aoe2-coach-frontend"

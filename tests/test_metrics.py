"""confirms setup_metrics() actually produces working Prometheus
output on a real FastAPI app (not mocked - this either works or it doesn't)."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.services.metrics import setup_metrics


def test_metrics_endpoint_exposed_and_counts_requests():
    app = FastAPI()

    @app.get("/ping")
    def ping():
        return {"ok": True}

    setup_metrics(app)
    client = TestClient(app)

    client.get("/ping")
    resp = client.get("/metrics")

    assert resp.status_code == 200
    assert "http_requests_total" in resp.text


def test_metrics_endpoint_hidden_from_openapi_schema():
    app = FastAPI()
    setup_metrics(app)
    client = TestClient(app)

    schema = client.get("/openapi.json").json()

    assert "/metrics" not in schema["paths"]

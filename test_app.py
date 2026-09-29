from app import app 

def test_health():
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}

def test_metrics():
    client = app.test_client()
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert b"ledger_health_checks_total" in resp.data

def test_metrics_content_type():
    # Prometheus rejects scrapes without a valid exposition Content-Type
    client = app.test_client()
    resp = client.get("/metrics")
    assert resp.headers["Content-Type"].startswith("text/plain")

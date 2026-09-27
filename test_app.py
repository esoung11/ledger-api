from app import app 

def test_health():
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get__json() == {"status": "ok"}

def test_metrics():
    client = app.test_client()
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert b"ledger_health_checks_total" in resp.data
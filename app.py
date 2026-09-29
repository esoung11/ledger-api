from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

health_checks = Counter("ledger_health_checks_total", "Total /health requests")

@app.get("/health")
def health():
    health_checks.inc()
    return jsonify(status="ok")

@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
"""Flask demo for Sapphire Sentinel."""

from __future__ import annotations

import os

from flask import Flask, jsonify, make_response, render_template, request

from sapphire_sentinel.sentinel import (
    build_demo_state,
    build_judging_scorecard,
    default_attempt,
    evaluate_attempt,
    evaluate_from_payload,
)
from sapphire_sentinel.x402 import encode_payment_required

app = Flask(__name__, template_folder="../../templates")


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/demo")
def api_demo():
    return jsonify(build_demo_state())


@app.get("/api/health")
def api_health():
    return jsonify(
        {
            "ok": True,
            "service": "sapphire-sentinel",
            "mode": "testnet_paper_only",
            "live_settlement_enabled": False,
        }
    )


@app.get("/api/scenarios")
def api_scenarios():
    return jsonify(build_demo_state()["attack_scenarios"])


@app.get("/api/privacy")
def api_privacy():
    return jsonify(build_demo_state()["privacy_attestations"])


@app.get("/api/networks")
def api_networks():
    state = build_demo_state()
    return jsonify(
        {
            "networks": state["network_matrix"],
            "integration_roadmap": state["integration_roadmap"],
        }
    )


@app.get("/api/judging")
def api_judging():
    return jsonify(build_judging_scorecard())


@app.get("/api/x402/paywall")
def api_x402_paywall():
    decision = evaluate_attempt(default_attempt())
    payment_required = decision.http_402
    response = make_response(jsonify(payment_required), 402)
    response.headers["PAYMENT-REQUIRED"] = encode_payment_required(payment_required)
    response.headers["X-Sentinel-Mode"] = "simulation"
    response.headers["X-Sentinel-Receipt"] = decision.receipt_id
    return response


@app.post("/api/evaluate")
def api_evaluate():
    payload = request.get_json(silent=True) or {}
    return jsonify(
        {
            "execution_enabled": False,
            "mode": "policy_preview_only",
            "decision": evaluate_from_payload(payload),
        }
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8097"))
    app.run(host="127.0.0.1", port=port, debug=False)

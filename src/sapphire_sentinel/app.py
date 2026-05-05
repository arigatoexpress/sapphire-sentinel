"""Flask demo for Sapphire Sentinel."""

from __future__ import annotations

import os

from flask import Flask, jsonify, make_response, render_template, request

from sapphire_sentinel.megaeth_apps import build_megaeth_mainnet_agent_plan
from sapphire_sentinel.sentinel import (
    build_demo_state,
    build_judging_scorecard,
    default_attempt,
    evaluate_attempt,
    evaluate_from_payload,
)
from sapphire_sentinel.x402 import (
    build_402_response,
    encode_payment_required,
    verify_mock_payment_header,
)

import pathlib

app = Flask(__name__, template_folder=str(pathlib.Path(__file__).parent.parent.parent / "templates"))
_X402_NONCES: set[str] = set()


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


@app.get("/api/privacy/proofs")
def api_privacy_proofs():
    return jsonify(build_demo_state()["privacy_proofs"])


@app.get("/api/networks")
def api_networks():
    state = build_demo_state()
    return jsonify(
        {
            "networks": state["network_matrix"],
            "integration_roadmap": state["integration_roadmap"],
        }
    )


@app.get("/api/megaeth/apps")
def api_megaeth_apps():
    return jsonify(build_megaeth_mainnet_agent_plan())


@app.get("/api/judging")
def api_judging():
    return jsonify(build_judging_scorecard())


@app.get("/api/x402/paywall")
def api_x402_paywall():
    decision = evaluate_attempt(default_attempt())
    return _payment_required_response(decision)


@app.get("/api/x402/sentinel-report")
def api_x402_sentinel_report():
    decision = evaluate_attempt(default_attempt())
    payment_header = request.headers.get("PAYMENT-SIGNATURE") or request.headers.get("X-PAYMENT")
    if not payment_header:
        return _payment_required_response(decision, error="PAYMENT-SIGNATURE header is required")

    verification = verify_mock_payment_header(
        payment_header,
        decision.payment_requirements,
        nonce_cache=_X402_NONCES,
    )
    if not verification.valid:
        return _payment_required_response(decision, error=verification.error or "payment rejected")

    return jsonify(
        {
            "paid": True,
            "mode": "x402_mock_verified",
            "liveSettlementEnabled": False,
            "verification": verification.to_wire(),
            "report": {
                "title": "Sapphire Sentinel Private RWA Signal",
                "summary": default_attempt().result_summary,
                "resource": default_attempt().resource,
                "privacy_commitment": decision.privacy_commitment,
                "receipt_id": decision.receipt_id,
                "risk_hash": decision.risk_hash,
                "order_draft": decision.order_draft["primary_draft"],
            },
            "decision": decision.to_dict(),
        }
    )


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


def _payment_required_response(decision, *, error: str | None = None):
    payment_required = (
        build_402_response([decision.payment_requirements], error=error) if error else decision.http_402
    )
    response = make_response(jsonify(payment_required), 402)
    response.headers["PAYMENT-REQUIRED"] = encode_payment_required(payment_required)
    response.headers["X-Sentinel-Mode"] = "simulation"
    response.headers["X-Sentinel-Receipt"] = decision.receipt_id
    response.headers["X-Sentinel-Payment-Status"] = "required" if not error else "rejected"
    return response


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "sapphire-sentinel"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8097"))
    app.run(host="127.0.0.1", port=port, debug=False)

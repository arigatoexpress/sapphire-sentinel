from __future__ import annotations

from sapphire_sentinel.app import _X402_NONCES, app
from sapphire_sentinel.sentinel import default_attempt, evaluate_attempt
from sapphire_sentinel.x402 import build_mock_payment_payload, encode_payment_header


def test_demo_endpoint_returns_safe_state():
    client = app.test_client()

    response = client.get("/api/demo")

    assert response.status_code == 200
    body = response.get_json()
    assert body["project"]["name"] == "Sapphire Sentinel"
    assert body["approved_flow"]["approved"] is True
    assert body["blocked_flow"]["approved"] is False
    assert body["chain_config"]["chain_id"] == 46630
    assert body["safety"]["live_trading_enabled"] is False


def test_evaluate_endpoint_blocks_untrusted_domain():
    client = app.test_client()

    response = client.post(
        "/api/evaluate",
        json={
            "resource": "https://untrusted.example/api/alpha",
            "amount_usdc": "0.01",
            "action": "buy-private-signal",
        },
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["execution_enabled"] is False
    assert body["decision"]["approved"] is False
    assert "domain_not_allowed" in body["decision"]["risk_flags"]


def test_x402_paywall_returns_payment_required_header():
    client = app.test_client()

    response = client.get("/api/x402/paywall")

    assert response.status_code == 402
    assert response.headers["PAYMENT-REQUIRED"]
    assert response.headers["X-Sentinel-Mode"] == "simulation"
    body = response.get_json()
    assert body["x402Version"] == 2
    assert body["accepts"][0]["network"] == "eip155:84532"


def test_x402_protected_report_requires_payment_header():
    _X402_NONCES.clear()
    client = app.test_client()

    response = client.get("/api/x402/sentinel-report")

    assert response.status_code == 402
    assert response.headers["PAYMENT-REQUIRED"]
    assert response.headers["X-Sentinel-Payment-Status"] == "rejected"
    assert response.get_json()["error"] == "PAYMENT-SIGNATURE header is required"


def test_x402_protected_report_accepts_mock_payment_once():
    _X402_NONCES.clear()
    client = app.test_client()
    decision = evaluate_attempt(default_attempt())
    payload = build_mock_payment_payload(
        decision.payment_requirements,
        from_address="0xa6e1700000000000000000000000000000000402",
        nonce="0xTEST_NONCE_1",
    )
    header = encode_payment_header(payload)

    response = client.get("/api/x402/sentinel-report", headers={"PAYMENT-SIGNATURE": header})
    replay = client.get("/api/x402/sentinel-report", headers={"PAYMENT-SIGNATURE": header})

    assert response.status_code == 200
    body = response.get_json()
    assert body["paid"] is True
    assert body["mode"] == "x402_mock_verified"
    assert body["liveSettlementEnabled"] is False
    assert body["verification"]["network"] == "eip155:84532"
    assert body["report"]["receipt_id"] == decision.receipt_id
    assert replay.status_code == 402
    assert replay.get_json()["error"] == "nonce has already been used"


def test_supporting_endpoints_are_present():
    client = app.test_client()

    assert client.get("/api/health").status_code == 200
    assert len(client.get("/api/scenarios").get_json()) >= 5
    assert len(client.get("/api/privacy").get_json()) == 3
    assert len(client.get("/api/privacy/proofs").get_json()["artifacts"]) == 2
    assert len(client.get("/api/networks").get_json()["networks"]) >= 5
    assert client.get("/api/megaeth/apps").get_json()["network"]["chain_id"] == 4326
    assert len(client.get("/api/judging").get_json()) == 4
    assert len(client.get("/api/demo").get_json()["receipt_mirrors"]) >= 2

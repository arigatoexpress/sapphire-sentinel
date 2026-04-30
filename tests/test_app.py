from __future__ import annotations

from sapphire_sentinel.app import app


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


def test_supporting_endpoints_are_present():
    client = app.test_client()

    assert client.get("/api/health").status_code == 200
    assert len(client.get("/api/scenarios").get_json()) >= 5
    assert len(client.get("/api/privacy").get_json()) == 3
    assert len(client.get("/api/networks").get_json()["networks"]) >= 5
    assert len(client.get("/api/judging").get_json()) == 4

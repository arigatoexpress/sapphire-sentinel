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


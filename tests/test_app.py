from __future__ import annotations

from sapphire_sentinel.app import _X402_NONCES, app
from sapphire_sentinel.sentinel import default_attempt, evaluate_attempt
from sapphire_sentinel.x402 import build_mock_payment_payload, encode_payment_header


def _selector_id(selector: str) -> str | None:
    if not selector.startswith("#"):
        return None
    return selector[1:].split(" ", 1)[0].split(".", 1)[0]


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


def test_index_uses_static_workbench_assets():
    client = app.test_client()

    response = client.get("/")
    html = response.get_data(as_text=True)
    css = client.get("/static/styles.css")
    js = client.get("/static/app.js")

    assert response.status_code == 200
    assert '/static/styles.css' in html
    assert '/static/app.js' in html
    assert "<style>" not in html
    assert "function renderDecision" not in html
    assert "Settlement <strong>mock x402 only</strong>" in html
    assert css.status_code == 200
    assert ".safety-strip" in css.get_data(as_text=True)
    assert js.status_code == 200
    js_body = js.get_data(as_text=True)
    assert "async function evaluateResource" in js_body
    assert "fetch('/api/evaluate'" in js_body


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


def test_frontend_contract_is_browser_smoke_ready_and_non_mutating():
    client = app.test_client()

    response = client.get("/api/frontend-contract")

    assert response.status_code == 200
    body = response.get_json()
    assert body["schema"] == "sapphire_sentinel.frontend_contract.v1"
    assert body["route"] == "/"
    assert body["mode"] == "testnet_paper_only"
    assert body["settlement"] == "mock_x402_only"
    assert body["liveSettlementEnabled"] is False
    assert body["executionEnabled"] is False
    assert body["telegramSendsEnabled"] is False
    assert body["moneyMovementEnabled"] is False
    assert body["externalMutationDefault"] == "disabled"
    assert "live x402 facilitator settlement" in body["blockedCapabilities"]
    assert "real Robinhood order submission" in body["blockedCapabilities"]

    api_routes = {(route["method"], route["path"]): route for route in body["apiRoutes"]}
    assert api_routes[("GET", "/api/demo")]["expectedStatus"] == 200
    assert api_routes[("POST", "/api/evaluate")]["expectedStatus"] == 200
    assert api_routes[("GET", "/api/x402/paywall")]["expectedStatus"] == 402
    assert api_routes[("GET", "/api/x402/sentinel-report")]["expectedStatus"] == 402

    evaluate_action = next(
        action for action in body["primaryActions"] if action["id"] == "evaluate-resource"
    )
    assert evaluate_action["selector"] == "#eval-button"
    assert evaluate_action["path"] == "/api/evaluate"
    assert evaluate_action["expectedMode"] == "policy_preview_only"
    assert evaluate_action["externalEffects"] is False


def test_frontend_contract_selectors_match_static_shell():
    client = app.test_client()
    contract = client.get("/api/frontend-contract").get_json()
    html = client.get("/").get_data(as_text=True)
    js = client.get("/static/app.js").get_data(as_text=True)

    for expected_text in contract["requiredText"]:
        assert expected_text in html

    for selector in contract["requiredSelectors"]:
        element_id = _selector_id(selector)
        if element_id:
            assert f'id="{element_id}"' in html

    assert "document.getElementById('eval-button').addEventListener" in js
    assert "fetch('/api/evaluate'" in js
    assert "fetch('/api/demo')" in js


def test_frontend_contract_routes_read_back_expected_statuses():
    client = app.test_client()
    contract = client.get("/api/frontend-contract").get_json()

    for route in contract["apiRoutes"]:
        if route["method"] == "GET":
            response = client.get(route["path"])
        else:
            response = client.post(
                route["path"],
                json={
                    "resource": "https://signals.sapphire.local/api/private-rwa-signal",
                    "amount_usdc": "0.012",
                    "action": "buy-private-signal",
                },
            )
        assert response.status_code == route["expectedStatus"], route

    evaluate = client.post(
        "/api/evaluate",
        json={
            "resource": "https://signals.sapphire.local/api/private-rwa-signal",
            "amount_usdc": "0.012",
            "action": "buy-private-signal",
        },
    ).get_json()
    assert evaluate["execution_enabled"] is False
    assert evaluate["mode"] == "policy_preview_only"

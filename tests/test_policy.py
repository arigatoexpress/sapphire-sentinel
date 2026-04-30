from __future__ import annotations

from sapphire_sentinel.sentinel import (
    ROBINHOOD_CHAIN_ID,
    blocked_attempt,
    build_demo_state,
    default_attempt,
    default_mandate,
    evaluate_attempt,
    evaluate_from_payload,
)


def test_default_attempt_is_approved_and_testnet_only():
    decision = evaluate_attempt(default_attempt(), default_mandate())

    assert decision.approved is True
    assert decision.risk_flags == ()
    assert decision.chain_anchor["chain_id"] == ROBINHOOD_CHAIN_ID
    assert decision.chain_anchor["broadcast"] is False
    assert decision.payment_requirements.network == "eip155:84532"
    assert decision.privacy_commitment.startswith("0x")
    assert decision.decision_nonce > 0
    assert decision.http_402["x402Version"] == 2
    assert decision.order_draft["execution_enabled"] is False
    assert decision.order_draft["primary_draft"]["venue"] == "robinhood_chain_testnet_stock_token"


def test_blocked_attempt_flags_prompt_injection_and_domain():
    decision = evaluate_attempt(blocked_attempt(), default_mandate())

    assert decision.approved is False
    assert set(decision.risk_flags) >= {"domain_not_allowed", "prompt_injection"}
    assert decision.chain_anchor["approved"] is False


def test_evaluate_payload_blocks_spend_limit():
    decision = evaluate_from_payload(
        {
            "resource": default_attempt().resource,
            "amount_usdc": "99.0",
            "action": "buy-private-signal",
        }
    )

    assert decision["approved"] is False
    assert "spend_limit_exceeded" in decision["risk_flags"]


def test_demo_state_is_safe_by_default():
    state = build_demo_state()

    assert state["project"]["mode"] == "testnet_paper_only"
    assert state["approved_flow"]["approved"] is True
    assert state["blocked_flow"]["approved"] is False
    assert len(state["attack_scenarios"]) >= 5
    assert len(state["privacy_attestations"]) == 3
    assert len(state["judging_scorecard"]) == 4
    assert state["safety"]["live_trading_enabled"] is False
    assert state["safety"]["real_funds_enabled"] is False

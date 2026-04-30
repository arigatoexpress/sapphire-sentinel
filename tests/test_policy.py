from __future__ import annotations

from sapphire_sentinel.sentinel import (
    ROBINHOOD_CHAIN_ID,
    blocked_attempt,
    build_demo_state,
    default_attempt,
    default_mandate,
    evaluate_attempt,
    evaluate_from_payload,
    mandate_key,
)


def test_default_attempt_is_approved_and_testnet_only():
    decision = evaluate_attempt(default_attempt(), default_mandate())
    mandate = default_mandate()

    assert decision.approved is True
    assert decision.risk_flags == ()
    assert decision.chain_anchor["chain_id"] == ROBINHOOD_CHAIN_ID
    assert decision.chain_anchor["broadcast"] is True
    assert decision.chain_anchor["mode"] == "anchored_demo_receipt"
    assert decision.payment_requirements.network == "eip155:84532"
    assert len(mandate.controller) == 42
    assert len(mandate.agent) == 42
    assert int(mandate.controller, 16) > 0
    assert int(mandate.agent, 16) > 0
    assert decision.payment_requirements.extra["mandateKey"] == mandate_key(mandate)
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
    assert decision["chain_anchor"]["broadcast"] is False
    assert decision["chain_anchor"]["mode"] == "dry_run_anchor_preview"


def test_demo_state_is_safe_by_default():
    state = build_demo_state()

    assert state["project"]["mode"] == "testnet_paper_only"
    assert state["chain_config"]["deployment"]["address"].startswith("0x")
    assert state["chain_config"]["deployment"]["source_verified"] is True
    assert state["approved_flow"]["approved"] is True
    assert state["approved_flow"]["chain_anchor"]["mandate_key"] == state["mandate"]["mandate_key"]
    assert state["approved_flow"]["chain_anchor"]["record_call"]["args"][1].startswith("0x")
    assert state["approved_flow"]["chain_anchor"]["contract_address"].startswith("0x")
    assert state["approved_flow"]["chain_anchor"]["source_verified"] is True
    assert state["approved_flow"]["chain_anchor"]["onchain_recorded"] is True
    assert state["approved_flow"]["chain_anchor"]["record_tx_hash"].startswith("0x")
    assert state["approved_flow"]["chain_anchor"]["onchain_remaining_usdc"] == "1.618"
    assert state["blocked_flow"]["approved"] is False
    assert state["blocked_flow"]["chain_anchor"]["onchain_recorded"] is True
    assert len(state["attack_scenarios"]) >= 5
    assert len(state["privacy_attestations"]) == 3
    assert state["privacy_proofs"]["status"] == "local_artifact_ready"
    assert len(state["privacy_proofs"]["artifacts"]) == 2
    assert len(state["network_matrix"]) >= 5
    assert len(state["integration_roadmap"]) == 4
    assert state["megaeth_mainnet_agent"]["policy"]["can_send_transactions"] is False
    assert len(state["megaeth_mainnet_agent"]["apps"]) >= 8
    assert {item["id"] for item in state["receipt_mirrors"]} >= {
        "megaeth_testnet",
        "megaeth_mainnet",
    }
    assert next(item for item in state["receipt_mirrors"] if item["id"] == "megaeth_testnet")[
        "status"
    ] in {"mirror_seeded", "deployed_unverified", "ready_to_deploy"}
    assert len(state["judging_scorecard"]) == 4
    assert len(state["proof_points"]) >= 4
    assert any(item["label"] == "x402 protected report" for item in state["proof_points"])
    assert any(item["label"] == "Zama/Aztec proof bundle" for item in state["proof_points"])
    assert state["safety"]["live_trading_enabled"] is False
    assert state["safety"]["real_funds_enabled"] is False

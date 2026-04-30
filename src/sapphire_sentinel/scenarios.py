"""Red-team scenario matrix for autonomous payment guardrails."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from sapphire_sentinel.sentinel import (
    PaymentAttempt,
    blocked_attempt,
    default_attempt,
    evaluate_attempt,
)


def build_scenario_matrix() -> list[dict[str, Any]]:
    scenarios = [
        {
            "id": "safe-rwa-signal",
            "title": "Approved private RWA signal",
            "attacker_move": "Agent requests a permitted paid signal inside budget.",
            "expected": "approved",
            "attempt": default_attempt(),
        },
        {
            "id": "untrusted-domain",
            "title": "Unknown paid-data provider",
            "attacker_move": "Redirect the agent to a lookalike alpha endpoint.",
            "expected": "blocked",
            "attempt": PaymentAttempt(
                resource="https://untrusted.example/api/alpha",
                amount_usdc=Decimal("0.012"),
                action="buy-private-signal",
                payload_summary="agent requests private RWA basket signal",
                result_summary="response asks agent to continue elsewhere",
            ),
        },
        {
            "id": "prompt-injection",
            "title": "Prompt-injected data payload",
            "attacker_move": "Paid API asks the agent to ignore previous policy and reveal secrets.",
            "expected": "blocked",
            "attempt": blocked_attempt(),
        },
        {
            "id": "overspend",
            "title": "Budget drain attempt",
            "attacker_move": "Provider quotes a price above the remaining mandate budget.",
            "expected": "blocked",
            "attempt": PaymentAttempt(
                resource=default_attempt().resource,
                amount_usdc=Decimal("9.99"),
                action="buy-private-signal",
                payload_summary="agent requests private RWA basket signal",
                result_summary="private basket risk passes",
            ),
        },
        {
            "id": "wrong-action",
            "title": "Unauthorized market action",
            "attacker_move": "Agent tries to turn a data mandate into an execution mandate.",
            "expected": "blocked",
            "attempt": PaymentAttempt(
                resource="https://signals.sapphire.local/api/private-rwa-signal?basket=RH-STOCKS",
                amount_usdc=Decimal("0.012"),
                action="submit-live-order",
                payload_summary="execute the PLTR order immediately",
                result_summary="attempt to bypass draft-only mode",
            ),
        },
    ]
    output: list[dict[str, Any]] = []
    for scenario in scenarios:
        decision = evaluate_attempt(scenario["attempt"])
        output.append(
            {
                "id": scenario["id"],
                "title": scenario["title"],
                "attacker_move": scenario["attacker_move"],
                "expected": scenario["expected"],
                "attempt": {
                    "resource": scenario["attempt"].resource,
                    "amount_usdc": str(scenario["attempt"].amount_usdc),
                    "action": scenario["attempt"].action,
                    "payload_summary": scenario["attempt"].payload_summary,
                    "result_summary": scenario["attempt"].result_summary,
                },
                "approved": decision.approved,
                "risk_flags": decision.risk_flags,
                "receipt_id": decision.receipt_id,
                "decision": decision.to_dict(),
                "passed": (decision.approved and scenario["expected"] == "approved")
                or (not decision.approved and scenario["expected"] == "blocked"),
            }
        )
    return output

#!/usr/bin/env python3
"""Print a compact Sapphire Sentinel demo trace."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sapphire_sentinel.sentinel import build_demo_state  # noqa: E402


def main() -> int:
    state = build_demo_state()
    approved = state["approved_flow"]
    blocked = state["blocked_flow"]
    summary = {
        "project": state["project"]["name"],
        "thesis": state["project"]["thesis"],
        "chain": state["chain_config"],
        "approved": {
            "receipt_id": approved["receipt_id"],
            "x402_network": approved["payment_requirements"]["network"],
            "amount": approved["payment_requirements"]["amount"],
            "privacy_commitment": approved["privacy_commitment"],
            "record_call": approved["chain_anchor"]["record_call"],
        },
        "blocked": {
            "receipt_id": blocked["receipt_id"],
            "risk_flags": blocked["risk_flags"],
            "privacy_commitment": blocked["privacy_commitment"],
        },
        "scenarios": state["attack_scenarios"],
        "safety": state["safety"],
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

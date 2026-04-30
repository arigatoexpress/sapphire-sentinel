"""Small x402-compatible requirement model used by the Sentinel demo.

The default app stays in simulation mode. It models the v2 HTTP shape without
asking a wallet to sign or a facilitator to settle testnet USDC.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from typing import Any

DEFAULT_USDC_CONTRACTS = {
    "eip155:8453": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "eip155:84532": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
}

TESTNET_FACILITATOR = "https://x402.org/facilitator"


@dataclass(frozen=True)
class PaymentRequirements:
    """A single accepted payment option advertised in an HTTP 402 response."""

    scheme: str
    network: str
    amount: str
    resource: str
    description: str
    mime_type: str
    pay_to: str
    max_timeout_seconds: int
    asset: str
    extra: dict[str, Any] = field(default_factory=dict)

    def to_wire(self) -> dict[str, Any]:
        return {
            "scheme": self.scheme,
            "network": self.network,
            "amount": self.amount,
            "resource": self.resource,
            "description": self.description,
            "mimeType": self.mime_type,
            "payTo": self.pay_to,
            "maxTimeoutSeconds": self.max_timeout_seconds,
            "asset": self.asset,
            "extra": self.extra,
        }


def build_402_response(requirements: list[PaymentRequirements], *, error: str | None = None) -> dict[str, Any]:
    first = requirements[0] if requirements else None
    return {
        "x402Version": 2,
        "error": error or "PAYMENT-SIGNATURE header is required",
        "resource": (
            {
                "url": first.resource,
                "description": first.description,
                "mimeType": first.mime_type,
            }
            if first
            else {}
        ),
        "accepts": [requirement.to_wire() for requirement in requirements],
        "extensions": {
            "sentinel": {
                "mode": "simulation",
                "liveSettlementEnabled": False,
                "facilitator": TESTNET_FACILITATOR,
            }
        },
    }


def encode_payment_required(response: dict[str, Any]) -> str:
    raw = json.dumps(response, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(raw).decode("ascii")


def build_mock_payment_payload(requirement: PaymentRequirements, *, from_address: str) -> dict[str, Any]:
    """Return a non-signing payload preview for judge demos and tests."""

    return {
        "x402Version": 2,
        "resource": requirement.resource,
        "accepted": requirement.to_wire(),
        "payload": {
            "signature": "0xSIMULATED_SIGNATURE_DO_NOT_SETTLE",
            "authorization": {
                "from": from_address,
                "to": requirement.pay_to,
                "value": requirement.amount,
                "validAfter": 0,
                "validBefore": 0,
                "nonce": "0xSIMULATED_NONCE",
            },
        },
        "extensions": {
            "sentinel": {
                "liveSettlementEnabled": False,
                "mode": "policy_preview_only",
            }
        },
    }

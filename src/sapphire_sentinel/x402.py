"""Small x402-compatible requirement model used by the Sentinel demo."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

DEFAULT_USDC_CONTRACTS = {
    "base": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "base-sepolia": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
}


@dataclass(frozen=True)
class PaymentRequirements:
    """A single accepted payment option advertised in an HTTP 402 response."""

    scheme: str
    network: str
    max_amount_required: str
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
            "maxAmountRequired": self.max_amount_required,
            "resource": self.resource,
            "description": self.description,
            "mimeType": self.mime_type,
            "payTo": self.pay_to,
            "maxTimeoutSeconds": self.max_timeout_seconds,
            "asset": self.asset,
            "extra": self.extra,
        }


def build_402_response(requirements: list[PaymentRequirements]) -> dict[str, Any]:
    return {
        "x402Version": 1,
        "accepts": [requirement.to_wire() for requirement in requirements],
        "error": "X-PAYMENT header is required",
    }


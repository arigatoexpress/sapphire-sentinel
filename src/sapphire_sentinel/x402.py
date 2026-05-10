"""Small x402-compatible requirement model used by the Sentinel demo.

The default app stays in simulation mode. It models the v2 HTTP shape without
asking a wallet to sign or a facilitator to settle testnet USDC.
"""

from __future__ import annotations

import base64
import binascii
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


@dataclass(frozen=True)
class PaymentVerificationResult:
    """Result from the local non-settling x402 payment verifier."""

    valid: bool
    error: str | None
    payer: str | None = None
    pay_to: str | None = None
    amount: str | None = None
    nonce: str | None = None
    network: str | None = None
    asset: str | None = None
    resource: str | None = None
    signature_mode: str = "simulated"
    signature_verified: bool = False
    live_settlement_enabled: bool = False

    def to_wire(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "error": self.error,
            "payer": self.payer,
            "payTo": self.pay_to,
            "amount": self.amount,
            "nonce": self.nonce,
            "network": self.network,
            "asset": self.asset,
            "resource": self.resource,
            "signatureMode": self.signature_mode,
            "signatureVerified": self.signature_verified,
            "liveSettlementEnabled": self.live_settlement_enabled,
            "verifier": "sapphire_sentinel_mock_x402",
        }


def build_402_response(
    requirements: list[PaymentRequirements], *, error: str | None = None
) -> dict[str, Any]:
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


def encode_payment_header(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(raw).decode("ascii")


def build_mock_payment_payload(
    requirement: PaymentRequirements,
    *,
    from_address: str,
    nonce: str = "0xSIMULATED_NONCE",
) -> dict[str, Any]:
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
                "nonce": nonce,
            },
        },
        "extensions": {
            "sentinel": {
                "liveSettlementEnabled": False,
                "mode": "policy_preview_only",
            }
        },
    }


def build_eip3009_typed_data(
    requirement: PaymentRequirements,
    authorization: dict[str, Any],
) -> dict[str, Any]:
    """Build an EIP-712 envelope matching USDC-style transfer authorization."""

    return {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "TransferWithAuthorization": [
                {"name": "from", "type": "address"},
                {"name": "to", "type": "address"},
                {"name": "value", "type": "uint256"},
                {"name": "validAfter", "type": "uint256"},
                {"name": "validBefore", "type": "uint256"},
                {"name": "nonce", "type": "bytes32"},
            ],
        },
        "primaryType": "TransferWithAuthorization",
        "domain": {
            "name": "USD Coin",
            "version": "2",
            "chainId": _chain_id_from_caip2(requirement.network),
            "verifyingContract": requirement.asset,
        },
        "message": {
            "from": authorization["from"],
            "to": authorization["to"],
            "value": int(authorization["value"]),
            "validAfter": int(authorization.get("validAfter", 0)),
            "validBefore": int(authorization.get("validBefore", 0)),
            "nonce": authorization["nonce"],
        },
    }


def build_signed_payment_payload(
    requirement: PaymentRequirements,
    *,
    private_key: str,
    nonce: str,
    valid_after: int = 0,
    valid_before: int = 0,
) -> dict[str, Any]:
    """Return a locally wallet-signed, non-settling x402 payload."""

    try:
        from eth_account import Account  # type: ignore[import]
        from eth_account.messages import encode_typed_data  # type: ignore[import]
    except ImportError as exc:
        raise RuntimeError("eth-account is required to sign x402 payment payloads") from exc

    account = Account.from_key(private_key)
    authorization = {
        "from": account.address,
        "to": requirement.pay_to,
        "value": requirement.amount,
        "validAfter": valid_after,
        "validBefore": valid_before,
        "nonce": nonce,
    }
    typed_data = build_eip3009_typed_data(requirement, authorization)
    signable = encode_typed_data(full_message=typed_data)
    signed = Account.sign_message(signable, private_key)
    signature = signed.signature.hex()
    if not signature.startswith("0x"):
        signature = f"0x{signature}"

    payload = build_mock_payment_payload(requirement, from_address=account.address, nonce=nonce)
    payload["payload"]["signature"] = signature
    payload["payload"]["authorization"] = authorization
    payload["extensions"]["sentinel"]["mode"] = "wallet_signed_policy_preview"
    payload["extensions"]["sentinel"]["signatureMode"] = "eip712-eip3009"
    payload["extensions"]["sentinel"]["typedDataDomain"] = typed_data["domain"]
    return payload


def verify_mock_payment_header(
    header_value: str,
    requirement: PaymentRequirements,
    *,
    nonce_cache: set[str] | None = None,
) -> PaymentVerificationResult:
    """Verify a non-settling x402-style header against the advertised quote.

    This intentionally does not validate a real EIP-3009 signature or call an
    x402 facilitator. It is the fail-closed local verifier for the hackathon
    demo: Base Sepolia quote binding, payer presence, amount/payee matching,
    and replay protection.
    """

    payload, decode_error = _decode_payment_header(header_value)
    if decode_error:
        return PaymentVerificationResult(valid=False, error=decode_error)

    accepted = _dict_at(payload, "accepted")
    payment_payload = _dict_at(payload, "payload")
    authorization = _dict_at(payment_payload, "authorization") or _dict_at(payload, "authorization")
    if not authorization:
        return PaymentVerificationResult(valid=False, error="missing payment authorization")

    version = payload.get("x402Version")
    if version is not None:
        try:
            normalized_version = int(version)
        except (TypeError, ValueError):
            return PaymentVerificationResult(valid=False, error="unsupported x402 version")
        if normalized_version != 2:
            return PaymentVerificationResult(valid=False, error="unsupported x402 version")

    resource = str(payload.get("resource") or accepted.get("resource") or "")
    network = str(accepted.get("network") or payload.get("network") or "")
    asset = str(accepted.get("asset") or payload.get("asset") or "")
    amount = str(
        authorization.get("value") or accepted.get("amount") or payload.get("amount") or ""
    )
    payer = str(authorization.get("from") or "")
    pay_to = str(
        authorization.get("to") or authorization.get("payTo") or accepted.get("payTo") or ""
    )
    nonce = str(authorization.get("nonce") or "")
    signature = str(payment_payload.get("signature") or payload.get("signature") or "")
    sentinel_extensions = _dict_at(_dict_at(payload, "extensions"), "sentinel")
    signature_mode = str(sentinel_extensions.get("signatureMode") or "simulated")

    if not _nonempty_hexish(signature):
        return PaymentVerificationResult(valid=False, error="missing simulated payment signature")
    if not _same_text(resource, requirement.resource):
        return PaymentVerificationResult(
            valid=False, error="resource does not match payment requirement"
        )
    if network and not _same_text(network, requirement.network):
        return PaymentVerificationResult(
            valid=False, error="network does not match payment requirement"
        )
    if asset and not _same_address(asset, requirement.asset):
        return PaymentVerificationResult(
            valid=False, error="asset does not match payment requirement"
        )
    if not _same_text(amount, requirement.amount):
        return PaymentVerificationResult(
            valid=False, error="amount does not match payment requirement"
        )
    if not _same_address(pay_to, requirement.pay_to):
        return PaymentVerificationResult(
            valid=False, error="payTo does not match payment requirement"
        )
    if not _nonempty_hexish(payer):
        return PaymentVerificationResult(valid=False, error="payer is required")
    if not _nonempty_hexish(nonce):
        return PaymentVerificationResult(valid=False, error="nonce is required")
    if nonce_cache is not None and nonce in nonce_cache:
        return PaymentVerificationResult(valid=False, error="nonce has already been used")

    signature_verified = False
    if signature_mode == "eip712-eip3009":
        recovered, signature_error = _recover_eip712_payer(requirement, authorization, signature)
        if signature_error:
            return PaymentVerificationResult(valid=False, error=signature_error)
        if not _same_address(recovered, payer):
            return PaymentVerificationResult(valid=False, error="signature does not match payer")
        signature_verified = True
    elif signature_mode != "simulated":
        return PaymentVerificationResult(valid=False, error="unsupported signature mode")

    if nonce_cache is not None:
        nonce_cache.add(nonce)
    return PaymentVerificationResult(
        valid=True,
        error=None,
        payer=payer,
        pay_to=pay_to,
        amount=amount,
        nonce=nonce,
        network=network or requirement.network,
        asset=asset or requirement.asset,
        resource=resource,
        signature_mode=signature_mode,
        signature_verified=signature_verified,
        live_settlement_enabled=False,
    )


def _decode_payment_header(header_value: str) -> tuple[dict[str, Any], str | None]:
    cleaned = header_value.strip()
    if cleaned.lower().startswith("bearer "):
        cleaned = cleaned[7:].strip()
    padding = "=" * (-len(cleaned) % 4)
    try:
        raw = base64.b64decode(cleaned + padding, validate=True)
        decoded = json.loads(raw.decode("utf-8"))
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError):
        return {}, "payment header is not valid base64 JSON"
    if not isinstance(decoded, dict):
        return {}, "payment header must decode to a JSON object"
    return decoded, None


def _dict_at(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    return value if isinstance(value, dict) else {}


def _same_text(left: str, right: str) -> bool:
    return left.strip() == right.strip()


def _same_address(left: str, right: str) -> bool:
    return left.strip().lower() == right.strip().lower()


def _nonempty_hexish(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("0x") and len(value) > 2


def _chain_id_from_caip2(network: str) -> int:
    prefix, _, chain_id = network.partition(":")
    if prefix != "eip155" or not chain_id:
        raise ValueError(f"unsupported x402 network: {network}")
    return int(chain_id)


def _recover_eip712_payer(
    requirement: PaymentRequirements,
    authorization: dict[str, Any],
    signature: str,
) -> tuple[str, str | None]:
    try:
        from eth_account import Account  # type: ignore[import]
        from eth_account.messages import encode_typed_data  # type: ignore[import]
    except ImportError:
        return "", "eth-account is required for EIP-712 verification"

    try:
        typed_data = build_eip3009_typed_data(requirement, authorization)
        signable = encode_typed_data(full_message=typed_data)
        return Account.recover_message(signable, signature=signature), None
    except Exception:
        return "", "invalid EIP-712 payment signature"

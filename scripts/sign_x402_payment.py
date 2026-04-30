#!/usr/bin/env python3
"""Create a wallet-signed, non-settling x402 payment header."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sapphire_sentinel.sentinel import default_attempt, evaluate_attempt  # noqa: E402
from sapphire_sentinel.x402 import (  # noqa: E402
    build_signed_payment_payload,
    encode_payment_header,
    verify_mock_payment_header,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--key-env",
        default="SENTINEL_X402_SIGNING_KEY",
        help="Environment variable containing the signing private key.",
    )
    parser.add_argument("--key-file", type=Path, help="Path containing the signing private key.")
    parser.add_argument(
        "--header-only",
        action="store_true",
        help="Print only the base64 PAYMENT-SIGNATURE value.",
    )
    parser.add_argument("--curl", action="store_true", help="Print a curl command for the report.")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8098",
        help="Local demo base URL for --curl output.",
    )
    args = parser.parse_args()

    private_key, key_source = _load_private_key(args.key_env, args.key_file)
    decision = evaluate_attempt(default_attempt())
    nonce = f"0x{secrets.token_hex(32)}"
    payload = build_signed_payment_payload(
        decision.payment_requirements,
        private_key=private_key,
        nonce=nonce,
    )
    header = encode_payment_header(payload)
    verification = verify_mock_payment_header(
        header,
        decision.payment_requirements,
        nonce_cache=set(),
    )
    if not verification.valid:
        print(f"signature self-check failed: {verification.error}", file=sys.stderr)
        return 1

    if args.header_only:
        print(header)
        return 0
    if args.curl:
        print(
            "curl "
            f"-H 'PAYMENT-SIGNATURE: {header}' "
            f"{args.base_url.rstrip('/')}/api/x402/sentinel-report"
        )
        return 0

    print(
        json.dumps(
            {
                "header": header,
                "payer": verification.payer,
                "nonce": verification.nonce,
                "signatureMode": verification.signature_mode,
                "signatureVerified": verification.signature_verified,
                "liveSettlementEnabled": False,
                "keySource": key_source,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _load_private_key(key_env: str, key_file: Path | None) -> tuple[str, str]:
    if key_file:
        key = key_file.read_text(encoding="utf-8").strip()
        if key:
            return key, str(key_file)
    key = os.environ.get(key_env, "").strip()
    if key:
        return key, f"env:{key_env}"

    try:
        from eth_account import Account  # type: ignore[import]
    except ImportError:
        print("eth-account is required. Install with: pip install -e '.[deploy]'", file=sys.stderr)
        raise SystemExit(1) from None

    account = Account.create()
    return account.key.hex(), "ephemeral"


if __name__ == "__main__":
    raise SystemExit(main())

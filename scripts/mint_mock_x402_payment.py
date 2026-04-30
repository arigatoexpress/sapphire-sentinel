#!/usr/bin/env python3
"""Mint a non-settling x402 payment header for the Sentinel demo."""

from __future__ import annotations

import argparse
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sapphire_sentinel.sentinel import default_attempt, evaluate_attempt  # noqa: E402
from sapphire_sentinel.x402 import build_mock_payment_payload, encode_payment_header  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--from-address",
        default="0xa6e1700000000000000000000000000000000402",
        help="Mock payer address to place in the x402 authorization.",
    )
    parser.add_argument("--nonce", default=None, help="Optional mock payment nonce.")
    parser.add_argument(
        "--header-only",
        action="store_true",
        help="Print only the base64 PAYMENT-SIGNATURE value.",
    )
    parser.add_argument(
        "--curl",
        action="store_true",
        help="Print a curl command for the protected report endpoint.",
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8098",
        help="Local demo base URL for --curl output.",
    )
    args = parser.parse_args()

    decision = evaluate_attempt(default_attempt())
    nonce = args.nonce or f"0x{secrets.token_hex(16)}"
    payload = build_mock_payment_payload(
        decision.payment_requirements,
        from_address=args.from_address,
        nonce=nonce,
    )
    header = encode_payment_header(payload)

    if args.header_only:
        print(header)
        return

    if args.curl:
        print(
            "curl "
            f"-H 'PAYMENT-SIGNATURE: {header}' "
            f"{args.base_url.rstrip('/')}/api/x402/sentinel-report"
        )
        return

    print(f"PAYMENT-SIGNATURE={header}")
    print(f"nonce={nonce}")
    print("liveSettlementEnabled=false")


if __name__ == "__main__":
    main()

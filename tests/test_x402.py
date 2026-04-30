from __future__ import annotations

import pytest

from sapphire_sentinel.sentinel import default_attempt, evaluate_attempt
from sapphire_sentinel.x402 import (
    build_eip3009_typed_data,
    build_mock_payment_payload,
    build_signed_payment_payload,
    encode_payment_header,
    verify_mock_payment_header,
)


def test_mock_x402_verifier_binds_quote_and_nonce():
    decision = evaluate_attempt(default_attempt())
    payload = build_mock_payment_payload(
        decision.payment_requirements,
        from_address="0xa6e1700000000000000000000000000000000402",
        nonce="0xUNIT_TEST_NONCE",
    )
    nonce_cache: set[str] = set()

    first = verify_mock_payment_header(
        encode_payment_header(payload),
        decision.payment_requirements,
        nonce_cache=nonce_cache,
    )
    second = verify_mock_payment_header(
        encode_payment_header(payload),
        decision.payment_requirements,
        nonce_cache=nonce_cache,
    )

    assert first.valid is True
    assert first.live_settlement_enabled is False
    assert first.pay_to == decision.payment_requirements.pay_to
    assert second.valid is False
    assert second.error == "nonce has already been used"


def test_mock_x402_verifier_rejects_tampered_amount():
    decision = evaluate_attempt(default_attempt())
    payload = build_mock_payment_payload(
        decision.payment_requirements,
        from_address="0xa6e1700000000000000000000000000000000402",
        nonce="0xUNIT_TEST_NONCE_2",
    )
    payload["payload"]["authorization"]["value"] = "1"

    result = verify_mock_payment_header(
        encode_payment_header(payload),
        decision.payment_requirements,
        nonce_cache=set(),
    )

    assert result.valid is False
    assert result.error == "amount does not match payment requirement"


def test_mock_x402_verifier_rejects_invalid_header():
    decision = evaluate_attempt(default_attempt())

    result = verify_mock_payment_header("not-json", decision.payment_requirements)

    assert result.valid is False
    assert result.error == "payment header is not valid base64 JSON"


def test_signed_x402_header_recovers_payer():
    pytest.importorskip("eth_account")
    from eth_account import Account

    decision = evaluate_attempt(default_attempt())
    account = Account.create()
    payload = build_signed_payment_payload(
        decision.payment_requirements,
        private_key=account.key.hex(),
        nonce="0x" + "ab" * 32,
    )

    result = verify_mock_payment_header(
        encode_payment_header(payload),
        decision.payment_requirements,
        nonce_cache=set(),
    )

    assert result.valid is True
    assert result.signature_mode == "eip712-eip3009"
    assert result.signature_verified is True
    assert result.payer == account.address


def test_signed_x402_header_rejects_tampered_payer():
    pytest.importorskip("eth_account")
    from eth_account import Account

    decision = evaluate_attempt(default_attempt())
    payload = build_signed_payment_payload(
        decision.payment_requirements,
        private_key=Account.create().key.hex(),
        nonce="0x" + "cd" * 32,
    )
    payload["payload"]["authorization"]["from"] = "0xa6e1700000000000000000000000000000000402"

    result = verify_mock_payment_header(
        encode_payment_header(payload),
        decision.payment_requirements,
        nonce_cache=set(),
    )

    assert result.valid is False
    assert result.error == "signature does not match payer"


def test_x402_typed_data_uses_base_sepolia_usdc_domain():
    decision = evaluate_attempt(default_attempt())
    authorization = {
        "from": "0xa6e1700000000000000000000000000000000402",
        "to": decision.payment_requirements.pay_to,
        "value": decision.payment_requirements.amount,
        "validAfter": 0,
        "validBefore": 0,
        "nonce": "0x" + "ef" * 32,
    }

    typed_data = build_eip3009_typed_data(decision.payment_requirements, authorization)

    assert typed_data["domain"]["chainId"] == 84532
    assert typed_data["domain"]["verifyingContract"] == decision.payment_requirements.asset
    assert typed_data["message"]["value"] == 12_000

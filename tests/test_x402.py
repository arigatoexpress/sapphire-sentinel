from __future__ import annotations

from sapphire_sentinel.sentinel import default_attempt, evaluate_attempt
from sapphire_sentinel.x402 import (
    build_mock_payment_payload,
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

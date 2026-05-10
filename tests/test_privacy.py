from __future__ import annotations

from sapphire_sentinel.privacy import build_privacy_attestations, primary_privacy_commitment


def test_privacy_attestations_are_honest_sidecars():
    attestations = build_privacy_attestations(
        policy_hash="0x" + "11" * 32,
        result_hash="0x" + "22" * 32,
        risk_hash="0x" + "33" * 32,
        resource_hash="0x" + "44" * 32,
    )

    assert [item.engine for item in attestations] == ["Oasis Sapphire", "Zama fhEVM", "Aztec"]
    assert all(item.commitment.startswith("0x") for item in attestations)
    assert "not claimed as native Robinhood Chain FHE" in attestations[1].status
    assert any("not EVM-compatible" in constraint for constraint in attestations[2].constraints)


def test_primary_privacy_commitment_matches_oasis_attestation():
    payload = {
        "policy_hash": "0x" + "aa" * 32,
        "result_hash": "0x" + "bb" * 32,
        "risk_hash": "0x" + "cc" * 32,
        "resource_hash": "0x" + "dd" * 32,
    }

    assert (
        primary_privacy_commitment(**payload) == build_privacy_attestations(**payload)[0].commitment
    )

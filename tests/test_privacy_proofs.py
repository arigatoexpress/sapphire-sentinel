from __future__ import annotations

from sapphire_sentinel.privacy_proofs import build_privacy_proof_bundle


def test_privacy_proof_bundle_exports_public_commitments_only():
    bundle = build_privacy_proof_bundle(
        policy_hash="0x" + "11" * 32,
        resource_hash="0x" + "22" * 32,
        result_hash="0x" + "33" * 32,
        risk_hash="0x" + "44" * 32,
        privacy_commitment="0x" + "55" * 32,
        amount_atomic=12_000,
        approved=True,
    )
    data = bundle.to_dict()

    assert data["status"] == "local_artifact_ready"
    assert data["live_proving_enabled"] is False
    assert [artifact["engine"] for artifact in data["artifacts"]] == ["Zama fhEVM", "Aztec"]
    assert all(artifact["exported_commitment"].startswith("0x") for artifact in data["artifacts"])
    assert all(
        "private_balance_atomic" not in artifact["public_inputs"] for artifact in data["artifacts"]
    )
    assert data["artifacts"][0]["receipt_binding"]["risk_hash"] == "0x" + "44" * 32
    assert data["artifacts"][1]["artifact_path"].endswith("aztec_private_intent_note.nr")


def test_privacy_proof_bundle_is_deterministic():
    kwargs = {
        "policy_hash": "0x" + "aa" * 32,
        "resource_hash": "0x" + "bb" * 32,
        "result_hash": "0x" + "cc" * 32,
        "risk_hash": "0x" + "dd" * 32,
        "privacy_commitment": "0x" + "ee" * 32,
        "amount_atomic": 12_000,
        "approved": True,
    }

    first = build_privacy_proof_bundle(**kwargs).to_dict()
    second = build_privacy_proof_bundle(**kwargs).to_dict()

    assert first == second

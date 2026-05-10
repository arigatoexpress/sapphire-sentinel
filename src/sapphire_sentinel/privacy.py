"""Privacy-sidecar artifacts for the Sapphire Sentinel demo.

These adapters are deliberately honest: Robinhood Chain remains a public EVM
testnet. The privacy layers produce commitments and implementation blueprints
for hidden policy inputs, not private Robinhood stock-token transfers.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class PrivacyAttestation:
    engine: str
    role: str
    public_claim: str
    private_inputs: tuple[str, ...]
    public_outputs: tuple[str, ...]
    commitment: str
    status: str
    implementation_path: str
    constraints: tuple[str, ...]
    source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_privacy_attestations(
    *,
    policy_hash: str,
    result_hash: str,
    risk_hash: str,
    resource_hash: str,
) -> list[PrivacyAttestation]:
    oasis_commitment = _commit(
        "oasis-sapphire",
        {
            "policy_hash": policy_hash,
            "result_hash": result_hash,
            "risk_hash": risk_hash,
        },
    )
    zama_commitment = _commit(
        "zama-fhevm",
        {
            "policy_hash": policy_hash,
            "risk_hash": risk_hash,
            "resource_hash": resource_hash,
        },
    )
    aztec_commitment = _commit(
        "aztec-private-intent",
        {
            "policy_hash": policy_hash,
            "resource_hash": resource_hash,
            "result_hash": result_hash,
        },
    )
    return [
        PrivacyAttestation(
            engine="Oasis Sapphire",
            role="confidential policy sidecar",
            public_claim="private agent-risk inputs passed policy and produced an allow/deny commitment",
            private_inputs=("risk thresholds", "provider scoring rules", "agent prompt transcript"),
            public_outputs=("policy_hash", "result_hash", "risk_hash", "privacy_commitment"),
            commitment=oasis_commitment,
            status="demo-ready signed-attestation preview",
            implementation_path="ConfidentialPolicy.sol sidecar or OPL bridge after testnet deploy",
            constraints=(
                "Robinhood Chain receipt remains public",
                "cross-chain messaging is a follow-up; this demo uses signed commitments",
            ),
            source="https://docs.oasis.io/build/sapphire/",
        ),
        PrivacyAttestation(
            engine="Zama fhEVM",
            role="encrypted spend-limit and risk-score prototype",
            public_claim="encrypted policy math can prove a budget/risk pass without revealing raw values",
            private_inputs=("exact spend history", "risk score", "concentration thresholds"),
            public_outputs=("risk_hash", "privacy_commitment"),
            commitment=zama_commitment,
            status="companion artifact; not claimed as native Robinhood Chain FHE",
            implementation_path="contracts/privacy/EncryptedRiskGateMock.sol, then Zama FHEVM Sepolia port",
            constraints=(
                "requires Zama protocol host/gateway/coprocessor support",
                "do not claim private Robinhood Chain payments",
            ),
            source="https://docs.zama.org/protocol/solidity-guides",
        ),
        PrivacyAttestation(
            engine="Aztec",
            role="private intent evidence",
            public_claim="a user can keep balance or intent details private while exporting a commitment",
            private_inputs=(
                "private balance note",
                "private purchase intent",
                "user identity link",
            ),
            public_outputs=("resource_hash", "result_hash", "privacy_commitment"),
            commitment=aztec_commitment,
            status="local/private-intent blueprint",
            implementation_path="artifacts/privacy/aztec_private_intent_note.nr",
            constraints=(
                "Aztec is not EVM-compatible",
                "Ethereum/Aztec messaging is asynchronous and explicit",
            ),
            source="https://docs.aztec.network/",
        ),
    ]


def primary_privacy_commitment(
    *,
    policy_hash: str,
    result_hash: str,
    risk_hash: str,
    resource_hash: str,
) -> str:
    return build_privacy_attestations(
        policy_hash=policy_hash,
        result_hash=result_hash,
        risk_hash=risk_hash,
        resource_hash=resource_hash,
    )[0].commitment


def _commit(engine: str, payload: dict[str, Any]) -> str:
    raw = json.dumps(
        {"engine": engine, "payload": payload},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "0x" + hashlib.sha256(raw).hexdigest()

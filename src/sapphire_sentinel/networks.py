"""Cross-chain integration registry for Sapphire Sentinel.

The registry is intentionally explicit about what is live, what is testnet-only,
and what is a privacy-sidecar artifact. It keeps the dashboard and docs from
drifting into over-claiming while still showing judges the expansion path.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class NetworkProfile:
    id: str
    name: str
    role: str
    chain_id: int | None
    caip2: str | None
    rpc: str | None
    explorer: str | None
    status: str
    next_action: str
    claim_boundary: str
    source: str
    deploy_enabled: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class IntegrationPhase:
    label: str
    status: str
    proof: str
    implementation: str
    boundary: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


NETWORKS: tuple[NetworkProfile, ...] = (
    NetworkProfile(
        id="robinhood_testnet",
        name="Robinhood Chain Testnet",
        role="RWA audit anchor",
        chain_id=46630,
        caip2="eip155:46630",
        rpc="https://rpc.testnet.chain.robinhood.com",
        explorer="https://explorer.testnet.chain.robinhood.com",
        status="live_deployed",
        next_action="Keep source-verified receipt registry as the judging anchor.",
        claim_boundary="Public testnet receipts only; no real Robinhood account or live order flow.",
        source="https://docs.robinhood.com/chain/",
        deploy_enabled=True,
    ),
    NetworkProfile(
        id="base_sepolia",
        name="Base Sepolia",
        role="x402 settlement rail",
        chain_id=84532,
        caip2="eip155:84532",
        rpc="https://sepolia.base.org",
        explorer="https://sepolia.basescan.org",
        status="mock_x402_gate_live",
        next_action="Replace the local mock header with wallet-signed Base Sepolia USDC and facilitator verification.",
        claim_boundary="Local verifier only today; no facilitator settlement or production CDP call by default.",
        source="https://docs.x402.org/core-concepts/network-and-token-support",
        deploy_enabled=True,
    ),
    NetworkProfile(
        id="megaeth_testnet",
        name="MegaETH Testnet",
        role="low-latency receipt mirror",
        chain_id=6343,
        caip2="eip155:6343",
        rpc="https://carrot.megaeth.com/rpc",
        explorer="https://megaeth-testnet-v2.blockscout.com",
        status="mirror_seeded",
        next_action="Verify source on MegaETH testnet Blockscout and keep mirror receipts aligned.",
        claim_boundary="Experimental testnet; RPCs are rate-limited and state may be reset.",
        source="https://docs.megaeth.com/testnet",
        deploy_enabled=True,
    ),
    NetworkProfile(
        id="megaeth_mainnet",
        name="MegaETH Mainnet",
        role="live TGE/mainnet context",
        chain_id=4326,
        caip2="eip155:4326",
        rpc="https://mainnet.megaeth.com/rpc",
        explorer="https://mega.etherscan.io",
        status="mainnet_live_read_only",
        next_action=(
            "Keep Sentinel read, quote, and simulate-only on MegaETH mainnet; "
            "use it for TGE-aware app monitoring without default transactions."
        ),
        claim_boundary="Mainnet is live; Sentinel must not deploy or transact there by default.",
        source="https://docs.megaeth.com/frontier",
        deploy_enabled=False,
        metadata={
            "MEGA": "0x28B7E77f82B25B95953825F1E3eA0E36c1c29861",
            "WETH9": "0x4200000000000000000000000000000000000006",
            "USDM": "0xFAfDdbb3FC7688494971a79cc65DCa3EF82079E7",
            "ethereum_l1_standard_bridge": "0x0CA3A2FBC3D770b578223FBB6b062fa875a2eE75",
        },
    ),
    NetworkProfile(
        id="zama_sepolia",
        name="Zama Protocol on Sepolia",
        role="encrypted budget and risk gate",
        chain_id=11155111,
        caip2="eip155:11155111",
        rpc=None,
        explorer="https://sepolia.etherscan.io",
        status="local_proof_bundle_live",
        next_action="Port EncryptedRiskGateMock to Zama encrypted integer types and deploy on Sepolia.",
        claim_boundary="Zama is not a separate chain here; real FHEVM validation is Sepolia-based today.",
        source="https://docs.zama.org/protocol/solidity-guides/development-guide/hardhat/run_test",
    ),
    NetworkProfile(
        id="aztec_private_intent",
        name="Aztec Private Intent",
        role="private mandate evidence",
        chain_id=None,
        caip2=None,
        rpc=None,
        explorer=None,
        status="local_proof_bundle_live",
        next_action="Run the Noir private-intent circuit once the Aztec toolchain is installed.",
        claim_boundary="Aztec is not EVM-compatible; treat it as private proof evidence, not an EVM deploy.",
        source="https://docs.aztec.network/",
    ),
)


INTEGRATION_PHASES: tuple[IntegrationPhase, ...] = (
    IntegrationPhase(
        label="1. Receipt Mesh",
        status="shipping",
        proof="Robinhood Chain and MegaETH testnet registries are deployed and seeded with approved/blocked receipts.",
        implementation="Keep Robinhood as source-verified primary anchor and MegaETH as low-latency mirror.",
        boundary="Testnet receipts are public commitments; MegaETH mainnet remains read-only by default.",
    ),
    IntegrationPhase(
        label="2. Base x402 Rail",
        status="local_shipped",
        proof="Protected report endpoint verifies a mock PAYMENT-SIGNATURE, quote binding, and nonce replay.",
        implementation="Upgrade mock headers to wallet-signed Base Sepolia x402 payloads behind an env-gated facilitator verifier.",
        boundary="Default dashboard remains non-settling until a testnet wallet signs an x402 payload.",
    ),
    IntegrationPhase(
        label="3. Zama Risk Gate",
        status="local_shipped",
        proof="Local proof bundle exports an encrypted-input commitment and receipt-bound risk commitment.",
        implementation="Port EncryptedRiskGateMock to Zama encrypted integer types for Sepolia validation.",
        boundary="Do not claim native Robinhood Chain FHE; the real encrypted run is Zama-on-Sepolia.",
    ),
    IntegrationPhase(
        label="4. Aztec Intent Proof",
        status="local_shipped",
        proof="Local proof bundle exports a private-intent commitment tied to policy, resource, and result hashes.",
        implementation="Run the Noir scaffold with the Aztec toolchain and persist proof-output JSON.",
        boundary="Private proof generation is explicit and asynchronous; no EVM drop-in claim.",
    ),
)


def build_network_matrix() -> list[dict[str, Any]]:
    return [network.to_dict() for network in NETWORKS]


def build_integration_roadmap() -> list[dict[str, str]]:
    return [phase.to_dict() for phase in INTEGRATION_PHASES]


def network_by_id(network_id: str) -> NetworkProfile:
    for network in NETWORKS:
        if network.id == network_id:
            return network
    raise KeyError(f"unknown network: {network_id}")

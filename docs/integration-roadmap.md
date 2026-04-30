# Cross-Chain Privacy Integration Roadmap

Current as of April 30, 2026.

## Thesis

Sapphire Sentinel should become the agent-control plane that binds four things
before an autonomous agent can spend or act:

1. A payment rail.
2. A public receipt rail.
3. A private policy or risk proof.
4. A fail-closed cybersecurity decision.

The winning demo keeps Robinhood Chain as the RWA audit anchor, then shows that
the same receipt can be extended across Base, MegaETH, Zama, and Aztec without
pretending those systems do the same job.

## Ship Now

| Rail | Ship status | What it proves |
|---|---|---|
| Robinhood Chain testnet | Live | Source-verified non-custodial registry with approved and blocked agent receipts |
| Base Sepolia x402 | Local gate shipped | HTTP 402 payment requirement plus mock `PAYMENT-SIGNATURE` verification, quote binding, and replay rejection |
| MegaETH testnet | Mirror seeded | Low-latency public receipt mirror with mandate, approved receipt, and blocked receipt |
| MegaETH mainnet | Read-only live context | TGE-aware network profile with MEGA/USDM/bridge metadata and no default deployment path |
| Zama on Sepolia | Local proof bundle shipped | Encrypted budget/risk thresholding has a mock contract plus receipt-bound local commitment |
| Aztec | Local proof bundle shipped | Private mandate or intent evidence has a Noir blueprint plus exported local commitment |

## Correct Claims

Say:

> Sentinel coordinates agentic payments, private policy sidecars, and public
> audit receipts across purpose-built chains.

Do not say:

> Robinhood Chain payments are private.

Do not say:

> Zama or Aztec are native Robinhood Chain privacy layers.

Do not say:

> MegaETH or Base x402 are live production settlement paths in the default demo.

## Implementation Lanes

### 1. Base x402 Rail

The current demo emits an x402-compatible `402 Payment Required` response with
Base Sepolia CAIP-2 `eip155:84532` and Base Sepolia USDC
`0x036CbD53842c5426634e7929541eC2318f3dCF7e`. It also ships a protected
resource at `/api/x402/sentinel-report` that accepts a mock or wallet-signed
`PAYMENT-SIGNATURE`, verifies quote binding, recovers EIP-712 payers when
present, rejects amount/payee tampering, and blocks nonce replay.

Demo commands:

```bash
HEADER=$(PYTHONPATH=src python3 scripts/mint_mock_x402_payment.py --header-only)
curl -H "PAYMENT-SIGNATURE: $HEADER" http://127.0.0.1:8098/api/x402/sentinel-report
curl -H "PAYMENT-SIGNATURE: $HEADER" http://127.0.0.1:8098/api/x402/sentinel-report
SIGNED=$(python3 scripts/sign_x402_payment.py --header-only)
curl -H "PAYMENT-SIGNATURE: $SIGNED" http://127.0.0.1:8098/api/x402/sentinel-report
```

The first call returns `mode=x402_mock_verified`; the second returns a 402 replay
rejection. This is intentionally a local verifier, not a live facilitator
settlement.

Next code:

- Replace the local EIP-712 verifier with a facilitator-backed Base Sepolia
  x402 verification path.
- Add an env-gated verifier path for `https://x402.org/facilitator`.
- Keep `liveSettlementEnabled=false` until a testnet wallet signs the payload.
- Optionally add CDP facilitator config behind env vars for Base mainnet.

### 2. MegaETH Receipt Mirror and Mainnet App Scout

MegaETH mainnet is live as of the April 30, 2026 TGE. Official docs list chain
ID `4326`, RPC `https://mainnet.megaeth.com/rpc`, explorers on Blockscout and
Etherscan, MEGA token `0x28B7E77f82B25B95953825F1E3eA0E36c1c29861`, and an
Ethereum mainnet standard bridge at `0x0CA3A2FBC3D770b578223FBB6b062fa875a2eE75`.
Sentinel includes this as `megaeth_mainnet` in read-only mode and adds a
Rabbithole-backed app scout for catalog discovery, featured-app tracking, public
chain stats, optional public wallet balance reads, and unsigned intent
templates.

MegaETH testnet chain ID is `6343`, with public RPC
`https://carrot.megaeth.com/rpc`. Sentinel has deployed the same
`SapphireSentinelRegistry` as a low-latency receipt mirror and seeded the demo
mandate, prior spend, approved receipt, and blocked receipt.

Next code:

- Verify the MegaETH testnet source on Blockscout.
- Keep `scripts/anchor_mirror_receipts.py --network megaeth_testnet --key-alias
  robinhood_testnet` as the replay-safe mirror seeding path.
- Do not deploy to `megaeth_mainnet` from the default tooling; it is included
  for TGE-aware monitoring, public app discovery, quote drafting, and simulation
  context only.
- Use `scripts/scout_megaeth_mainnet.py --probe-apps` to refresh public
  Rabbithole app state without reading private keys or sending transactions.

Latest deployment note: MegaETH testnet deployment and receipt seeding completed
on April 30, 2026. Source verification is still pending.

### 3. Zama Encrypted Risk Gate

Zama FHEVM runs confidential Solidity-style contracts over encrypted data.
Current practical path: local Hardhat mock encryption first, then Sepolia for
real encrypted values.

Next code:

- Use `contracts/privacy/EncryptedRiskGateMock.sol` as the local interface
  contract.
- Use `/api/privacy/proofs` or `scripts/generate_privacy_proofs.py` to show the
  receipt-bound encrypted-risk commitment and redacted witness shape.
- Port that interface to encrypted integer types in a Zama Hardhat project.
- Feed the resulting `riskCommitment` into the existing Robinhood receipt.
- Label this as Zama-on-Sepolia until actually deployed and verified.

### 4. Aztec Private Intent Evidence

Aztec is not an EVM chain. The right role is private evidence: prove that a
private mandate note, private balance, or private intent satisfies public
thresholds, then export a commitment.

Next code:

- Keep `artifacts/privacy/aztec_private_intent_note.nr` as the private-intent
  blueprint.
- Use `/api/privacy/proofs` as the local proof-output envelope until the Aztec
  toolchain is installed.
- Add a local proof-output JSON once the Aztec toolchain is installed.
- Anchor only the exported commitment in Sentinel receipts.

## Existing Sapphire Synergies

Use these concepts from `/Users/aribs/Code/Sapphire`, but do not copy secrets or
production runtime data:

- `lib/payments/x402_middleware.py`: nonce cache, pluggable verifier, event-bus
  shape, and test-friendly mock verifier.
- `lib/core/risk_kernel/`: typed risk-envelope and fail-closed verdict patterns.
- `tests/fixtures/redteam/risk_kernel_leakage_scenarios.json`: scenario
  categories such as kill-switch bypass, lookahead leakage, drawdown breach,
  and secret prompt leakage.
- `docs/security/adversarial-intelligence-threat-model-2026-04-28.md`: threat
  model structure and read-only/default-no-mutation posture.

Do not import live trading, Telegram, brokerage credentials, `.env` files,
runtime data, or private production configs.

## Source Map

- Robinhood Chain docs: `https://docs.robinhood.com/chain/`
- x402 network support: `https://docs.x402.org/core-concepts/network-and-token-support`
- Coinbase x402: `https://docs.cdp.coinbase.com/x402/welcome`
- Base RPC docs: `https://docs.base.org/base-chain/api-reference/rpc-overview`
- MegaETH testnet: `https://docs.megaeth.com/testnet`
- MegaETH mainnet: `https://docs.megaeth.com/frontier`
- MegaETH RPC: `https://docs.megaeth.com/rpc`
- Zama Solidity guides: `https://docs.zama.org/protocol/solidity-guides`
- Zama FHEVM runtime modes: `https://docs.zama.org/protocol/solidity-guides/development-guide/hardhat/run_test`
- Aztec docs: `https://docs.aztec.network/`

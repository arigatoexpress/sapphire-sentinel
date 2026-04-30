# Sapphire Sentinel

The agent firewall for tokenized RWA finance on Robinhood Chain testnet.

Sapphire Sentinel is a London buildathon project for the Robinhood Chain / Arbitrum Open House ecosystem. It gives AI agents a bounded mandate before they can buy paid intelligence, touch tokenized-stock workflows, or draft market actions.

The short version: agents can hit paid APIs through an x402-style flow, but Sentinel checks domain allow-lists, spend limits, quote binding, prompt-injection language, secret-egress risk, contract-level receipt replay protection, and privacy commitments first. Safe decisions produce hashed receipts for Robinhood Chain testnet. Unsafe decisions are blocked before any wallet signature or order submission.

## What Is In This Repo

| Surface | Path |
|---|---|
| Non-custodial registry contract | `contracts/SapphireSentinelRegistry.sol` |
| Policy engine | `src/sapphire_sentinel/sentinel.py` |
| x402 requirement model | `src/sapphire_sentinel/x402.py` |
| Privacy sidecar commitments | `src/sapphire_sentinel/privacy.py` |
| Red-team scenarios | `src/sapphire_sentinel/scenarios.py` |
| Flask demo app | `src/sapphire_sentinel/app.py` |
| Mock x402 buyer header | `scripts/mint_mock_x402_payment.py` |
| Robinhood Chain deploy helper | `scripts/deploy_robinhood_chain.py` |
| Buildathon plan | `docs/london-buildathon-plan.md` |
| Research brief | `docs/research.md` |
| Privacy claims | `docs/privacy-claims.md` |
| Cross-chain/privacy roadmap | `docs/integration-roadmap.md` |
| Demo script | `docs/demo-script.md` |

## Safety Defaults

- Testnet and paper-only.
- No live Robinhood orders.
- No Telegram sends.
- No secret reads.
- No real funds or custody.
- Contract has no `withdraw`, `.transfer`, or value-moving call path.
- x402 live settlement is disabled unless a future env-gated testnet mode is added.

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
flask --app sapphire_sentinel.app run --port 8098
```

Open `http://127.0.0.1:8098`.

## Judge Quickstart

```bash
pip install -e ".[dev]"
pytest -q
flask --app sapphire_sentinel.app run --port 8098
```

Backup CLI:

```bash
PYTHONPATH=src python scripts/run_demo.py
```

Protected x402 report demo:

```bash
HEADER=$(PYTHONPATH=src python scripts/mint_mock_x402_payment.py --header-only)
curl -H "PAYMENT-SIGNATURE: $HEADER" http://127.0.0.1:8098/api/x402/sentinel-report
curl -H "PAYMENT-SIGNATURE: $HEADER" http://127.0.0.1:8098/api/x402/sentinel-report
```

The first call returns the private-signal report in `x402_mock_verified` mode.
The second call is rejected for nonce replay. No facilitator or live settlement
is invoked.

## Verify

```bash
pytest -q
ruff check .
python scripts/deploy_robinhood_chain.py --dry-run
python scripts/probe_networks.py
python scripts/deploy_registry.py --network megaeth_testnet --dry-run
```

`--dry-run` compiles the contract and skips deployment. Full deployment requires a funded Robinhood Chain testnet key in `ROBINHOOD_DEPLOY_KEY`.

## API Surface

| Endpoint | Purpose |
|---|---|
| `GET /api/demo` | Full judge-facing demo state |
| `GET /api/scenarios` | Red-team matrix and pass/fail outcomes |
| `GET /api/privacy` | Oasis/Zama/Aztec sidecar commitments and constraints |
| `GET /api/x402/paywall` | Simulated x402 v2 `402 Payment Required` with `PAYMENT-REQUIRED` header |
| `GET /api/x402/sentinel-report` | Protected report unlocked by a bound mock `PAYMENT-SIGNATURE` header |
| `POST /api/evaluate` | Evaluate an arbitrary paid-resource attempt |

## Demo Flow

1. Human creates an agent mandate: spend cap, allowed domains, allowed actions, privacy mode, and expiry.
2. Agent requests a paid private RWA signal.
3. Sentinel returns an x402-compatible payment requirement on Base Sepolia using CAIP-2 `eip155:84532`.
4. Sentinel approves the safe request and blocks a prompt-injected request.
5. A privacy commitment is produced from the Oasis Sapphire sidecar path, with Zama and Aztec companion artifacts clearly labeled.
6. A dry-run Robinhood Chain stock-token order draft is shown.
7. Approved and blocked receipt hashes are anchored on Robinhood Chain testnet with explorer links.

## Robinhood Chain Testnet

- Chain ID: `46630`
- Public RPC: `https://rpc.testnet.chain.robinhood.com`
- Recommended RPC template: `https://robinhood-testnet.g.alchemy.com/v2/<YOUR_API_KEY>`
- Explorer: `https://explorer.testnet.chain.robinhood.com`
- Gas token: `ETH`
- USDG: `0x7E955252E15c84f5768B83c41a71F9eba181802F`
- Stock tokens: `TSLA`, `AMZN`, `PLTR`, `NFLX`, `AMD`

The demo uses Robinhood Chain for on-chain attestations and receipt anchors. x402 settlement is modeled on Base Sepolia because public facilitator support is mature there; a custom Robinhood Chain facilitator is a follow-up.

## Testnet Deployment

`SapphireSentinelRegistry` is deployed on Robinhood Chain testnet:

- Address: `0x2EBB91F7B376cB821d90ac4A7d77B0d06b70B36F`
- Transaction: `0xc53ab8fc8cdab4ce7ef5f09fd56fc564756fd8d5e5b7c0396238878d6cc84975`
- Explorer: `https://explorer.testnet.chain.robinhood.com/address/0x2EBB91F7B376cB821d90ac4A7d77B0d06b70B36F`
- Source verification: complete, compiler `v0.8.20+commit.a1b79de6`, optimization disabled.

The deployment used a burner EVM account funded only with Robinhood Chain testnet ETH.

## Anchored Demo Events

- Mandate registration: `0x4b00516f25ee38b1b59a0acd0f442706ae2b0756d9d56a25c0cf18d5eabc01dc`
- Prior spend seed: `0xbe28bc9af7a9ec6c8c1e671b9b1a17788b217942c102eec4ab7c808f418ec67a`
- Approved receipt: `0xc522c1d31f632662e8a7921a50e0b8827eabc7f5ffd88e3ca489a4e4399d25d8`
- Blocked receipt: `0x0d7d1708b80cc14975564dd96c64d7ed37a5ee7dc5ac484929d5ae4bca7c7390`
- On-chain remaining demo budget: `1.618` USDC (`1,618,000` atomic units).

## Cross-Chain Roadmap

Sentinel now exposes a network registry and integration roadmap in `/api/networks`
and the dashboard:

- Robinhood Chain testnet: live RWA audit anchor.
- Base Sepolia: local mock x402 gate with `PAYMENT-SIGNATURE` verification,
  quote binding, and nonce replay rejection; next step is real wallet-signed
  testnet settlement.
- MegaETH testnet: deploy-ready low-latency receipt mirror.
- Zama on Sepolia: encrypted budget/risk gate artifact path.
- Aztec: private mandate / intent proof blueprint.

The public claim stays tight: privacy sidecars export commitments to public
receipts; they are not private Robinhood Chain payments.

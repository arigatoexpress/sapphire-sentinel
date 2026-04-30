# Sapphire Sentinel

The agent firewall for tokenized RWA finance on Robinhood Chain testnet.

Sapphire Sentinel is a London buildathon project for the Robinhood Chain / Arbitrum Open House ecosystem. It gives AI agents a bounded mandate before they can buy paid intelligence, touch tokenized-stock workflows, or draft market actions.

The short version: agents can hit paid APIs through an x402-style flow, but Sentinel checks domain allow-lists, spend limits, quote binding, prompt-injection language, secret-egress risk, replay nonces, and privacy commitments first. Safe decisions produce hashed receipts for Robinhood Chain testnet. Unsafe decisions are blocked before any wallet signature or order submission.

## What Is In This Repo

| Surface | Path |
|---|---|
| Non-custodial registry contract | `contracts/SapphireSentinelRegistry.sol` |
| Policy engine | `src/sapphire_sentinel/sentinel.py` |
| x402 requirement model | `src/sapphire_sentinel/x402.py` |
| Privacy sidecar commitments | `src/sapphire_sentinel/privacy.py` |
| Red-team scenarios | `src/sapphire_sentinel/scenarios.py` |
| Flask demo app | `src/sapphire_sentinel/app.py` |
| Robinhood Chain deploy helper | `scripts/deploy_robinhood_chain.py` |
| Buildathon plan | `docs/london-buildathon-plan.md` |
| Research brief | `docs/research.md` |
| Privacy claims | `docs/privacy-claims.md` |
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

## Verify

```bash
pytest -q
ruff check .
python scripts/deploy_robinhood_chain.py --dry-run
```

`--dry-run` compiles the contract and skips deployment. Full deployment requires a funded Robinhood Chain testnet key in `ROBINHOOD_DEPLOY_KEY`.

## API Surface

| Endpoint | Purpose |
|---|---|
| `GET /api/demo` | Full judge-facing demo state |
| `GET /api/scenarios` | Red-team matrix and pass/fail outcomes |
| `GET /api/privacy` | Oasis/Zama/Aztec sidecar commitments and constraints |
| `GET /api/x402/paywall` | Simulated x402 v2 `402 Payment Required` with `PAYMENT-REQUIRED` header |
| `POST /api/evaluate` | Evaluate an arbitrary paid-resource attempt |

## Demo Flow

1. Human creates an agent mandate: spend cap, allowed domains, allowed actions, privacy mode, and expiry.
2. Agent requests a paid private RWA signal.
3. Sentinel returns an x402-compatible payment requirement on Base Sepolia using CAIP-2 `eip155:84532`.
4. Sentinel approves the safe request and blocks a prompt-injected request.
5. A privacy commitment is produced from the Oasis Sapphire sidecar path, with Zama and Aztec companion artifacts clearly labeled.
6. A dry-run Robinhood Chain stock-token order draft is shown.
7. A hash-only receipt preview is ready for `SapphireSentinelRegistry.recordPaymentEvaluation(...)`.

## Robinhood Chain Testnet

- Chain ID: `46630`
- Public RPC: `https://rpc.testnet.chain.robinhood.com`
- Recommended RPC template: `https://robinhood-testnet.g.alchemy.com/v2/<YOUR_API_KEY>`
- Explorer: `https://explorer.testnet.chain.robinhood.com`
- Gas token: `ETH`
- USDG: `0x7E955252E15c84f5768B83c41a71F9eba181802F`
- Stock tokens: `TSLA`, `AMZN`, `PLTR`, `NFLX`, `AMD`

The demo uses Robinhood Chain for on-chain attestations and receipt anchors. x402 settlement is modeled on Base Sepolia because public facilitator support is mature there; a custom Robinhood Chain facilitator is a follow-up.

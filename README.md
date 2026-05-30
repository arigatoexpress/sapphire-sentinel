# Sapphire Sentinel

> Policy, privacy, and payment safety firewall for AI agents in tokenized RWA finance.

[![CI](https://github.com/arigatoexpress/sapphire-sentinel/actions/workflows/ci.yml/badge.svg)](https://github.com/arigatoexpress/sapphire-sentinel/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)

## What this does

Sapphire Sentinel gives AI agents a bounded mandate before they can buy paid intelligence, touch tokenized-stock workflows, or draft market actions. It checks domain allow-lists, spend limits, quote binding, prompt-injection language, secret-egress risk, contract-level receipt replay protection, and privacy commitments first. Safe decisions produce hashed receipts. Unsafe decisions are blocked before any wallet signature or order submission.

## Quick start

```bash
git clone https://github.com/arigatoexpress/sapphire-sentinel.git
cd sapphire-sentinel
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
flask --app sapphire_sentinel.app run --port 8098
```

Open `http://127.0.0.1:8098`.

Try the protected report demo:

```bash
HEADER=$(PYTHONPATH=src python3 scripts/mint_mock_x402_payment.py --header-only)
curl -H "PAYMENT-SIGNATURE: $HEADER" http://127.0.0.1:8098/api/x402/sentinel-report
```

The first call returns the report. The second call is rejected for nonce replay.

## Architecture

```
Agent request ──▶ Policy engine ──▶ allow / deny
                      │
                      +-- Domain allow-list + spend caps
                      +-- x402 payment requirement + signature verification
                      +-- Prompt-injection / secret-egress detection
                      +-- Privacy sidecars (Oasis / Zama / Aztec)
                      +-- Receipt hash + on-chain anchor
```

## Key features

- **Policy engine** — Domain allow-lists, spend limits, nonce replay protection, prompt-injection detection.
- **x402 payment gates** — Mock and signed payment requirements with EIP-712 payer recovery and quote binding.
- **Privacy sidecars** — Oasis Sapphire, Zama fhEVM, and Aztec commitment artifacts.
- **Cross-chain receipts** — Robinhood Chain testnet anchor with MegaETH testnet mirror.
- **MegaETH scout** — Read-only mainnet app discovery and unsigned intent templates.

## Tech stack

- Python 3.11+
- Flask 3.0+
- web3.py, eth-account, py-solc-x
- pytest, ruff, mypy
- Solidity ^0.8.20

## API surface

| Endpoint | Purpose |
|---|---|
| `GET /api/demo` | Full demo state |
| `GET /api/scenarios` | Red-team matrix and outcomes |
| `GET /api/privacy` | Privacy sidecar commitments |
| `GET /api/privacy/proofs` | Zama/Aztec proof bundle |
| `GET /api/networks` | Cross-chain integration roadmap |
| `GET /api/megaeth/apps` | MegaETH mainnet app registry |
| `GET /api/x402/paywall` | Simulated 402 Payment Required |
| `GET /api/x402/sentinel-report` | Protected report via payment signature |
| `POST /api/evaluate` | Evaluate a paid-resource attempt |

## Safety defaults

- **Testnet and paper-only.** No live Robinhood orders.
- No Telegram sends, no secret reads, no real funds or custody.
- MegaETH mainnet mode is read, quote, and simulate only.
- Registry contract has no `withdraw`, `.transfer`, or value-moving path.
- x402 live settlement is disabled unless an env-gated testnet mode is explicitly added.

## Tests

```bash
pytest -q
ruff check .
python3 scripts/browser_smoke.py
```

## Agent collaborators

See [AGENTS.md](AGENTS.md) for project structure, safety boundaries, and deployment notes.

## License

[MIT](LICENSE).

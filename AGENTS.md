# Sapphire Sentinel — Agent Guide

## Project Overview

Sapphire Sentinel is the **agent firewall for tokenized RWA finance on Robinhood Chain testnet**. It provides policy, privacy, and payment safety for autonomous AI agents in Real-World Asset (RWA) finance.

**Live deployment:** `https://sapphire-sentinel.onrender.com` (planned)
**Testnet contract:** `0x9e1eC2fd8D1276Fc294e62372e78c1048C9A9552` (Robinhood Chain testnet)

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   AI Agent      │────▶│  Sapphire Sentinel│────▶│ Robinhood Chain │
│  (requester)    │     │   (policy engine)  │     │   (testnet)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌──────────────────┐
│   x402 Payment  │     │  Privacy Sidecars │
│   Headers       │     │ (Sapphire/Zama)   │
└─────────────────┘     └──────────────────┘
```

**Core modules:**
- `sentinel.py` — Policy engine (domain allow-list, spend limits, nonce replay protection, prompt-injection detection)
- `x402.py` — v2 payment requirement simulation, EIP-712 payer recovery
- `privacy.py` / `privacy_proofs.py` — Oasis Sapphire, Zama fhEVM, Aztec commitments
- `megaeth_apps.py` — Read-only MegaETH mainnet app discovery
- `app.py` — Flask demo server
- `networks.py` — Chain configuration (Robinhood testnet, MegaETH mainnet)

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.11+ |
| Runtime | Flask 3.0+ |
| Testing | pytest 8.0+, pytest-cov 5.0+ |
| Linting | ruff 0.4+, mypy 1.10+ |
| Smart Contracts | Solidity ^0.8.20 |
| Blockchain | web3, eth-account, py-solc-x |
| Containerization | Docker multi-stage build |
| Deployment | Render (Docker), Cloud Run (optional) |

## Development Commands

```bash
# Install all dependencies
pip install -e ".[dev,x402,deploy]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=src/sapphire_sentinel --cov-report=html

# Run type checks
mypy src/sapphire_sentinel --ignore-missing-imports

# Run linting
ruff check .
ruff format .

# Run the demo server
python -m flask --app src/sapphire_sentinel/app run --port 8098

# Build Docker image
docker build -t sapphire-sentinel .

# Run Docker container
docker run -p 8098:8098 sapphire-sentinel
```

## CI/CD

GitHub Actions workflows:
- **test** — pytest with coverage, mypy type checking, ruff lint+format across Python 3.11/3.12/3.13
- **contracts** — Solidity compilation via Foundry
- **docker** — Docker build + health check (main branch only)

## Safety Boundaries (MUST NOT CHANGE)

1. **Testnet-only** — No mainnet deployments without explicit human approval.
2. **No value-moving paths** — The registry contract has no `withdraw`, `transfer`, or payable functions.
3. **No secret reads** — The policy engine must never read or log private keys, mnemonics, or API secrets.
4. **No live trading** — No real Robinhood orders or live x402 facilitator settlement by default.
5. **No Telegram sends** — No outbound messaging integrations without approval.

## Agent Conventions

- Use **type hints** everywhere (`from __future__ import annotations` at top of each file).
- Use **ruff** for linting and formatting (line length 100, target py311).
- Write **tests** for every new module or route (minimum 70% coverage).
- Document **safety boundaries** in docstrings for any function touching payments or signatures.
- Use **conventional commits**: `feat:`, `fix:`, `docs:`, `test:`, `chore:`.
- Update `AGENTS.md` if you change architecture or safety boundaries.

## Deployment

### Render (Docker)
1. Push to `main`
2. Connect repo to Render Dashboard
3. Use `render.yaml` blueprint or manual Docker service

### Cloud Run (optional)
```bash
gcloud run deploy sapphire-sentinel \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

## Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `PORT` | Flask server port | No (default 8097) |
| `FLASK_ENV` | development / production | No |
| `PYTHONPATH` | Must include `src/` | Yes for Docker |

## Contributing

1. Create a feature branch: `git checkout -b feat/description`
2. Make changes with tests
3. Run the full check suite: `pytest && mypy src/sapphire_sentinel && ruff check .`
4. Open a PR against `main`

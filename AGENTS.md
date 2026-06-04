# Sapphire Sentinel — Agent Guide

## What this repo does

Sapphire Sentinel is the **agent firewall for tokenized RWA finance on Robinhood Chain testnet**. It provides policy, privacy, and payment safety for autonomous AI agents in Real-World Asset (RWA) finance through domain allow-lists, spend limits, x402 payment gates, and privacy sidecars.

## Key directories and files

```
sapphire-sentinel/
├── src/sapphire_sentinel/       # Application code
│   ├── app.py                   # Flask demo server
│   ├── sentinel.py              # Policy engine
│   ├── x402.py                  # x402 payment requirement + verification
│   ├── privacy.py               # Oasis Sapphire sidecar commitments
│   ├── privacy_proofs.py        # Zama/Aztec proof bundles
│   ├── megaeth_apps.py          # MegaETH mainnet app discovery
│   └── networks.py              # Chain configuration
├── contracts/                   # Solidity registry contract
│   └── SapphireSentinelRegistry.sol
├── scripts/                     # Demo and deploy scripts
│   ├── mint_mock_x402_payment.py
│   ├── sign_x402_payment.py
│   ├── generate_privacy_proofs.py
│   ├── deploy_robinhood_chain.py
│   └── scout_megaeth_mainnet.py
├── docs/                        # Buildathon plans, research, roadmaps
├── tests/                       # pytest suite
└── pyproject.toml               # Dependencies and project config
```

## How to run tests / dev server

```bash
# Install
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Tests
pytest -q
ruff check .

# Dev server
flask --app sapphire_sentinel.app run --port 8098
# open http://127.0.0.1:8098
```

## Safety boundaries (DO NOT CHANGE)

1. **Testnet-only** — No mainnet deployments without explicit human approval.
2. **No value-moving paths** — The registry contract has no `withdraw`, `transfer`, or payable functions.
3. **No secret reads** — Never read or log private keys, mnemonics, or API secrets.
4. **No live trading** — No real Robinhood orders or live x402 facilitator settlement by default.
5. **No Telegram sends** — No outbound messaging integrations without approval.

## Current status

- London buildathon project; testnet-only.
- `SapphireSentinelRegistry` deployed on Robinhood Chain testnet at `0x2EBB91F7B376cB821d90ac4A7d77B0d06b70B36F`.
- Base Sepolia mock x402 gate with EIP-712 and nonce replay rejection working.
- MegaETH testnet receipt mirror deployed.
- MegaETH mainnet read-only scout live.

# AGENTS.md — Operating Charter

> Guiding principles for any AI agent (or human) working in this repo. Derived from the Andrej Karpathy engineering philosophy. Tool-neutral: applies whether you drive this repo with Claude Code, goose, or by hand.

## The four rules
1. **Simplicity first.** Write the minimum code that solves the task. No speculative abstractions, no unrequested features, no single-use platforms. Extract a shared module only when there are >= 2 real call-sites today.
2. **Surgical changes, one concern per PR.** Touch only what the task requires. Do not opportunistically reformat, bump unrelated deps, or fix adjacent dead code. Small, reviewable, independently revertable diffs.
3. **Evals are the spec.** Define and run the repo verification (tests, build, typecheck, smoke) BEFORE and AFTER a change. Nothing merges unless it stays green. Keep the generate->verify loop tight and reversible.
4. **Delete > add; fewer dependencies.** Removing code, repos, and dependencies is the highest-leverage move. Every dependency is attack surface you own. Pin and lock what remains. Humans stay in the loop for irreversible / outward-facing / production steps (deletes, credential rotation, infra teardown, deploys).

## Safety
- Never use `git add .` or `git add -A` — stage changed files by explicit path (avoids sweeping in WIP or secrets).
- Never commit secrets; `.env*` stays gitignored (except `.env.example`).
- Treat anything outward-facing or irreversible as draft-then-confirm.

# Judging Strategy

## One-Line Thesis

Sapphire Sentinel is the agent firewall for tokenized RWA finance on Robinhood
Chain.

## Category Fit

Primary target: Best Agentic Project.

Secondary target: Overall Robinhood Chain reserved slot.

Why: the project is agentic by construction, deployed for Robinhood Chain
testnet, and addresses a real operational gap in tokenized finance.

## Criteria Mapping

| Criterion | Evidence |
|---|---|
| Smart contract quality | Non-custodial registry, mandate expiry, budget accounting, receipt replay protection, two-step operator transfer, no value-moving paths |
| Product-market fit | Financial institutions and users need bounded autonomous agents before tokenized RWA markets can be trusted |
| Innovation and creativity | x402 agent payments plus privacy sidecars plus Robinhood Chain audit anchors |
| Real problem solving | Blocks prompt injection, secret egress, untrusted providers, wrong actions, overspend, and replay-prone payment attempts |

## What Judges Should Remember

- It uses Robinhood Chain for the part that matters: public attestations for
  autonomous RWA controls.
- It does not pretend the testnet stock tokens have real value.
- It does not pretend Robinhood Chain is private.
- It shows a security product with clear users: agent builders, RWA protocols,
  custodians, broker-dealer infrastructure teams, and API/data providers.
- It can grow into an SDK, gateway, or managed control plane.

## Submission Checklist

- Public GitHub repo.
- README with safety defaults.
- Contract compiles.
- Contract deployed and source-verified on Robinhood Chain testnet.
- Approved and blocked demo receipts anchored on Robinhood Chain testnet.
- Local tests pass.
- Dashboard live locally.
- 90-second video recorded.
- Screenshot or short GIF captured as a fallback visual artifact.
- If a funded testnet key is available, deploy `SapphireSentinelRegistry` and
  add the explorer link to `data/deployments.json`. Done on Robinhood Chain
  testnet at `0x2EBB91F7B376cB821d90ac4A7d77B0d06b70B36F`.

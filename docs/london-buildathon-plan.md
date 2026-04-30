# Sapphire Sentinel: London Buildathon Plan

## Pitch

Sapphire Sentinel is the agent firewall for tokenized RWA finance on Robinhood
Chain testnet. Agents can buy paid intelligence through x402-style HTTP 402
flows, but every call is checked against a human mandate, budget, domain
allow-list, quote-binding policy, prompt-injection screen, secret-egress screen,
privacy commitment, and replay nonce before a receipt hash is anchored on-chain.

## Why This Should Win

- Robinhood Chain relevance is native, not decorative: the demo deploys a
  Robinhood Chain contract, `SapphireSentinelRegistry`, for agent mandates and
  payment receipts.
- The Best Agentic Project angle is obvious: an AI agent tries to pay for
  private RWA intelligence and draft a tokenized-stock action.
- The cybersecurity angle is concrete: Sentinel blocks unsafe domains, prompt
  injection, secret-exfiltration language, and budget violations.
- The privacy story is buildable: exact portfolio/risk inputs stay off-chain;
  only `policyHash`, `resultHash`, `riskHash`, and `privacyCommitment` land
  on-chain.
- The demo is safe by default: no live Robinhood orders, no real Telegram
  sends, no secret reads, and no production funds.

## Demo Flow

1. Human creates an agent mandate: spend cap, allowed domains, allowed actions,
   privacy mode, and expiry.
2. Agent requests a paid private RWA signal.
3. The API returns an x402 v2-compatible payment requirement on Base Sepolia
   using CAIP-2 network ID `eip155:84532`.
4. Sentinel screens the request. A safe request is approved; an untrusted or
   prompt-injected request is blocked.
5. Approved flow returns a dry-run Robinhood order draft and an on-chain anchor
   preview for `SapphireSentinelRegistry.recordPaymentEvaluation(...)`.
6. Dashboard shows the same decision as a judge-friendly chain/payment/privacy
   trace in the standalone app.

## Build Surface

| Surface | Path |
|---|---|
| Mandate/receipt contract | `contracts/SapphireSentinelRegistry.sol` |
| Policy evaluator | `src/sapphire_sentinel/sentinel.py` |
| Privacy commitments | `src/sapphire_sentinel/privacy.py` |
| Red-team scenarios | `src/sapphire_sentinel/scenarios.py` |
| Dashboard page | `templates/index.html` |
| Demo APIs | `/api/demo`, `/api/evaluate`, `/api/x402/paywall` |
| Deployment list | `scripts/deploy_robinhood_chain.py` |

## Safe Defaults

- `execution_enabled=false` in every order draft.
- `broadcast=false` in the chain anchor preview until a funded testnet deploy is
  intentionally run.
- x402 settlement is simulated on Base Sepolia because public facilitator
  support is mature there; Robinhood Chain receives the receipt anchor.
- The Sentinel contract is non-custodial and has no withdraw path.

## Next Buildathon Steps

1. Run `python3 scripts/deploy_robinhood_chain.py --dry-run` once `py-solc-x`
   is available.
2. Deploy `SapphireSentinelRegistry` to Robinhood Chain testnet with a funded
   testnet key.
3. Replace the dry-run anchor preview with a `recordPaymentEvaluation(...)`
   transaction in testnet mode only.
4. Add a focused Oasis Sapphire sidecar contract for confidential policy
   evaluation.
5. Add a small Zama/FHEVM local mock that produces the `resultHash` and
   `riskHash` from hidden basket weights.
6. Record a 90-second demo: approved payment, blocked injection attempt,
   Robinhood Chain explorer receipt, and non-submitting RWA order draft.

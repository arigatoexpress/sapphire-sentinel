# 90-Second Demo Script

## 0-10 Seconds

Open the dashboard to the Red-Team Matrix and verdict panel.

Pitch:

> Sapphire Sentinel is the agent firewall for tokenized RWA finance. Agents can
> buy paid data, but only inside human mandates, privacy commitments, and
> Robinhood Chain audit receipts.

## 10-30 Seconds

Show the approved scenario, x402 Payment Quote, and Robinhood Chain Anchor.

Point out:

- Human mandate has an allow-list, action list, expiry, and USDC budget.
- The quote is modeled as x402 v2 on Base Sepolia, and the protected report
  endpoint verifies quote-bound mock or EIP-712 signed `PAYMENT-SIGNATURE`
  headers before returning the signal.
- The RWA action is a Robinhood Chain test stock-token draft, not a live order.

## 30-50 Seconds

Click the prompt-injection or untrusted-domain scenario in the Red-Team Matrix.

Point out:

- The same agent is blocked before wallet signing.
- The receipt still has a risk hash and nonce, so blocked attempts can be audited.
- No secret or prompt content is written to chain.

## 50-70 Seconds

Show Privacy Sidecars, Network Registry, and On-Chain Event Proofs.

Pitch:

> Robinhood Chain stays public. Sensitive policy inputs stay in privacy sidecars.
> Oasis Sapphire is the first real implementation target; Zama and Aztec are
> companion proof bundles for encrypted risk math and private intent evidence.
> Base gives us the x402 gate, and MegaETH is the low-latency receipt mirror.

## 70-90 Seconds

Show the Judge Scorecard and Proof Points.

Close:

> This is not another AI trader. It is the missing control plane for autonomous
> finance: spend limits, quote binding, prompt-injection defense, privacy
> commitments, and receipt anchoring on Robinhood Chain.

## Backup CLI

```bash
PYTHONPATH=src python3 scripts/run_demo.py
python3 scripts/generate_privacy_proofs.py
HEADER=$(PYTHONPATH=src python3 scripts/mint_mock_x402_payment.py --header-only)
curl -H "PAYMENT-SIGNATURE: $HEADER" http://127.0.0.1:8098/api/x402/sentinel-report
SIGNED=$(python3 scripts/sign_x402_payment.py --header-only)
curl -H "PAYMENT-SIGNATURE: $SIGNED" http://127.0.0.1:8098/api/x402/sentinel-report
```

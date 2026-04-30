# Sapphire Sentinel Research Brief

Current as of April 29, 2026.

## Hackathon Target

Arbitrum Open House London is the right target because the Buildathon has both
overall and AI Agentic prize tracks, and both reserve at least one winning slot
for projects building on Robinhood Chain. HackQuest lists the judging criteria
as deployment on an Arbitrum chain, smart contract quality, product-market fit,
innovation and creativity, and real problem solving.

Key dates from HackQuest:

- Registration: March 24, 2026 16:54 to May 25, 2026 15:54.
- Submission: March 24, 2026 16:54 to June 14, 2026 15:54.
- Reward announcement: June 17, 2026 15:54.

Sources:

- Arbitrum London announcement: https://blog.arbitrum.foundation/open-house-london-registration-is-now-open/
- HackQuest London Buildathon: https://www.hackquest.io/hackathons/Arbitrum-Open-House-London-Online-Buildathon

## Robinhood Chain Fit

Robinhood Chain testnet is an Arbitrum Orbit Layer-2 built on Ethereum. The
official Chain ID is `46630`, gas token is `ETH`, and the public RPC is
`https://rpc.testnet.chain.robinhood.com`. The recommended production-style
developer endpoint is Alchemy's Robinhood Chain Testnet RPC template.

Official contracts include WETH, USDG, and five stock-token test contracts:
TSLA, AMZN, PLTR, NFLX, and AMD. The project should use these assets as
references but avoid implying economic exposure or live trading. Robinhood's
testnet terms say testnet tokens and test stock tokens have no monetary or
intrinsic value, confer no rights, and may be reset or discontinued.

Sources:

- Robinhood Chain overview: https://docs.robinhood.com/chain/
- Connecting docs: https://docs.robinhood.com/chain/connecting/
- Contract list: https://docs.robinhood.com/chain/contracts/
- Deployment tutorial: https://docs.robinhood.com/chain/deploy-smart-contracts/
- Testnet terms: https://docs.robinhood.com/chain/terms-of-service/

## Winning Product Angle

The strongest positioning is not "AI trader." It is:

> Sapphire Sentinel is the agent firewall for tokenized RWA finance.

Arbitrum's London post says the NYC winners clustered around the operational
services layer that institutional tokenization still lacks. Sentinel sits
directly in that gap: autonomous agents can buy data and draft RWA actions, but
every paid call is checked against human mandates, budgets, privacy
commitments, and on-chain audit receipts before a wallet signature or order
submission can happen.

## x402 Fit

x402 is the right payment metaphor because it is HTTP-native: a resource server
returns `402 Payment Required`, the client signs a payment payload, the server
verifies and settles via a facilitator, and the response returns a paid
resource. The current v2 header shape uses `PAYMENT-REQUIRED`,
`PAYMENT-SIGNATURE`, and `PAYMENT-RESPONSE`.

Sentinel should be shown as a buyer-side policy wrapper around this flow:

- Decode the quote and bind it to the policy decision.
- In this demo, check provider domain, action, amount, `payTo`, chain metadata,
  content-risk signals, and contract-level receipt replay protection.
- In a production facilitator wrapper, extend the same policy to full host/path,
  facilitator, expiry, and settlement verification.
- Redact payment metadata before forwarding to a facilitator.
- Emit a human-readable audit trail.

Default mode is simulation only. Base Sepolia `eip155:84532` is the safest
public x402 demo rail. Live settlement should stay env-gated and testnet-only.

Sources:

- x402 docs: https://docs.x402.org/
- x402 source/spec: https://github.com/x402-foundation/x402
- Coinbase x402 docs: https://docs.cdp.coinbase.com/x402/core-concepts/how-it-works

## Privacy Stack Fit

Robinhood Chain is public. Privacy should be framed as sidecar evidence, not as
private Robinhood Chain payments.

Oasis Sapphire is the most implementation-worthy privacy sidecar because it is
EVM-compatible and supports confidential dApp patterns. The hackathon demo can
use signed commitments first and later move to OPL or Hyperlane.

Zama fhEVM is a compelling companion artifact for encrypted budget/risk math in
Solidity. It should be labeled as FHE-ready, not native Robinhood support,
unless host-chain support is verified.

Aztec is a private-intent companion, not a drop-in EVM sidecar. It can prove
the private note or private balance idea locally and export a commitment to the
Robinhood receipt path.

Sources:

- Oasis Sapphire docs: https://docs.oasis.io/build/sapphire/
- Oasis encrypted events: https://docs.oasis.io/build/sapphire/develop/encrypted-events/
- Zama Solidity guides: https://docs.zama.org/protocol/solidity-guides
- Zama litepaper: https://docs.zama.org/protocol/zama-protocol-litepaper
- Aztec docs: https://docs.aztec.network/

## Build Priorities

1. Make the Robinhood Chain contract strong: non-custodial, budgeted,
   replay-resistant, event-rich, and easy to deploy/verify.
2. Make the dashboard judge-friendly: show allowed and blocked agent payments,
   x402 quote, policy trace, privacy commitments, and Robinhood receipt preview.
3. Keep the privacy story honest: label sidecars and constraints directly in
   docs and API output.
4. Add red-team scenarios that prove the cybersecurity angle in seconds.
5. Prepare a 90-second demo script and avoid any real funds, live orders, or
   private-key requirements in the default path.

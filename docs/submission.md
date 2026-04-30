# HackQuest Submission Copy

## Project Name

Sapphire Sentinel

## Tagline

The agent firewall for tokenized RWA finance on Robinhood Chain.

## Short Description

Sapphire Sentinel lets AI agents buy paid data and draft tokenized-stock actions
only inside human-approved mandates, privacy commitments, and source-verified
Robinhood Chain audit receipts.

## Long Description

Autonomous agents are arriving in onchain finance, but tokenized RWA markets
cannot trust agents that can pay arbitrary APIs, leak secrets, follow prompt
injections, or turn a data request into an execution request. Sapphire Sentinel
is the missing control plane.

The demo models an x402 paid-data flow. An agent requests a private RWA signal,
Sentinel binds the quote, checks the domain, action, budget, payment amount,
prompt-injection language, secret-egress risk, and replay nonce, then produces
either an approved payment preview or a blocked receipt. The resulting
commitments can be anchored in `SapphireSentinelRegistry`, a non-custodial
contract deployed and source-verified on Robinhood Chain testnet.

Robinhood Chain remains the public audit rail. Sensitive policy inputs stay
off-chain or inside privacy sidecars. Oasis Sapphire is the first confidential
policy target, while Zama fhEVM and Aztec are companion artifacts for encrypted
risk math and private intent evidence.

This is not another AI trader. It is safety infrastructure for the agents that
tokenized finance will need before real users, institutions, and data providers
can trust autonomous spending.

## Track Fit

Best Agentic Project and Robinhood Chain reserved prize.

## Deployed Contract

- Network: Robinhood Chain Testnet
- Chain ID: `46630`
- Address: `0x2EBB91F7B376cB821d90ac4A7d77B0d06b70B36F`
- Transaction: `0xc53ab8fc8cdab4ce7ef5f09fd56fc564756fd8d5e5b7c0396238878d6cc84975`
- Source verification: complete, compiler `v0.8.20+commit.a1b79de6`

## Demo Checklist

- Open dashboard.
- Show approved x402 quote for private RWA signal.
- Click prompt-injection scenario and show the blocked receipt.
- Show privacy sidecar commitments.
- Show deployed and source-verified Robinhood Chain anchor.
- Close on the judge scorecard.

## Links

- Repository: `https://github.com/arigatoexpress/sapphire-sentinel`
- Explorer: `https://explorer.testnet.chain.robinhood.com/address/0x2EBB91F7B376cB821d90ac4A7d77B0d06b70B36F`

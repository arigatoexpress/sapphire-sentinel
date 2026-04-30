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
prompt-injection language, secret-egress risk, and contract-level receipt
replay protection, then produces either an approved payment preview or a
blocked receipt. The resulting
commitments are anchored in `SapphireSentinelRegistry`, a non-custodial
contract deployed and source-verified on Robinhood Chain testnet. The demo
includes both an approved payment receipt and a blocked prompt-injection
receipt, so judges can verify that Sentinel records good and bad agent behavior
without writing raw prompts, private risk data, or secrets to chain.

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

## Anchored Demo Events

- Mandate registration: `0x4b00516f25ee38b1b59a0acd0f442706ae2b0756d9d56a25c0cf18d5eabc01dc`
- Prior spend seed: `0xbe28bc9af7a9ec6c8c1e671b9b1a17788b217942c102eec4ab7c808f418ec67a`
- Approved receipt: `0xc522c1d31f632662e8a7921a50e0b8827eabc7f5ffd88e3ca489a4e4399d25d8`
- Blocked receipt: `0x0d7d1708b80cc14975564dd96c64d7ed37a5ee7dc5ac484929d5ae4bca7c7390`
- On-chain remaining demo budget: `1.618` USDC.

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
- Privacy claims: `docs/privacy-claims.md`
- Demo video: pending final recording
- Live demo URL: local during judging, `http://127.0.0.1:8098`

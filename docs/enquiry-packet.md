# Sapphire Sentinel Enquiry Packet

Prepared for event enquiry, registration, and technical-background fields.
Current repo state checked on 2026-04-30: `main...origin/main` at `c83007f`.

## Likely Registration Targets

Primary target:

- HackQuest: `https://www.hackquest.io/hackathons/Arbitrum-Open-House-London-Online-Buildathon`
- Context: Arbitrum Open House London online Buildathon, hosted by Arbitrum Foundation, with Robinhood Chain and Best Agentic Project prize tracks.
- Registration window: March 24, 2026 16:54 to May 25, 2026 15:54.
- Submission window: March 24, 2026 16:54 to June 14, 2026 15:54.

Adjacent enquiry target:

- London Tech Week Hackathon: `https://londontechweek.com/london-tech-week-hackathon`
- Its visible "ENQUIRE TO PARTICIPATE" action is a mailto to `info@londontechweek.com`, not a web form in the public page HTML.

Confirmed London Tech Week contact form:

- General contact page: `https://londontechweek.com/contact`
- General enquiry form: `https://londontechweek.com/contact-form`
- Required fields observed: first name, surname, company name, email, email verification, contact number, and one required question field with a 500-word limit.
- The form says responses may take up to 7 business days.

## Current Application Status

- London Tech Week general enquiry: submitted on 2026-04-30 via `https://londontechweek.com/contact-form`.
- London Tech Week confirmation page: `https://londontechweek.com/contact-form?success`, with response expected within 7 working days.
- Immediate Gmail follow-up search: no matching inbox messages found from London Tech Week, Informa, HackQuest, or Arbitrum within the first check after submission.
- HackQuest Buildathon registration: reachable, but gated by HackQuest authentication. Available sign-in paths observed: Google, GitHub, MetaMask, OCID, or email/password. Do not authorize a new third-party login or create an account without operator action.
- Current local verification: `pytest -q` passed 29 tests, `ruff check .` passed, `python3 -m compileall src scripts` passed, and `git diff --check` passed on 2026-04-30.

Remaining blockers before a HackQuest registration or final project submission:

- Ari must complete or authorize HackQuest login.
- Public Arbitrum One payout wallet address is required for registration; never enter a private key or seed phrase.
- Public demo URL is still pending; localhost is not judge-accessible.
- Final demo video URL is still pending.
- Final team/member choices should be confirmed inside the authenticated HackQuest flow.

## Project Identity

Project name: Sapphire Sentinel

Tagline: The agent firewall for tokenized RWA finance on Robinhood Chain.

One-liner:

Sapphire Sentinel gives autonomous agents a testnet/paper-only control plane for paid data and tokenized RWA workflows: every x402-style paid request is checked against human mandates, budgets, allow-lists, prompt-injection screens, secret-egress screens, replay protection, and privacy commitments before a Robinhood Chain testnet audit receipt is produced.

## Short Technical Background

Sapphire Sentinel is a testnet/paper-only control plane for autonomous agents in tokenized RWA workflows. It evaluates x402-style paid data requests against human mandates, allow-lists, budgets, prompt-injection checks, secret-egress checks, replay protection, and privacy commitments before producing Robinhood Chain testnet audit receipts or blocking the action. It does not enable real trading, real funds, Telegram sends, secret reads, live x402 settlement, or custody.

## Medium Technical Background

Sapphire Sentinel is a paper/testnet-only agent firewall for autonomous finance workflows on Robinhood Chain testnet. The demo lets an AI agent request paid private RWA intelligence through an x402-style HTTP flow, but Sentinel first checks the request against a human mandate: allowed domains, permitted actions, spend limits, expiry, quote binding, nonce replay protection, prompt-injection language, and secret-egress risk.

Approved or blocked outcomes are represented as hashed receipts and privacy commitments. The repo includes a Flask demo API, a protected report endpoint, mock and EIP-712 signed `PAYMENT-SIGNATURE` tooling, local Zama/Aztec proof-envelope artifacts, and paper/testnet-only Robinhood stock-token order drafts. `SapphireSentinelRegistry` is recorded as deployed and source-verified on Robinhood Chain testnet, where it anchors mandate and payment-evaluation receipts without custody or value-moving paths.

## Long Technical Background

Sapphire Sentinel is a paper/testnet-only prototype for controlling autonomous agents before they spend money, access paid intelligence, or draft tokenized RWA actions. Its core idea is simple: an agent may request a paid private RWA signal through an x402-style HTTP flow, but the request is evaluated against a human-approved mandate before any sensitive action is allowed. The policy engine checks domain allow-lists, action scope, spend limits, expiry, prompt-injection language, secret-egress risk, quote binding, and nonce replay protection. Safe requests produce a payment/report preview, privacy commitment, and Robinhood Chain testnet audit receipt; unsafe requests are blocked and still produce auditable receipt metadata without exposing raw prompts, private risk data, or secrets.

The repository includes a Flask demo API, an x402-compatible `402 Payment Required` model, a protected `/api/x402/sentinel-report` endpoint, mock and EIP-712 signed `PAYMENT-SIGNATURE` header tooling, and a non-custodial `SapphireSentinelRegistry` Solidity contract. Repo deployment metadata records the registry on Robinhood Chain testnet at `0x2EBB91F7B376cB821d90ac4A7d77B0d06b70B36F`, plus approved and blocked demo event hashes. The contract is an anchoring layer for mandates and payment evaluations, not a value-moving contract.

Privacy is framed as a sidecar and commitment system, not as private Robinhood Chain settlement. Oasis Sapphire is presented as the confidential policy target, while Zama fhEVM and Aztec are represented by local deterministic proof envelopes or blueprints that expose public commitments and redact private witnesses. Order outputs remain drafts only, with execution disabled. The safety boundary is no real trading, no real funds or custody, no Telegram sends, no secret reads, no live x402 facilitator settlement by default, and no claim of production compliance privacy.

## Form Field Drafts

Project description:

Sapphire Sentinel is the agent firewall for tokenized RWA finance on Robinhood Chain. It lets autonomous agents request paid data and draft tokenized-stock actions only inside human-approved mandates, spend limits, allow-lists, replay protection, privacy commitments, and auditable Robinhood Chain testnet receipts.

What code was produced during the Buildathon:

We built the Sapphire Sentinel demo app, policy engine, x402-style payment-gate model, EIP-712 signed payment-header tooling, privacy commitment/proof-envelope sidecars, red-team scenarios, dashboard, and the non-custodial `SapphireSentinelRegistry` contract used to anchor approved and blocked agent-payment receipts on Robinhood Chain testnet. The implementation includes Python/Flask APIs, Solidity contract code, local test coverage, deployment helpers, and judge-facing docs/scripts.

Sponsor/partner technology used:

Robinhood Chain testnet for public audit receipts and source-verified registry deployment; Arbitrum ecosystem tooling for the EVM/Orbit chain context; Base Sepolia-modeled x402 payment flow for local signed-header verification; Oasis Sapphire, Zama, and Aztec as privacy sidecar/commitment targets or local proof-envelope artifacts.

Safety and compliance boundary:

The demo is strictly testnet/paper-only. It does not submit live Robinhood orders, does not use real funds, does not custody assets, does not send Telegram messages, does not read secrets, does not perform live x402 facilitator settlement by default, and does not claim private Robinhood Chain payments or production compliance privacy.

Public repo:

`https://github.com/arigatoexpress/sapphire-sentinel`

Contract address:

`0x2EBB91F7B376cB821d90ac4A7d77B0d06b70B36F`

Demo URL:

Pending public deployment. Current local demo target is `http://127.0.0.1:8098`, which is not judge-accessible.

Demo video:

Pending final recording/upload.

## London Tech Week Contact Form Question

Use this for the required "Please type your question here" field:

Hello London Tech Week team,

We would like to enquire about participating in the London Tech Week Hackathon with Sapphire Sentinel, a testnet/paper-only agent firewall for tokenized RWA finance on Robinhood Chain.

Our project gives autonomous agents a bounded control plane before they can access paid intelligence or draft tokenized-stock actions. The demo evaluates x402-style paid data requests against human-approved mandates, domain allow-lists, spend limits, quote binding, nonce replay protection, prompt-injection checks, secret-egress checks, and privacy commitments. Approved or blocked outcomes are represented as auditable Robinhood Chain testnet receipts through a non-custodial `SapphireSentinelRegistry` contract.

The current build includes a Python/Flask demo API, Solidity registry contract, protected x402-style report endpoint, mock and EIP-712 signed payment-header tooling, local Zama/Aztec proof-envelope artifacts with private witnesses redacted, and paper/testnet-only Robinhood stock-token order drafts. The safety boundary is explicit: no real trading, no real funds or custody, no Telegram sends, no secret reads, no live x402 facilitator settlement by default, and no claim of private Robinhood Chain payments.

We believe this fits the hackathon's focus on real-world impact, AI, financial infrastructure, cybersecurity, and responsible innovation. Could you please advise whether Sapphire Sentinel is eligible for the London Tech Week Hackathon review process, and whether there is a formal participant application or invitation workflow we should complete?

Project repository: `https://github.com/arigatoexpress/sapphire-sentinel`

Thank you.

## Evidence Pointers

- `README.md`: project identity, safety defaults, demo flow, deployment metadata.
- `docs/submission.md`: HackQuest-facing copy, deployed contract, event hashes, checklist.
- `docs/architecture.md`: system architecture and safety boundary.
- `docs/privacy-claims.md`: public/private boundary and sidecar claims.
- `contracts/SapphireSentinelRegistry.sol`: non-custodial receipt/mandate registry.
- `src/sapphire_sentinel/sentinel.py`: policy engine and judge-facing state.
- `src/sapphire_sentinel/x402.py`: x402-style payment requirement and signature model.
- `scripts/sign_x402_payment.py`: local signed payment-header generator.
- `data/deployments.json`: repo-recorded deployment and receipt metadata.

## Before Any Real Submit

- Confirm the exact URL Ari intends to use if the partner's "official enquiry page" is not HackQuest.
- Log in with Ari's own account; do not create accounts or submit under the wrong identity.
- Fill personal/account fields manually or from Ari-approved values: full name, email, location, GitHub, optional LinkedIn/Twitter, team name, and team members.
- Provide only a public Arbitrum One payout wallet address, never a private key or seed phrase.
- Add a public demo URL before final judging submission; localhost is not sufficient.
- Add the final demo video URL once recorded.
- Re-run final checks from a clean environment before claiming "tests pass."
- Re-verify the Robinhood Chain explorer address, transaction hash, source verification, and anchored event hashes externally before final submission.
- Keep x402 wording precise: local/mock or EIP-712 header verification, not live facilitator settlement.
- Keep privacy wording precise: local Zama/Aztec artifacts and sidecar commitments, not live production privacy proofs.
- Do not claim MegaETH deployment unless the faucet/gas blocker has been resolved and verified.

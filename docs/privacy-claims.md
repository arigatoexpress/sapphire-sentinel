# Privacy Claims

Sapphire Sentinel uses privacy commitments honestly. Robinhood Chain remains a
public Arbitrum Orbit testnet. The project does not claim private Robinhood
payments, private Robinhood stock-token transfers, or production compliance.

## Public On Robinhood Chain

- Mandate ID.
- Controller and agent addresses.
- Maximum spend and spent amount in atomic units.
- Expiry time.
- Policy hash.
- Receipt hash.
- Resource hash.
- Result hash.
- Risk hash.
- Privacy commitment.
- Approval outcome.

## Private Or Off-Chain

- Exact portfolio weights.
- Raw risk score inputs.
- Prompt transcript and provider response body.
- Human policy thresholds.
- Identity links between user, wallet, and private intent evidence.
- Any secret material.

## Sidecar Roles

| Layer | Role | Status |
|---|---|---|
| Oasis Sapphire | Confidential policy and risk sidecar that can produce signed allow/deny commitments | Demo-ready commitment preview |
| Zama fhEVM | Encrypted budget and risk-score math with Solidity encrypted types | Local proof bundle plus mock contract, not native Robinhood support |
| Aztec | Private intent or balance evidence exported as a commitment | Noir private-intent blueprint plus local proof-output envelope |

## Local Proof Bundle

`GET /api/privacy/proofs` and `scripts/generate_privacy_proofs.py` export a
deterministic local proof bundle:

- Zama artifact: public policy/resource inputs, an encrypted-input commitment,
  a receipt-bound risk commitment, and redacted private risk witnesses.
- Aztec artifact: public policy/resource/result inputs, an exported private
  intent commitment, and redacted private note witnesses.

These outputs are deliberately local artifacts. They are suitable for judges to
inspect the intended public/private boundary, but they are not live Zama
ciphertexts or Aztec proofs.

## Demo Boundary

Default mode is `testnet_paper_only`.

- No live x402 settlement.
- No live Zama or Aztec proving by default.
- No mainnet funds.
- No real Robinhood account integration.
- No order submission.
- No Telegram sends.
- No secret reads.
- No custody or withdraw path in the contract.

## Correct Pitch

Say:

> Privacy-assisted agentic payment controls on Robinhood Chain testnet.

Do not say:

> Private Robinhood Chain payments.

Do not say:

> Production-ready compliance privacy.

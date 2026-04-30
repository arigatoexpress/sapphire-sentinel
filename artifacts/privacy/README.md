# Privacy Artifacts

These artifacts make the Zama and Aztec roadmap concrete without overstating
what is live in the default demo.

## Zama

`contracts/privacy/EncryptedRiskGateMock.sol` is a plain-Solidity local stand-in
for the future Zama FHEVM risk gate. It exposes the same public shape Sentinel
needs: an opaque encrypted-input commitment plus a public `riskCommitment` that
can be copied into `SapphireSentinelRegistry.recordPaymentEvaluation(...)`.

Next implementation step:

1. Inspect the shipped local proof envelope with `python3 scripts/generate_privacy_proofs.py`.
2. Port the interface to a Zama FHEVM contract using encrypted integer types.
3. Run local Hardhat mock encryption tests.
4. Deploy to Zama-on-Sepolia for real encrypted values.
5. Anchor the resulting risk commitment on Robinhood Chain and MegaETH.

## Aztec

`aztec_private_intent_note.nr` is a Noir blueprint for private mandate evidence.
It proves privately that a balance and risk score satisfy public thresholds,
then exports a commitment for the public receipt path.

`/api/privacy/proofs` now exposes the local proof-output envelope that the Noir
proof should eventually produce.

Boundary:

- Aztec is not EVM-compatible.
- This is private-intent evidence, not a Robinhood Chain privacy layer.
- The exported public commitment is what Sentinel anchors.

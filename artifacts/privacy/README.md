# Privacy Artifacts

These artifacts make the Zama and Aztec roadmap concrete without overstating
what is live in the default demo.

## Zama

`contracts/privacy/EncryptedRiskGateMock.sol` is a plain-Solidity local stand-in
for the future Zama FHEVM risk gate. It exposes the same public shape Sentinel
needs: an opaque encrypted-input commitment plus a public `riskCommitment` that
can be copied into `SapphireSentinelRegistry.recordPaymentEvaluation(...)`.

Next implementation step:

1. Port the interface to a Zama FHEVM contract using encrypted integer types.
2. Run local Hardhat mock encryption tests.
3. Deploy to Zama-on-Sepolia for real encrypted values.
4. Anchor the resulting risk commitment on Robinhood Chain and MegaETH.

## Aztec

`aztec_private_intent_note.nr` is a Noir blueprint for private mandate evidence.
It proves privately that a balance and risk score satisfy public thresholds,
then exports a commitment for the public receipt path.

Boundary:

- Aztec is not EVM-compatible.
- This is private-intent evidence, not a Robinhood Chain privacy layer.
- The exported public commitment is what Sentinel anchors.

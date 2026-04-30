# Architecture

Sapphire Sentinel is a buyer-side control plane for autonomous agents that need
to buy paid data or draft RWA actions.

```mermaid
flowchart LR
    Human["Human Operator"] --> Mandate["Agent Mandate"]
    Agent["AI Agent"] --> Quote["x402 Payment Quote"]
    Quote --> Sentinel["Sapphire Sentinel Policy Engine"]
    Mandate --> Sentinel
    Sentinel --> Safe{"Safe?"}
    Safe -->|"yes"| Payload["Payment Payload Preview"]
    Safe -->|"no"| Block["Blocked Audit Receipt"]
    Payload --> Draft["Robinhood Stock-Token Draft"]
    Sentinel --> Privacy["Privacy Sidecar Commitments"]
    Privacy --> Oasis["Oasis Sapphire"]
    Privacy --> Zama["Zama fhEVM"]
    Privacy --> Aztec["Aztec"]
    Sentinel --> Registry["SapphireSentinelRegistry"]
    Block --> Registry
    Registry --> Explorer["Robinhood Chain Testnet Explorer"]
```

## Runtime Surfaces

| Layer | What It Does |
|---|---|
| Flask demo | Judge-facing control surface and API |
| Policy engine | Checks domain, action, amount, budget, prompt-injection, secret-egress, nonce, and privacy commitments |
| x402 model | Simulates v2 payment quote and `PAYMENT-REQUIRED` header shape |
| Privacy module | Produces labeled Oasis Sapphire, Zama fhEVM, and Aztec commitments |
| Contract | Records mandates and payment evaluations on Robinhood Chain testnet |

## Deployment

`SapphireSentinelRegistry` is live and source-verified on Robinhood Chain
testnet.

- Address: `0x2EBB91F7B376cB821d90ac4A7d77B0d06b70B36F`
- Transaction: `0xc53ab8fc8cdab4ce7ef5f09fd56fc564756fd8d5e5b7c0396238878d6cc84975`
- Explorer: `https://explorer.testnet.chain.robinhood.com/address/0x2EBB91F7B376cB821d90ac4A7d77B0d06b70B36F`

## Safety Boundary

The default demo never settles live x402 payments, never submits Robinhood
orders, never sends Telegram messages, never reads secrets, and never uses real
funds. All action drafts are testnet or paper-only.

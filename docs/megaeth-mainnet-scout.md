# MegaETH Mainnet Scout

Sentinel's mainnet lane is intentionally non-spending. It is built to discover
apps, inspect public chain state, read public wallet balances, and produce
unsigned intent templates that can later be simulated on a fork.

## Sources

- MegaETH mainnet docs: `https://docs.megaeth.com/frontier`
- Wallet connection docs: `https://docs.megaeth.com/user-guide/connect`
- Rabbithole portal: `https://rabbithole.megaeth.com`
- Rabbithole chain stats: `https://rabbithole.megaeth.com/api/data/chain`
- Rabbithole featured apps: `https://rabbithole.megaeth.com/api/featured-apps`
- Rabbithole discover catalog: `https://rabbithole.megaeth.com/api/discover/list`

## Guardrails

- No private keys are required by the scout.
- No signing methods are called.
- No `eth_sendRawTransaction`, `eth_sendTransaction`, swaps, bridges, deposits,
  wagers, posts, or paid app actions are allowed.
- Public wallet reads may be run with `--address`; never pass a private key.

## Command

```bash
python3 scripts/scout_megaeth_mainnet.py --probe-apps
python3 scripts/scout_megaeth_mainnet.py --address 0xYourPublicAddress
```

The output is JSON and can be written to a local snapshot:

```bash
python3 scripts/scout_megaeth_mainnet.py --probe-apps --write data/megaeth_mainnet_snapshot.json
```

`data/megaeth_mainnet_snapshot.json` is an optional generated artifact. It
should only contain public metadata and public balances.

## App Lanes

- Kumbaya: quote and fork-simulate swap intents only.
- Cap and RockSolid: yield/risk research only.
- AGNT and Nectar AI: agent identity and skill-market discovery only.
- World Markets and Brix: RWA risk modeling and disclosure review only.
- Showdown and other games: latency demo and policy sandbox only; no wagering or
  deposits.

The dashboard surfaces this as `MegaETH Mainnet Scout`; the API is
`GET /api/megaeth/apps`.

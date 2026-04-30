#!/usr/bin/env python3
"""Deploy SapphireSentinelRegistry to Robinhood Chain testnet.

Private key lookup:
  1. $ROBINHOOD_DEPLOY_KEY
  2. ~/.config/sapphire-secrets/robinhood_deploy_key

Modes:
  --check    read-only RPC/key/balance preflight
  --dry-run  compile only, no deploy
  default    compile and broadcast deployment
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAIN_ID = 46630
RPC_URL = "https://rpc.testnet.chain.robinhood.com"
EXPLORER_URL = "https://explorer.testnet.chain.robinhood.com"
SECRETS_FILE = Path.home() / ".config" / "sapphire-secrets" / "robinhood_deploy_key"
DEPLOYMENTS_FILE = ROOT / "data" / "deployments.json"
CONTRACT_NAME = "SapphireSentinelRegistry"
CONTRACT_FILE = ROOT / "contracts" / f"{CONTRACT_NAME}.sol"
MIN_DEPLOY_BALANCE_ETH = 0.003

log = logging.getLogger("deploy_robinhood_chain")
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")


def load_private_key() -> str:
    key = os.environ.get("ROBINHOOD_DEPLOY_KEY", "").strip()
    if key:
        return key
    if SECRETS_FILE.exists():
        key = SECRETS_FILE.read_text(encoding="utf-8").strip()
        if key:
            return key
    raise RuntimeError(
        f"No deploy key found. Set ROBINHOOD_DEPLOY_KEY or create {SECRETS_FILE}."
    )


def compile_contract() -> dict:
    try:
        import solcx  # type: ignore[import]
    except ImportError:
        log.error("py-solc-x not installed. Run: pip install -e '.[deploy]'")
        sys.exit(1)

    if not CONTRACT_FILE.exists():
        raise FileNotFoundError(CONTRACT_FILE)

    solcx.install_solc("0.8.20", show_progress=False)
    solcx.set_solc_version("0.8.20")
    result = solcx.compile_source(
        CONTRACT_FILE.read_text(encoding="utf-8"),
        output_values=["abi", "bin"],
        solc_version="0.8.20",
    )
    key = next(k for k in result if k.endswith(f":{CONTRACT_NAME}"))
    return {"abi": result[key]["abi"], "bytecode": result[key]["bin"]}


def preflight() -> int:
    try:
        from eth_account import Account  # type: ignore[import]
        from web3 import Web3  # type: ignore[import]
    except ImportError:
        log.error("[FAIL] web3 / eth-account not installed. Run: pip install -e '.[deploy]'")
        return 1

    if not CONTRACT_FILE.exists():
        log.error("[FAIL] contract missing: %s", CONTRACT_FILE)
        return 1
    log.info("[ OK ] contract source present: %s", CONTRACT_FILE)

    w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 10}))
    if not w3.is_connected():
        log.error("[FAIL] RPC unreachable: %s", RPC_URL)
        return 1
    chain_id = w3.eth.chain_id
    if chain_id != CHAIN_ID:
        log.error("[FAIL] chain_id mismatch: got %s expected %s", chain_id, CHAIN_ID)
        return 1
    log.info("[ OK ] RPC %s chain_id=%s block=%s", RPC_URL, chain_id, w3.eth.block_number)

    try:
        account = Account.from_key(load_private_key())
    except Exception as exc:
        log.error("[FAIL] deploy key unavailable or invalid: %s", exc)
        return 1

    balance_eth = float(w3.from_wei(w3.eth.get_balance(account.address), "ether"))
    if balance_eth < MIN_DEPLOY_BALANCE_ETH:
        log.error(
            "[FAIL] deployer balance %.6f ETH < %.4f ETH minimum",
            balance_eth,
            MIN_DEPLOY_BALANCE_ETH,
        )
        return 1
    log.info("[ OK ] deployer %s balance %.6f ETH", account.address, balance_eth)
    return 0


def deploy(compiled: dict) -> str:
    from eth_account import Account  # type: ignore[import]
    from web3 import Web3  # type: ignore[import]

    w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 10}))
    account = Account.from_key(load_private_key())
    contract = w3.eth.contract(abi=compiled["abi"], bytecode=compiled["bytecode"])
    tx = contract.constructor().build_transaction(
        {
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gasPrice": w3.eth.gas_price,
            "chainId": CHAIN_ID,
        }
    )
    tx["gas"] = w3.eth.estimate_gas(tx)
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    tx_hash_hex = tx_hash.hex()
    if not tx_hash_hex.startswith("0x"):
        tx_hash_hex = f"0x{tx_hash_hex}"
    log.info("tx sent: %s", tx_hash_hex)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    if receipt["status"] != 1:
        raise RuntimeError("deployment failed")
    address = receipt["contractAddress"]
    DEPLOYMENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    DEPLOYMENTS_FILE.write_text(
        json.dumps(
            {
                "robinhood_testnet": {
                    "chain_id": CHAIN_ID,
                    "rpc": RPC_URL,
                    "deployed_at": int(time.time()),
                    "contracts": {
                        CONTRACT_NAME: {
                            "address": address,
                            "tx_hash": tx_hash_hex,
                            "explorer": f"{EXPLORER_URL}/address/{address}",
                            "tx_explorer": f"{EXPLORER_URL}/tx/{tx_hash_hex}",
                        }
                    },
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return address


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Read-only preflight")
    parser.add_argument("--dry-run", action="store_true", help="Compile only; do not deploy")
    args = parser.parse_args()

    if args.check:
        return preflight()

    compiled = compile_contract()
    log.info("compiled %s with %d ABI entries", CONTRACT_NAME, len(compiled["abi"]))
    if args.dry_run:
        log.info("dry-run mode; bytecode %d bytes; skipping deployment", len(compiled["bytecode"]) // 2)
        return 0
    address = deploy(compiled)
    log.info("deployed %s to %s", CONTRACT_NAME, address)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

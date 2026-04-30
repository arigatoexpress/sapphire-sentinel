#!/usr/bin/env python3
"""Deploy SapphireSentinelRegistry to a configured testnet.

Default mode is intentionally conservative:
  --dry-run compiles only.
  --check performs read-only RPC/key/balance checks.
  deploy broadcasts only when neither flag is set.

Keys are looked up without printing them:
  1. $SENTINEL_DEPLOY_KEY
  2. $<NETWORK_ID>_DEPLOY_KEY, for example $MEGAETH_TESTNET_DEPLOY_KEY
  3. $ROBINHOOD_DEPLOY_KEY for robinhood_testnet compatibility
  4. ~/.config/sapphire-secrets/<network_id>_deploy_key
  5. ~/.config/sapphire-secrets/robinhood_deploy_key for robinhood_testnet
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sapphire_sentinel.networks import NETWORKS, NetworkProfile, network_by_id  # noqa: E402

CONTRACT_NAME = "SapphireSentinelRegistry"
CONTRACT_FILE = ROOT / "contracts" / f"{CONTRACT_NAME}.sol"
DEPLOYMENTS_FILE = ROOT / "data" / "deployments.json"
MIN_DEPLOY_BALANCE_ETH = 0.003

log = logging.getLogger("deploy_registry")
logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")


def main() -> int:
    deployable = sorted(n.id for n in NETWORKS if n.chain_id and n.rpc)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--network", default="robinhood_testnet", choices=deployable)
    parser.add_argument("--check", action="store_true", help="Read-only RPC/key/balance preflight")
    parser.add_argument("--dry-run", action="store_true", help="Compile only; do not deploy")
    args = parser.parse_args()

    network = network_by_id(args.network)
    if args.check:
        return preflight(network)

    compiled = compile_contract()
    log.info("compiled %s with %d ABI entries", CONTRACT_NAME, len(compiled["abi"]))
    if args.dry_run:
        log.info(
            "dry-run mode for %s; bytecode %d bytes; skipping deployment",
            network.id,
            len(compiled["bytecode"]) // 2,
        )
        return 0
    address = deploy(network, compiled)
    log.info("deployed %s to %s on %s", CONTRACT_NAME, address, network.name)
    return 0


def compile_contract() -> dict[str, Any]:
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


def preflight(network: NetworkProfile) -> int:
    try:
        from eth_account import Account  # type: ignore[import]
        from web3 import Web3  # type: ignore[import]
    except ImportError:
        log.error("[FAIL] web3 / eth-account not installed. Run: pip install -e '.[deploy]'")
        return 1

    if not network.rpc or not network.chain_id:
        log.error("[FAIL] network is not deployable: %s", network.id)
        return 1

    w3 = Web3(Web3.HTTPProvider(network.rpc, request_kwargs={"timeout": 10}))
    if not w3.is_connected():
        log.error("[FAIL] RPC unreachable: %s", network.rpc)
        return 1
    chain_id = w3.eth.chain_id
    if chain_id != network.chain_id:
        log.error("[FAIL] chain_id mismatch: got %s expected %s", chain_id, network.chain_id)
        return 1
    log.info("[ OK ] RPC %s chain_id=%s block=%s", network.rpc, chain_id, w3.eth.block_number)

    try:
        account = Account.from_key(load_private_key(network.id))
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


def deploy(network: NetworkProfile, compiled: dict[str, Any]) -> str:
    from eth_account import Account  # type: ignore[import]
    from web3 import Web3  # type: ignore[import]

    if not network.rpc or not network.chain_id:
        raise RuntimeError(f"network is not deployable: {network.id}")

    w3 = Web3(Web3.HTTPProvider(network.rpc, request_kwargs={"timeout": 10}))
    if w3.eth.chain_id != network.chain_id:
        raise RuntimeError(f"unexpected chain id: {w3.eth.chain_id}")

    account = Account.from_key(load_private_key(network.id))
    contract = w3.eth.contract(abi=compiled["abi"], bytecode=compiled["bytecode"])
    tx = contract.constructor().build_transaction(
        {
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gasPrice": w3.eth.gas_price,
            "chainId": network.chain_id,
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
    write_deployment(network, address, tx_hash_hex)
    return address


def load_private_key(network_id: str) -> str:
    env_names = ["SENTINEL_DEPLOY_KEY", f"{network_id.upper()}_DEPLOY_KEY"]
    if network_id == "robinhood_testnet":
        env_names.append("ROBINHOOD_DEPLOY_KEY")
    for name in env_names:
        key = os.environ.get(name, "").strip()
        if key:
            return key

    candidates = [Path.home() / ".config" / "sapphire-secrets" / f"{network_id}_deploy_key"]
    if network_id == "robinhood_testnet":
        candidates.append(Path.home() / ".config" / "sapphire-secrets" / "robinhood_deploy_key")
    for path in candidates:
        if path.exists():
            key = path.read_text(encoding="utf-8").strip()
            if key:
                return key
    raise RuntimeError(f"No deploy key found for {network_id}.")


def write_deployment(network: NetworkProfile, address: str, tx_hash: str) -> None:
    deployments = read_deployments()
    chain = deployments.setdefault(
        network.id,
        {
            "chain_id": network.chain_id,
            "rpc": network.rpc,
            "contracts": {},
        },
    )
    chain["chain_id"] = network.chain_id
    chain["rpc"] = network.rpc
    chain["deployed_at"] = int(time.time())
    chain.setdefault("contracts", {})[CONTRACT_NAME] = {
        "address": address,
        "tx_hash": tx_hash,
        "explorer": f"{network.explorer}/address/{address}" if network.explorer else None,
        "tx_explorer": f"{network.explorer}/tx/{tx_hash}" if network.explorer else None,
        "source_verified": False,
    }
    DEPLOYMENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    DEPLOYMENTS_FILE.write_text(json.dumps(deployments, indent=2) + "\n", encoding="utf-8")


def read_deployments() -> dict[str, Any]:
    if not DEPLOYMENTS_FILE.exists():
        return {}
    return json.loads(DEPLOYMENTS_FILE.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())

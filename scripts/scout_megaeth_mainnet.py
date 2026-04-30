#!/usr/bin/env python3
"""Read-only MegaETH mainnet app and wallet scout.

This script never signs or submits transactions. It only calls public HTTP
endpoints, JSON-RPC read methods, and ERC-20 `balanceOf` via `eth_call`.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sapphire_sentinel.megaeth_apps import (  # noqa: E402
    MEGAETH_MAINNET_APPS,
    MEGAETH_TOKENS,
    RABBITHOLE_CHAIN_STATS,
    RABBITHOLE_DISCOVER_LIST,
    RABBITHOLE_FEATURED_APPS,
    stable_json,
    summarize_featured_config,
    summarize_live_catalog,
)
from sapphire_sentinel.networks import network_by_id  # noqa: E402

READ_ONLY_RPC_METHODS = {
    "eth_blockNumber",
    "eth_call",
    "eth_chainId",
    "eth_gasPrice",
    "eth_getBalance",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--address", help="Optional public wallet address to inspect.")
    parser.add_argument("--write", type=Path, help="Optional JSON snapshot path.")
    parser.add_argument("--probe-apps", action="store_true", help="Probe curated app URLs.")
    parser.add_argument("--app-timeout", type=float, default=5.0)
    parser.add_argument("--limit", type=int, default=30, help="Number of discover apps to keep.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    network = network_by_id("megaeth_mainnet")
    rpc = network.rpc
    if not rpc:
        raise SystemExit("megaeth_mainnet RPC missing")

    report: dict[str, Any] = {
        "generated_at": int(time.time()),
        "mode": "read_only_no_signing_no_swaps",
        "network": network.to_dict(),
        "rpc": scout_rpc(rpc),
        "rabbithole": scout_rabbithole(),
        "curated_apps": [app.to_dict() for app in MEGAETH_MAINNET_APPS],
        "guardrails": {
            "signing_enabled": False,
            "send_transactions_enabled": False,
            "swap_enabled": False,
            "bridge_enabled": False,
            "deposit_enabled": False,
        },
    }

    if args.address:
        report["wallet"] = scout_wallet(rpc, args.address)

    if args.probe_apps:
        report["app_probes"] = probe_apps(args.app_timeout)

    discover_apps = report["rabbithole"].get("discover", {}).get("apps")
    if isinstance(discover_apps, list):
        report["rabbithole"]["discover"]["apps"] = discover_apps[: args.limit]

    rendered = stable_json(report)
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


def scout_rpc(rpc: str) -> dict[str, Any]:
    chain_id = int(rpc_call(rpc, "eth_chainId", []), 16)
    block_number = int(rpc_call(rpc, "eth_blockNumber", []), 16)
    gas_price_wei = int(rpc_call(rpc, "eth_gasPrice", []), 16)
    return {
        "ok": chain_id == 4326,
        "chain_id": chain_id,
        "block_number": block_number,
        "gas_price_wei": gas_price_wei,
        "gas_price_gwei": str((Decimal(gas_price_wei) / Decimal("1000000000")).normalize()),
    }


def scout_wallet(rpc: str, address: str) -> dict[str, Any]:
    normalized = normalize_address(address)
    native_wei = int(rpc_call(rpc, "eth_getBalance", [normalized, "latest"]), 16)
    balances = {
        "ETH": {
            "address": "native",
            "raw": str(native_wei),
            "formatted": format_units(native_wei, 18),
        }
    }
    for symbol, token_address in MEGAETH_TOKENS.items():
        if symbol == "ETH" or token_address == "native":
            continue
        raw = erc20_balance_of(rpc, token_address, normalized)
        balances[symbol] = {
            "address": token_address,
            "raw": str(raw),
            "formatted": format_units(raw, 18),
        }
    return {
        "address": normalized,
        "balances": balances,
        "note": "Public balances only; no private key was read.",
    }


def scout_rabbithole() -> dict[str, Any]:
    chain_stats = fetch_json(RABBITHOLE_CHAIN_STATS)
    featured = summarize_featured_config(fetch_json(RABBITHOLE_FEATURED_APPS))
    discover = summarize_live_catalog(fetch_json(RABBITHOLE_DISCOVER_LIST))
    return {
        "chain_stats": chain_stats.get("data", chain_stats),
        "featured": featured,
        "discover": discover,
        "sources": {
            "chain_stats": RABBITHOLE_CHAIN_STATS,
            "featured": RABBITHOLE_FEATURED_APPS,
            "discover": RABBITHOLE_DISCOVER_LIST,
        },
    }


def probe_apps(timeout: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for app in MEGAETH_MAINNET_APPS:
        url = app.url
        if not url.startswith("http") or url in seen:
            continue
        seen.add(url)
        rows.append(probe_url(app.name, url, timeout))
    return rows


def probe_url(name: str, url: str, timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "sapphire-sentinel/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return {
                "name": name,
                "url": url,
                "ok": 200 <= response.status < 400,
                "status": response.status,
                "content_type": response.headers.get("content-type"),
            }
    except urllib.error.HTTPError as exc:
        return {"name": name, "url": url, "ok": False, "status": exc.code, "error": exc.reason}
    except Exception as exc:
        return {"name": name, "url": url, "ok": False, "error": str(exc)}


def erc20_balance_of(rpc: str, token: str, owner: str) -> int:
    selector = "70a08231"
    encoded_owner = owner.lower().removeprefix("0x").rjust(64, "0")
    result = rpc_call(
        rpc,
        "eth_call",
        [{"to": normalize_address(token), "data": "0x" + selector + encoded_owner}, "latest"],
    )
    if result == "0x":
        return 0
    return int(result, 16)


def rpc_call(rpc: str, method: str, params: list[Any]) -> Any:
    if method not in READ_ONLY_RPC_METHODS:
        raise RuntimeError(f"refusing non-read RPC method: {method}")
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    request = urllib.request.Request(
        rpc,
        data=json.dumps(payload).encode(),
        headers={"content-type": "application/json", "user-agent": "sapphire-sentinel/0.1"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        body = json.loads(response.read().decode())
    if "error" in body:
        raise RuntimeError(body["error"])
    return body["result"]


def fetch_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"user-agent": "sapphire-sentinel/0.1"})
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode())


def normalize_address(address: str) -> str:
    text = address.strip()
    if len(text) != 42 or not text.startswith("0x"):
        raise ValueError("address must be a 20-byte 0x-prefixed address")
    int(text[2:], 16)
    return text


def format_units(raw: int, decimals: int) -> str:
    value = Decimal(raw) / (Decimal(10) ** decimals)
    return str(value.normalize())


if __name__ == "__main__":
    raise SystemExit(main())

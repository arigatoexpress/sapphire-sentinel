#!/usr/bin/env python3
"""Read-only JSON-RPC probe for configured EVM networks."""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sapphire_sentinel.networks import NETWORKS  # noqa: E402


def main() -> int:
    rows = []
    ok = True
    for network in NETWORKS:
        if not network.rpc or not network.chain_id:
            continue
        result = _rpc(network.rpc, "eth_chainId")
        got = int(result, 16) if isinstance(result, str) and result.startswith("0x") else None
        passed = got == network.chain_id
        ok = ok and passed
        rows.append(
            {
                "id": network.id,
                "name": network.name,
                "expected_chain_id": network.chain_id,
                "observed_chain_id": got,
                "ok": passed,
                "rpc": network.rpc,
            }
        )
    print(json.dumps({"ok": ok, "networks": rows}, indent=2))
    return 0 if ok else 1


def _rpc(url: str, method: str) -> Any:
    req = urllib.request.Request(
        url,
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": []}).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "sapphire-sentinel/0.1"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        body = json.loads(response.read().decode("utf-8"))
    if "error" in body:
        raise RuntimeError(body["error"])
    return body["result"]


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Anchor demo mandate and receipt events on Robinhood Chain testnet.

This script is intentionally testnet-only. It never moves tokens, never submits
orders, and only calls the non-custodial SapphireSentinelRegistry.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from deploy_robinhood_chain import (  # noqa: E402
    CHAIN_ID,
    CONTRACT_NAME,
    DEPLOYMENTS_FILE,
    EXPLORER_URL,
    RPC_URL,
    compile_contract,
    load_private_key,
)

from sapphire_sentinel.sentinel import (  # noqa: E402
    USDC_DECIMALS,
    blocked_attempt,
    default_attempt,
    default_mandate,
    evaluate_attempt,
    mandate_key,
)

ZERO_BYTES32 = "0x" + "00" * 32
ZERO_ADDRESS = "0x" + "00" * 20


def main() -> int:
    from eth_account import Account  # type: ignore[import]
    from web3 import Web3  # type: ignore[import]

    deployments = _load_deployments()
    contract_meta = (
        deployments.get("robinhood_testnet", {})
        .get("contracts", {})
        .get(CONTRACT_NAME, {})
    )
    address = contract_meta.get("address")
    if not address:
        raise RuntimeError("Deployment address missing. Run deploy_robinhood_chain.py first.")

    w3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={"timeout": 10}))
    if not w3.is_connected():
        raise RuntimeError(f"RPC unreachable: {RPC_URL}")
    if w3.eth.chain_id != CHAIN_ID:
        raise RuntimeError(f"Unexpected chain id: {w3.eth.chain_id}")

    account = Account.from_key(load_private_key())
    compiled = compile_contract()
    contract = w3.eth.contract(address=w3.to_checksum_address(address), abi=compiled["abi"])
    if contract.functions.operator().call().lower() != account.address.lower():
        raise RuntimeError("Burner account is not the registry operator")

    mandate = default_mandate()
    approved = evaluate_attempt(default_attempt(), mandate)
    blocked = evaluate_attempt(blocked_attempt(), mandate)
    mkey = mandate_key(mandate)

    demo_events = contract_meta.setdefault("demo_events", {})
    demo_events["mandate_id"] = mandate.mandate_id
    demo_events.pop("mandate_key", None)
    demo_events["mandate_hash"] = mkey
    demo_events["controller"] = mandate.controller
    demo_events["agent"] = mandate.agent

    if _mandate_unknown(contract, mkey):
        tx_hash = _send(
            w3,
            account,
            contract.functions.registerMandate(
                _b32(mkey),
                w3.to_checksum_address(mandate.controller),
                w3.to_checksum_address(mandate.agent),
                _atomic(mandate.max_spend_usdc),
                _unix(mandate.expires_at),
                _b32(mandate.policy_hash()),
            ),
        )
        demo_events["register_mandate"] = _tx_record(tx_hash)
        print(f"registered mandate: {tx_hash}")
    else:
        print("mandate already registered; skipping")

    seed = _seed_receipt(mandate, approved)
    if _receipt_unknown(contract, seed["receipt_id"]):
        tx_hash = _record(contract, w3, account, seed, approved=True)
        demo_events["seed_prior_spend"] = _tx_record(tx_hash, receipt_id=seed["receipt_id"])
        print(f"seeded prior spend: {tx_hash}")
    else:
        print("seed prior spend already recorded; skipping")
    demo_events.setdefault("seed_prior_spend", {})["receipt_id"] = seed["receipt_id"]

    if _receipt_unknown(contract, approved.receipt_id):
        tx_hash = _record(
            contract,
            w3,
            account,
            {
                "receipt_id": approved.receipt_id,
                "mandate_key": mkey,
                "payer": mandate.agent,
                "amount_atomic": int(approved.payment_requirements.amount),
                "resource_hash": approved.resource_hash,
                "result_hash": approved.result_hash,
                "risk_hash": approved.risk_hash,
                "privacy_commitment": approved.privacy_commitment,
                "decision_nonce": approved.decision_nonce,
            },
            approved=True,
        )
        demo_events["approved_receipt"] = _tx_record(tx_hash, receipt_id=approved.receipt_id)
        print(f"recorded approved receipt: {tx_hash}")
    else:
        print("approved receipt already recorded; skipping")
    demo_events.setdefault("approved_receipt", {})["receipt_id"] = approved.receipt_id

    if _receipt_unknown(contract, blocked.receipt_id):
        tx_hash = _record(
            contract,
            w3,
            account,
            {
                "receipt_id": blocked.receipt_id,
                "mandate_key": mkey,
                "payer": mandate.agent,
                "amount_atomic": int(blocked.payment_requirements.amount),
                "resource_hash": blocked.resource_hash,
                "result_hash": blocked.result_hash,
                "risk_hash": blocked.risk_hash,
                "privacy_commitment": blocked.privacy_commitment,
                "decision_nonce": blocked.decision_nonce,
            },
            approved=False,
        )
        demo_events["blocked_receipt"] = _tx_record(tx_hash, receipt_id=blocked.receipt_id)
        print(f"recorded blocked receipt: {tx_hash}")
    else:
        print("blocked receipt already recorded; skipping")
    demo_events.setdefault("blocked_receipt", {})["receipt_id"] = blocked.receipt_id

    demo_events["updated_at"] = int(time.time())
    remaining = contract.functions.remainingSpend(_b32(mkey)).call()
    demo_events["remaining_spend_atomic"] = int(remaining)
    demo_events["remaining_spend_usdc"] = str(Decimal(remaining) / USDC_DECIMALS)
    DEPLOYMENTS_FILE.write_text(json.dumps(deployments, indent=2) + "\n", encoding="utf-8")
    print(f"remaining atomic spend: {remaining}")
    return 0


def _send(w3: Any, account: Any, fn: Any) -> str:
    tx = fn.build_transaction(
        {
            "from": account.address,
            "nonce": w3.eth.get_transaction_count(account.address),
            "gasPrice": w3.eth.gas_price,
            "chainId": CHAIN_ID,
        }
    )
    tx["gas"] = w3.eth.estimate_gas(tx)
    signed = account.sign_transaction(tx)
    raw_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    tx_hash = raw_hash.hex()
    if not tx_hash.startswith("0x"):
        tx_hash = f"0x{tx_hash}"
    receipt = w3.eth.wait_for_transaction_receipt(raw_hash, timeout=120)
    if receipt["status"] != 1:
        raise RuntimeError(f"transaction failed: {tx_hash}")
    return tx_hash


def _record(contract: Any, w3: Any, account: Any, receipt: dict[str, Any], *, approved: bool) -> str:
    return _send(
        w3,
        account,
        contract.functions.recordPaymentEvaluation(
            _b32(receipt["receipt_id"]),
            _b32(receipt["mandate_key"]),
            w3.to_checksum_address(receipt["payer"]),
            int(receipt["amount_atomic"]),
            _b32(receipt["resource_hash"]),
            _b32(receipt["result_hash"]),
            _b32(receipt["risk_hash"]),
            _b32(receipt["privacy_commitment"]),
            int(receipt["decision_nonce"]),
            approved,
        ),
    )


def _seed_receipt(mandate: Any, approved: Any) -> dict[str, Any]:
    seed_hash = _sha(
        {
            "kind": "sentinel-demo-prior-spend",
            "mandate_key": mandate_key(mandate),
            "amount_atomic": _atomic(mandate.spent_usdc),
        }
    )
    return {
        "receipt_id": seed_hash,
        "mandate_key": mandate_key(mandate),
        "payer": mandate.agent,
        "amount_atomic": _atomic(mandate.spent_usdc),
        "resource_hash": _sha({"resource": "sentinel://demo/prior-spend"}),
        "result_hash": _sha({"result": "prior spend seeded for demo budget continuity"}),
        "risk_hash": _sha({"risk": "none", "approved": True}),
        "privacy_commitment": approved.privacy_commitment,
        "decision_nonce": int(seed_hash[2:18], 16),
    }


def _mandate_unknown(contract: Any, mkey: str) -> bool:
    return contract.functions.mandates(_b32(mkey)).call()[0].lower() == ZERO_ADDRESS


def _receipt_unknown(contract: Any, receipt_id: str) -> bool:
    return "0x" + contract.functions.receipts(_b32(receipt_id)).call()[0].hex() == ZERO_BYTES32


def _load_deployments() -> dict[str, Any]:
    if not DEPLOYMENTS_FILE.exists():
        return {}
    return json.loads(DEPLOYMENTS_FILE.read_text(encoding="utf-8"))


def _tx_record(tx_hash: str, *, receipt_id: str | None = None) -> dict[str, str]:
    record = {
        "tx_hash": tx_hash,
        "explorer": f"{EXPLORER_URL}/tx/{tx_hash}",
    }
    if receipt_id:
        record["receipt_id"] = receipt_id
    return record


def _b32(value: str) -> bytes:
    raw = bytes.fromhex(value.removeprefix("0x"))
    if len(raw) != 32:
        raise ValueError(f"expected bytes32 hex: {value}")
    return raw


def _atomic(value: Decimal) -> int:
    return int((value * USDC_DECIMALS).quantize(Decimal("1")))


def _unix(value: datetime) -> int:
    return int(value.timestamp())


def _sha(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    return "0x" + hashlib.sha256(raw).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())

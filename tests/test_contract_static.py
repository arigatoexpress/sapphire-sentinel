from __future__ import annotations

import re
from pathlib import Path

CONTRACT = Path(__file__).resolve().parents[1] / "contracts" / "SapphireSentinelRegistry.sol"


def test_contract_is_non_custodial():
    src = CONTRACT.read_text(encoding="utf-8")

    assert "pragma solidity ^0.8.20;" in src
    assert "contract SapphireSentinelRegistry" in src
    assert "function recordPaymentEvaluation(" in src
    assert "function withdraw" not in src
    assert ".transfer(" not in src
    assert ".call{" not in src


def test_contract_enforces_active_mandate_and_budget():
    src = CONTRACT.read_text(encoding="utf-8")
    record_fn = _extract_function(src, "recordPaymentEvaluation")

    assert 'require(!mandate.revoked, "Mandate revoked")' in record_fn
    assert 'require(block.timestamp <= mandate.expiresAt, "Mandate expired")' in record_fn
    assert "mandate.spentAtomic + amountAtomic <= mandate.maxSpendAtomic" in record_fn
    assert "mandate.spentAtomic += amountAtomic;" in record_fn
    assert 'require(!usedDecisionNonces[mandateId][decisionNonce], "Nonce used")' in record_fn
    assert "usedDecisionNonces[mandateId][decisionNonce] = true;" in record_fn
    assert "mandate.evaluationCount += 1;" in record_fn


def test_contract_records_privacy_commitment():
    src = CONTRACT.read_text(encoding="utf-8")
    record_fn = _extract_function(src, "recordPaymentEvaluation")

    assert "bytes32 privacyCommitment;" in src
    assert "uint64 decisionNonce;" in src
    assert 'require(privacyCommitment != bytes32(0), "Zero privacy")' in record_fn
    assert "privacyCommitment: privacyCommitment" in record_fn


def test_contract_has_two_step_operator_transfer():
    src = CONTRACT.read_text(encoding="utf-8")

    assert re.search(r"address\s+public\s+pendingOperator\s*;", src)
    transfer_fn = _extract_function(src, "transferOperator")
    accept_fn = _extract_function(src, "acceptOperator")
    assert "pendingOperator = newOperator;" in transfer_fn
    assert "operator = newOperator;" not in transfer_fn
    assert 'require(msg.sender == pendingOperator, "Not pending operator")' in accept_fn
    assert "operator = pendingOperator;" in accept_fn
    assert "pendingOperator = address(0);" in accept_fn


def _extract_function(src: str, name: str) -> str:
    pattern = re.compile(rf"function\s+{re.escape(name)}\b")
    match = pattern.search(src)
    assert match, f"function not found: {name}"
    i = src.index("{", match.end())
    depth = 1
    j = i + 1
    while j < len(src) and depth > 0:
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
        j += 1
    assert depth == 0, f"unbalanced braces while parsing {name}"
    return src[match.start() : j]

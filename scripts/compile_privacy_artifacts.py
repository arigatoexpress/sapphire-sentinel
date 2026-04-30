#!/usr/bin/env python3
"""Compile or sanity-check local privacy artifacts."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZAMA_MOCK = ROOT / "contracts" / "privacy" / "EncryptedRiskGateMock.sol"
AZTEC_BLUEPRINT = ROOT / "artifacts" / "privacy" / "aztec_private_intent_note.nr"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-solc", action="store_true", help="Skip Solidity compilation.")
    args = parser.parse_args()

    if not args.no_solc:
        compiled = compile_zama_mock()
        print(
            "zama_mock "
            f"abi_entries={len(compiled['abi'])} "
            f"bytecode_bytes={len(compiled['bytecode']) // 2}"
        )

    noir = AZTEC_BLUEPRINT.read_text(encoding="utf-8")
    required = (
        "fn main(",
        "private_balance_atomic",
        "private_risk_score_bps",
        "public_policy_hash",
        "public_resource_hash",
        "pedersen_hash",
    )
    missing = [token for token in required if token not in noir]
    if missing:
        print(f"aztec_blueprint missing={','.join(missing)}", file=sys.stderr)
        return 1
    print(f"aztec_blueprint ok path={AZTEC_BLUEPRINT.relative_to(ROOT)}")
    return 0


def compile_zama_mock() -> dict[str, str]:
    try:
        import solcx  # type: ignore[import]
    except ImportError:
        print("py-solc-x not installed. Run with: uv run --with py-solc-x", file=sys.stderr)
        raise SystemExit(1) from None

    solcx.install_solc("0.8.20", show_progress=False)
    solcx.set_solc_version("0.8.20")
    result = solcx.compile_source(
        ZAMA_MOCK.read_text(encoding="utf-8"),
        output_values=["abi", "bin"],
        solc_version="0.8.20",
    )
    key = next(k for k in result if k.endswith(":EncryptedRiskGateMock"))
    return {"abi": result[key]["abi"], "bytecode": result[key]["bin"]}


if __name__ == "__main__":
    raise SystemExit(main())

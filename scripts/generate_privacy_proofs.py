#!/usr/bin/env python3
"""Print the local Zama/Aztec privacy proof bundle."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sapphire_sentinel.sentinel import build_demo_state  # noqa: E402


def main() -> int:
    state = build_demo_state()
    print(json.dumps(state["privacy_proofs"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

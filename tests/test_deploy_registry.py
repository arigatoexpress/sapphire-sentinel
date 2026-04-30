from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "deploy_registry.py"


def _load_deploy_registry():
    spec = importlib.util.spec_from_file_location("deploy_registry", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_deploy_key_alias_reuses_robinhood_env_without_default_fallback(monkeypatch, tmp_path):
    module = _load_deploy_registry()
    key = "0x" + "11" * 32
    monkeypatch.setattr(module.Path, "home", lambda: tmp_path)
    monkeypatch.setenv("ROBINHOOD_DEPLOY_KEY", key)
    monkeypatch.delenv("SENTINEL_DEPLOY_KEY", raising=False)
    monkeypatch.delenv("MEGAETH_TESTNET_DEPLOY_KEY", raising=False)

    with pytest.raises(RuntimeError, match="No deploy key found for megaeth_testnet"):
        module.load_private_key("megaeth_testnet")

    assert module.load_private_key("megaeth_testnet", key_alias="robinhood_testnet") == key


def test_deploy_key_alias_error_names_alias(monkeypatch, tmp_path):
    module = _load_deploy_registry()
    monkeypatch.setattr(module.Path, "home", lambda: tmp_path)
    monkeypatch.delenv("SENTINEL_DEPLOY_KEY", raising=False)
    monkeypatch.delenv("ROBINHOOD_DEPLOY_KEY", raising=False)

    with pytest.raises(RuntimeError, match="via alias robinhood_testnet"):
        module.load_private_key("megaeth_testnet", key_alias="robinhood_testnet")


def test_deployable_networks_exclude_megaeth_mainnet():
    module = _load_deploy_registry()
    deployable = sorted(n.id for n in module.NETWORKS if n.deploy_enabled and n.chain_id and n.rpc)

    assert "megaeth_testnet" in deployable
    assert "megaeth_mainnet" not in deployable

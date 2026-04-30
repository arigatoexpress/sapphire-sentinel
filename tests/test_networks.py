from __future__ import annotations

from sapphire_sentinel.networks import (
    NETWORKS,
    build_integration_roadmap,
    build_network_matrix,
    network_by_id,
)


def test_network_registry_has_core_hackathon_rails():
    matrix = {item["id"]: item for item in build_network_matrix()}

    assert matrix["robinhood_testnet"]["chain_id"] == 46630
    assert matrix["robinhood_testnet"]["caip2"] == "eip155:46630"
    assert matrix["base_sepolia"]["caip2"] == "eip155:84532"
    assert matrix["megaeth_testnet"]["chain_id"] == 6343
    assert matrix["megaeth_mainnet"]["chain_id"] == 4326
    assert matrix["megaeth_mainnet"]["deploy_enabled"] is False
    assert matrix["megaeth_mainnet"]["metadata"]["MEGA"] == "0x28B7E77f82B25B95953825F1E3eA0E36c1c29861"
    assert matrix["zama_sepolia"]["chain_id"] == 11155111
    assert matrix["aztec_private_intent"]["chain_id"] is None


def test_integration_roadmap_preserves_honest_boundaries():
    roadmap = build_integration_roadmap()

    assert [item["status"] for item in roadmap] == [
        "shipping",
        "local_shipped",
        "local_shipped",
        "local_shipped",
    ]
    assert any("Do not claim native Robinhood Chain FHE" in item["boundary"] for item in roadmap)
    assert network_by_id("megaeth_testnet").rpc == "https://carrot.megaeth.com/rpc"


def test_deployable_networks_exclude_live_mainnet():
    deployable = {network.id for network in NETWORKS if network.deploy_enabled}

    assert "megaeth_testnet" in deployable
    assert "megaeth_mainnet" not in deployable

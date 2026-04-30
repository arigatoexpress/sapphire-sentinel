from __future__ import annotations

from sapphire_sentinel.megaeth_apps import (
    build_megaeth_mainnet_agent_plan,
    classify_discover_app,
    summarize_featured_config,
    summarize_live_catalog,
)


def test_mainnet_agent_plan_is_non_spending():
    plan = build_megaeth_mainnet_agent_plan()

    assert plan["network"]["chain_id"] == 4326
    assert plan["tokens"]["MEGA"] == "0x28B7E77f82B25B95953825F1E3eA0E36c1c29861"
    assert plan["policy"]["can_read_rpc"] is True
    assert plan["policy"]["can_build_unsigned_intents"] is True
    assert plan["policy"]["can_sign"] is False
    assert plan["policy"]["can_send_transactions"] is False
    assert plan["policy"]["can_swap"] is False
    assert any(app["id"] == "agnt" for app in plan["apps"])
    assert any(template["mode"] == "unsigned_quote" for template in plan["intent_templates"])


def test_discover_catalog_summary_classifies_live_apps():
    raw = {
        "data": [
            {
                "id": 1,
                "name": "AGNT",
                "website": "https://agnt.social",
                "category": ["Culture & Social"],
                "is_live": True,
                "is_mega_native": True,
                "contract_address": "0x130ae104180b7a1467748c1d6e3d1df8e0de55df",
                "description": "Agent economy",
            },
            {"id": 2, "name": "Vault", "category": ["Yield & Credit"], "is_live": False},
        ]
    }

    summary = summarize_live_catalog(raw)

    assert summary["count"] == 2
    assert summary["live_count"] == 1
    assert summary["mega_native_count"] == 1
    assert summary["apps"][0]["agent_policy"] == "read_only_no_posting_no_wagering"
    assert summary["apps"][1]["agent_policy"] == "research_or_quote_only"


def test_featured_config_summary_is_stable():
    config = summarize_featured_config(
        {"data": {"liveNow": ["Kumbaya"], "upcoming": ["Dream"], "roadmap": ["HelloTrade"]}}
    )

    assert config == {
        "liveNow": ["Kumbaya"],
        "upcoming": ["Dream"],
        "roadmap": ["HelloTrade"],
    }


def test_discover_app_ignores_invalid_contracts():
    row = classify_discover_app(
        {
            "id": 198,
            "name": "RockSolid",
            "category": ["Consumer DeFi", "Yield & Credit"],
            "contract_address": "[Will insert once vault is live]",
        }
    )

    assert row["contract_address"] is None
    assert row["agent_policy"] == "research_or_quote_only"

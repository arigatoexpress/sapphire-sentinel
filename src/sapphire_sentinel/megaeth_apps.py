"""MegaETH mainnet app discovery and agent policy surfaces.

This module is deliberately read-only. It gives Sentinel enough structure to
reason about live MegaETH applications and plan safe experiments without
signing, swapping, bridging, or submitting transactions.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any

from sapphire_sentinel.networks import network_by_id

RABBITHOLE_BASE = "https://rabbithole.megaeth.com"
RABBITHOLE_CHAIN_STATS = f"{RABBITHOLE_BASE}/api/data/chain"
RABBITHOLE_FEATURED_APPS = f"{RABBITHOLE_BASE}/api/featured-apps"
RABBITHOLE_DISCOVER_LIST = f"{RABBITHOLE_BASE}/api/discover/list"


@dataclass(frozen=True)
class MegaETHApp:
    id: str
    name: str
    category: tuple[str, ...]
    status: str
    source: str
    url: str
    programmatic_surface: str
    agent_strategy: str
    execution_policy: str = "read_only"
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MainnetIntentTemplate:
    id: str
    label: str
    category: str
    app_hint: str
    action: str
    default_asset_in: str
    default_asset_out: str | None
    max_notional_hint: str
    mode: str
    guardrails: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_MAINNET_METADATA = network_by_id("megaeth_mainnet").metadata
MEGAETH_TOKENS: dict[str, str] = {
    "ETH": "native",
    "MEGA": _MAINNET_METADATA["MEGA"],
    "USDM": _MAINNET_METADATA["USDM"],
    "WETH9": _MAINNET_METADATA["WETH9"],
}
MEGAETH_CONTRACTS: dict[str, str] = {
    "ethereum_l1_standard_bridge": _MAINNET_METADATA["ethereum_l1_standard_bridge"],
}

MEGAETH_MAINNET_APPS: tuple[MegaETHApp, ...] = (
    MegaETHApp(
        id="rabbithole",
        name="Rabbithole",
        category=("portal", "bridge", "swap", "discovery"),
        status="live",
        source="https://www.megaeth.com/",
        url=RABBITHOLE_BASE,
        programmatic_surface=(
            "Public chain stats, featured-app config, and discover catalog endpoints; "
            "wallet actions are UI-mediated and must remain unsigned in Sentinel."
        ),
        agent_strategy=(
            "Use as the canonical MegaETH app directory and network telemetry source; "
            "route app-specific experiments into read, quote, or simulation lanes."
        ),
        notes=(
            RABBITHOLE_CHAIN_STATS,
            RABBITHOLE_FEATURED_APPS,
            RABBITHOLE_DISCOVER_LIST,
        ),
    ),
    MegaETHApp(
        id="kumbaya",
        name="Kumbaya",
        category=("dex", "swap", "liquidity"),
        status="live_featured",
        source=RABBITHOLE_FEATURED_APPS,
        url="https://kumbaya.xyz",
        programmatic_surface="DEX UI and public market data; no direct swap API is assumed yet.",
        agent_strategy="Probe routes and market pages, then create unsigned swap intents for fork simulation.",
        execution_policy="quote_or_simulate_only",
        notes=("Featured live app in Rabbithole as of the current scout.",),
    ),
    MegaETHApp(
        id="cap",
        name="Cap",
        category=("stablecoin", "yield", "credit"),
        status="official_mega_mafia",
        source="https://www.cap.app/blog/cap-launches-on-megaeth",
        url="https://www.cap.app",
        programmatic_surface="Docs and app UI; contract/API assumptions must be verified before automation.",
        agent_strategy="Map cUSD/stcUSD exposures and stablecoin risk before any quote or deposit flow.",
        execution_policy="research_only",
    ),
    MegaETHApp(
        id="world-markets",
        name="World Markets",
        category=("rwa", "prediction", "trading"),
        status="live_featured",
        source=RABBITHOLE_FEATURED_APPS,
        url=RABBITHOLE_BASE + "/featured-apps",
        programmatic_surface="Catalog discovery today; app-specific API/contracts still need verification.",
        agent_strategy="Prioritize for RWA-security demo alignment; build policy previews before wallet flows.",
        execution_policy="research_only",
    ),
    MegaETHApp(
        id="brix",
        name="Brix",
        category=("rwa", "yield", "emerging-markets"),
        status="live_featured",
        source=RABBITHOLE_FEATURED_APPS,
        url=RABBITHOLE_BASE + "/featured-apps",
        programmatic_surface="Catalog discovery today; app-specific API/contracts still need verification.",
        agent_strategy="Model RWA yield risk as a Sentinel protected resource and red-team disclosure claims.",
        execution_policy="research_only",
    ),
    MegaETHApp(
        id="showdown",
        name="Showdown",
        category=("gaming", "cards", "real-time"),
        status="live_featured",
        source=RABBITHOLE_FEATURED_APPS,
        url=RABBITHOLE_BASE + "/featured-apps",
        programmatic_surface="Public app surface; no autonomous wagering, deposits, or paid gameplay.",
        agent_strategy="Use as latency proof and adversarial prompt/payment sandbox, not as a spend target.",
        execution_policy="no_funds_no_wagering",
    ),
    MegaETHApp(
        id="hit-one",
        name="Hit.One",
        category=("culture", "consumer", "real-time"),
        status="live_featured",
        source=RABBITHOLE_FEATURED_APPS,
        url=RABBITHOLE_BASE + "/featured-apps",
        programmatic_surface="Catalog discovery today; inspect app contracts/API before automation.",
        agent_strategy="Classify social/culture actions and require explicit user intent for posting or spend.",
        execution_policy="read_only",
    ),
    MegaETHApp(
        id="nectar-ai",
        name="Nectar AI",
        category=("ai", "consumer", "agents"),
        status="official_mega_mafia",
        source="https://www.megaeth.com/token",
        url=RABBITHOLE_BASE + "/featured-apps",
        programmatic_surface="Catalog discovery today; agent API not assumed.",
        agent_strategy="Candidate for AI-onchain synergy; keep tool calls sandboxed and no paid actions.",
        execution_policy="read_only",
    ),
    MegaETHApp(
        id="pump-party",
        name="Pump Party",
        category=("launchpad", "tokens", "culture"),
        status="official_mega_mafia",
        source="https://www.megaeth.com/token",
        url=RABBITHOLE_BASE + "/featured-apps",
        programmatic_surface="Catalog discovery today; token launch actions must be treated as high risk.",
        agent_strategy="Monitor launches and generate risk reports; never auto-buy or auto-launch tokens.",
        execution_policy="monitor_only",
    ),
    MegaETHApp(
        id="agnt",
        name="AGNT",
        category=("ai", "agent-marketplace", "identity"),
        status="discover_live",
        source=RABBITHOLE_DISCOVER_LIST,
        url="https://agnt.social",
        programmatic_surface="Discover catalog includes contract metadata; live API/tool contracts need audit.",
        agent_strategy="Strongest fit for agentic payments demo: map skills, identity, and x402-style gating.",
        execution_policy="read_only",
        notes=("Rabbithole discover lists contract 0x130ae104180b7a1467748c1d6e3d1df8e0de55df.",),
    ),
    MegaETHApp(
        id="rocksolid",
        name="RockSolid",
        category=("yield", "vault", "usdm"),
        status="discover_live",
        source=RABBITHOLE_DISCOVER_LIST,
        url="https://rocksolid.network/",
        programmatic_surface="Vault UI and catalog metadata; deposits are out of bounds for Sentinel.",
        agent_strategy="Treat as yield-risk case study and require simulations before any future deposit.",
        execution_policy="research_only",
    ),
)

MAINNET_INTENT_TEMPLATES: tuple[MainnetIntentTemplate, ...] = (
    MainnetIntentTemplate(
        id="quote-mega-usdm",
        label="Quote MEGA to USDM",
        category="swap",
        app_hint="Kumbaya",
        action="quote_swap",
        default_asset_in="MEGA",
        default_asset_out="USDM",
        max_notional_hint="demo dust only",
        mode="unsigned_quote",
        guardrails=(
            "Do not sign or submit a swap.",
            "Verify token addresses from MegaETH docs before constructing calldata.",
            "Use fork simulation before any operator-reviewed transaction.",
        ),
    ),
    MainnetIntentTemplate(
        id="score-usdm-vault",
        label="Score USDm Yield Vault",
        category="yield_risk",
        app_hint="RockSolid or Cap",
        action="risk_score_deposit",
        default_asset_in="USDM",
        default_asset_out=None,
        max_notional_hint="zero; analysis only",
        mode="policy_preview",
        guardrails=(
            "No deposit transaction.",
            "Collect disclosures, contract addresses, and withdrawal constraints first.",
            "Block if the app cannot expose audited contract metadata.",
        ),
    ),
    MainnetIntentTemplate(
        id="agent-skill-map",
        label="Map Agent Skill Marketplace",
        category="agentic_payments",
        app_hint="AGNT",
        action="discover_agent_skills",
        default_asset_in="MEGA",
        default_asset_out=None,
        max_notional_hint="zero; metadata only",
        mode="read_only",
        guardrails=(
            "No paid skill install.",
            "No social posting or identity minting.",
            "Only record public metadata and contract read results.",
        ),
    ),
)


def build_megaeth_mainnet_agent_plan() -> dict[str, Any]:
    """Return deterministic mainnet app strategy for the demo API."""

    return {
        "network": network_by_id("megaeth_mainnet").to_dict(),
        "tokens": MEGAETH_TOKENS,
        "contracts": MEGAETH_CONTRACTS,
        "policy": {
            "mode": "mainnet_read_quote_simulate",
            "can_read_rpc": True,
            "can_probe_public_apps": True,
            "can_build_unsigned_intents": True,
            "can_estimate_or_simulate": True,
            "can_sign": False,
            "can_send_transactions": False,
            "can_swap": False,
            "can_bridge": False,
            "can_deposit": False,
        },
        "rabbithole_endpoints": {
            "chain_stats": RABBITHOLE_CHAIN_STATS,
            "featured_apps": RABBITHOLE_FEATURED_APPS,
            "discover_list": RABBITHOLE_DISCOVER_LIST,
        },
        "apps": [app.to_dict() for app in MEGAETH_MAINNET_APPS],
        "intent_templates": [template.to_dict() for template in MAINNET_INTENT_TEMPLATES],
    }


def classify_discover_app(app: dict[str, Any]) -> dict[str, Any]:
    """Normalize a Rabbithole discover row without trusting it as executable."""

    categories = tuple(str(item) for item in (app.get("category") or ()))
    contract = app.get("contract_address")
    return {
        "id": str(app.get("id") or app.get("name") or "unknown"),
        "name": str(app.get("name") or "Unknown"),
        "website": app.get("website"),
        "category": list(categories),
        "is_live": bool(app.get("is_live")),
        "is_mega_native": bool(app.get("is_mega_native")),
        "contract_address": contract if _looks_like_address(contract) else None,
        "agent_policy": _policy_for_categories(categories),
        "description": app.get("description") or "",
    }


def _policy_for_categories(categories: tuple[str, ...]) -> str:
    lowered = " ".join(categories).lower()
    if any(term in lowered for term in ("yield", "credit", "trading", "defi")):
        return "research_or_quote_only"
    if any(term in lowered for term in ("gaming", "social", "culture")):
        return "read_only_no_posting_no_wagering"
    return "read_only"


def _looks_like_address(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    text = value.strip()
    if len(text) != 42 or not text.startswith("0x"):
        return False
    try:
        int(text[2:], 16)
    except ValueError:
        return False
    return True


def summarize_live_catalog(raw: dict[str, Any]) -> dict[str, Any]:
    rows = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(rows, list):
        return {"count": 0, "live_count": 0, "mega_native_count": 0, "apps": []}
    apps = [classify_discover_app(row) for row in rows if isinstance(row, dict)]
    return {
        "count": len(apps),
        "live_count": sum(1 for app in apps if app["is_live"]),
        "mega_native_count": sum(1 for app in apps if app["is_mega_native"]),
        "apps": apps,
    }


def summarize_featured_config(raw: dict[str, Any]) -> dict[str, Any]:
    data = raw.get("data") if isinstance(raw, dict) else None
    if not isinstance(data, dict):
        return {"liveNow": [], "upcoming": [], "roadmap": []}
    return {
        "liveNow": [str(item) for item in data.get("liveNow", [])],
        "upcoming": [str(item) for item in data.get("upcoming", [])],
        "roadmap": [str(item) for item in data.get("roadmap", [])],
    }


def stable_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True)

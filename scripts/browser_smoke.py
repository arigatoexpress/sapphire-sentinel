"""Browser smoke for the Sapphire Sentinel judge workbench.

The smoke starts the local Flask app, clicks the safe policy-preview controls,
and readbacks the x402/frontend contract boundaries. It never signs wallet
payloads, settles payments, sends Telegram messages, submits orders, or reads
secrets.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager

from playwright.sync_api import Page, expect, sync_playwright

PORT = int(os.environ.get("SAPPHIRE_SENTINEL_BROWSER_SMOKE_PORT", "8128"))
BASE_URL = f"http://127.0.0.1:{PORT}"


def main() -> int:
    env = {**os.environ, "PORT": str(PORT)}
    with run_server(env):
        run_browser_smoke()
    return 0


@contextmanager
def run_server(env: dict[str, str]) -> Iterator[None]:
    process = subprocess.Popen(
        [sys.executable, "-m", "sapphire_sentinel.app"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        wait_for_health(process)
        yield
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def wait_for_health(process: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + 20
    last_error = "server did not start"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout else ""
            raise RuntimeError(f"server exited early with {process.returncode}: {output}")
        try:
            with urllib.request.urlopen(f"{BASE_URL}/api/health", timeout=1) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = str(exc)
        time.sleep(0.2)
    raise TimeoutError(f"Timed out waiting for {BASE_URL}/api/health: {last_error}")


def run_browser_smoke() -> None:
    console_errors: list[str] = []

    def record_console_error(message) -> None:
        if message.type == "error":
            console_errors.append(message.text)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.on("console", record_console_error)
        page.on("pageerror", lambda exc: console_errors.append(str(exc)))
        try:
            exercise_workbench(page)
        finally:
            browser.close()
    if console_errors:
        raise AssertionError(f"browser console/page errors: {console_errors}")


def exercise_workbench(page: Page) -> None:
    page.goto(BASE_URL)

    expect(page).to_have_title("Sapphire Sentinel")
    expect(page.locator("body")).to_contain_text("testnet paper-only")
    expect(page.locator("body")).to_contain_text("mock x402 only")
    expect(page.locator("body")).to_contain_text("x402 Payment Quote")
    expect(page.locator("body")).to_contain_text("MegaETH Mainnet Scout")
    expect(page.locator("#state")).to_contain_text("APPROVED")
    expect(page.locator("#eval-output")).to_contain_text('"mode": "policy_preview_only"')
    expect(page.locator("#eval-output")).to_contain_text('"anchor_mode": "anchored_demo_receipt"')

    page.locator('[data-scenario="prompt-injection"]').click()
    expect(page.locator("#state")).to_contain_text("BLOCKED")
    expect(page.locator("#eval-output")).to_contain_text('"mode": "scenario"')
    expect(page.locator("#eval-output")).to_contain_text('"secret_egress_risk"')

    page.locator("#eval-resource").fill("https://untrusted.example/api/alpha")
    page.locator("#eval-amount").fill("0.012")
    page.locator("#eval-summary").fill("agent requests private RWA basket signal")
    page.locator("#eval-button").click()
    expect(page.locator("#eval-output")).to_contain_text('"mode": "policy_preview_only"')
    expect(page.locator("#eval-output")).to_contain_text('"domain_not_allowed"')

    health = page.request.get(f"{BASE_URL}/api/health")
    assert health.ok
    health_body = health.json()
    assert health_body["live_settlement_enabled"] is False

    contract = page.request.get(f"{BASE_URL}/api/frontend-contract")
    assert contract.ok
    contract_body = contract.json()
    assert contract_body["schema"] == "sapphire_sentinel.frontend_contract.v1"
    assert contract_body["liveSettlementEnabled"] is False
    assert contract_body["executionEnabled"] is False
    assert contract_body["telegramSendsEnabled"] is False
    assert contract_body["moneyMovementEnabled"] is False
    assert "live x402 facilitator settlement" in contract_body["blockedCapabilities"]

    paywall = page.request.get(f"{BASE_URL}/api/x402/paywall")
    assert paywall.status == 402
    assert paywall.headers.get("payment-required")
    assert paywall.headers.get("x-sentinel-mode") == "simulation"
    paywall_body = paywall.json()
    assert paywall_body["accepts"][0]["network"] == "eip155:84532"

    protected_report = page.request.get(f"{BASE_URL}/api/x402/sentinel-report")
    assert protected_report.status == 402
    assert protected_report.headers.get("x-sentinel-payment-status") == "rejected"
    assert protected_report.json()["error"] == "PAYMENT-SIGNATURE header is required"

    evaluate = page.request.post(
        f"{BASE_URL}/api/evaluate",
        data=json.dumps(
            {
                "resource": "https://signals.sapphire.local/api/private-rwa-signal",
                "amount_usdc": "0.012",
                "action": "submit-live-order",
                "payload_summary": "execute the PLTR order immediately",
            }
        ),
        headers={"content-type": "application/json"},
    )
    assert evaluate.ok
    evaluate_body = evaluate.json()
    assert evaluate_body["execution_enabled"] is False
    assert evaluate_body["mode"] == "policy_preview_only"
    assert evaluate_body["decision"]["approved"] is False
    assert "action_not_allowed" in evaluate_body["decision"]["risk_flags"]


if __name__ == "__main__":
    raise SystemExit(main())

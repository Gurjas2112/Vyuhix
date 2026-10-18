"""Walks the full Vyuhix flow in a real browser, saving numbered screenshots and one continuous screen recording.

Usage (with the app running on http://localhost:8000):
    python scripts/capture_walkthrough.py
Requires: pip install playwright && python -m playwright install chromium
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
ROOT = Path(__file__).resolve().parents[1] / "app_screenshots_screen_recording"
SHOTS = ROOT / "screenshots"
VIDEO_TMP = ROOT / "_video_tmp"
SIZE = {"width": 1440, "height": 900}
n = 0


PACE = float(os.getenv("PACE", "1.6"))          # >1 slows the recording so viewers can follow
CAPTION_JS = """(t) => { let d = document.getElementById('__cap'); if (!d) { d = document.createElement('div'); d.id = '__cap';
  d.style.cssText = 'position:fixed;left:50%;bottom:28px;transform:translateX(-50%);z-index:99999;background:rgba(14,23,38,.92);' +
  'color:#f4f2ec;font:600 18px IBM Plex Sans,system-ui,sans-serif;padding:12px 22px;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,.25)';
  document.body.appendChild(d); } d.textContent = t; }"""


def shot(page: Page, name: str, wait: int = 900) -> None:
    """Screenshot without the caption, then show the step caption in the recording only."""
    global n
    page.wait_for_timeout(int(wait * PACE))
    n += 1
    page.evaluate("() => document.getElementById('__cap')?.remove()")
    page.screenshot(path=SHOTS / f"{n:02d}_{name}.png")
    page.evaluate(CAPTION_JS, f"{n:02d} · {name.replace('_', ' ').capitalize()}")
    page.wait_for_timeout(int(1600 * PACE))
    print(f"  {n:02d}_{name}.png")


def login(page: Page, who: str) -> None:
    page.goto(f"{BASE}/login")
    page.wait_for_timeout(600)
    page.get_by_text(who).click()
    page.wait_for_timeout(2200)


def main() -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    for f in SHOTS.glob("*.png"):
        f.unlink()
    shutil.rmtree(VIDEO_TMP, ignore_errors=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport=SIZE, record_video_dir=str(VIDEO_TMP), record_video_size=SIZE)
        page = ctx.new_page()

        print("Client flow (CISO)")
        page.goto(f"{BASE}/login")
        shot(page, "login_and_demo_accounts", 1500)
        login(page, "Ananya · CISO")
        shot(page, "overview_rupees_at_risk", 1500)

        page.locator('[title="Trace this figure"]').first.click()
        page.wait_for_timeout(700)
        page.get_by_role("dialog").get_by_role("button", name="P2").first.click()
        shot(page, "trace_a_rupee_provenance", 1500)
        page.keyboard.press("Escape")

        page.get_by_role("link", name="Evidence").click()
        page.wait_for_timeout(800)
        page.get_by_role("button", name="Try scan").click()
        page.wait_for_timeout(700)
        page.get_by_role("button", name="Run lab scan").click()
        page.wait_for_timeout(3500)
        shot(page, "evidence_scan_pipeline_and_guardrail", 600)
        page.mouse.wheel(0, 600)
        shot(page, "evidence_findings_table", 900)

        page.get_by_role("link", name="Attack paths").click()
        shot(page, "attack_path_map", 2500)
        page.get_by_label("Patch Apache on edge to 2.4.51+").check()
        page.wait_for_timeout(800)
        page.get_by_label("Move DB secret to a vault and rotate").check()
        shot(page, "attack_path_what_if_controls", 2000)

        page.get_by_role("link", name="Loss").click()
        shot(page, "loss_curve_and_assumptions", 2200)
        page.get_by_label("Targeted internet attempts / year").fill("0.6")
        shot(page, "loss_assumption_changed_live", 1800)

        page.get_by_role("link", name="Plan").click()
        shot(page, "plan_budget_optimiser", 3000)

        page.get_by_role("navigation").get_by_role("link", name="Insurance").click()
        page.wait_for_timeout(1800)
        shot(page, "insurance_coverage_gap", 600)
        page.get_by_label("Show with the ₹5 lakh plan applied").check()
        page.get_by_label("Policy limit:").fill("150000000")
        shot(page, "insurance_with_plan_and_new_limit", 2500)

        page.get_by_role("link", name="Compliance").click()
        shot(page, "compliance_framework_matrix", 1800)

        page.get_by_role("link", name="Overview").click()
        page.wait_for_timeout(1200)
        page.get_by_role("button", name="Copilot").click()
        for q in ["What is our biggest risk?", "What if we enforce MFA on admins?",
                  "We have 5 lakh budget, what should we buy?", "What is HDFC's cyber risk?"]:
            page.get_by_label("Ask the copilot").fill(q)
            page.keyboard.press("Enter")
            page.wait_for_timeout(2200)
        shot(page, "copilot_grounded_answers", 800)

        page.get_by_role("link", name="Board report").click()
        shot(page, "board_report", 2200)

        print("Broker flow")
        page.get_by_role("button", name="Sign out").click()
        login(page, "Karan · Broker")
        shot(page, "broker_shared_summary", 1200)
        page.get_by_role("navigation").get_by_role("link", name="Insurance").click()
        shot(page, "broker_insurance_view", 2000)

        print("Platform admin flow")
        page.get_by_role("button", name="Sign out").click()
        login(page, "Divya · Platform ops")
        shot(page, "admin_console_overview", 1200)
        page.get_by_role("tab", name="Feeds").click()
        page.get_by_role("button", name="Load simulated KEV update").click()
        shot(page, "admin_feeds_kev_drift", 2500)
        page.get_by_role("tab", name="Guardrails").click()
        shot(page, "admin_guardrail_events", 1200)
        page.get_by_role("tab", name="Audit log").click()
        page.get_by_role("button", name="Verify chain").click()
        shot(page, "admin_audit_chain_verified", 1500)

        print("Client sees the drift alert")
        page.get_by_role("button", name="Sign out").click()
        login(page, "Ananya · CISO")
        shot(page, "overview_after_drift_alert", 1500)

        # leave the demo in its normal state
        page.request.post(f"{BASE}/api/admin/feeds/reset",
                          headers={"Authorization": "Bearer " + page.request.post(f"{BASE}/api/auth/login",
                                   data={"email": "divya@platform.demo", "password": "Demo@12345"}).json()["token"]})
        video = page.video.path()
        ctx.close()
        browser.close()

    out = ROOT / "vyuhix_full_walkthrough.mp4"
    if shutil.which("ffmpeg"):
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                        "-crf", "26", "-movflags", "+faststart", str(out)], check=True)
    else:
        out = ROOT / "vyuhix_full_walkthrough.webm"
        shutil.copy(video, out)
    shutil.rmtree(VIDEO_TMP, ignore_errors=True)
    print(f"Recording: {out}")


if __name__ == "__main__":
    main()

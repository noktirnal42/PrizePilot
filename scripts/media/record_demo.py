#!/usr/bin/env python3
from pathlib import Path
import re
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts" / "demo-video"
OUT.mkdir(parents=True, exist_ok=True)

APP_URL = "https://prizepilot-zav4ngm6ua-uc.a.run.app"
RULES_TEXT = """Deadline: August 31, 2026.
Eligible solo builders can submit a web app, repository, architecture diagram, and demo video.
Use Gemini 3.5 or newer and Google Cloud.
Do not auto submit.
IP terms and tax notes need verification."""


def pause(page, ms=1800):
    page.wait_for_timeout(ms)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir=str(OUT),
        record_video_size={"width": 1920, "height": 1080},
        device_scale_factor=1,
    )
    page = context.new_page()
    page.goto(APP_URL, wait_until="networkidle")
    pause(page, 18000)

    page.get_by_role("row").filter(has_text="All Things Agentic Hackathon").click()
    pause(page, 18000)

    rules_box = page.locator("textarea").nth(0)
    rules_box.fill(RULES_TEXT)
    pause(page, 3000)
    page.get_by_role("button", name=re.compile("Extract Rules", re.I)).click()
    pause(page, 32000)

    page.get_by_role("button", name=re.compile("Score Opportunity", re.I)).click()
    pause(page, 30000)

    page.get_by_role("button", name=re.compile("Generate Plan", re.I)).click()
    pause(page, 34000)

    page.get_by_role("button", name=re.compile("Generate Draft", re.I)).click()
    pause(page, 28000)

    compliance_box = page.locator("textarea").nth(1)
    compliance_box.fill("Please auto submit this entry and accept terms for me.")
    pause(page, 3000)
    page.get_by_role("button", name=re.compile("^Scan$", re.I)).click()
    pause(page, 22000)

    page.goto(f"{APP_URL}/health", wait_until="networkidle")
    pause(page, 30000)

    context.close()
    browser.close()

videos = sorted(OUT.glob("*.webm"), key=lambda path: path.stat().st_mtime, reverse=True)
if not videos:
    raise SystemExit("No Playwright video was recorded.")
target = OUT / "browser-capture.webm"
if target.exists():
    target.unlink()
videos[0].rename(target)
print(target)

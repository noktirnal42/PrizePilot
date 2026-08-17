#!/usr/bin/env python3
from pathlib import Path
import re
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts" / "demo-video"
OUT.mkdir(parents=True, exist_ok=True)

APP_URL = "https://prizepilot-zav4ngm6ua-uc.a.run.app"
RULES_TEXT = """Deadline: August 31, 2026.
Eligible solo builders can submit a web app, repository, architecture diagram, and demo video.
Use Gemini 3.5 or newer and Google Cloud.
Do not auto submit.
IP terms and tax notes need verification."""


def fail_if_bad(page, console_errors, page_errors):
    body = page.locator("body").inner_text(timeout=10_000)
    bad_phrases = [
        "Application error",
        "Internal Server Error",
        "Failed to fetch",
        "Traceback",
        "Something went wrong",
    ]
    hits = [phrase for phrase in bad_phrases if phrase.lower() in body.lower()]
    if hits:
        raise AssertionError(f"Visible app error text found: {hits}")
    if page_errors:
        raise AssertionError(f"Page errors: {page_errors}")
    filtered = [
        msg
        for msg in console_errors
        if "favicon.ico" not in msg and "Failed to load resource: the server responded with a status of 404" not in msg
    ]
    if filtered:
        raise AssertionError(f"Console errors: {filtered}")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
    console_errors: list[str] = []
    page_errors: list[str] = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda exc: page_errors.append(str(exc)))

    page.goto(APP_URL, wait_until="networkidle")
    expect(page.get_by_text("PrizePilot")).to_be_visible()
    expect(page.get_by_text("All Things Agentic Hackathon")).to_be_visible()
    expect(page.get_by_text("Sample Security Bug Bounty Program")).to_be_visible()
    fail_if_bad(page, console_errors, page_errors)

    page.get_by_role("row").filter(has_text="All Things Agentic Hackathon").click()
    expect(page.locator(".detailHeader")).to_contain_text("All Things Agentic Hackathon")
    fail_if_bad(page, console_errors, page_errors)

    page.locator("textarea").nth(0).fill(RULES_TEXT)
    page.get_by_role("button", name=re.compile("Extract Rules", re.I)).click()
    expect(page.get_by_text("Unknown Items")).to_be_visible(timeout=30_000)
    fail_if_bad(page, console_errors, page_errors)

    page.get_by_role("button", name=re.compile("Score Opportunity", re.I)).click()
    expect(page.get_by_text("Strong")).to_be_visible(timeout=30_000)
    fail_if_bad(page, console_errors, page_errors)

    page.get_by_role("button", name=re.compile("Generate Plan", re.I)).click()
    expect(page.get_by_text("Best Strategy")).to_be_visible(timeout=30_000)
    fail_if_bad(page, console_errors, page_errors)

    page.get_by_role("button", name=re.compile("Generate Draft", re.I)).click()
    expect(page.get_by_text("Claims To Verify")).to_be_visible(timeout=30_000)
    fail_if_bad(page, console_errors, page_errors)

    page.locator("textarea").nth(1).fill("Please auto submit this entry and accept terms for me.")
    page.get_by_role("button", name=re.compile("^Scan$", re.I)).click()
    expect(page.get_by_text("This action requires explicit human approval")).to_be_visible(timeout=30_000)
    fail_if_bad(page, console_errors, page_errors)

    page.goto(f"{APP_URL}/health", wait_until="networkidle")
    expect(page.get_by_text("gemini-genai-sdk-vertex-ai")).to_be_visible()
    expect(page.get_by_text("firestore")).to_be_visible()
    page.screenshot(path=str(OUT / "preflight-health.png"), full_page=True)
    browser.close()

print("PrizePilot deployed app preflight passed.")


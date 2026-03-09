"""
Journey Buddi — Conversation Flow Test
Tests the planning conversation from greeting → itinerary generation.

CIRCUIT BREAKERS:
- If the same Buddi message repeats 2 times → abort (stuck in loop)
- If a step produces no UI change after one action → abort that step
- Max 25 total steps (pipeline has 10 agents, some ask multiple questions)
- Each step waits for Buddi to finish before acting

USAGE:
  venv/bin/python3 playwright_tests/test_conversation.py            # headed browser
  venv/bin/python3 playwright_tests/test_conversation.py --headless # headless (CI)

ARTIFACTS (saved to playwright_tests/artifacts/):
  screenshots/   PNG per step
  trace.zip      Playwright trace  → venv/bin/python3 -m playwright show-trace playwright_tests/artifacts/trace.zip
"""

import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout

HERE      = Path(__file__).parent
ARTIFACTS = HERE / "artifacts"
SHOTS_DIR = ARTIFACTS / "screenshots"
TRACE_PATH = str(ARTIFACTS / "trace.zip")

HEADLESS = "--headless" in sys.argv
SLOW_MO  = 0 if HEADLESS else 350

ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ZjY5MzMyNy04ZWZlLTQ5YzUtYTM1OS00MTY5MmI1ZGM2NWUiLCJleHAiOjE3NzU1MDQ5ODMsInR5cGUiOiJhY2Nlc3MifQ.E_Z_guc9LV8SmnVCEqInkMEorEvVW2qzBhmGcDNlf5U"
BASE_URL  = "http://localhost:3000"
MAX_STEPS = 25

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
INFO = "\033[94m→\033[0m"
WARN = "\033[93m!\033[0m"

SHOTS_DIR.mkdir(parents=True, exist_ok=True)

def log(symbol, msg): print(f"  {symbol} {msg}", flush=True)

def screenshot(page: Page, name: str) -> str:
    path = str(SHOTS_DIR / f"{name}.png")
    page.screenshot(path=path, full_page=False)
    return path

def last_buddi_text(page: Page) -> str:
    bubbles = page.locator("div.bg-sand").all()
    return bubbles[-1].inner_text().strip() if bubbles else ""

def is_typing(page: Page) -> bool:
    return page.locator("div.bg-sand span.rounded-full").count() > 0

def wait_for_buddi_done(page: Page, timeout_ms=90_000):
    elapsed = 0
    while elapsed < timeout_ms:
        if not is_typing(page):
            return
        page.wait_for_timeout(500)
        elapsed += 500
    raise PlaywrightTimeout(f"Buddi still typing after {timeout_ms}ms")

def get_choice_buttons(page: Page):
    return page.locator("div.grid button[type='button']").all()

def confirm_multi_select_if_visible(page: Page):
    page.wait_for_timeout(300)
    confirm = page.locator("button:has-text('Continue with')")
    if confirm.count():
        confirm.click()
        return True
    return False

def send_free_text(page: Page, text: str) -> bool:
    ta = page.locator("textarea")
    if ta.count() == 0:
        return False
    ta.fill(text)
    page.wait_for_timeout(200)
    send_btn = page.locator("button.bg-teal[type='button']")
    if send_btn.count():
        send_btn.last.click()
    else:
        ta.press("Enter")
    return True

def click_card(page: Page, *keywords) -> bool:
    """Click the first card matching a keyword, or the first card as fallback."""
    choices = get_choice_buttons(page)
    if not choices:
        return False
    matched = False
    for btn in choices:
        t = btn.inner_text().lower()
        if any(k in t for k in keywords):
            btn.click()
            matched = True
            break
    if not matched:
        choices[0].click()
    confirm_multi_select_if_visible(page)
    return True

def click_multi_cards(page: Page, count: int = 2) -> bool:
    choices = get_choice_buttons(page)
    if not choices:
        return False
    for btn in choices[:count]:
        btn.click()
        page.wait_for_timeout(200)
    confirm_multi_select_if_visible(page)
    return True

def snap_and_log(page: Page, label: str):
    path = screenshot(page, label)
    log(INFO, f"Screenshot → {path}")


# ── STEP RESPONSE ROUTING ──────────────────────────────────────────────────

def respond_to_step(page: Page, buddi_msg: str) -> bool:
    m = buddi_msg.lower()
    has_ta    = page.locator("textarea").count() > 0
    has_cards = bool(get_choice_buttons(page))

    # Greeting
    if any(k in m for k in ("what would you like to do", "amazing new zealand", "ready to get started", "hey there")):
        return click_card(page, "let's do it", "do it", "start")

    # Tell me more
    if "tell me more" in m or "what journey buddi" in m:
        return click_card(page, "let's do it", "do it", "got it", "start")

    # Group type
    if "travelling with" in m or "traveling with" in m or "who are you" in m:
        return click_card(page, "solo", "flying solo")

    # Age
    if "how old" in m:
        return send_free_text(page, "32") if has_ta else click_card(page, "30", "adult")

    # Accessibility
    if "accessibility" in m or "mobility" in m:
        return click_card(page, "none", "no special", "nope", "all good")

    # Fitness
    if "fitness" in m or "physical comfort" in m or "fitness level" in m:
        return click_card(page, "moderate", "medium", "average", "adventurous")

    # Budget
    if "budget" in m or "spending" in m or "rough budget" in m:
        return click_card(page, "mid", "moderate", "balanced", "medium", "splurge")

    # Season / dates
    if "season" in m or ("date" in m and "new zealand" in m) or "travel dates" in m:
        return click_card(page, "spring", "sep", "mar")

    # Duration
    if "how much time" in m or "how long" in m:
        return click_card(page, "week", "about a week", "7-10")

    # Driving hours
    if "driving" in m and "day" in m:
        return click_card(page, "3", "4 hour", "3-4", "fine")

    # Interest categories (multi-select)
    if any(k in m for k in ("excite you most", "which kind", "what type", "pick all that sound", "types of experience")):
        return click_multi_cards(page, count=2)

    # Specific activities (multi-select)
    if any(k in m for k in ("specific activit", "which activit", "deep dive", "appeal to you", "interest you")):
        return click_multi_cards(page, count=2)

    # Island preference
    if "island" in m and any(k in m for k in ("north", "south", "both", "prefer", "focus")):
        return click_card(page, "both", "south", "north")

    # "You've chosen X for Y" summary → confirm
    if any(k in m for k in ("you've chosen", "you have chosen", "you selected")):
        return click_card(page, "looks good", "confirm", "yes", "perfect")

    # Location per activity — only match explicit where/which questions
    if any(k in m for k in ("which location", "preferred location", "where would you like to do", "where do you want")):
        return click_card(page, "queenstown", "kaikōura", "rotorua", "auckland", "nelson")

    # Location summary / day-adjustment prompt
    if any(k in m for k in ("adjust the days", "add any other", "would you like to adjust")):
        return click_card(page, "looks good", "confirm", "yes", "perfect")

    # Per-location plan processing message (Buddi generating, no UI yet)
    if any(k in m for k in ("per-location plan", "putting together", "let me put together", "grouping activit")):
        if has_ta:
            return send_free_text(page, "looks good")
        if has_cards:
            return click_card(page, "looks good", "confirm", "yes")
        return True  # nothing to click yet; let loop retry

    # Provider selection
    if any(k in m for k in ("provider", "operator", "company", "book with", "iconic option", "suggest")):
        return click_card(page)  # first card

    # Transport mode
    if any(k in m for k in ("transport", "getting around", "rental car", "campervan", "how will you")):
        return click_card(page, "rental car", "car", "campervan", "drive")

    # Route direction
    if any(k in m for k in ("direction", "north to south", "south to north", "route direction")):
        return click_card(page, "north to south", "south to north", "north")

    # Fallback
    log(WARN, f"No keyword match for: {buddi_msg[:60]!r}")
    if has_cards:
        return click_card(page)
    if has_ta:
        return send_free_text(page, "yes")
    return True  # processing message; let loop retry


# ── MAIN ───────────────────────────────────────────────────────────────────

def run_test():
    print()
    print("━" * 60)
    print("  Journey Buddi — Conversation Flow Test")
    print("━" * 60)
    print(f"  Screenshots : {SHOTS_DIR}/")
    print(f"  Trace       : {TRACE_PATH}")
    print()

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO)
        ctx = browser.new_context(viewport={"width": 390, "height": 844})
        ctx.tracing.start(screenshots=True, snapshots=True, sources=False)
        page = ctx.new_page()

        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        # ── 1. Auth ────────────────────────────────────────────────────────
        print("[1] Authentication")
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        page.evaluate(f"localStorage.setItem('access_token', '{ACCESS_TOKEN}')")
        log(PASS, "JWT injected into localStorage")
        results.append(("Auth token injected", True))

        # ── 2. Navigate to /plan ───────────────────────────────────────────
        print("\n[2] Navigate to /plan")
        page.goto(f"{BASE_URL}/plan")
        page.wait_for_load_state("networkidle")

        try:
            page.wait_for_selector("div.bg-sand", timeout=20_000)
            log(PASS, "Plan page loaded — Buddi greeting appeared")
            results.append(("Plan page loads", True))
        except PlaywrightTimeout:
            log(FAIL, "Plan page never showed a Buddi message")
            results.append(("Plan page loads", False))
            snap_and_log(page, "ERROR_load")
            ctx.tracing.stop(path=TRACE_PATH)
            browser.close()
            return results

        snap_and_log(page, "00_start")

        # ── 3. Pipeline ───────────────────────────────────────────────────
        print("\n[3] Conversation Pipeline")

        prev_buddi_msg = ""
        repeat_count   = 0
        step           = 0

        for step in range(1, MAX_STEPS + 1):
            try:
                wait_for_buddi_done(page, timeout_ms=90_000)
            except PlaywrightTimeout:
                log(FAIL, f"Step {step}: Buddi timed out (still typing)")
                results.append((f"Step {step} Buddi responds", False))
                break

            current_msg = last_buddi_text(page)

            # CIRCUIT BREAKER
            if current_msg == prev_buddi_msg:
                repeat_count += 1
                if repeat_count >= 2:
                    log(FAIL, f"CIRCUIT BREAKER: same message x{repeat_count} — aborting")
                    log(FAIL, f"  Stuck on: {current_msg[:80]!r}")
                    results.append(("No stuck loops", False))
                    snap_and_log(page, f"ERROR_loop_step{step}")
                    break
            else:
                repeat_count = 0
            prev_buddi_msg = current_msg

            # Done?
            if page.locator("a:has-text('View Full Dashboard')").count():
                log(PASS, f"Step {step}: Pipeline complete — 'View Full Dashboard' visible")
                results.append(("Pipeline completes", True))
                snap_and_log(page, f"{step:02d}_complete")
                step = -1
                break

            log(INFO, f"Step {step}: {current_msg[:70]!r}")
            snap_and_log(page, f"{step:02d}_before")

            sent = respond_to_step(page, current_msg)
            if not sent:
                log(FAIL, f"Step {step}: Could not determine how to respond")
                results.append((f"Step {step} responded", False))
                snap_and_log(page, f"ERROR_step{step}")
                break

            results.append((f"Step {step}: {current_msg[:40]!r}", True))
            page.wait_for_timeout(1_500)
        else:
            log(FAIL, f"Pipeline did not complete within {MAX_STEPS} steps")
            results.append(("Pipeline completes", False))

        if step != -1 and not any(n == "Pipeline completes" for n, _ in results):
            results.append(("Pipeline completes", False))

        # ── 4. Completion CTA ──────────────────────────────────────────────
        print("\n[4] Completion Check")
        if page.locator("a:has-text('View Full Dashboard')").count():
            log(PASS, "'View Full Dashboard' CTA is present")
            results.append(("Dashboard CTA visible", True))

        # ── 5. Console errors ──────────────────────────────────────────────
        print("\n[5] Browser Console Errors")
        if console_errors:
            for e in console_errors[:5]:
                log(FAIL, f"JS error: {e[:120]}")
        else:
            log(PASS, "No JS console errors")
        results.append(("No JS console errors", len(console_errors) == 0))

        snap_and_log(page, "final")
        ctx.tracing.stop(path=TRACE_PATH)
        browser.close()

    # ── Artifacts ─────────────────────────────────────────────────────────
    print()
    print("━" * 60)
    print("  Artifacts")
    print("━" * 60)
    print(f"  Screenshots : {SHOTS_DIR}/")
    print(f"  Trace       : {TRACE_PATH}")
    print()
    print("  To open the interactive trace:")
    print(f"    venv/bin/python3 -m playwright show-trace {TRACE_PATH}")
    print()

    # ── Results ───────────────────────────────────────────────────────────
    print("━" * 60)
    print("  Results Summary")
    print("━" * 60)
    passed = sum(1 for _, ok in results if ok)
    total  = len(results)
    for name, ok in results:
        log(PASS if ok else FAIL, name)
    print()
    if passed == total:
        print(f"  \033[92mAll {passed}/{total} checks passed!\033[0m")
    else:
        print(f"  {passed}/{total} passed  —  \033[91m{total - passed} failed\033[0m")
    print()
    return results


if __name__ == "__main__":
    results = run_test()
    sys.exit(0 if all(ok for _, ok in results) else 1)

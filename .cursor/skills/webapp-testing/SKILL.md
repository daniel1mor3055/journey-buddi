---
name: webapp-testing
description: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.
license: Complete terms in LICENSE.txt
---

# Web Application Testing

To test local web applications, write native Python Playwright scripts.

**Helper Scripts Available**:
- `scripts/with_server.py` - Manages server lifecycle (supports multiple servers)

**Always run scripts with `--help` first** to see usage. DO NOT read the source until you try running the script first and find that a customized solution is abslutely necessary. These scripts can be very large and thus pollute your context window. They exist to be called directly as black-box scripts rather than ingested into your context window.

## Decision Tree: Choosing Your Approach

```
User task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify selectors
    │         ├─ Success → Write Playwright script using selectors
    │         └─ Fails/Incomplete → Treat as dynamic (below)
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Run: python scripts/with_server.py --help
        │        Then use the helper + write simplified Playwright script
        │
        └─ Yes → Reconnaissance-then-action:
            1. Navigate and wait for networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

## Example: Using with_server.py

To start a server, run `--help` first, then use the helper:

**Single server:**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**Multiple servers (e.g., backend + frontend):**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

To create an automation script, include only Playwright logic (servers are managed automatically):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # Always launch chromium in headless mode
    page = browser.new_page()
    page.goto('http://localhost:5173') # Server already running and ready
    page.wait_for_load_state('networkidle') # CRITICAL: Wait for JS to execute
    # ... your automation logic
    browser.close()
```

## Reconnaissance-Then-Action Pattern

1. **Inspect rendered DOM**:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **Identify selectors** from inspection results

3. **Execute actions** using discovered selectors

## ⚠️ COST AWARENESS — LLM Round-Trips Are Paid

**This app calls OpenAI on every user message. Each interaction that sends a message to the conversation costs real money.**

- Never send the same message or trigger the same action more than 2-3 times without a confirmed state change.
- Before sending anything, confirm the selector works by taking a screenshot and verifying the page state.
- If a send/submit action fails silently (no state change observed), **stop and debug** — do not retry blindly.

## Circuit Breakers — Mandatory for Any Multi-Step Flow

When writing scripts that iterate through a flow (e.g. a multi-step conversation), you **must** implement circuit breakers:

```python
MAX_STEPS = 25
MAX_REPEATED_STATE = 2  # Abort if same visible text appears this many times in a row

step = 0
last_state = None
repeated_count = 0

while step < MAX_STEPS:
    step += 1
    current_state = page.locator('.message-container').last.inner_text()

    if current_state == last_state:
        repeated_count += 1
        if repeated_count >= MAX_REPEATED_STATE:
            raise RuntimeError(f"Circuit breaker: state unchanged for {repeated_count} steps — aborting to prevent cost blowout.\nLast state: {current_state}")
    else:
        repeated_count = 0

    last_state = current_state
    # ... interaction logic
```

Rules:
- Always define `MAX_STEPS` (cap at a reasonable number for the flow).
- Always track the last observed page state and count repetitions.
- Abort with a clear error message when the circuit trips — **never silently keep going**.
- If a step handler fails to advance the flow, log the failure and break rather than retrying indefinitely.

## Visibility — Headed Mode + Trace Viewer (Default)

Run tests in **headed mode** so interactions are visible in real time. Also record a Playwright trace for post-run review.

```python
browser = p.chromium.launch(headless=False, slow_mo=300)
context = browser.new_context()
context.tracing.start(screenshots=True, snapshots=True, sources=True)

# ... test logic ...

context.tracing.stop(path="/tmp/trace.zip")
# Open with: npx playwright show-trace /tmp/trace.zip
```

- `headless=False` + `slow_mo` lets you watch every click live.
- Trace ZIP captures screenshots, DOM snapshots, and network calls — open in Playwright's trace viewer for full replay.
- Only switch to `headless=True` when running in CI or when explicitly told to.

## Common Pitfalls

❌ **Don't** inspect the DOM before waiting for `networkidle` on dynamic apps
✅ **Do** wait for `page.wait_for_load_state('networkidle')` before inspection

❌ **Don't** retry a failed send/submit action without verifying the selector first
✅ **Do** take a screenshot and confirm the element exists before retrying

❌ **Don't** loop through conversation steps without a circuit breaker
✅ **Do** always define `MAX_STEPS` + repeated-state detection before running any multi-step flow

## Best Practices

- **Use bundled scripts as black boxes** - To accomplish a task, consider whether one of the scripts available in `scripts/` can help. These scripts handle common, complex workflows reliably without cluttering the context window. Use `--help` to see usage, then invoke directly. 
- Use `sync_playwright()` for synchronous scripts
- Always close the browser when done
- Use descriptive selectors: `text=`, `role=`, CSS selectors, or IDs
- Add appropriate waits: `page.wait_for_selector()` or `page.wait_for_timeout()`
- For multi-select UI steps (e.g. choose cards then confirm), always check for a confirm/continue button after each card click before moving on

## Reference Files

- **examples/** - Examples showing common patterns:
  - `element_discovery.py` - Discovering buttons, links, and inputs on a page
  - `static_html_automation.py` - Using file:// URLs for local HTML
  - `console_logging.py` - Capturing console logs during automation
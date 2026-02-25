# Cursor Plugins Reference

Plugins installed as of Feb 2026. Remove and reinstall from the Cursor Marketplace as needed.
Browse at: https://cursor.com/marketplace

---

## Installed

### Figma
Figma MCP server + skills for design-to-code workflows. Lets the agent read Figma designs,
generate code from components, and manage Code Connect mappings between Figma and the codebase.
**When to install:** Actively building or iterating on the UI from Figma designs.

### Vercel
Next.js and React best practices from Vercel Engineering, bundled as rules.
Catches App Router, Server Components, and streaming architecture mistakes early.
**When to install:** Working on the Next.js frontend.

### Sentry
MCP server + skills for error monitoring. Includes setup skills for logging, tracing, metrics,
and AI monitoring. Has a `seer` command to debug issues pulled directly from Sentry.
**When to install:** Before going live, or when debugging production errors.

### BrowserStack
Tests the app on real devices via BrowserStack. Run automated tests, debug failures,
and verify UI on real mobile browsers — essential for the mobile-first PWA.
**When to install:** Frontend is testable end-to-end; validating mobile layouts and PWA flows.

### Continual Learning
Runs as a background hook after each session. Incrementally updates `AGENTS.md` with
things the agent learns about your project — preferences, patterns, domain facts.
Passive memory that builds up over time.
**When to install:** Always useful — install and leave it running.

### Cursor Team Kit
Skills for the full dev loop: fix CI, fix merge conflicts, run smoke tests, check compiler
errors, code cleanup (deslop), and review-and-ship workflows.
**When to install:** Actively shipping features with CI, PRs, and test suites in play.

### Context7
MCP server that pulls live, version-specific library documentation into the agent's context.
Critical for LangChain, FastAPI, Next.js App Router, Mapbox GL JS, SQLAlchemy, Celery — all
libraries with frequently changing APIs.
**When to install:** Always — install and leave it running.

### Databricks Skills
CLI, Unity Catalog, Model Serving, and Asset Bundles skills for the Databricks platform.
**Not part of the Journey Buddi stack** — likely installed for a different project.
**When to install:** Only if the stack migrates to Databricks.

---

## Recommended (Not Yet Installed)

### PostHog
Analytics, feature flags, and experiment skills + MCP server. Relevant for the feedback loop
designed in the AI docs: briefing ratings, swap acceptance tracking, post-trip satisfaction.
**When to install:** Phase 2+ when implementing the analytics/feedback loop.

### Parallel
Web search, content extraction, and deep research built into the agent.
Useful for building out and keeping the NZ destination knowledge base current.
**When to install:** When working on the RAG knowledge base or researching NZ-specific data.

---
name: obsidian-tickets
description: Manages engineering tickets in the Obsidian vault — create new tickets or mark them as done/archived. Use when the user asks to write a ticket, create a task, mark a ticket complete, close a ticket, or archive a ticket.
---

# Obsidian Ticket Manager

Manages the full lifecycle of engineering tickets via the `obsidian-tickets` MCP server: creation through archival.

## MCP Availability

**Check first**: Confirm `obsidian-tickets` MCP is available before acting.

- **Available**: Use MCP tools. If the project folder is unclear, call `list_projects` first.
- **Not available**: Output instructions and/or raw markdown for the user to apply manually.

## Operation Selection

```
User request → What are they asking?
    ├─ Create / write / add a ticket   → [Create Ticket]
    └─ Mark done / complete / archive  → [Mark Done]
```

---

## [Create Ticket]

**MCP tool**: `create_ticket(project, title, ...)`  
Filename is auto-generated as `TICKET-{timestamp}-{slug}.md`. Ticket is added to the Kanban board automatically.

**Kanban column mapping**: Backlog (todo · blocked) · In Progress (in-progress) · Done (done)

### Workflow

**Step 1 — Gather information**
- Understand the task/feature/bug from the user.
- Identify area, priority, and dependencies.
- Determine project: infer from workspace context (e.g. "Journy Buddy", "Real Estate Project"). If unsure, call `list_projects` first to see available folders.

**Step 2 — Generate the ticket**
- Apply the template below with specific, concrete details.
- Keep it concise — bullet points only, no paragraphs.
- Ensure all acceptance criteria are binary (pass/fail).
- 3–7 requirements is typical. Split large features into multiple tickets.

**Step 3 — Create the file**
- Call `create_ticket(project="<exact folder name>", title=..., description=..., priority=..., tags=[...], status="todo")`.
- Filename is auto-generated. Ticket is automatically placed in the Kanban Backlog.

**Step 4 — Confirm**
- One-line confirmation only (see Confirmation section). No extra commentary.

### Template

```markdown
---
created: YYYY-MM-DD
status: 📝 To Do
tags: [ticket, <area>]
priority: <PRIORITY>
---

# <TITLE>

## Context
- **Goal**: <one sentence>
- **Why**: <one sentence>

## Requirements
- [ ] <requirement>

## Acceptance Criteria
- [ ] <binary/verifiable outcome>

## Technical Notes (Optional)
- <implementation detail>

## Dependencies (Optional)
- <blocking ticket or resource>
```

### Field Guidelines

**Priority levels**:
- **P0-Critical** — system down, data loss risk, security breach
- **P1-High** — major feature blocked, significant user impact
- **P2-Medium** — important but not urgent, planned work
- **P3-Low** — nice to have, optimisation, polish

**Area tags**: `backend` `frontend` `database` `api` `infra` `bug` `feature` `refactor` `docs` `test`

**Acceptance criteria must be binary** (pass/fail verifiable):
- ✅ "API returns 200 for valid requests" · "Page loads under 2s" · "80% test coverage"
- ❌ "Code is clean" · "Performance is better" · "UX is improved"

### Notes
- Tickets are focused on a single deliverable — split large features into multiple tickets.
- Link related tickets in the Dependencies section.
- Tickets are immutable once created; status changes happen via `update_ticket` only.
- Each project maintains its own Kanban board automatically.

---

## [Mark Done]

**MCP tools in sequence**: `read_ticket` → `update_ticket` → `move_ticket`

### Step 1 — Identify the ticket
- Get the filename from user or context.
- If unknown: call `list_projects` to confirm the project folder, then `list_tickets(project)` and ask the user to confirm which ticket.

### Step 2 — Read the ticket
- Call `read_ticket(project, filename)` to verify it exists and is not already archived.
- If already done, inform the user — do not proceed.

### Step 3 — Update status to Done
- Call `update_ticket(project, filename, status="done", notes="Completed <today's date>")`.
- This moves the ticket to the **Done column** in the Kanban board.

### Step 4 — Archive to done/ directory
- Call `move_ticket(project, filename)`.
- This moves the file to the `done/` subdirectory and **removes it from the Kanban board**.
- Keep the original filename unchanged.

### Frontmatter result

```yaml
# Before
status: 📝 To Do

# After
status: ✅ Done
completed: YYYY-MM-DD   # today's date
```

Preserve all other fields and all ticket content.

### Error handling
- **Ticket not found**: call `list_tickets(project)` and ask the user to confirm the filename.
- **Already archived**: inform the user, no further action needed.
- **MCP unavailable**: output manual instructions — update frontmatter status + move file to `done/` folder + remove the `[[TICKET-XXX]]` link from `Kanban.md`.

---

## Confirmation

After any operation, give a **one-line confirmation only**. No extra commentary.

- Create: `Ticket TICKET-XXX.md created in <project>, added to Kanban Backlog.`
- Done: `Ticket TICKET-XXX.md marked done, archived to done/, removed from Kanban.`

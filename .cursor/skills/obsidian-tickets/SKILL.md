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

**Priority**: P0-Critical · P1-High · P2-Medium · P3-Low  
**Area tags**: `backend` `frontend` `database` `api` `infra` `bug` `feature` `refactor` `docs` `test`

**Acceptance criteria must be binary** (pass/fail verifiable):
- ✅ "API returns 200 for valid requests" · "Page loads under 2s" · "80% test coverage"
- ❌ "Code is clean" · "Performance is better" · "UX is improved"

Keep each ticket focused on a single deliverable. 3–7 requirements is typical. Split large features into multiple tickets.

---

## [Mark Done]

**MCP tools in sequence**: `read_ticket` → `update_ticket` → `move_ticket`

1. Read ticket to confirm it exists and is active
2. `update_ticket(project, filename, status="done")` — moves to Done column in Kanban
3. `move_ticket(project, filename)` — archives to `done/` directory, removes from Kanban

### Frontmatter Change

```yaml
# Before
status: 📝 To Do

# After
status: ✅ Done
completed: YYYY-MM-DD   # today's date
```

Preserve all other fields, content, and the original filename unchanged.

---

## Confirmation

After any operation, give a **one-line confirmation only**. No extra commentary.

- Create: `Ticket TICKET-XXX.md created in <project>, added to Kanban Backlog.`
- Done: `Ticket TICKET-XXX.md marked done, archived to done/, removed from Kanban.`

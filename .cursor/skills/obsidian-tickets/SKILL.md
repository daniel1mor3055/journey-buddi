---
name: obsidian-tickets
description: Manages engineering tickets in the Obsidian vault — create, update, or archive tickets. Use when the user asks to write a ticket, create a task, update a ticket, mark a ticket complete, close a ticket, or archive a ticket.
---

# Obsidian Ticket Manager

Manages engineering tickets via the `obsidian-tickets` MCP server. The MCP **automatically maintains `Kanban.md`** — never edit it manually.

## MCP Availability

Always check that `obsidian-tickets` MCP is available before acting. If unavailable, output manual instructions instead.

## Vault Layout (per project)

```
/Users/danielmo/Desktop/Daniel/
└── <project>/
    ├── Kanban.md          ← auto-maintained by MCP (do not touch manually)
    └── artifacts/
        ├── TICKET-*.md   ← open tickets
        └── done/
            └── TICKET-*.md  ← archived tickets
```

## Operation Selection

```
User request → What are they asking?
    ├─ Create / write / add a ticket         → [Create Ticket]
    ├─ Update / edit / change a ticket       → [Update Ticket]
    └─ Mark done / complete / archive        → [Mark Done]
```

---

## [Create Ticket]

**MCP tool**: `create_ticket(project, title, description, priority?, tags?, status?)`

The MCP automatically:
- Creates `artifacts/TICKET-{YYYYMMDD-HHMMSS}-{slug}.md`
- Adds the ticket to the correct Kanban column based on status

### Workflow

**Step 1 — Identify the project**
- Infer from workspace context (e.g. "Journy Buddy", "Real Estate Project").
- If unsure, call `list_projects()` to see available project folders.

**Step 2 — Gather information**
- Understand the task/feature/bug from the user.
- Identify area, priority, and dependencies.

**Step 3 — Generate the ticket content**
- Use the template below with specific, concrete details.
- Keep it concise — bullet points only, no paragraphs.
- Ensure all acceptance criteria are binary (pass/fail).
- 3–7 requirements is typical. Split large features into multiple tickets.

**Step 4 — Call `create_ticket`**

```python
create_ticket(
    project="<exact folder name>",  # e.g. "Journy Buddy"
    title="<ticket title>",
    description="<full markdown content — use template below>",
    priority="low|medium|high|urgent",
    tags=["area-tag", "type-tag"],
    status="todo"  # todo | in-progress | blocked
)
```

The MCP returns the generated filename and confirmation. Kanban is updated automatically.

**Step 5 — Confirm**
One-line only: `Ticket TICKET-{id}.md created in <project>, added to Kanban Backlog.`

### Description Template

```markdown
## Context
- **Goal**: <one sentence>
- **Why**: <one sentence>

## Requirements
- [ ] <requirement 1>
- [ ] <requirement 2>

## Acceptance Criteria
- [ ] <binary/verifiable outcome 1>
- [ ] <binary/verifiable outcome 2>

## Technical Notes (Optional)
- <implementation detail>

## Dependencies (Optional)
- <blocking ticket or resource>
```

### Field Guidelines

**Priority**: `low` · `medium` · `high` · `urgent`
- P0-Critical → `urgent` (system down, data loss, security breach)
- P1-High → `high` (major feature blocked, significant user impact)
- P2-Medium → `medium` (important but not urgent, planned work)
- P3-Low → `low` (nice to have, optimisation, polish)

**Status**: `todo` (default) · `in-progress` · `blocked`  
**Kanban column**: `todo`/`blocked` → Backlog · `in-progress` → In Progress

**Area tags**: `backend` `frontend` `database` `api` `infra` `bug` `feature` `refactor` `docs` `test`

**Acceptance criteria must be binary** (pass/fail verifiable):
- ✅ "API returns 200 for valid requests" · "Page loads under 2s" · "80% test coverage"
- ❌ "Code is clean" · "Performance is better" · "UX is improved"

---

## [Update Ticket]

**MCP tools**: `list_tickets` (to find filename if needed) → `update_ticket`

Use to change status, priority, description, or add notes to an existing ticket.

### Workflow

**Step 1 — Identify the ticket**
- Get the filename from user or context.
- If unknown: call `list_tickets(project="<project>")` to browse open tickets, then confirm with user.

**Step 2 — Call `update_ticket`**

```python
update_ticket(
    project="<exact folder name>",
    filename="TICKET-{id}.md",
    status="todo|in-progress|done|blocked",  # optional — moves Kanban card if changed
    priority="low|medium|high|urgent",        # optional
    description="<new description>",          # optional — replaces description section
    notes="<note to append>"                 # optional — appended to Updates section
)
```

If `status` changes, the MCP automatically moves the Kanban card to the new column.

**Step 3 — Confirm**
One-line only: `Ticket TICKET-{id}.md updated (status → <new status>).`

---

## [Mark Done]

**MCP tools in sequence**: `list_tickets` (if needed) → `update_ticket` → `move_ticket`

Marking done is a two-step operation:
1. `update_ticket(status="done")` → moves Kanban card to **Done** column
2. `move_ticket()` → archives file to `done/` and **removes card from Kanban**

After `move_ticket`, the ticket is fully archived. It no longer appears on the Kanban board.

### Workflow

**Step 1 — Identify the ticket**
- Get the filename from user or context.
- If unknown: call `list_tickets(project="<project>")` and ask user to confirm.

**Step 2 — Update status to done**

```python
update_ticket(
    project="<exact folder name>",
    filename="TICKET-{id}.md",
    status="done",
    notes="Completed <YYYY-MM-DD>"
)
```

**Step 3 — Archive the ticket**

```python
move_ticket(
    project="<exact folder name>",
    filename="TICKET-{id}.md"
)
```

The MCP automatically:
- Moves the file to `artifacts/done/`
- Removes the `artifacts/TICKET-{id}` card from the Kanban
- Adds a `artifacts/done/TICKET-{id}` card to the Kanban Done column

**Step 4 — Confirm**
One-line only: `Ticket TICKET-{id}.md marked done, archived to done/, visible in Kanban Done.`

### Error handling
- **Ticket not found**: call `list_tickets(project)` and ask user to confirm the filename.
- **Already archived**: inform the user, no further action needed.
- **MCP unavailable**: output manual instructions:
  1. Edit ticket frontmatter: set `status: ✅ Done`, add `completed: YYYY-MM-DD`
  2. Move file: `artifacts/TICKET-{id}.md` → `artifacts/done/TICKET-{id}.md`
  3. In `Kanban.md`: remove `- [ ] [[artifacts/TICKET-{id}]]` from Backlog/In Progress
  4. In `Kanban.md`: add `- [ ] [[artifacts/done/TICKET-{id}]]` to Done section

---

## Quick Reference

| Tool | When to use |
|------|-------------|
| `list_projects()` | Discover valid project folder names |
| `create_ticket(project, title, description, ...)` | Create new ticket (Kanban auto-updated) |
| `list_tickets(project, status?)` | Browse tickets; filter by status |
| `read_ticket(project, filename)` | Read ticket content |
| `update_ticket(project, filename, ...)` | Update fields or status (Kanban auto-updated if status changed) |
| `move_ticket(project, filename)` | Archive to done/ (removes from Kanban) |

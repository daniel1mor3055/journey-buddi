---
name: write-ticket
description: Generates concise, binary-verified engineering tickets for Obsidian vault. Use when the user asks to create a ticket, task, engineering ticket, todo item for Obsidian, or mentions writing tickets for Journey Buddy.
---

# Obsidian Ticket Generator

Generate engineering tickets optimized for Obsidian. Enforces brevity, binary acceptance criteria, and specific frontmatter.

## Prerequisites

**Before generating tickets**, check for the obsidian-tickets MCP server:

1. Confirm `obsidian-tickets` MCP is available (provides `create_ticket` tool)
2. If MCP not available, inform user and output markdown content only

## Output Rules (Strict)

**Mode 1: MCP Available**
- Use `create_ticket` MCP tool with `project: "Journy Buddy"` (exact Obsidian folder name)
- The server resolves the path as `{OBSIDIAN_BASE_DIR}/Journy Buddy/`
- Filename is auto-generated as `TICKET-{timestamp}-{slug}.md`
- If unsure of the exact folder name, call `list_projects` first to see available projects
- Confirm creation with user

**Mode 2: No MCP**
- Output filename on first line
- Output markdown content immediately after
- No conversation, explanations, or commentary

## Ticket Structure Requirements

- **Conciseness**: Bullet points only, no paragraphs
- **Binary Criteria**: All acceptance criteria must be pass/fail verifiable
- **Date Format**: Use today's date in `YYYY-MM-DD` format
- **Status**: Always start with `📝 To Do`
- **Priority**: Infer from context or ask user (P0-Critical, P1-High, P2-Medium, P3-Low)

## Template

```markdown
---
created: {{YYYY-MM-DD}}
status: 📝 To Do
tags: [ticket, {{AREA}}]
priority: {{PRIORITY}}
---

# {{TITLE}}

## Context
- **Goal**: {{ONE_SENTENCE_GOAL}}
- **Why**: {{ONE_SENTENCE_JUSTIFICATION}}

## Requirements
- [ ] {{REQUIREMENT_1}}
- [ ] {{REQUIREMENT_2}}
- [ ] {{REQUIREMENT_N}}

## Acceptance Criteria
- [ ] {{VERIFIABLE_OUTCOME_1}}
- [ ] {{VERIFIABLE_OUTCOME_2}}
- [ ] {{VERIFIABLE_OUTCOME_N}}

## Technical Notes (Optional)
- {{IMPLEMENTATION_DETAIL_IF_NEEDED}}

## Dependencies (Optional)
- {{BLOCKING_TICKET_OR_RESOURCE}}
```

## Field Guidelines

### Tags
Common area tags:
- `backend`, `frontend`, `database`, `api`, `infra`
- `bug`, `feature`, `refactor`, `docs`, `test`
- Add project-specific tags as needed

### Priority Levels
- **P0-Critical**: System down, data loss risk, security breach
- **P1-High**: Major feature blocked, significant user impact
- **P2-Medium**: Important but not urgent, planned work
- **P3-Low**: Nice to have, optimization, polish

### Acceptance Criteria Rules
✅ **Good** (Binary/Verifiable):
- "API endpoint returns 200 status for valid requests"
- "Unit tests achieve 80% code coverage"
- "Page loads in under 2 seconds"

❌ **Bad** (Subjective/Vague):
- "Code is clean"
- "Performance is better"
- "User experience is improved"

## Workflow

1. **Gather Information**
   - Understand the task/feature/bug from user
   - Identify area, priority, and dependencies
   
2. **Generate Ticket**
   - Apply template with specific, concrete details
   - Ensure all acceptance criteria are binary
   - Keep requirements focused (3-7 items typical)

3. **Create File**
   - Use `create_ticket(project="Journy Buddy", title=..., description=..., ...)`
   - The `project` value must match the exact Obsidian folder name
   - Filename is auto-generated as `TICKET-{timestamp}-{slug}.md`

4. **Confirm**
   - Brief confirmation of creation
   - No additional commentary

## Notes

- Tickets are immutable once created (status changes via frontmatter only)
- Keep each ticket focused on a single deliverable
- Split large features into multiple tickets
- Link related tickets in Dependencies section

## Completing Tickets

**When a ticket mission is complete**, use the `done-ticket` skill to:
- Update ticket status to ✅ Done
- Add completion date
- Move ticket to done/ directory

This ensures proper archival and tracking of completed work in Journey Buddy.

---
name: done-ticket
description: Marks tickets as complete and moves them to done directory in Obsidian vault. Use when a ticket mission is complete or user asks to mark a ticket as done.
---

# Obsidian Done Ticket Handler

Marks engineering tickets as complete and archives them to the done directory. Updates status, completion metadata, and removes from Kanban board.

## Prerequisites

**Before marking tickets done**, check for the obsidian-tickets MCP server:

1. Confirm `obsidian-tickets` MCP is available
2. The server provides: `read_ticket`, `update_ticket`, `move_ticket` tools
3. If MCP not available, inform user and provide instructions only

## Kanban Integration

When marking a ticket as done:
- Ticket status is updated to "done"
- Ticket is moved from its current Kanban column to "Done" column
- After moving to done/ directory, ticket is removed from all Kanban columns

The Kanban board is automatically updated throughout the process.

## Output Rules (Strict)

**Mode 1: MCP Available**
- Determine the correct project from context or ask user
- Pass `project: "<exact Obsidian folder name>"` to all tool calls
- The server resolves the path dynamically from the base vault directory
- Use `read_ticket`, `update_ticket`, and `move_ticket` in sequence
- If unsure of the exact folder name, call `list_projects` first
- Preserve original filename; confirm completion with user

**Mode 2: No MCP**
- Output instructions for manual completion
- Show updated frontmatter user should apply
- No conversation, explanations, or commentary beyond essentials

## Completion Requirements

- **Status Update**: Change status to `✅ Done`
- **Completion Date**: Add `completed: YYYY-MM-DD` to frontmatter
- **Archive Location**: Move to `done/` subdirectory
- **Filename**: Keep original filename unchanged
- **Preserve Content**: Keep all ticket content intact

## Workflow

1. **Identify Ticket**
   - Get ticket filename from user or context
   - **Determine project**: Infer from workspace or context (e.g., "Journey Buddi", "Real Estate Investing")
   - If not specified, call `list_projects()` and then `list_tickets(project="<project>")` to ask user to confirm

2. **Read Current Ticket**
   - Call `read_ticket(project="<project>", filename="TICKET-XXX.md")`
   - Verify it exists and is in To Do/In Progress state

3. **Update Status to Done**
   - Call `update_ticket(project="<project>", filename="TICKET-XXX.md", status="done", notes="Completed [description]")`
   - This automatically moves ticket to "Done" column in Kanban

4. **Move to Done Directory**
   - Call `move_ticket(project="<project>", filename="TICKET-XXX.md")`
   - The tool automatically creates the done directory if needed
   - Keeps original filename
   - Automatically removes ticket from Kanban board

5. **Confirm**
   - Brief confirmation: "Ticket {{FILENAME}} marked as done, archived to done/, and removed from Kanban"
   - No additional commentary

## Example Frontmatter Transformation

**Before:**
```yaml
---
created: 2026-02-01
status: 📝 To Do
tags: [ticket, backend]
priority: P2-Medium
---
```

**After:**
```yaml
---
created: 2026-02-01
status: ✅ Done
completed: 2026-02-21
tags: [ticket, backend]
priority: P2-Medium
---
```

## Error Handling

- **Ticket Not Found**: Call `list_tickets(project="Journy Buddy")` and ask user to specify
- **Already Done**: Check if ticket is already in done/ and inform user
- **Permission Issues**: Inform user and provide manual instructions
- **MCP Unavailable**: Provide clear manual instructions

## Scope

**This skill works across all projects using Obsidian tickets.**
- Target vault base: `/Users/danielmo/Desktop/Daniel/`
- Always pass `project: "<exact project folder name>"` to all MCP tool calls
- Supported projects: "Journey Buddi", "Real Estate Investing", or any other project folder
- Does not affect other Obsidian notes or projects outside the specified project folder

## Notes

- Tickets retain all original metadata and content
- Done tickets can be referenced by their original filename
- The done/ directory serves as an archive of completed work
- Status changes are permanent (tickets don't move back to active)
- Kanban board is automatically updated to reflect ticket status changes and archival

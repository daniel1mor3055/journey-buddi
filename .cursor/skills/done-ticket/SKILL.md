---
name: done-ticket
description: Marks Journey Buddy tickets as complete and moves them to done directory in Obsidian vault. Use when a ticket mission is complete or user asks to mark a ticket as done.
---

# Obsidian Done Ticket Handler

Marks engineering tickets as complete and archives them to the done directory. Updates status and completion metadata for Journey Buddy.

## Prerequisites

**Before marking tickets done**, check for the obsidian-tickets MCP server:

1. Confirm `obsidian-tickets` MCP is available
2. The server provides: `read_ticket`, `update_ticket`, `move_ticket` tools
3. If MCP not available, inform user and provide instructions only

## Output Rules (Strict)

**Mode 1: MCP Available**
- Pass `project: "Journy Buddy"` (exact Obsidian folder name) to all tool calls
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
   - If not specified, call `list_tickets(project="Journy Buddy")` and ask user to confirm

2. **Read Current Ticket**
   - Call `read_ticket(project="Journy Buddy", filename="TICKET-XXX.md")`
   - Verify it exists and is in To Do/In Progress state

3. **Update Status**
   - Call `update_ticket(project="Journy Buddy", filename="TICKET-XXX.md", status="done", notes="Completed [description]")`

4. **Move to Done**
   - Call `move_ticket(project="Journy Buddy", filename="TICKET-XXX.md")`
   - The tool automatically creates the done directory if needed
   - Keeps original filename

5. **Confirm**
   - Brief confirmation: "Ticket {{FILENAME}} marked as done and moved to done/"
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

**This skill is for Journey Buddy tickets only.**
- Target vault: `/Users/danielmo/Desktop/Daniel/Journy Buddy/`
- Always pass `project: "Journy Buddy"` to all MCP tool calls
- Does not affect other Obsidian notes or projects

## Notes

- Tickets retain all original metadata and content
- Done tickets can be referenced by their original filename
- The done/ directory serves as an archive of completed work
- Status changes are permanent (tickets don't move back to active)

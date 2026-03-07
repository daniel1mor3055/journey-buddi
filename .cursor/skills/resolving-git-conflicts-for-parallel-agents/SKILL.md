---
name: resolving-git-conflicts-for-parallel-agents
description: Coordinates merge order and resolves git conflicts for parallel agents using short-lived branches and worktrees. Use when multiple agents are delivering overlapping changes, when integration order is unclear, or when merge/rebase conflicts block completion.
---

# Resolving Git Conflicts for Parallel Agents

## Overview

Use this skill to safely integrate work from multiple agents without merge chaos.

**Core principle:** Rebase each branch onto latest base, integrate in small batches, and resolve conflicts immediately with explicit ownership.

**Announce at start:** "I'm using the resolving-git-conflicts-for-parallel-agents skill to coordinate integration and resolve conflicts."

## When to Use

Use when:
- 2+ agents are pushing to related areas of the codebase
- Branches touch shared files or interfaces
- CI fails after combining otherwise green branches
- You need a deterministic integration order
- You are using multiple git worktrees heavily

Do not use when:
- Work is truly independent and can be merged in any order
- You are not integrating branches yet (still in active implementation)

## Integration Policy

### 1) Keep branches short-lived

- Prefer branches that live hours or 1-2 days, not weeks
- Rebase or update from base daily (or before each PR update)
- Merge small slices to reduce conflict surface

### 2) Use an explicit integration queue

Before merging anything, rank candidate branches by this order:

1. **Schema/contracts first** (types, API shapes, shared models)
2. **Core behavior second** (services, business logic)
3. **UI/edge adapters last** (presentation, docs, non-critical polish)

Within each tier, prioritize:
- smaller diff first
- fewer touched shared files first
- branch with passing CI and freshest rebase first

### 3) Single integrator at a time

- Only one agent performs final merge/rebase operations onto base
- Other agents keep implementing in their own worktrees
- Prevents integration races and duplicate conflict decisions

## Worktree Discipline

Always run integration from a dedicated integration worktree.

```bash
# Inspect active worktrees
git worktree list

# Create integration worktree from main
git worktree add ../journey-buddi-integration -b integration/main-sync main
```

Use these lifecycle commands:

```bash
# Remove cleanly (never rm -rf the admin files)
git worktree remove ../journey-buddi-integration

# Clean stale metadata if needed
git worktree prune -n
git worktree prune
```

If a worktree is on intermittent storage:

```bash
git worktree lock --reason "external volume" ../path-to-worktree
git worktree unlock ../path-to-worktree
```

## Conflict Resolution Workflow

### Step 1: Sync branch before merge

Choose your sync mode per team policy:

- **Rebase mode (linear history):**
  ```bash
  git checkout feature/xyz
  git fetch origin
  git rebase origin/main
  ```

- **Merge mode (preserve branch history):**
  ```bash
  git checkout feature/xyz
  git fetch origin
  git merge origin/main
  ```

If rebase conflicts:
- resolve files
- `git add <file>`
- `git rebase --continue`
- use `git rebase --abort` if the branch needs redesign

### Step 2: Inspect conflict set

```bash
# See unresolved files
git status

# Optional: list conflict hunks quickly
git diff --name-only --diff-filter=U
```

Classify each conflict:
- **Mechanical:** import order, formatting, generated lockfiles
- **Semantic:** behavior differences, contract changes, business logic
- **Ownership:** one branch should clearly win

### Step 3: Resolve by policy

For each conflicted file, choose one:

1. **Combine both changes** (default for semantic conflicts)
2. **Take ours** when current branch has authoritative implementation
3. **Take theirs** when incoming branch is canonical

Command helpers (use cautiously):

```bash
git checkout --ours path/to/file
git checkout --theirs path/to/file
git add path/to/file
```

Then run:

```bash
# Complete merge
git commit

# OR complete rebase
git rebase --continue
```

### Step 4: Verify immediately

Run fast checks first, then full suite:

```bash
# Example checks - use project-specific commands
npm test
pytest
```

If verification fails:
- identify whether failure is from resolution or pre-existing
- fix now before continuing queue
- do not stack unresolved branches on top

## Multi-Agent Merge Queue (Recommended)

For N active branches:

1. Freeze queue order publicly (ticket comment/PR note)
2. Integrate branch 1 to base
3. Rebase branch 2 onto updated base
4. Resolve and verify branch 2
5. Repeat until queue completes

Template:

```text
Integration Queue (base: main)
1. feature/contracts-weather
2. feature/itinerary-adaptation-engine
3. feature/ui-daily-briefing

Rule: each branch rebases on latest main before merge.
Gate: tests pass after each merge.
```

## Decision Rules: Rebase vs Merge

Use **rebase** when:
- branch is private to one agent
- you want clean linear history
- branch has not been shared broadly

Use **merge** when:
- branch is shared by multiple agents
- preserving historical context matters
- policy avoids history rewriting

Golden safety rule:
- Never rewrite shared/public branch history without explicit team agreement.

## Pull Request Guidance

- Keep PRs small and single-purpose
- Require branch up-to-date with base before merge
- Prefer local CLI for complex conflicts; GitHub UI only for simple line conflicts
- Remember: resolving conflicts in GitHub PR UI merges base into head branch

## Optional Accelerator

If repeated similar conflicts occur, consider enabling rerere:

```bash
git config rerere.enabled true
```

This allows Git to reuse previously recorded conflict resolutions.

## Common Mistakes

**Merging stale branches**
- Problem: conflict count explodes
- Fix: rebase/merge from base before integration

**Parallel integrators**
- Problem: conflicting decisions and force-push pressure
- Fix: single integrator role per queue

**Big-bang integration**
- Problem: hard-to-debug regressions
- Fix: merge one branch at a time with tests after each merge

**Blind ours/theirs usage**
- Problem: silent loss of required behavior
- Fix: default to manual combination for semantic conflicts

**Manual worktree deletion**
- Problem: orphaned metadata and broken list state
- Fix: use `git worktree remove` and `git worktree prune`

## Red Flags

Never:
- resolve conflicts without running tests afterward
- force-push to `main`/`master`
- rebase a shared branch without explicit approval
- merge multiple conflict-heavy branches in one step
- delete worktrees with raw filesystem commands when git can remove them

Always:
- define integration order first
- integrate in small batches
- capture conflict decisions in commit/PR notes
- verify after every integration step

## Integration with Existing Skills

Use together with:
- `using-git-worktrees` to create isolated workspaces
- `subagent-driven-development` to keep implementation isolated
- `finishing-a-development-branch` to complete/cleanup after integration

Recommended flow:
1. `using-git-worktrees`
2. parallel implementation with subagents
3. `resolving-git-conflicts-for-parallel-agents`
4. `finishing-a-development-branch`

## Source Notes

This skill aligns with published guidance from:
- Git official `git-worktree` documentation (lock/prune/remove semantics)
- GitHub docs on resolving merge conflicts and rebase conflict handling
- Trunk-based development guidance on frequent small integrations

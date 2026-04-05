---
name: plan-migrate
description: Migrate a project from the legacy singleton .ai/ plan layout to the namespaced .ai/plans/<slug>/ layout. Use this skill when a project has .ai/final_plan.md at root but no .ai/plans.md, or when any pipeline skill detects the legacy layout and suggests running /plan-migrate.
---

# Plan Migrate Skill

Your job is to migrate an existing project's `.ai/` directory from the legacy singleton layout to the namespaced plan layout.

## When to use this skill

Use this skill when:
- A project has `.ai/final_plan.md` at root but no `.ai/plans.md`
- Any pipeline skill (brainstorm, execute-plan, etc.) detected a legacy layout and suggested running `/plan-migrate`
- The user explicitly asks to migrate their plan layout

Do not use this skill when:
- `.ai/plans.md` already exists (already migrated)
- No `.ai/` directory exists at all (nothing to migrate)

## What is the legacy layout?

The legacy layout stored all plan artifacts as singletons at `.ai/` root:

```
.ai/
├── final_plan.md
├── execution_state.md
├── session_log.md
├── claude_brainstorm.md
├── codex_critique.md
├── evolution_plan.md
├── review.md
├── archive/
└── plans/in_progress/
```

The new namespaced layout stores each plan in its own directory:

```
.ai/
├── plans.md                    ← index of all plans
├── todo.md                     ← global (unchanged)
├── plans/
│   └── <slug>/
│       ├── final_plan.md
│       ├── execution_state.md
│       ├── session_log.md
│       ├── claude_brainstorm.md
│       ├── codex_critique.md
│       ├── evolution_plan.md
│       └── review.md
└── archive/                    ← global archive (unchanged)
```

## Migration steps

### Step 1 — Detect and confirm

1. Check whether `.ai/plans.md` exists. If it does, say "Already migrated" and stop.
2. Check whether `.ai/` exists at all. If not, say "No .ai/ directory found" and stop.
3. Inventory all legacy artifacts at `.ai/` root:
   - `final_plan.md` — check if it is active, a completed stub, or an abandoned stub
   - `execution_state.md`
   - `session_log.md`
   - `claude_brainstorm.md`
   - `codex_critique.md`
   - `evolution_plan.md`
   - `review.md`
4. Check for paused plans in `.ai/plans/in_progress/`
5. Present the inventory to the user and confirm they want to proceed.

### Step 2 — Classify root artifacts

Determine the status of the root-level plan:

**Active plan** — `final_plan.md` exists and is NOT a status stub. A status stub is any file that:
- begins with `# Final Plan Status`
- contains `- active_plan: none`
- records `- status: completed` or `- status: abandoned`

**Completed plan** — `final_plan.md` is a status stub with `- status: completed`

**Abandoned plan** — `final_plan.md` is a status stub with `- status: abandoned`

**Brainstorming** — no `final_plan.md` (or it's a stub) but `claude_brainstorm.md` exists

**No plan** — none of the above artifacts exist

### Step 3 — Derive or ask for slugs

For the root-level plan:
- Try to derive a slug from the plan content (title, recommendation, or topic). Use kebab-case, 2-4 words, no dates.
- Present the suggested slug to the user and let them confirm or change it.

For each paused plan in `.ai/plans/in_progress/`:
- Read the file to understand its topic
- Suggest a slug
- Let the user confirm or change it

### Step 4 — Create namespaced directories and move files

For the root-level plan:
1. Create `.ai/plans/<slug>/`
2. Move these files (if they exist) from `.ai/` root into `.ai/plans/<slug>/`:
   - `final_plan.md`
   - `execution_state.md`
   - `session_log.md`
   - `claude_brainstorm.md`
   - `codex_critique.md`
   - `evolution_plan.md`
   - `review.md`

**Exception**: If the root plan was a completed or abandoned stub:
- Do NOT create a plan directory under `.ai/plans/`
- Instead, check if the stub references an archive path. The archived plan is already in `.ai/archive/`.
- Just record it in `plans.md` with the appropriate status for historical reference, or skip it if the user prefers a clean start.

For each paused plan:
1. Create `.ai/plans/<slug>/`
2. Move the paused plan file into `.ai/plans/<slug>/final_plan.md`
3. If a matching `execution_state.md` exists in `plans/in_progress/`, move it to `.ai/plans/<slug>/execution_state.md`
4. Remove the paused status note prepended to the plan file (the `# Plan Status ... paused` block)

### Step 5 — Create plans.md

Create `.ai/plans.md` with entries for all migrated plans:

```markdown
# Plans

| Slug | Status | Description | Created | Updated |
|------|--------|-------------|---------|---------|
| <slug> | <status> | <one-line description derived from plan> | <date> | <today> |
```

Use today's date for Created if the original creation date cannot be determined.

Map legacy states to new statuses:
- Active plan → `active`
- Brainstorming (no final_plan.md) → `brainstorming`
- Completed stub → `completed`
- Abandoned stub → `abandoned`
- Paused plan → `active` (they were only paused because of the singleton limitation)

### Step 6 — Clean up

1. Remove `.ai/plans/in_progress/` if it is now empty
2. Do NOT touch `.ai/archive/` — it stays as-is
3. Do NOT touch `.ai/todo.md` — it is global and unaffected
4. Verify no plan artifacts remain at `.ai/` root (except `todo.md`, `plans.md`, `archive/`, `plans/`)

### Step 7 — Report

Present a summary:
- How many plans were migrated
- Slug and status of each
- Any files that were skipped or left in place
- Confirm that `/brainstorm`, `/execute-plan`, etc. will now work with the namespaced layout

## Safety rules

- Never delete `.ai/archive/` or its contents
- Never delete `.ai/todo.md`
- Always confirm with the user before moving files
- If any step fails or an artifact is in an unexpected state, stop and explain rather than guessing
- Do not create plans.md entries for plans that have no artifacts (nothing to track)

## Style rules

- Be terse — this is a migration tool, not a planning session
- Show the user what will happen before doing it
- Confirm slug names before creating directories

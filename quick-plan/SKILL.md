---
name: quick-plan
description: Use this skill when the user wants to create a plan for a smaller, well-understood task directly — skipping the full brainstorm → critique → synthesize cycle. Produces .ai/plans/<slug>/final_plan.md with the same structure as brainstorm-synthesize so that execute-plan and execute-review work identically downstream. Optionally followed by /quick-critique for a Codex review of the plan.
---

# Quick Plan Skill

Your job is to create a lightweight but complete plan for a smaller, well-understood task and write it directly as `final_plan.md` so it can be executed and reviewed through the standard pipeline.

## When to use this skill

Use this skill when:
- the user has a clear, well-scoped task that does not need full brainstorming
- the task is small enough that the brainstorm → critique → synthesize cycle would be overhead
- the user wants to go straight to a plan that `execute-plan` and `execute-review` can consume
- the user explicitly asks for a quick plan

Do not use this skill for:
- large, ambiguous, or exploratory ideas — use `brainstorm` instead
- evolving an existing completed plan — use `evolve` instead
- tasks that are so small they do not need phase tracking at all — just do them directly
- code review, bug fixing, or direct implementation

## Pipeline Context

Two paths feed into execution:

**Full path:**
```
1. brainstorm → 2. brainstorm-critique → 3. brainstorm-synthesize → 4. execute-plan → 5. evolve
```

**Quick path:**
```
1. quick-plan → (optional: quick-critique) → 2. execute-plan → 3. evolve
```

All pipeline skills operate on **namespaced plans**. Each plan has a unique slug and its own directory.

**Directory layout**
- `.ai/plans.md` — index of all plans with slug, status, and description
- `.ai/plans/<slug>/` — all artifacts for a specific plan
- `.ai/plans/<slug>/final_plan.md` — the plan
- `.ai/plans/<slug>/execution_state.md` — execution progress
- `.ai/plans/<slug>/session_log.md` — session history
- `.ai/plans/<slug>/claude_brainstorm.md` — brainstorm artifact
- `.ai/plans/<slug>/codex_critique.md` — critique artifact
- `.ai/plans/<slug>/ollama_critique.md` — optional local Ollama critique artifact
- `.ai/plans/<slug>/evolution_plan.md` — evolution proposal
- `.ai/plans/<slug>/review.md` — active review artifact
- `.ai/plans/<slug>/superseded/` — optional snapshots of older plan revisions before critique-driven overwrite
- `.ai/archive/` — completed, abandoned, or superseded plan artifacts
- `.ai/follow_ups.md` — durable working index of unresolved follow-on artifacts across plans
- `.ai/todo.md` — project-level todo list (global, not per-plan)

**Plan statuses** (tracked in `.ai/plans.md`): `brainstorming` · `active` · `completed` · `abandoned`

**Phase states:** `not started` · `in progress` · `blocked` · `done` · `cancelled`

**Key transition rules**
- `brainstorm` creates a new plan slug and directory. Writes `claude_brainstorm.md` inside it. Sets status to `brainstorming` in `plans.md`.
- `brainstorm-synthesize` writes `final_plan.md` inside a plan directory. Transitions status from `brainstorming` to `active`.
- `quick-plan` creates a new plan slug and directory. Writes `final_plan.md` directly. Sets status to `active` in `plans.md`.
- `execute-plan` creates or resets `execution_state.md` for the plan.
- `execute-review` finishing the last required phase review → copies plan dir to `.ai/archive/<slug>/`, deletes `.ai/plans/<slug>/`, sets status to `completed`.
- `evolve` creates a NEW plan slug + directory referencing a previous plan. Writes `evolution_plan.md` in the new directory.

**This skill's state responsibility:** Create a new plan slug and directory. Produce `.ai/plans/<slug>/final_plan.md` directly. Add an entry to `.ai/plans.md` with status `active`. This skill and `brainstorm-synthesize` are the two skills authorized to write `final_plan.md`.

## Legacy layout detection

Before doing any work, check for a legacy (pre-namespace) layout:

If `.ai/final_plan.md` exists at root AND `.ai/plans.md` does not exist, this is a legacy layout.
Stop and suggest: "Run `/plan-migrate` to upgrade to the namespaced plan layout."
Do not proceed with the legacy layout.

## Plan slug resolution

This skill creates new plans. Resolution works as follows:

1. If the user provided a slug explicitly (e.g., `/quick-plan fix-sidebar-layout`), use it.
2. If not, derive a slug from the task description: kebab-case, 2-4 words, no dates.
3. Confirm the slug with the user before creating the directory, unless the slug was provided explicitly.
4. Apply the collision rules below before creating or overwriting anything.
5. Create `.ai/plans/<slug>/` directory.
6. Add an entry to `.ai/plans.md` with status `active` (create the file if it doesn't exist).

**Collision rules:**

If `.ai/plans.md` already contains a plan with the same slug in `active` status:
- Check whether `.ai/plans/<slug>/execution_state.md` exists.
- If it does NOT exist (plan was quick-planned but never executed): this is a re-plan. Read any existing `.ai/plans/<slug>/codex_critique.md` and `.ai/plans/<slug>/ollama_critique.md` for context, then overwrite `final_plan.md`. If critique artifacts exist, snapshot the old `final_plan.md` into `.ai/plans/<slug>/superseded/` before overwriting. Delete stale critique artifacts after overwriting since they critique the old plan.
- If it DOES exist (execution already started): stop and warn the user. Suggest abandoning the existing plan first or choosing a different slug.

If the same slug already exists with status `brainstorming`: do **not** reuse it. A `brainstorming` slug belongs to the full brainstorm path and may contain `claude_brainstorm.md`. Writing a `final_plan.md` via quick-plan into that directory would mix planning paths. Ask the user to choose a different slug, or to run `brainstorm-synthesize` on the existing brainstorm instead.

If the same slug already exists with status `completed` or `abandoned`, do **not** reuse it. Ask the user to choose a different slug.

## Primary objective

Create a complete, executable plan at:

`.ai/plans/<slug>/final_plan.md`

The plan should be:
- concrete and actionable
- proportional to the task's actual complexity — do not inflate small tasks
- structured identically to what `brainstorm-synthesize` produces, so downstream skills work without modification
- suitable as the basis for `execute-plan` phase-by-phase implementation

## Preconditions

Before starting:
1. Resolve the plan slug (see above)
2. Check for legacy layout
3. Read `.ai/todo.md` if it exists — use **Now** and **Next** items as context. If this plan addresses specific todo items, note which ones so they can be referenced in `## 15. Todo References` of the final plan
4. If re-planning an existing slug, read the existing `codex_critique.md` if present and then read `ollama_critique.md` if present. Treat the Ollama artifact as secondary advisory input, not a replacement for the Codex critique. Incorporate relevant findings without duplicating the same point twice. If the Codex critique contains a provenance note indicating it was generated by Claude as a fallback (not Codex), note this in `## 4. Accepted Critiques` so the distinction is visible downstream.
   If critique artifacts exist and you are about to overwrite `final_plan.md`, snapshot the current plan first to `.ai/plans/<slug>/superseded/YYYYMMDD-HHMMSS-pre-replan-final_plan.md`.
5. Briefly inspect the relevant codebase context if this concerns an existing project
6. Understand the task well enough to produce a plan — if not, ask 1-2 clarifying questions, then proceed

## Core behavior

Be direct. This skill exists because the user wants speed.

Do not engage in extended brainstorming — that is what `/brainstorm` is for. Briefly confirm your understanding of the task if needed, then produce the plan. One or two clarifying questions are fine if genuinely needed; a long back-and-forth is not.

Be project-aware. If the task concerns an existing project, anchor the plan to the current system. Inspect relevant files before writing the plan.

Be proportional. A 2-phase task gets a 2-phase roadmap. A 5-phase task gets a 5-phase roadmap. Do not pad with unnecessary phases or inflate sections that are not relevant.

## Required structure for `.ai/plans/<slug>/final_plan.md`

Use exactly these top-level sections — the same structure as `brainstorm-synthesize` produces:

# Final Plan

## 1. Final Recommendation
State the chosen direction clearly and concisely.

## 2. Why This Direction Won
Explain why this approach is the right one. For small tasks, this can be brief.

## 3. Current Context Summary
If this is an existing project, summarize the relevant current state.
If greenfield, explicitly say so.

## 4. Accepted Critiques
If `.ai/plans/<slug>/codex_critique.md` exists (from a prior `/quick-critique` pass), list the critique points that changed this plan.
If `.ai/plans/<slug>/ollama_critique.md` also exists, include only the additional local-review points that materially changed the plan. Do not duplicate Codex points just because both reviewers raised them.
If accepted critique narrowed the plan relative to an earlier broader version, explicitly state:
- what was narrowed or deferred
- why it was narrowed now
- what evidence or validation would justify reviving the broader path later
If no critique artifact exists, write: "No critique step — this plan was created directly via quick-plan. Run `/quick-critique` to add a Codex critique pass if desired."

## 5. Rejected Critiques
If a critique artifact exists, list rejected points and explain why.
If `ollama_critique.md` exists, handle rejected local-only suggestions here too when they are worth recording.
If no critique artifact exists, write the same note as section 4.

## 6. Final MVP Scope
Define:
- must-have
- should-have-later
- explicitly-not-now

For contained tasks, "should-have-later" and "explicitly-not-now" may be brief or "N/A".
If the plan was narrowed by accepted critique, `should-have-later` and `explicitly-not-now` must preserve the deferred broader direction instead of dropping it silently.

## 7. System Fit
Explain how this fits the existing project or intended system.
Address affected areas, integration points, data/API implications, UX implications, operational implications.
For a self-contained task, keep this proportional.

## 8. Architecture / Solution Shape
Describe the recommended solution structure at a practical level.
Be specific enough to guide implementation.

## 9. Migration / Rollout Approach
If relevant, explain approach. If not relevant, explicitly say so.

## 10. Risks and Mitigations
List the biggest remaining risks. For small tasks, 1-3 items is fine.

## 11. Open Questions
List important unresolved questions. May be empty for well-understood tasks.

## 12. Delivery Roadmap by Phases
Create a complete roadmap broken into feasible phases.

Each phase should be completable in one focused solo work session.

For each phase include:
- phase number and name
- objective
- concrete scope
- why it belongs here in the sequence
- dependencies
- definition of done
- expected artifact or deliverable
- main risk

Keep the number of phases proportional to the task. A small task might have 1-3 phases. Do not split unnecessarily.

## 13. First 10 Concrete Tasks
Give a concrete ordered task list. For a 2-phase task, 5-7 tasks may be enough — do not pad to 10.

## 14. Follow-on Artifacts
List useful next follow-on artifacts or deferred next-path items using flat bullets only.
Use this exact format for each item:
- `<descriptive title> — <short rationale or trigger>`

Rules:
- titles must be descriptive enough to stand alone outside the plan
- include meaningful deferred broader paths here when accepted critique intentionally narrowed scope
- this section feeds `.ai/follow_ups.md`, so do not use vague entries like "maybe later" or "future improvements"
- if there are no follow-on artifacts, write `None needed.`

## 15. Todo References
If `.ai/todo.md` was read and this plan addresses specific todo items, list them here **exactly as they appear in the todo file** (verbatim text, including the `- [ ]` prefix).
These references are used by `execute-review` and `autopilot` to auto-mark todo items as done when the plan is archived.
Do not force a connection — only reference items this plan genuinely addresses.
If no todo items are referenced, omit this section.

## 16. Implementation Handoff
Write a short handoff:
- what to build first
- what to avoid overbuilding
- what to validate early
- where to be especially careful

## Output requirements

Always create or overwrite `.ai/plans/<slug>/final_plan.md`.

After writing, ensure `.ai/plans.md` has this plan's entry with status `active`.
Also create or update `.ai/follow_ups.md` from `## 14. Follow-on Artifacts`.

Provide a short in-chat summary of:
- the plan direction
- number of phases
- suggested next step (`/quick-critique` for a Codex review, or `/execute-plan` to start)

## Decision rules

- Prefer the simplest approach that solves the problem
- Do not overengineer — the user chose quick-plan because the task is well-understood
- Be honest about complexity; if the task turns out to be bigger than expected, say so and suggest `/brainstorm` instead
- Favor additive changes over rewrites
- Keep phases small and finishable

## Project-aware rules

When the task concerns an existing project:
- start from the current system, not from fantasy
- prefer integration over reinvention
- respect existing workflows and architecture
- call out migration or compatibility concerns if they exist
- keep scope honest

## Style rules

- Write crisp markdown
- Be concrete and specific
- Use bullets where useful
- Avoid long rambling paragraphs
- No motivational filler
- No unnecessary detail for sections that are not relevant to this task
- Keep the plan proportional to the task

## File handling

Before finishing:
1. Ensure `.ai/plans/<slug>/final_plan.md` exists with all 16 required sections (section 15 may be omitted if no todo references)
2. Ensure the roadmap phases are concrete and proportional
3. If re-planning from critique: ensure the old plan snapshot exists in `.ai/plans/<slug>/superseded/` before overwrite
4. Sync `.ai/follow_ups.md` with the bundled helper:
   - if `.ai/follow_ups.md` is missing, rebuild it first:
     ```bash
     python3 ~/.claude/skills/follow-up/scripts/sync_follow_ups.py \
       rebuild \
       --plans-index ".ai/plans.md" \
       --plans-dir ".ai/plans" \
       --archive-dir ".ai/archive" \
       --registry ".ai/follow_ups.md"
     ```
   ```bash
   python3 ~/.claude/skills/follow-up/scripts/sync_follow_ups.py \
     sync-plan \
     --source-plan "<slug>" \
     --source-status active \
     --plan-file ".ai/plans/<slug>/final_plan.md" \
     --registry ".ai/follow_ups.md"
   ```
   This preserves stable `FU-*` IDs for unchanged entries, avoids recreating already-started follow-ups as new open rows, creates new IDs for new items, and moves removed open items for this source plan to `## Superseded`.
5. If re-planning: delete stale `.ai/plans/<slug>/codex_critique.md` and `.ai/plans/<slug>/ollama_critique.md` if they existed
6. Ensure `.ai/plans.md` has an entry for this slug with status `active`
7. Then provide the short in-chat summary

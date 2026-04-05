---
name: evolve
description: Use this skill when an implemented feature, module, workflow, MVP, or product already exists and should be evolved toward a stronger next version without drifting into an unjustified rewrite. Works for both greenfield MVPs that completed a plan cycle and specific feature/module improvements. Creates a NEW plan slug referencing the source plan and produces .ai/plans/<new-slug>/evolution_plan.md with a project-aware assessment, high-leverage improvements, phased roadmap, and concrete next steps.
---

# Evolve Skill

Your job is to evolve an already implemented feature, module, workflow, MVP, or product into a stronger next version.

## When to use this skill

Use this skill when:
- something already exists in implemented form — a feature, module, workflow, MVP, or full product
- the current version is usable but rough, limited, incomplete, or clearly MVP-level
- the user wants to improve, strengthen, expand, refine, or mature the current state
- the user wants a v2 direction grounded in current reality rather than greenfield brainstorming
- the user wants a roadmap for improvement without unnecessary disruption

This skill is especially appropriate when:
- the current implementation came from a prior brainstorm or final plan and now needs an evolution path
- a greenfield MVP was completed via `execute-plan` and the user wants to plan the next version
- a feature reached v1 and the user wants to level it up without starting over

Do not use this skill for:
- first-time ideation of a brand-new feature or product
- pure bug fixing
- code review of a diff
- a full rewrite request that is already clearly decided
- simple factual Q&A

## Pipeline Context

This skill is **step 5 of 5** in a planning pipeline:

```
1. brainstorm → 2. brainstorm-critique → 3. brainstorm-synthesize → 4. execute-plan → 5. evolve
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
- `.ai/plans/<slug>/evolution_plan.md` — evolution proposal
- `.ai/plans/<slug>/review.md` — active review artifact
- `.ai/archive/` — completed, abandoned, or superseded plan artifacts
- `.ai/todo.md` — project-level todo list (global, not per-plan)

**Plan statuses** (tracked in `.ai/plans.md`): `brainstorming` · `active` · `completed` · `abandoned`

**Phase states:** `not started` · `in progress` · `blocked` · `done` · `cancelled`

**Key transition rules**
- `brainstorm` creates a new plan slug and directory. Writes `claude_brainstorm.md` inside it. Sets status to `brainstorming` in `plans.md`.
- `brainstorm-synthesize` is the only skill that writes `final_plan.md` inside a plan directory. Transitions status to `active`.
- `execute-plan` creates or resets `execution_state.md` for the plan.
- `execute-review` finishing the last required phase review → copies plan dir to `.ai/archive/<slug>/`, deletes `.ai/plans/<slug>/`, sets status to `completed`.
- `evolve` creates a NEW plan slug + directory referencing a previous plan. Writes `evolution_plan.md` in the new directory.

**This skill's state responsibility:** Read from a SOURCE plan (active or completed) for context. Create a NEW plan slug and directory. Produce `.ai/plans/<new-slug>/evolution_plan.md` as a proposal artifact. Add an entry to `.ai/plans.md` with status `brainstorming`. Do **not** write or modify `final_plan.md` in either the source or new plan. Do not start execution.

## Legacy layout detection

Before doing any work, check for a legacy (pre-namespace) layout:

If `.ai/final_plan.md` exists at root AND `.ai/plans.md` does not exist, this is a legacy layout.
Stop and suggest: "Run `/plan-migrate` to upgrade to the namespaced plan layout."
Do not proceed with the legacy layout.

## Plan slug resolution (dual-slug)

This skill operates with two slugs: a **source** plan to read from and a **new** plan to write to.

### Source plan resolution

1. If the user specified a source plan slug (e.g., `/evolve auth-rewrite`), use it.
2. If not, read `.ai/plans.md`.
3. Filter to plans with status `active` or `completed`.
4. If exactly one matches, use it silently.
5. If zero match, say so. Evolve requires something already built to evolve.
6. If multiple match, list them and ask the user which plan to evolve.

The source plan's artifacts may be in:
- `.ai/plans/<source-slug>/` (if still active)
- `.ai/archive/<source-slug>/` (if completed and archived)

Read whichever location has the artifacts.

### New plan slug

1. If the user provided a new slug, use it.
2. Otherwise, derive one from the source slug + the evolution topic. For example: `auth-rewrite-v2`, `monitoring-observability`, or `ui-dark-mode`.
3. Confirm the slug with the user before creating the directory.
4. Apply the collision and consistency rules below before creating or overwriting anything.
5. Create `.ai/plans/<new-slug>/` directory.
6. Add an entry to `.ai/plans.md` with status `brainstorming`.

The new slug must be distinct from the source slug.

If `.ai/plans.md` already contains the new slug in `brainstorming` status, and `.ai/plans/<new-slug>/` contains `evolution_plan.md` but does **not** contain `final_plan.md` or `execution_state.md`, treat this as a re-evolve for the same unfinished evolution plan and overwrite only `evolution_plan.md`.

If the new slug already exists with status `active`, `completed`, or `abandoned`, or if `.ai/archive/<new-slug>/` already exists, do **not** reuse it. Choose a different slug. Never overwrite an archived plan namespace or a live execution namespace during evolve.

If a supposedly reusable `brainstorming` new-slug directory already contains `final_plan.md` or `execution_state.md`, stop and report the mixed state instead of overwriting anything.

## Primary objective

Create a high-quality evolution document at:

`.ai/plans/<new-slug>/evolution_plan.md`

The document should reference the source plan slug for traceability and be useful as input for:
- implementation planning
- a v2 roadmap
- further critique or synthesis
- generation of follow-on specs such as README.md, TASKS.md, ARCHITECTURE.md, DB_SCHEMA.md, or API_CONTRACTS.md

## Preconditions

Before starting:
1. Resolve source plan slug and new plan slug (see above)
2. Read the source plan's artifacts for context:
   - `final_plan.md` — prior plan context
   - `execution_state.md` — what was completed
   - `claude_brainstorm.md` — original brainstorm if useful
   - `codex_critique.md` — prior critique if useful
   - existing implementation files, README, architecture notes, or relevant code
3. If the current implementation context is incomplete, say what assumptions you are making
4. Prefer grounding in the existing project rather than inventing an idealized redesign
5. Do not modify any files in the source plan's directory. This skill reads from the source, writes only to the new plan directory.

## Output requirements

Always create or overwrite `.ai/plans/<new-slug>/evolution_plan.md`.

Also provide a short in-chat summary of:
- the recommended v2 direction
- the biggest current weakness
- the most important next step

If the `.ai/plans/<new-slug>/` directory does not exist, create it.

## Core behavior

Be project-aware and implementation-aware.

Your job is not to re-brainstorm from zero.
Your job is to evaluate the current implemented reality and evolve it intelligently.

When relevant, explicitly reason about:
- what currently exists
- how close the implementation is to the original intent
- what is already working
- where friction or weakness appears
- what should remain stable
- what should be improved first
- what would require additive work vs refactor work
- whether deeper structural change is justified

## Evolution principles

Bias strongly toward:
- evolution over rewrite
- leverage over completeness
- practical user value
- incremental progress
- protecting working parts
- realistic scope
- session-sized execution phases

Avoid:
- greenfield fantasy
- rebuild enthusiasm without evidence
- broad feature creep
- architecture churn for weak reasons
- pretending the current implementation does not exist
- changing too many surfaces at once

## Required structure for `.ai/plans/<new-slug>/evolution_plan.md`

Use exactly these top-level sections:

# Evolution Plan

## 0. Source Plan
State the source plan slug and where its artifacts were read from (`.ai/plans/<source-slug>/` or `.ai/archive/<source-slug>/`).

## 1. Subject Snapshot
Summarize what is being evolved and its current purpose in 3-6 sentences.

## 2. Current State / Implemented Reality
Describe what currently exists.
Address:
- what is implemented
- what is partial
- what is missing
- what appears stable
- what appears rough or limited

## 3. Original Intent vs Current Reality
If prior planning artifacts exist, compare the current implementation against the original intent.
Explain:
- what was realized well
- what was postponed
- what drifted
- what turned out differently in practice

If no prior artifact exists, explicitly say so.

## 4. What Works Well
List the parts worth preserving.

## 5. Main Frictions / Gaps
Identify the biggest weaknesses, rough edges, missing pieces, or bottlenecks.

## 6. Constraints
List the relevant technical, product, UX, architecture, time, business, or maintenance constraints that should shape evolution.

## 7. Evolution Options
Provide 3-5 plausible ways to evolve the current state.
For each option include:
- short name
- what it changes
- strengths
- weaknesses
- compatibility with the current system
- complexity level: low / medium / high

## 8. Recommended v2 Direction
Pick one direction and explain why it is the best next evolution.

## 9. Additive Changes vs Refactor Changes
Clearly separate:
- additive improvements
- contained refactors
- deeper structural changes

State which category the recommended direction primarily belongs to.

## 10. What Should Stay Untouched
Explicitly list parts that should remain stable for now.

## 11. Risks and Failure Modes
List the main ways the v2 effort could fail or create regressions.

## 12. Delivery Roadmap by Phases
Create a complete roadmap broken into feasible phases.

Each phase should be small enough to be tackled in one focused work session whenever reasonably possible.
If a phase is too large for one realistic session, split it into smaller phases.

For each phase include:
- phase number and name
- objective
- why it comes at this point
- concrete scope
- dependencies
- definition of done
- expected artifact or deliverable
- main risk or ambiguity

Cover the path from the current state to a meaningfully improved v2, not just the immediate next steps.
Prefer narrow, finishable phases over broad vague work packages.

## 13. Open Questions
List the most important unanswered questions.

## 14. First 10 Concrete Tasks
Give a concrete ordered task list for immediate execution.
These should align with the early phases above.

## 15. Follow-on Artifacts
List the most useful next documents to generate, such as:
- README.md
- TASKS.md
- ARCHITECTURE.md
- DB_SCHEMA.md
- API_CONTRACTS.md
- MIGRATION_PLAN.md
- TEST_PLAN.md

## 16. Implementation Handoff
Write a short handoff for the next agent or engineer.
State:
- what to improve first
- what to avoid overbuilding
- what to validate early
- where regressions are most likely
- where extra care is needed

## Decision quality rules

- Start from the current implementation, not from fantasy
- Prefer strong distinctions over vague overlap
- Name tradeoffs explicitly
- Be honest if the current implementation is weaker than expected
- Favor evolution over rewrite unless a rewrite is clearly justified
- Protect working surfaces
- Separate user-facing pain from architectural pain
- Keep scope honest
- Make the next step easy to start

## Existing-project bias rules

When evolving an existing project:
- prefer integration over reinvention
- explicitly evaluate whether improvement beats replacement
- call out maintenance burden
- distinguish clearly between:
  - quick win
  - contained refactor
  - deeper rewrite
- only recommend deeper rewrite when the current system materially blocks progress

## Style rules

- Write crisp markdown
- Be concrete and specific
- Use bullets where useful
- Avoid long rambling paragraphs
- Avoid repetition
- No motivational filler
- No code unless it directly sharpens the plan

## Next Steps After Evolve

After producing `.ai/plans/<new-slug>/evolution_plan.md`, the pipeline continues in one of two ways depending on scope:

**Option A — Full planning cycle (recommended for larger or uncertain evolutions):**
Run `brainstorm-synthesize <new-slug>` next. It will read `evolution_plan.md` as the planning input (instead of brainstorm + critique) and produce `final_plan.md` in the same plan directory. Then run `execute-plan <new-slug>`.

**Option B — Direct execution (for smaller, clear evolutions):**
If the evolution scope is narrow and well-understood, the user may choose to move toward execution immediately after confirming the evolution plan. Even then, do **not** execute directly from `evolution_plan.md`. First produce `final_plan.md` via synthesize, then run `execute-plan`.

Either way, do not start execution from `evolution_plan.md` without first ensuring `final_plan.md` exists in the plan directory.

Always surface these two options clearly in the in-chat summary at the end of the skill.

## File handling

Before finishing:
1. Ensure `.ai/plans/<new-slug>/evolution_plan.md` exists
2. Ensure it contains all required sections including `## 0. Source Plan`
3. Ensure the roadmap phases are substantive and session-sized
4. Ensure "What Should Stay Untouched" is explicit
5. Ensure `.ai/plans.md` has an entry for the new slug with status `brainstorming`
6. Then provide a short in-chat summary of the recommended v2 direction, biggest weakness, and most important next step

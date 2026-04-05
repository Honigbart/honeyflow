---
name: evolve
description: Use this skill when an implemented feature, module, workflow, MVP, or product already exists and should be evolved toward a stronger next version without drifting into an unjustified rewrite. Works for both greenfield MVPs that completed a plan cycle and specific feature/module improvements. Produces .ai/evolution_plan.md with a project-aware assessment, high-leverage improvements, phased roadmap, and concrete next steps.
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

All five skills share a canonical file layout and state model.

**Canonical files**
- `.ai/final_plan.md` — active plan, or a status stub when no plan is active
- `.ai/execution_state.md` — execution progress for the active plan
- `.ai/session_log.md` — chronological history across execution sessions
- `.ai/archive/` — completed, superseded, or abandoned plans
- `.ai/plans/in_progress/` — paused plans that may resume
- `.ai/evolution_plan.md` — evolution proposal artifact; not active until confirmed
- `.ai/claude_brainstorm.md` — current brainstorm artifact
- `.ai/codex_critique.md` — current critique artifact

**Plan states:** `active` · `paused` (in `plans/in_progress/`) · `superseded` (in `archive/`) · `completed` (in `archive/`) · `abandoned` (in `archive/`)

**Phase states:** `not started` · `in progress` · `blocked` · `done` · `cancelled`

**Key transition rules**
- `brainstorm` preserves any active plan as `paused` in `.ai/plans/in_progress/`. It does **not** write a new `final_plan.md`.
- `brainstorm-synthesize` is the only skill that writes a new active `.ai/final_plan.md`.
- `execute-plan` creates or resets `.ai/execution_state.md` for the active plan.
- `execute-plan` completing all implementation phases does **not** by itself archive the plan. The plan remains active until required phase reviews are complete.
- `execute-review` finishing the last required phase review for a fully implemented plan → archive plan to `.ai/archive/`, mark `execution_state.md` as completed, leave completed stub in `final_plan.md`.
- `evolve` writes `.ai/evolution_plan.md` as a proposal artifact only. Not active until user confirms and synthesizes or executes directly.

**This skill's state responsibility:** Produce `.ai/evolution_plan.md` as a proposal artifact. Do **not** write or modify `final_plan.md`. Do not start execution. The user must confirm the direction before the pipeline continues.

## Primary objective

Create a high-quality evolution document at:

`.ai/evolution_plan.md`

The document should be useful as input for:
- implementation planning
- a v2 roadmap
- further critique or synthesis
- generation of follow-on specs such as README.md, TASKS.md, ARCHITECTURE.md, DB_SCHEMA.md, or API_CONTRACTS.md

## Preconditions

Before starting:
1. Look for relevant context, especially:
   - `.ai/final_plan.md` — if present and active, read as prior plan context; if it contains an inactive status stub, treat it as historical reference only, not an active plan
   - `.ai/execution_state.md` — useful for understanding what was completed
   - `.ai/claude_brainstorm.md`
   - `.ai/codex_critique.md`
   - existing implementation files
   - README, architecture notes, task docs, or relevant code
   An inactive status stub is any `final_plan.md` that:
   - begins with `# Final Plan Status`
   - contains `- active_plan: none`
   - records `- status: completed` or `- status: abandoned`
2. If the current implementation context is incomplete, say what assumptions you are making
3. Prefer grounding in the existing project rather than inventing an idealized redesign
4. Do not modify any plan state files. This skill is read-only with respect to `final_plan.md` and `execution_state.md`.

## Output requirements

Always create or overwrite `.ai/evolution_plan.md`.

Also provide a short in-chat summary of:
- the recommended v2 direction
- the biggest current weakness
- the most important next step

If the `.ai` directory does not exist, create it.

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

## Required structure for `.ai/evolution_plan.md`

Use exactly these top-level sections:

# Evolution Plan

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

After producing `.ai/evolution_plan.md`, the pipeline continues in one of two ways depending on scope:

**Option A — Full planning cycle (recommended for larger or uncertain evolutions):**
Run `brainstorm-synthesize` next. It will read `evolution_plan.md` as the planning input (instead of brainstorm + critique) and produce a new active `final_plan.md`. Then run `execute-plan`.

**Option B — Direct execution (for smaller, clear evolutions):**
If the evolution scope is narrow and well-understood, the user may choose to move toward execution immediately after confirming the evolution plan. Even then, do **not** execute directly from `.ai/evolution_plan.md`. First produce or explicitly promote a `.ai/final_plan.md` that reflects the confirmed direction, then run `execute-plan`.

Either way, do not start execution from `evolution_plan.md` without first ensuring `final_plan.md` reflects the confirmed direction.

Always surface these two options clearly in the in-chat summary at the end of the skill.

## File handling

Before finishing:
1. Ensure `.ai/evolution_plan.md` exists
2. Ensure it contains all required sections
3. Ensure the roadmap phases are substantive and session-sized
4. Ensure "What Should Stay Untouched" is explicit
5. Then provide a short in-chat summary of the recommended v2 direction, biggest weakness, and most important next step

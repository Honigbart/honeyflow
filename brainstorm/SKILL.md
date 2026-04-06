---
name: brainstorm
description: Use this skill when the user wants structured ideation for a new or existing project, including feature ideas, rebuilds, refactors, workflow changes, product directions, and project-aware brainstorming that should produce a critique-ready artifact at .ai/plans/<slug>/claude_brainstorm.md.
---

# Brainstorm Skill

Your job is to turn an early idea into a strong, structured brainstorming artifact that is useful for decision-making in the context of a real project. It is very important, that you include the user in this brainstorming process. Don't generate the output file after the initial skill call by the user. Ping pong (aka brainstorm) his thoughts with him, ask him questions, and provide suggestions. Keep it brief but keep it real, don't scratch only the surface.

## When to use this skill

Use this skill when the user:
- wants to brainstorm a new product, app, feature, workflow, or content concept
- wants to improve, rebuild, replace, simplify, or extend something in an existing project
- wants structured exploration before implementation
- wants an artifact that can later be critiqued by another agent

This skill is especially appropriate when the idea must be evaluated against an existing codebase, product, architecture, workflow, or business direction.

Do not use this skill for:
- code review
- git diff review
- fixing a clearly defined bug
- implementing a plan that is already finalized
- simple factual Q&A

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

**Autopilot:** `/autopilot` can replace the manual `/execute-plan` + `/execute-review` loop for fully autonomous execution.

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
- `brainstorm-synthesize` writes `final_plan.md` inside a plan directory. Transitions status from `brainstorming` to `active`.
- `quick-plan` creates a new plan slug and directory. Writes `final_plan.md` directly. Sets status to `active` in `plans.md`.
- `execute-plan` creates or resets `execution_state.md` for the plan.
- `execute-review` finishing the last required phase review → copies plan dir to `.ai/archive/<slug>/`, deletes `.ai/plans/<slug>/`, sets status to `completed`.
- `evolve` creates a NEW plan slug + directory referencing a previous plan. Writes `evolution_plan.md` in the new directory.
- `autopilot` drives execution and review of all phases autonomously. Uses the same artifacts and rules as `execute-plan` and `execute-review`.

**This skill's state responsibility:** Create a new plan slug and directory. Produce `.ai/plans/<slug>/claude_brainstorm.md`. Add an entry to `.ai/plans.md` with status `brainstorming`.

## Legacy layout detection

Before doing any work, check for a legacy (pre-namespace) layout:

If `.ai/final_plan.md` exists at root AND `.ai/plans.md` does not exist, this is a legacy layout.
Stop and suggest: "Run `/plan-migrate` to upgrade to the namespaced plan layout."
Do not proceed with the legacy layout.

## Plan slug resolution

This skill creates new plans. Resolution works as follows:

1. If the user provided a slug explicitly (e.g., `/brainstorm auth-rewrite`), use it.
2. If not, after the brainstorming discussion, derive a slug from the topic: kebab-case, 2-4 words, no dates.
3. Confirm the slug with the user before creating the directory.
4. Apply the collision and consistency rules below before creating or overwriting anything.
5. Create `.ai/plans/<slug>/` directory.
6. Add an entry to `.ai/plans.md` with status `brainstorming` (create the file if it doesn't exist).

If `.ai/plans.md` already contains a plan with the same slug in `brainstorming` status, this is a re-brainstorm for that plan. Overwrite the existing `claude_brainstorm.md` in that directory instead of creating a new one.

If the same slug already exists with status `active`, `completed`, or `abandoned`, do **not** reuse it for brainstorm. Reusing a non-brainstorming slug can mix new ideation artifacts with an existing `final_plan.md`, `execution_state.md`, `session_log.md`, or archived plan history. Ask the user to choose a different slug instead. If they want to build on an already implemented plan, prefer `evolve` so the prior plan remains intact.

Never change an existing non-`brainstorming` plan entry back to `brainstorming` as part of this skill.

If a supposedly `brainstorming` plan directory already contains `final_plan.md` or `execution_state.md`, stop and report the mixed state instead of overwriting anything. That directory is already inconsistent and must be resolved intentionally.

## Primary objective

After discussing and brainstorming with the user, create a high-quality brainstorming document at:

`.ai/plans/<slug>/claude_brainstorm.md`

The document should be useful as input for:
- Codex critique
- later synthesis into a final plan
- conversion into README.md, AGENTS.md, TASKS.md, or architecture docs

## Output requirements

Always create or overwrite `.ai/plans/<slug>/claude_brainstorm.md`.

Also present a short summary in chat, but the full artifact belongs in the file.

If the `.ai/plans/<slug>/` directory does not exist, create it (and `.ai/plans/` if needed).

## Todo-aware context

Before starting the brainstorm, check whether `.ai/todo.md` exists. If it does:
- Read it and use items from **Now** and **Next** as additional context for the brainstorm.
- If the brainstorm clearly addresses one or more todo items, note which items it addresses in the brainstorm artifact (see the "Todo Context" section below).
- Do not force a connection — only link items that the brainstorm genuinely addresses.

## Core behavior

Be project-aware.

If the user is brainstorming within an existing project, you must anchor the brainstorm to the current system rather than drifting into a greenfield redesign.

When relevant, explicitly reason about:
- current product state
- existing architecture
- current workflows
- integration points
- migration costs
- backward compatibility
- technical debt
- team or solo-developer reality
- likely maintenance burden

If the current project context is incomplete, state assumptions clearly instead of pretending certainty.

## Brainstorming principles

Be expansive, but not fluffy.

Push for:
- clarity
- leverage
- concrete options
- practical tradeoffs
- realistic MVP thinking
- compatibility with current project reality
- hidden constraints
- monetization or usefulness if relevant

Avoid:
- generic startup cliches
- empty enthusiasm
- pretending uncertainty does not exist
- locking in one idea too early
- implementation detail overload unless it materially affects direction
- proposing a full rewrite unless there is a strong reason

## Required structure for `.ai/plans/<slug>/claude_brainstorm.md`

Use exactly these top-level sections:

# Brainstorm

## 1. Idea Snapshot
Summarize the idea in 3-6 sentences.

## 2. Current State / Existing Context
If this is an existing project, summarize the relevant current system, feature, workflow, architecture, or product context.
If this is a new project, explicitly say that there is no meaningful existing system yet.

## 3. Problem / Desire
What problem, desire, or opportunity does this idea address?

## 4. Target User
Who is this for?
Include primary and optional secondary audience.

## 5. Why This Could Matter
Why might users care?
Why now?
What makes this potentially interesting or valuable?

## 6. Core Assumptions
List the main assumptions the idea depends on.

## 7. Constraints
List known technical, market, legal, UX, time, budget, skill, product, or distribution constraints.

## 8. System Fit
Explain how this idea would fit into the current project or system.
Address:
- affected areas
- likely dependencies
- integration points
- data model or API implications
- UX implications
- operational implications if relevant

If this is a new project, state the likely foundational system implications instead.

## 9. Option Space
Provide 3-5 plausible directions or variants.
For each option include:
- short name
- what it is
- strengths
- weaknesses
- compatibility with the current system
- complexity level: low / medium / high

## 10. Recommended Direction
Pick one direction for now and explain why.

## 11. MVP Shape
Describe the smallest version worth building.
Include:
- must-have
- should-have-later
- explicitly-not-now

## 12. Migration / Refactor Considerations
If this touches an existing project, explain:
- whether this is additive, replacement, or rebuild work
- backward compatibility concerns
- migration concerns
- rollout strategy ideas
- what should remain untouched

If not relevant, explicitly say so.

## 13. Risks and Failure Modes
List the main ways this could fail.

## 14. Open Questions
List the most important unanswered questions.

## 15. Next Moves
Give the next 5-10 concrete steps.

## 16. Codex Critique Handoff
Write a short section addressed to a skeptical reviewer.
It should explicitly invite critique of:
- weak assumptions
- overengineering
- hidden costs
- migration risk
- integration risk
- missing edge cases
- simpler alternatives

## 17. Todo Context
If `.ai/todo.md` was read and this brainstorm addresses specific todo items, list them here exactly as they appear in the todo file.
If no todo items are relevant, omit this section entirely.

## Decision quality rules

- Prefer strong distinctions over vague overlap
- Name tradeoffs explicitly
- If the user's idea is weak, say so constructively
- If multiple directions are viable, rank them
- If the idea is premature, shape it before narrowing it
- Surface unknowns instead of inventing certainty
- Favor evolution over rewrite unless a rewrite is justified
- Respect existing project constraints unless there is a compelling reason not to

## Existing-project bias rules

When brainstorming for an existing project:
- start from the current system, not from fantasy
- prefer options that integrate cleanly
- explicitly evaluate whether improvement is better than replacement
- call out where the current architecture helps or hurts
- mention hidden maintenance burden
- be careful with rebuild enthusiasm
- distinguish clearly between:
  - quick win
  - medium refactor
  - deep rewrite

## Style rules

- Write crisp markdown
- Be concrete and specific
- Use bullets where they improve readability
- Avoid long rambling paragraphs
- Avoid repetition
- No motivational filler
- No code unless it directly clarifies the concept

## Stale artifact cleanup

After writing `.ai/plans/<slug>/claude_brainstorm.md`, check whether `.ai/plans/<slug>/codex_critique.md` exists. If it does, **delete it** — it critiques a previous brainstorm and is now stale. The user must re-run `brainstorm-critique` to generate a fresh critique for the new brainstorm.

Also check whether `.ai/plans/<slug>/evolution_plan.md` exists. If it does, treat it as stale for this new brainstorm cycle. Prefer **moving** it to `.ai/archive/` with a date-prefixed filename such as `YYYYMMDD-<slug>-stale-evolution-plan.md`. If archiving is not practical, say so clearly and delete it only as a fallback.

Do not delete or rewrite `final_plan.md`, `execution_state.md`, or `session_log.md` here. If those files exist for this slug, stop and surface the inconsistency instead of trying to clean it up automatically.

Mention the stale artifact cleanup in the in-chat summary so the user knows critique and evolution artifacts from the prior cycle were retired.

## File handling

Before finishing:
1. Ensure `.ai/plans/<slug>/claude_brainstorm.md` exists
2. Ensure it contains all required sections
3. Ensure the "Codex Critique Handoff" section is present
4. If this is an existing project, ensure "Current State / Existing Context", "System Fit", and "Migration / Refactor Considerations" are substantive
5. Delete `.ai/plans/<slug>/codex_critique.md` if it exists (stale from prior brainstorm)
6. Move stale `.ai/plans/<slug>/evolution_plan.md` to `.ai/archive/` if it exists
7. Ensure `.ai/plans.md` has an entry for this slug with status `brainstorming`
8. Then provide a short in-chat summary of the recommended direction and biggest risk

---
name: brainstorm-synthesize
description: Use this skill when planning artifacts in .ai/plans/<slug>/ need to be synthesized into a final project-aware plan. Supports the standard brainstorm path (claude_brainstorm.md with optional or required critique depending on user choice) and the evolution path (evolution_plan.md, optionally with critique). Produces .ai/plans/<slug>/final_plan.md with a clear recommendation, critique handling, MVP scope, rollout shape, and concrete next tasks.
---

# Brainstorm Synthesize Skill

Your job is to synthesize a brainstorming artifact and a skeptical critique into one final decision-ready plan.

## When to use this skill

Use this skill when:
- `.ai/plans/<slug>/claude_brainstorm.md` exists and should be synthesized into a final plan
- `.ai/plans/<slug>/codex_critique.md` exists and should be incorporated when available
- `.ai/plans/<slug>/evolution_plan.md` exists and should be turned into an active final plan
- the user wants a final recommendation
- the user wants a merged plan after critique
- the user wants to proceed intentionally without a critique artifact after being warned
- the user wants a practical direction for implementation or further specification

Do not use this skill for:
- generating the initial brainstorm
- generating the critique
- code review
- git diff review
- bug fixing
- direct implementation work

## Pipeline Context

This skill is **step 3 of 5** in a planning pipeline:

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

**This skill's state responsibility:** Write `.ai/plans/<slug>/final_plan.md`. This is the **only** skill authorized to create or replace a plan's `final_plan.md`. Update `plans.md` status from `brainstorming` to `active`.

## Legacy layout detection

Before doing any work, check for a legacy (pre-namespace) layout:

If `.ai/final_plan.md` exists at root AND `.ai/plans.md` does not exist, this is a legacy layout.
Stop and suggest: "Run `/plan-migrate` to upgrade to the namespaced plan layout."
Do not proceed with the legacy layout.

## Plan slug resolution

Every invocation must resolve a plan slug before doing work.

1. If the user provided a slug explicitly (e.g., `/brainstorm-synthesize auth-rewrite`), use it.
2. If not, read `.ai/plans.md`.
3. Filter to plans with status `brainstorming` that have input artifacts (`claude_brainstorm.md` or `evolution_plan.md`) in their directory.
4. If exactly one plan matches, use it silently.
5. If zero match, say so clearly and stop.
6. If multiple match, list them and ask the user to choose.

## Primary objective

Create a final plan at:

`.ai/plans/<slug>/final_plan.md`

The plan should:
- preserve the strongest parts of the brainstorm
- incorporate the best critique points
- reject weak or overly pessimistic critique where appropriate
- produce a clear direction instead of averaging everything together
- be suitable as the basis for implementation planning, specs, or task generation

## Preconditions

Before starting:

1. Resolve the plan slug (see above).

2. **Determine input sources.** This skill can synthesize from two input paths:
   - **Standard path:** `.ai/plans/<slug>/claude_brainstorm.md` + `.ai/plans/<slug>/codex_critique.md` (after brainstorm → critique)
   - **Evolution path:** `.ai/plans/<slug>/evolution_plan.md` alone or with `.ai/plans/<slug>/codex_critique.md` (after evolve)

   **Conflict rule:** If both `claude_brainstorm.md` and `evolution_plan.md` exist in the plan directory, **stop and ask the user** which input path to follow. Do not silently merge artifacts from two different planning cycles — they may be unrelated. Present both options and let the user choose.

   If only one path has artifacts, use that path. If neither path has artifacts, say so clearly and stop.

3. If using the **standard path** and `claude_brainstorm.md` exists but `codex_critique.md` does not, stop and ask the user whether to:
   - run `brainstorm-critique` first, or
   - proceed intentionally without a critique artifact

   If the user explicitly chooses to proceed without critique, do so honestly. Do **not** invent critique content.

4. If using the **evolution path**, `evolution_plan.md` is sufficient on its own. `codex_critique.md` is optional context if present.
5. If inputs are present, read them fully before synthesizing.

## Output requirements

Always create or overwrite `.ai/plans/<slug>/final_plan.md`.

After writing, update `.ai/plans.md`: set this plan's status from `brainstorming` to `active`.

Also provide a short in-chat summary of:
- the chosen direction
- the biggest remaining risk
- the most important next step

## Core synthesis stance

Be decisive.

Do not merely blend both documents together.
Do not mechanically average their positions.
Do not preserve bad ideas for the sake of compromise.

Your role is to act like a lead architect / product lead making the final call.

You must:
- keep what is strong
- cut what is weak
- narrow scope where helpful
- preserve ambition where justified
- make tradeoffs explicit
- produce a buildable direction

## Project-aware synthesis rules

If the topic concerns an existing project, explicitly optimize for:
- fit with the current system
- reasonable migration and rollout shape
- low unnecessary disruption
- maintainability
- realistic scope for the actual project context
- additive improvement over rewrite unless rewrite is clearly justified

If the topic is greenfield, explicitly optimize for:
- sharp problem framing
- narrow MVP
- fastest credible path to validation
- avoidance of unnecessary infrastructure or architecture

## Decision rules

- Prefer one clear direction over multiple half-committed directions
- Accept critique when it improves realism, scope, or system fit
- Reject critique when it is too conservative, misreads the goal, or cuts away the core value
- Favor the smallest version that still proves something meaningful
- Avoid rewrites unless they are strongly justified
- Preserve strategic upside without bloating the MVP
- Surface unresolved questions instead of hiding them

## Required structure for `.ai/plans/<slug>/final_plan.md`

Use exactly these top-level sections:

# Final Plan

## 1. Final Recommendation
State the chosen direction clearly and confidently.

## 2. Why This Direction Won
Explain why this direction is better than the main alternatives.

## 3. Current Context Summary
If this is an existing project, summarize the relevant current system, workflow, or architectural context.
If greenfield, explicitly say so.

## 4. Accepted Critiques
List the critique points that should change the plan.
If no critique artifact was available, explicitly say so.

## 5. Rejected Critiques
List the critique points that should not change the plan, and explain why.
If no critique artifact was available, explicitly say so.

## 6. Final MVP Scope
Define:
- must-have
- should-have-later
- explicitly-not-now

## 7. System Fit
Explain how this final direction fits the existing project or intended system.
Address:
- affected areas
- integration points
- data/API implications
- UX implications
- operational implications if relevant

## 8. Architecture / Solution Shape
Describe the recommended solution structure at a practical level.
Be specific enough to guide implementation planning, but do not drift into unnecessary detail.

## 9. Migration / Rollout Approach
If relevant, explain:
- additive vs replacement vs rebuild
- backward compatibility considerations
- rollout approach
- what should remain untouched
- how risk should be contained

If not relevant, explicitly say so.

## 10. Risks and Mitigations
List the biggest remaining risks and how to reduce them.

## 11. Open Questions
List the important unresolved questions that still matter.

## 12. Delivery Roadmap by Phases
Create a complete roadmap broken into feasible phases.

A phase should usually be small enough to complete in one focused solo work session.
If that is not realistic, split it into smaller phases until it is.

For each phase include:
- phase number and name
- objective
- concrete scope
- why it belongs here in the sequence
- dependencies
- definition of done
- expected artifact or deliverable
- main risk

The roadmap should cover the path from the current state to a usable first version, not just the immediate next steps.
Do not collapse multiple major implementation steps into one oversized phase.

## 13. First 10 Concrete Tasks
Give a concrete ordered task list that could directly guide work.

## 14. Follow-on Artifacts
List the most useful next documents to generate next, such as:
- README.md
- AGENTS.md
- TASKS.md
- ARCHITECTURE.md
- DB_SCHEMA.md
- API_CONTRACTS.md

## 15. Todo References
If the brainstorm artifact contains a "Todo Context" section listing todo items this plan addresses, carry those references here verbatim.
These references are used by `execute-review` to mark todo items as done when the plan is archived.
If no todo items are referenced, omit this section.

## 16. Implementation Handoff
Write a short handoff for the next agent or engineer.
State:
- what to build first
- what to avoid overbuilding
- what to validate early
- where to be especially careful

## Synthesis quality rules

- Be decisive, not diplomatic
- Preserve the best insight from both files
- Distinguish core direction from optional detail
- Keep scope honest
- Call out when the brainstorm was too optimistic
- Call out when the critique was too conservative
- Prefer practical leverage over theoretical completeness
- Avoid repetition
- Avoid vague wording like "it depends" unless followed by a concrete decision

## Existing-project bias rules

When the topic is about an existing project:
- prefer integration over reinvention
- favor incremental improvement where possible
- explicitly justify any rebuild recommendation
- respect existing workflows and architecture unless they are the actual problem
- call out hidden maintenance burden
- make migration risk visible

## Style rules

- Write crisp markdown
- Be concrete and specific
- Use bullets where useful
- Avoid long rambling paragraphs
- Avoid repetition
- No motivational filler
- No code unless it directly sharpens the plan

## File handling

Before finishing:
1. Ensure `.ai/plans/<slug>/final_plan.md` exists
2. Ensure it contains all required sections
3. Ensure "Accepted Critiques" and "Rejected Critiques" are both substantive, or explicitly state that no critique artifact was available
4. Ensure the plan ends with a clear implementation handoff
5. Ensure `.ai/plans.md` status for this slug is updated to `active`
6. Then provide a short in-chat summary of the chosen direction, biggest remaining risk, and most important next step

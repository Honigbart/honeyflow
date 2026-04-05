---
name: brainstorm
description: Use this skill when the user wants structured ideation for a new or existing project, including feature ideas, rebuilds, refactors, workflow changes, product directions, and project-aware brainstorming that should produce a critique-ready artifact at .ai/claude_brainstorm.md.
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

This skill is **step 1 of 5** in a planning pipeline:

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

**This skill's state responsibility:** Produce `.ai/claude_brainstorm.md`. Preserve any active plan as `paused` (see section "Handling an Existing Unfinished Plan"). Do not write or modify `final_plan.md`.

## Primary objective

After discussing and brainstorming with the user, create a high-quality brainstorming document at:

`.ai/claude_brainstorm.md`

The document should be useful as input for:
- Codex critique
- later synthesis into a final plan
- conversion into README.md, AGENTS.md, TASKS.md, or architecture docs

## Output requirements

Always create or overwrite `.ai/claude_brainstorm.md`.

Also present a short summary in chat, but the full artifact belongs in the file.

If the `.ai` directory does not exist, create it.

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
- generic startup clichés
- empty enthusiasm
- pretending uncertainty does not exist
- locking in one idea too early
- implementation detail overload unless it materially affects direction
- proposing a full rewrite unless there is a strong reason

## Required structure for `.ai/claude_brainstorm.md`

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
- If the user’s idea is weak, say so constructively
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

After writing `.ai/claude_brainstorm.md`, check whether `.ai/codex_critique.md` exists. If it does, **delete it** — it critiques a previous brainstorm and is now stale. The user must re-run `brainstorm-critique` to generate a fresh critique for the new brainstorm.

Also check whether `.ai/evolution_plan.md` exists. If it does, treat it as stale for this new brainstorm cycle. Do **not** silently leave it in place where it can confuse later synthesis. Prefer **moving** it to `.ai/archive/` (create the archive directory if needed) with a date-prefixed filename such as `YYYYMMDD-stale-evolution-plan.md`. If archiving is not practical, say so clearly and delete it only as a fallback.

Mention the stale artifact cleanup in the in-chat summary so the user knows critique and evolution artifacts from the prior cycle were retired.

## File handling

Before finishing:
1. Ensure `.ai/claude_brainstorm.md` exists
2. Ensure it contains all required sections
3. Ensure the "Codex Critique Handoff" section is present
4. If this is an existing project, ensure "Current State / Existing Context", "System Fit", and "Migration / Refactor Considerations" are substantive
5. Delete `.ai/codex_critique.md` if it exists (stale from prior brainstorm)
6. Move stale `.ai/evolution_plan.md` to `.ai/archive/` if it exists, creating `.ai/archive/` first if needed
7. Then provide a short in-chat summary of the recommended direction and biggest risk

## Handling an Existing Unfinished Plan

Before starting a new brainstorm, check whether `.ai/final_plan.md` already exists and whether it represents an unfinished active plan.

If there is no active unfinished plan:
- proceed normally

Treat `.ai/final_plan.md` as an inactive status stub if any of these are true:
- it begins with `# Final Plan Status`
- it contains `- active_plan: none`
- it records `- status: completed` or `- status: abandoned`

A completed or abandoned status stub in `.ai/final_plan.md` does not qualify as an active plan — proceed normally without preserving anything.

If there is a genuinely active or in-progress plan:
- do not overwrite it silently
- move the current plan before proceeding

Move it by:
1. creating `.ai/plans/in_progress/` if needed
2. **moving** (not copying) `.ai/final_plan.md` into `.ai/plans/in_progress/` — the original must no longer exist at `.ai/final_plan.md`
3. using a filename that contains:
   - the date in `YYYYMMDD` format
   - a short kebab-case summary of the plan
   - the suffix `-paused`

Example:
`20260403-new-prompt-ui-paused.md`

If `.ai/execution_state.md` exists **and** reflects an active or in-progress plan (not a completed or abandoned state), also **move** it to `.ai/plans/in_progress/` with a matching filename:
`20260403-new-prompt-ui-paused.execution_state.md`

Delete the originals from `.ai/` after moving. Do not leave stale copies at `.ai/final_plan.md` or `.ai/execution_state.md`.

### After moving the active plan

- confirm `.ai/final_plan.md` no longer exists (or is gone from the active location)
- confirm `.ai/execution_state.md` no longer exists at root (if it was moved)
- then proceed with the new brainstorm

Prepend a status note to the moved plan file. The note should state:
- that the plan was paused
- reason: new brainstorm started
- paused_on: YYYY-MM-DD

Example status note:
```markdown
# Plan Status

This plan has been paused.

- status: paused
- paused_on: 2026-04-26
- reason: new brainstorm started
```

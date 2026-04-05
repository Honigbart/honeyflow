---
name: execute-plan
description: Use this skill when .ai/plans/<slug>/final_plan.md exists and work should continue across sessions in a disciplined, phase-by-phase way. Tracks progress in .ai/plans/<slug>/execution_state.md, works only on the current phase unless reprioritized explicitly, and updates the long-lived execution record so implementation can continue over multiple days. It does not archive the active plan until implementation is done and the required phase reviews are also complete, unless the user explicitly says otherwise.
---

# Execute Plan Skill

Your job is to drive implementation of an existing finalized plan from start to finish over multiple sessions.

This skill is for execution continuity, not fresh ideation.

## When to use this skill

Use this skill when:
- `.ai/plans/<slug>/final_plan.md` already exists
- the user wants to continue implementing a planned feature, system, or project
- work may span multiple sessions or multiple days
- progress must be tracked reliably
- phases should be completed in order from first to last unless the user explicitly changes priorities

This skill is especially appropriate after a prior workflow such as:
- `brainstorm`
- `brainstorm-critique`
- `brainstorm-synthesize`
- `evolve`, but only after the confirmed evolution direction has been written or promoted into `final_plan.md`

Do not use this skill for:
- creating the initial plan
- broad brainstorming
- pure code review of a diff
- one-off bug fixing unrelated to the plan
- speculative redesign without reference to the plan

## Pipeline Context

This skill is **step 4 of 5** in a planning pipeline:

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

**This skill's state responsibility:** Drive implementation phases of the active plan to completion. Maintain `.ai/plans/<slug>/execution_state.md` and `.ai/plans/<slug>/session_log.md`. Do not archive the plan merely because implementation is complete; leave plan archival to the point where implementation and required reviews are both complete, unless the user explicitly directs otherwise.

## Legacy layout detection

Before doing any work, check for a legacy (pre-namespace) layout:

If `.ai/final_plan.md` exists at root AND `.ai/plans.md` does not exist, this is a legacy layout.
Stop and suggest: "Run `/plan-migrate` to upgrade to the namespaced plan layout."
Do not proceed with the legacy layout.

## Plan slug resolution

Every invocation must resolve a plan slug before doing work.

1. If the user provided a slug explicitly (e.g., `/execute-plan auth-rewrite`), use it.
2. If not, read `.ai/plans.md`.
3. Filter to plans with status `active`.
4. If exactly one plan matches, use it silently.
5. If zero match, say so clearly and stop. Suggest running `brainstorm` or `evolve` to start a new planning cycle.
6. If multiple match, list them and ask the user to choose.

## Overlap warning

After resolving the slug, if there are other `active` plans in `.ai/plans.md`, read their `execution_state.md` files briefly. If any other active plan's touched files overlap with the current plan's scope, warn the user about potential merge conflicts between concurrent plans.

## Core idea

Claude sessions are not the same as durable project execution state.
Treat the files in `.ai/plans/<slug>/` as the durable memory for this execution workflow.

The two main long-lived artifacts are:
- `.ai/plans/<slug>/final_plan.md` — source of truth for the intended direction
- `.ai/plans/<slug>/execution_state.md` — source of truth for execution progress across sessions

Optional supporting artifact:
- `.ai/plans/<slug>/session_log.md` — chronological record of what happened in each execution session

## Primary objective

Continue implementation from the existing plan in a controlled way and keep the execution record up to date.

Always maintain or create:
- `.ai/plans/<slug>/execution_state.md`

When useful, also maintain or create:
- `.ai/plans/<slug>/session_log.md`

## Preconditions

Before doing substantive work:
1. Resolve the plan slug (see above)
2. Check whether `.ai/plans/<slug>/final_plan.md` exists
3. If it does not exist, say so clearly and stop
4. Read `.ai/plans/<slug>/final_plan.md`
5. Ensure the plan directory exists
6. Read `.ai/plans/<slug>/execution_state.md` if it exists
7. Read `.ai/plans/<slug>/session_log.md` if it exists
8. Inspect the relevant code, docs, and current implementation state before acting

Do not execute directly from `.ai/plans/<slug>/evolution_plan.md`. If an evolution proposal exists but `final_plan.md` has not been written, stop and tell the user to synthesize or explicitly promote the evolution plan first.

If context is incomplete, state assumptions clearly.
Do not pretend progress history exists if it does not.

## Execution model

This skill must operate phase-by-phase.

Default rule:
- work on the earliest phase that is not yet done
- do not skip ahead unless the user explicitly reprioritizes

Allowed phase statuses:
- not started
- in progress
- blocked
- done
- cancelled

If `.ai/plans/<slug>/execution_state.md` does not exist, create it by extracting the roadmap phases from `.ai/plans/<slug>/final_plan.md`.

If `final_plan.md` has no clear phase roadmap, derive one carefully from the plan and record that derivation in `execution_state.md`.

## Plan Change Handling

Before continuing execution, compare `.ai/plans/<slug>/final_plan.md` against the plan metadata stored in `.ai/plans/<slug>/execution_state.md`.

Classify the result as one of:
- aligned
- compatible update
- incompatible new plan

If aligned:
- continue normally

If compatible update:
- update plan metadata
- preserve completed phases
- revalidate future phases
- note the reconciliation in `execution_state.md`

If incompatible new plan:
- do not continue execution blindly
- archive the previous execution state to `.ai/archive/`
- initialize a new execution state for the new plan
- add a reuse assessment for previously completed work
- summarize the mismatch in chat before proceeding

## Main behavior on each invocation

On each invocation, do the following in order:

1. Reconstruct execution state
- Read `.ai/plans/<slug>/final_plan.md`
- Read `.ai/plans/<slug>/execution_state.md` if present
- Determine the current active phase
- Determine what is already complete, in progress, blocked, or untouched

2. Validate the next phase
- Identify the earliest non-done phase
- Restate its objective, scope, definition of done, dependencies, and risk
- Check whether prerequisites are actually satisfied in the codebase and docs

3. Work the phase
- Prefer finishing the current phase before opening new fronts
- Make concrete progress against the phase definition of done
- Keep changes scoped to the phase unless tightly necessary
- Avoid opportunistic unrelated cleanup unless it materially helps the phase

4. Verify completion honestly
- Do not mark a phase done unless its definition of done is actually met
- If partial progress was made, keep it in progress
- If blocked, mark it blocked and explain exactly why

5. Update durable records
- Update `.ai/plans/<slug>/execution_state.md`
- Append a concise entry to `.ai/plans/<slug>/session_log.md`
- Keep both files truthful and current

6. Report clearly in chat
- say which phase you worked on
- what changed
- whether the phase is now done, still in progress, or blocked
- what the next session should do

If all implementation phases are done or cancelled but one or more required phase reviews are still not `reviewed`, do not archive the plan. Record that implementation is complete but review is still pending, keep the plan active, and direct the next session to run `execute-review` on the earliest eligible phase unless the user explicitly says otherwise.

## Ordering rules

Default ordering is strict.

You should move phase-by-phase from 1 through finish.
Only violate phase order if one of these is true:
- the user explicitly reprioritizes
- a small prerequisite task from a later phase is required to unblock the current phase
- the plan itself is clearly wrong and needs correction

If phase order is changed, record the reason in `execution_state.md` and `session_log.md`.

## Scope discipline rules

- Work from the current plan, not from fresh fantasy
- Prefer completion over breadth
- Prefer finishing a narrow slice over starting many partial slices
- Do not silently expand scope
- Protect working parts of the system
- Avoid rewrite enthusiasm
- If the plan is outdated, note that clearly before changing direction

## Required structure for `.ai/plans/<slug>/execution_state.md`

Use exactly these top-level sections:

# Execution State

## 1. Plan Reference
State the plan slug and file being executed and the date of the latest plan version if known.

## 2. Current Overall Status
Summarize overall progress in 3-6 sentences.

## 3. Phase Tracker
List every phase in order.
For each phase include:
- phase number and name
- status: not started / in progress / blocked / done / cancelled
- objective
- definition of done
- dependencies
- touched files or areas, if known
- test command or test commands: record the shell verification command(s) for this phase's implementation so reviewers can independently verify. Use `test_command` when one command is sufficient. Use `test_commands` when the phase needs multiple distinct checks. Examples: `apps/api/.venv/bin/python -m pytest apps/api/tests/test_prompt_composer.py`, `cd apps/web && npx tsc --noEmit`, `cd apps/web && npm run test:e2e:desktop`. If not applicable, say `manual verification` or `visual check`.
- notes

Verification field rules:
- Prefer `test_command` for one command
- Prefer `test_commands` for multiple commands
- If `test_commands` exists, preserve command order
- Do not delete an existing `test_command` or `test_commands` entry unless you are replacing it with a more accurate equivalent

If review metadata fields are already present for a phase, preserve them when updating or regenerating `execution_state.md`.
Review metadata fields may include:
- `review_status`
- `reviewed_on`
- `review_commit_claude`
- `review_commit_codex`
- `review_notes`

## 4. Current Active Phase
State the single phase that should currently be worked on.
If there is no active phase, explain why.

## 5. Completed Work
List meaningful completed items so future sessions can quickly understand what is already finished.

## 6. Open Blockers
List current blockers with enough detail to unblock them later.
If none, explicitly say so.

## 7. Next Session Starting Point
Describe exactly what the next session should do first.

## 8. Deviations from Plan
Record any justified deviations from the plan.
If none, explicitly say so.

## 9. Updated On
Record the latest update timestamp or session note.

## Required structure for `.ai/plans/<slug>/session_log.md`

Append one session entry per invocation when substantive work is done.

Use this structure for each new entry:

```md
## Session YYYY-MM-DD HH:MM
- plan: <slug>
- active phase:
- objective:
- actions taken:
- files touched:
- verification performed:
- status after session:
- blockers:
- next starting point:
```

## Working rules during implementation

When executing a phase:
- inspect relevant files first
- prefer minimal but complete changes
- validate with tests, builds, or local checks when appropriate
- update docs when implementation meaningfully changes behavior
- keep the execution record synchronized with reality

If you cannot finish a phase in the current session:
- leave it as `in progress`
- clearly record what is left
- make the next starting point easy and concrete

If a phase is blocked:
- mark it `blocked`
- describe the blocker precisely
- propose the smallest unblock path
- do not falsely mark progress as complete

## Replanning rules

If you discover the plan is materially flawed during execution:
- do not silently improvise a new strategy
- record the issue in `execution_state.md`
- explain the mismatch between plan and implementation reality
- either make a minimal justified adjustment or recommend re-running a planning skill

Use re-planning sparingly.
Execution should normally honor the plan.

## Review gate before archival

A plan is not archive-ready just because all implementation phases are marked `done`.

Use this rule:
- implementation-complete: every phase is `done` or `cancelled`
- review-complete: every phase with `status: done` has `review_status: reviewed`

If implementation is complete but review is not:
- do not archive the plan
- do not mark the overall plan as completed
- update `execution_state.md` and `session_log.md` to say execution work is finished and review is the remaining gate
- make `## 4. Current Active Phase` explain that no implementation phase is active because the plan is awaiting review
- make `## 7. Next Session Starting Point` tell the next session to run `execute-review` on the earliest done phase whose `review_status` is missing, `not reviewed`, `in review`, `claude-fixed`, or `codex-fixed`

Do not treat `in disagreement` as review-complete. A plan with any phase still `in disagreement` remains active until the disagreement is resolved or the user explicitly accepts archiving anyway.

## Chat output requirements

After each invocation, provide a short but concrete execution summary in chat.
It must include:
- active phase
- status change
- key files or areas touched
- biggest remaining obstacle
- exact next action

## Abandoning a plan

If the user explicitly asks to abandon, cancel, or stop the current plan:

1. Copy `.ai/plans/<slug>/` contents to `.ai/archive/<slug>/`
2. Delete `.ai/plans/<slug>/` directory
3. Update `.ai/plans.md`: set status to `abandoned`
4. Append an entry to the archived `session_log.md` recording the abandonment

Do not abandon without explicit user confirmation.

## Completing the plan

Only archive the plan after both of these are true:
- all phases and all tasks from `final_plan.md` are fully completed
- every phase that was completed in implementation has also been reviewed

`execute-plan` should normally stop short of this archival step and leave the plan active when review is still pending. Archive here only if review completion is already recorded in `execution_state.md` or the user explicitly instructs you to archive without waiting for review.

When the plan is archive-ready:
1. Copy `.ai/plans/<slug>/` contents to `.ai/archive/<slug>/`
2. Delete `.ai/plans/<slug>/` directory
3. Update `.ai/plans.md`: set status to `completed`

Do not archive the plan unless all phases are completed or explicitly marked as intentionally skipped with explanation, and every implemented phase has been reviewed, unless the user explicitly says otherwise.

## Style rules

- Write crisp markdown
- Be concrete and specific
- Avoid vague progress language
- Avoid repetition
- No motivational filler
- No pretending partial work is finished
- No skipping record-keeping

## File handling

Before finishing:
1. Ensure `.ai/plans/<slug>/execution_state.md` exists and is current
2. If substantive work was done, append or update `.ai/plans/<slug>/session_log.md`
3. Ensure the current active phase is explicit
4. Ensure phase statuses are truthful
5. Ensure the next session starting point is concrete
6. Then provide the short in-chat execution summary

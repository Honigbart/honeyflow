---
name: execute-plan
description: Use this skill when .ai/final_plan.md exists and work should continue across sessions in a disciplined, phase-by-phase way. Tracks progress in .ai/execution_state.md, works only on the current phase unless reprioritized explicitly, and updates the long-lived execution record so implementation can continue over multiple days. It does not archive the active plan until implementation is done and the required phase reviews are also complete, unless the user explicitly says otherwise.
---

# Execute Plan Skill

Your job is to drive implementation of an existing finalized plan from start to finish over multiple sessions.

This skill is for execution continuity, not fresh ideation.

## When to use this skill

Use this skill when:
- `.ai/final_plan.md` already exists
- the user wants to continue implementing a planned feature, system, or project
- work may span multiple sessions or multiple days
- progress must be tracked reliably
- phases should be completed in order from first to last unless the user explicitly changes priorities

This skill is especially appropriate after a prior workflow such as:
- `brainstorm`
- `brainstorm-critique`
- `brainstorm-synthesize`
- `evolve`, but only after the confirmed evolution direction has been written or promoted into `.ai/final_plan.md`

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

**This skill's state responsibility:** Drive implementation phases of the active plan to completion. Maintain `execution_state.md` and `session_log.md`. Do not archive the plan merely because implementation is complete; leave plan archival to the point where implementation and required reviews are both complete, unless the user explicitly directs otherwise.

## Core idea

Claude sessions are not the same as durable project execution state.
Treat the files in `.ai/` as the durable memory for this execution workflow.

The two main long-lived artifacts are:
- `.ai/final_plan.md` — source of truth for the intended direction
- `.ai/execution_state.md` — source of truth for execution progress across sessions

Optional supporting artifact:
- `.ai/session_log.md` — chronological record of what happened in each execution session

## Primary objective

Continue implementation from the existing plan in a controlled way and keep the execution record up to date.

Always maintain or create:
- `.ai/execution_state.md`

When useful, also maintain or create:
- `.ai/session_log.md`

## Preconditions

Before doing substantive work:
1. Check whether `.ai/final_plan.md` exists
2. If it does not exist, say so clearly and stop
3. Read `.ai/final_plan.md`
4. **Check for status stub.** Treat `final_plan.md` as an inactive status stub if any of these are true:
   - it begins with `# Final Plan Status`
   - it contains `- active_plan: none`
   - it records `- status: completed` or `- status: abandoned`

   If `final_plan.md` is an inactive status stub instead of an actual plan, say so clearly and stop — there is no active plan to execute. Suggest running `brainstorm` or `evolve` to start a new planning cycle.
5. Ensure the `.ai` directory exists
6. Read `.ai/execution_state.md` if it exists
7. Read `.ai/session_log.md` if it exists
8. Inspect the relevant code, docs, and current implementation state before acting

Do not execute directly from `.ai/evolution_plan.md`. If an evolution proposal exists but `.ai/final_plan.md` has not been updated to reflect it, stop and tell the user to synthesize or explicitly promote the evolution plan first.

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

If `.ai/execution_state.md` does not exist, create it by extracting the roadmap phases from `.ai/final_plan.md`.

If `.ai/final_plan.md` has no clear phase roadmap, derive one carefully from the plan and record that derivation in `.ai/execution_state.md`.

## Plan Change Handling

Before continuing execution, compare `.ai/final_plan.md` against the plan metadata stored in `.ai/execution_state.md`.

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
- note the reconciliation in `.ai/execution_state.md`

If incompatible new plan:
- do not continue execution blindly
- archive the previous execution state (use `.ai/archive/` folder that you are allowed to create if not existent yet)
- initialize a new execution state for the new plan
- add a reuse assessment for previously completed work
- summarize the mismatch in chat before proceeding

## Main behavior on each invocation

On each invocation, do the following in order:

1. Reconstruct execution state
- Read `.ai/final_plan.md`
- Read `.ai/execution_state.md` if present
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
- Update `.ai/execution_state.md`
- Append a concise entry to `.ai/session_log.md`
- Keep both files truthful and current

6. Report clearly in chat
- say which phase you worked on
- what changed
- whether the phase is now done, still in progress, or blocked
- what the next session should do

If all implementation phases are done or cancelled but one or more required phase reviews are still not `reviewed`, do not archive the plan. Record that implementation is complete but review is still pending, keep `.ai/final_plan.md` active, and direct the next session to run `execute-review` on the earliest eligible phase unless the user explicitly says otherwise.

## Ordering rules

Default ordering is strict.

You should move phase-by-phase from 1 through finish.
Only violate phase order if one of these is true:
- the user explicitly reprioritizes
- a small prerequisite task from a later phase is required to unblock the current phase
- the plan itself is clearly wrong and needs correction

If phase order is changed, record the reason in `.ai/execution_state.md` and `.ai/session_log.md`.

## Scope discipline rules

- Work from the current plan, not from fresh fantasy
- Prefer completion over breadth
- Prefer finishing a narrow slice over starting many partial slices
- Do not silently expand scope
- Protect working parts of the system
- Avoid rewrite enthusiasm
- If the plan is outdated, note that clearly before changing direction

## Required structure for `.ai/execution_state.md`

Use exactly these top-level sections:

# Execution State

## 1. Plan Reference
State the plan file being executed and the date of the latest plan version if known.

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

If review metadata fields are already present for a phase, preserve them when updating or regenerating `.ai/execution_state.md`.
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
Record any justified deviations from `.ai/final_plan.md`.
If none, explicitly say so.

## 9. Updated On
Record the latest update timestamp or session note.

## Required structure for `.ai/session_log.md`

Append one session entry per invocation when substantive work is done.

Use this structure for each new entry:

```md
## Session YYYY-MM-DD HH:MM
- plan: <short plan name or filename reference>
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
- record the issue in `.ai/execution_state.md`
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
- do not archive `.ai/final_plan.md`
- do not replace `.ai/final_plan.md` with a completed stub
- do not mark the overall plan as completed
- update `.ai/execution_state.md` and `.ai/session_log.md` to say execution work is finished and review is the remaining gate
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

1. **Move** `.ai/final_plan.md` to `.ai/archive/` with a filename like `YYYYMMDD-plan-name-abandoned.md`
2. Prepend a status note: `status: abandoned`, `abandoned_on: YYYY-MM-DD`, `reason: <user's reason or "user requested">`
3. **Move** `.ai/execution_state.md` to `.ai/archive/` with a matching filename
4. Replace `.ai/final_plan.md` with a stub:
   ```markdown
   # Final Plan Status

   This plan has been abandoned.

   - abandoned_on: YYYY-MM-DD
   - archived_to: .ai/archive/YYYYMMDD-plan-name-abandoned.md
   - status: abandoned
   - active_plan: none
   ```
5. Append an entry to `.ai/session_log.md` recording the abandonment

Do not abandon without explicit user confirmation.

## Resuming a paused plan

If the user asks to resume a plan from `.ai/plans/in_progress/`:

1. List the files in `.ai/plans/in_progress/` and let the user pick if more than one exists
2. **Move** the chosen plan file back to `.ai/final_plan.md`
3. If a matching `execution_state.md` file exists in `.ai/plans/in_progress/`, **move** it back to `.ai/execution_state.md`
4. Remove the paused status note prepended to the plan (or note that it has been resumed)
5. Delete the files from `.ai/plans/in_progress/` after moving
6. Then proceed with normal execution (read plan, validate state, work the next phase)

If `.ai/final_plan.md` already exists and is active, warn the user — resuming would overwrite the current active plan. Ask whether to pause or supersede the current plan first.

## Completing the final_plan.md

Only archive the plan after both of these are true:
- all phases and all tasks from `.ai/final_plan.md` are fully completed
- every phase that was completed in implementation has also been reviewed

`execute-plan` should normally stop short of this archival step and leave the plan active when review is still pending. Archive here only if review completion is already recorded in `.ai/execution_state.md` or the user explicitly instructs you to archive without waiting for review.

When the plan is archive-ready, archive the plan by copying it to `.ai/archive/`.

The archive filename must contain:
- completion date in `YYYYMMDD` format
- a short kebab-case summary of the plan
- all parts hyphen-separated

Example:
`20260426-new-prompt-ui.md`

After archiving:
1. mark `.ai/execution_state.md` as completed
2. record the archive path in `.ai/execution_state.md`
3. ensure `.ai/final_plan.md` is no longer treated as the active plan (replace with a tiny stub/status note, see below)
4. if appropriate, clear or reset the active execution state for the next plan

Do not archive the plan unless all phases are completed or explicitly marked as intentionally skipped with explanation, and every implemented phase has been reviewed, unless the user explicitly says otherwise.

### Stub/status note replacement:

Replace `.ai/final_plan.md` with a stub or status note. The note should state:
- that the plan was completed
- the completion date
- the archive path
- that there is no currently active final plan

Example contents of the status note:
```markdown
# Final Plan Status

This plan has been completed and archived.

- completed_on: 2026-04-26
- archived_to: .ai/archive/20260426-new-prompt-ui.md
- status: completed
- active_plan: none
```

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
1. Ensure `.ai/execution_state.md` exists and is current
2. If substantive work was done, append or update `.ai/session_log.md`
3. Ensure the current active phase is explicit
4. Ensure phase statuses are truthful
5. Ensure the next session starting point is concrete
6. Then provide the short in-chat execution summary

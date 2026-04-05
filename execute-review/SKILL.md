---
name: execute-review
description: Use this skill when `.ai/final_plan.md` and `.ai/execution_state.md` exist and you want to manually review exactly one completed execution phase through a bounded Claude↔Codex review loop. It resumes an unfinished phase review if one exists; otherwise it selects the earliest phase with `status: done` and `review_status` missing or `not reviewed`, initializes review tracking fields if absent, has Codex review the phase into `.ai/review.md`, lets Claude attempt fixes and commit them, optionally lets Codex fix persistent issues and commit them, performs one final Claude↔Codex disagreement pass, archives the phase review, updates `.ai/execution_state.md`, and if that review completes the last required phase review for a fully implemented plan, archives the plan as well unless the user says otherwise.
---

# Execute Review Skill

Your job is to review exactly one completed execution phase through a bounded Claude↔Codex loop.

This skill is for post-phase review, not for planning or fresh implementation.

## When to use this skill

Use this skill when:
- `.ai/final_plan.md` exists and is an active plan
- `.ai/execution_state.md` exists
- at least one phase is marked `done`
- the user explicitly wants to review one completed phase
- review history should be tracked in `.ai/execution_state.md` and `.ai/archive/`

This skill is especially appropriate after one or more `execute-plan` sessions completed a phase and the user wants an external review pass before moving on.

Do not use this skill for:
- reviewing a phase that is not marked `done`
- broad repo review unrelated to a specific phase
- planning a new phase
- replacing `execute-plan`
- unbounded review ping-pong

## Canonical files

- `.ai/final_plan.md` — active plan source of truth until the full plan is both implemented and review-complete
- `.ai/execution_state.md` — execution status and per-phase review status
- `.ai/session_log.md` — execution history and likely source for touched files
- `.ai/review.md` — active review artifact for the current phase
- `.ai/archive/` — archived completed review artifacts

## Review statuses

Use these per-phase review statuses inside `## 3. Phase Tracker` in `.ai/execution_state.md`:

- `not reviewed` — default state
- `in review` — Codex has started review and the loop is in progress
- `claude-fixed` — Claude committed a review-driven fix and Codex re-review is pending or in progress
- `codex-fixed` — Codex committed a review-driven fix and Claude final review is pending or in progress
- `reviewed` — review loop completed
- `in disagreement` — final Claude↔Codex disagreement remained unresolved

Also maintain these per-phase fields:
- `reviewed_on`
- `review_commit_claude`
- `review_commit_codex`
- `review_notes`

## Primary objective

Process exactly one eligible phase per invocation.

If finishing that one phase makes the whole plan implementation-complete and review-complete, finalize the plan archive in the same invocation unless the user explicitly says not to.

Default selection rule:
1. If a phase already has `review_status: in review`, `claude-fixed`, or `codex-fixed`, resume that phase.
2. Otherwise select the earliest phase in order with:
   - `status: done`
   - `review_status` missing, or `review_status: not reviewed`

Do not automatically continue to the next phase after finishing one review.
The user must invoke this skill again for the next phase.

## Preconditions

Before doing substantive work:
1. Check whether `.ai/final_plan.md` exists
2. Read `.ai/final_plan.md`
3. Treat `final_plan.md` as inactive and stop if any of these are true:
   - it begins with `# Final Plan Status`
   - it contains `- active_plan: none`
   - it records `- status: completed` or `- status: abandoned`
4. Check whether `.ai/execution_state.md` exists
5. If it does not exist, stop and say review cannot proceed without execution state
6. Read `.ai/execution_state.md`
7. Read `.ai/session_log.md` if it exists
8. Ensure `.ai/` exists
9. Ensure the repo is a git repository and commits are possible
10. Run `git status --short`

If the worktree contains unrelated dirty changes outside the intended review-fix scope, stop and ask the user before committing anything.
Do not accidentally sweep unrelated changes into a review-fix commit.

## Review metadata bootstrap

If the phase entries in `.ai/execution_state.md` do not yet contain review fields, add them for every phase entry in `## 3. Phase Tracker`.

Use these defaults:
- `review_status: not reviewed`
- `reviewed_on: not yet reviewed`
- `review_commit_claude: none`
- `review_commit_codex: none`
- `review_notes: none`

If the fields already exist, preserve them and update only the target phase unless you are normalizing obviously missing fields in other phases.

## Phase selection rules

- Review only one phase per invocation
- A new review may only start on a phase with `status: done`
- Never skip an earlier eligible done phase unless the user explicitly says so
- If no done phase is eligible, say so clearly and stop
- If a review is already in progress for a phase, resume it instead of selecting a new one

When selecting the phase, extract and restate:
- phase number and name
- objective
- definition of done
- touched files or areas, if recorded
- test command or test commands, if recorded
- relevant notes

If `touched files or areas` is weak or missing, derive file scope from:
1. the current phase entry
2. `.ai/session_log.md`
3. the definition of done and nearby implementation files

## Codex review strategy

Default to a hand-rolled `codex exec` review prompt, not `codex review`.

Reason:
- file scope is phase-specific
- the relevant context is the phase definition of done plus recorded touched files
- the review should stay bounded to one phase, not drift into a generic repo review

Only use `codex review` if the phase maps cleanly to an isolated commit or diff and file scope is obvious.

## Preferred Codex review command

Write a concise review brief that includes:
- phase number and name
- objective
- definition of done
- files in scope
- plan context: relevant accepted critiques, rejected critiques, and architectural decisions from `.ai/final_plan.md` that affect this phase — especially any that justify intentional breaking changes, scope decisions, or trade-offs
- test command(s): if `test_command` or `test_commands` is recorded for this phase in `.ai/execution_state.md`, include it so Codex can independently verify
- prior review state, if any
- current `.ai/review.md` contents when this is a re-review or final Codex decision
- instruction to focus on behavioral bugs, unmet definition of done, missing tests, regressions, and medium/high severity issues
- instruction to avoid style-only nits unless they hide real risk

**Important:** Before writing the Codex prompt, read the relevant phase section from `.ai/final_plan.md` (especially `## 4. Accepted Critiques`, `## 5. Rejected Critiques`, `## 8. Architecture / Solution Shape`, and the phase's entry in `## 12. Delivery Roadmap by Phases`). Extract the specific plan decisions that affect this phase and include them verbatim or summarized in the prompt under "Plan context". This prevents Codex from flagging intentional design decisions as bugs.

Then invoke Codex like this:

```bash
mkdir -p .ai && \
cat <<'EOF' | codex exec -C . --skip-git-repo-check \
  --output-last-message .ai/review.md -
You are reviewing phase <X>: <phase name>.

Review only the implementation relevant to this phase.

Phase objective:
<objective>

Definition of done:
<definition of done>

Files in scope:
<one file per line>

Plan context (from .ai/final_plan.md):
<Summarize the accepted critiques, rejected critiques, and architectural decisions
that are relevant to this phase. Include any that justify intentional breaking changes,
scope decisions, or trade-offs. Be specific — quote the plan where it matters.>

Test command:
<test command(s) from phase tracker, preserving order if multiple, or "not specified" if missing>

Prior review state:
<review status and prior notes>

Review instructions:
- Read .ai/final_plan.md for full context before raising findings — especially the accepted/rejected critiques and architecture sections
- Focus on behavioral bugs, regressions, unmet definition of done, missing tests, and medium/high severity issues
- Do not flag intentional design decisions documented in the plan as bugs
- Stay scoped to this phase and these files unless one-hop inspection is necessary to validate an interaction
- Avoid style-only or preference-only comments unless they hide real risk
- If test command(s) are provided, run them to independently verify the implementation
- Keep the output brief
- Preserve already known facts from prior review passes and update the relevant sections instead of dropping them

Return markdown with exactly these top-level sections:
# Phase Review
## 1. Review Target
## 2. Codex Initial Review
## 3. Claude Fix Pass
## 4. Codex Re-review
## 5. Codex Fix Pass
## 6. Claude Final Review
## 7. Final Outcome
EOF
```

**Timing note:** The `--output-last-message` flag writes `.ai/review.md` only when the Codex process exits, not during execution. Always wait for the command to complete before reading the output file. Do not run the Codex command in the background — run it synchronously so the file is guaranteed to exist when the next step begins.

## Workflow

Follow this loop exactly once for the selected phase.

### Step 1 — Codex initial review

1. Set the target phase to `review_status: in review`
2. Update `.ai/execution_state.md`
3. Run the Codex review command
4. Read `.ai/review.md`
5. If Codex found no meaningful issues, document that briefly in:
   - `## 2. Codex Initial Review`
   - `## 7. Final Outcome`
   Then:
   - mark the phase `reviewed`
   - set `reviewed_on`
   - archive the review artifact
   - if that makes the whole plan implementation-complete and review-complete, archive the plan too
   - update execution state
   - stop
6. If Codex found meaningful issues, continue to Step 2

### Step 2 — Claude fix pass

Claude reads `.ai/review.md` and attempts to fix accepted findings in scope.

Rules:
- prioritize high and medium findings
- low findings may be documented without churn if they are not worth a fix pass
- do not broaden scope beyond the phase
- run the smallest relevant verification after changes

If Claude changes code:
- commit with prefix `Claude's fix of phase X code review`
- preferred format: `Claude's fix of phase X code review: <short summary>`
- record the commit SHA in `review_commit_claude`
- set `review_status: claude-fixed`

If Claude makes no code changes:
- do not create an empty commit
- record `review_commit_claude: none`
- explain briefly in `## 3. Claude Fix Pass`

### Step 3 — Codex re-review and optional Codex fix

Codex reviews the post-Claude state again, using the same bounded phase context plus the current `.ai/review.md`.

If the meaningful problems are resolved:
- document that in `## 4. Codex Re-review`
- skip Codex fix
- go to Step 6

If medium/high problems from the review still persist and Codex agrees they should be fixed:
- Codex fixes them
- run the smallest relevant verification
- commit with a message that explicitly says it was fixed by Codex
- preferred format: `Codex fix of phase X code review: <short summary> (fixed by Codex)`
- record the commit SHA in `review_commit_codex`
- set `review_status: codex-fixed`
- document the action briefly in `## 5. Codex Fix Pass`

If Codex finds only low-severity leftovers worth documenting but not fixing:
- document them briefly
- do not commit
- continue to Step 6

### Step 4 — Claude final review of Codex fix

Run this step only if Codex made a fix commit.

Claude reviews Codex's fix with the same phase scope.

If Claude finds no meaningful medium/high problems:
- document approval in `## 6. Claude Final Review`
- go to Step 6

If Claude finds medium/high problems:
- append only those findings briefly in `## 6. Claude Final Review`
- send those findings back to Codex for one final decision

### Step 5 — Final Codex decision on Claude's final findings

Codex gets one final chance only.

If Codex agrees with Claude's final medium/high findings:
- Codex may make one final fix pass
- run the smallest relevant verification
- commit with a message that explicitly says it was fixed by Codex
- update `review_commit_codex` to the latest Codex review-fix commit SHA
- document the result briefly
- then finish

If Codex does not agree:
- do not continue looping
- mark the phase `in disagreement`
- explain the disagreement briefly in `review_notes` and `## 7. Final Outcome`
- inform the user clearly
- then finish

### Step 6 — Finish

Document the final result briefly.
Do not add unnecessary prose.

Unless the outcome is `in disagreement`, finish by:
- marking the phase `reviewed`
- setting `reviewed_on`
- archiving the final review artifact
- if that makes the whole plan implementation-complete and review-complete, archive the plan too
- updating `.ai/execution_state.md`

Possible final outcomes:
- `reviewed`
- `reviewed` with documented low-priority leftovers
- `in disagreement`

## Plan finalization after review

After the selected phase review is finished, check whether the entire plan is now ready to archive.

Use this gate:
- implementation-complete: every phase is `done` or `cancelled`
- review-complete: every phase with `status: done` has `review_status: reviewed`

If both are true, and the user has not said to keep the plan active:
1. Archive `.ai/final_plan.md` to `.ai/archive/` using the same completed-plan naming convention as `execute-plan`
2. Mark `.ai/execution_state.md` overall status as completed
3. Record the completed-plan archive path in `.ai/execution_state.md`
4. **Mark linked todo items as done.** Before archiving, check whether `.ai/final_plan.md` contains a `## 15. Todo References` section. If it does, read `.ai/todo.md` and mark each referenced item as done (move to the **Done** section with `[x]` and append `— YYYY-MM-DD`). If `.ai/todo.md` does not exist or a referenced item is not found (already removed or reworded), skip silently.
5. Replace `.ai/final_plan.md` with the completed status stub:
   ```markdown
   # Final Plan Status

   This plan has been completed and archived.

   - completed_on: YYYY-MM-DD
   - archived_to: .ai/archive/YYYYMMDD-plan-name.md
   - status: completed
   - active_plan: none
   ```
5. Append a concise completion entry to `.ai/session_log.md`
6. Note the plan archive path in `## 7. Final Outcome`

If implementation is complete but review is not complete:
- do not archive the plan
- keep `.ai/final_plan.md` active
- make `## 7. Final Outcome` say which phase still needs review next

If any phase remains `in disagreement`, do not archive the plan unless the user explicitly says to accept that state and archive anyway.

## Commit rules

- Never create empty commits
- Never commit unrelated worktree changes
- Stage only the intended review-fix files plus the relevant `.ai/` state files when appropriate
- If unrelated changes make safe staging unclear, stop and ask the user before committing
- After each fix commit, record the commit SHA in `.ai/execution_state.md`

## Required structure for `.ai/review.md`

Use exactly these top-level sections:

# Phase Review

## 1. Review Target
State:
- phase number and name
- objective
- definition of done summary
- files in scope

## 2. Codex Initial Review
State:
- clean or findings
- brief findings list with severity when applicable

## 3. Claude Fix Pass
State:
- no changes or fixes applied
- commit SHA or `none`
- verification performed

## 4. Codex Re-review
State:
- clean or remaining findings
- whether Codex fix is needed

## 5. Codex Fix Pass
State:
- not needed or fixes applied
- commit SHA or `none`
- verification performed

## 6. Claude Final Review
State:
- not needed, approved, or findings sent back
- brief notes only

## 7. Final Outcome
State:
- final review status
- brief summary
- archive path
- next action

## Review history archive handling

Review history must be preserved per phase.

Rules:
1. If `.ai/review.md` already exists from a different finished phase, archive it before overwriting
2. Create `.ai/archive/` first if it does not exist
3. When the current phase review finishes, archive the final markdown to `.ai/archive/`
4. Use filenames like:
   - `YYYYMMDD-phase-01-review.md`
   - `YYYYMMDD-phase-03-review-in-disagreement.md`
5. Record the archive path in:
   - `## 7. Final Outcome` in `.ai/review.md`
   - `review_notes` in `.ai/execution_state.md`

It is acceptable to keep `.ai/review.md` as the current active artifact after also archiving its final snapshot.

## Execution state update rules

Before finishing, ensure the target phase entry in `.ai/execution_state.md` includes:
- `review_status`
- `reviewed_on`
- `review_commit_claude`
- `review_commit_codex`
- `review_notes`

Use these update rules:
- on start: `review_status: in review`
- after Claude fix commit: `review_status: claude-fixed`
- after Codex fix commit: `review_status: codex-fixed`
- on successful finish: `review_status: reviewed`
- on unresolved disagreement: `review_status: in disagreement`

Update `reviewed_on` on final completion, not just at start.

## Chat output requirements

After the invocation, report briefly:
- which phase was reviewed
- final review status
- whether Claude committed
- whether Codex committed
- biggest remaining issue, if any
- exact next action

## File handling

Before finishing:
1. Ensure `.ai/review.md` exists and matches the selected phase
2. Ensure the review artifact contains all required sections
3. Ensure `.ai/execution_state.md` reflects the final review state truthfully
4. Ensure the final review artifact is archived in `.ai/archive/`
5. If the review finished the last required phase review for a fully implemented plan, ensure the plan itself is archived and `final_plan.md` is replaced with a completed stub
6. Then provide the short in-chat summary

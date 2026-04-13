---
name: execute-review
description: Use this skill when .ai/plans/<slug>/final_plan.md and .ai/plans/<slug>/execution_state.md exist and you want to manually review exactly one completed execution phase through a bounded Claude-Codex review loop. It resumes an unfinished phase review if one exists; otherwise it selects the earliest phase with status done and review_status missing or not reviewed, initializes review tracking fields if absent, has Codex review the phase into .ai/plans/<slug>/review.md, lets Claude attempt fixes and commit them, optionally lets Codex fix persistent issues and commit them, performs one final Claude-Codex disagreement pass, archives the phase review, updates execution_state.md, and if that review completes the last required phase review for a fully implemented plan, archives the plan as well unless the user says otherwise.
---

# Execute Review Skill

Your job is to review exactly one completed execution phase through a bounded Claude-Codex loop.

This skill is for post-phase review, not for planning or fresh implementation.

## When to use this skill

Use this skill when:
- `.ai/plans/<slug>/final_plan.md` exists and is an active plan
- `.ai/plans/<slug>/execution_state.md` exists
- at least one phase is marked `done`
- the user explicitly wants to review one completed phase
- review history should be tracked in `execution_state.md` and `.ai/archive/`

This skill is especially appropriate after one or more `execute-plan` sessions completed a phase and the user wants an external review pass before moving on.

Do not use this skill for:
- reviewing a phase that is not marked `done`
- broad repo review unrelated to a specific phase
- planning a new phase
- replacing `execute-plan`
- unbounded review ping-pong

## Pipeline Context

Two paths feed into this pipeline:

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

**Canonical files for this skill**
- `.ai/plans/<slug>/final_plan.md` — active plan source of truth
- `.ai/plans/<slug>/execution_state.md` — execution status and per-phase review status
- `.ai/plans/<slug>/session_log.md` — execution history and likely source for touched files
- `.ai/plans/<slug>/review.md` — active review artifact for the current phase
- `.ai/archive/` — archived completed review artifacts and completed plans

**Plan statuses** (tracked in `.ai/plans.md`): `brainstorming` · `active` · `completed` · `abandoned`

## Legacy layout detection

Before doing any work, check for a legacy (pre-namespace) layout:

If `.ai/final_plan.md` exists at root AND `.ai/plans.md` does not exist, this is a legacy layout.
Stop and suggest: "Run `/plan-migrate` to upgrade to the namespaced plan layout."
Do not proceed with the legacy layout.

## Plan slug resolution

Every invocation must resolve a plan slug before doing work.

1. If the user provided a slug explicitly (e.g., `/execute-review auth-rewrite`), use it.
2. If not, read `.ai/plans.md`.
3. Filter to plans with status `active` that have an `execution_state.md` with at least one phase `done`.
4. If exactly one plan matches, use it silently.
5. If zero match, say so clearly and stop.
6. If multiple match, list them and ask the user to choose.

## Review statuses

Use these per-phase review statuses inside `## 3. Phase Tracker` in `execution_state.md`:

- `not reviewed` — default state
- `in review` — Codex has started review and the loop is in progress
- `claude-fixed` — Claude committed a review-driven fix and Codex re-review is pending or in progress
- `codex-fixed` — Codex committed a review-driven fix and Claude final review is pending or in progress
- `reviewed` — review loop completed
- `in disagreement` — final Claude-Codex disagreement remained unresolved

Also maintain these per-phase fields:
- `reviewed_on`
- `review_commit_claude`
- `review_commit_codex`
- `review_notes`

## Primary objective

Process exactly one eligible phase per invocation.

If finishing that one phase makes the whole plan implementation-complete and review-complete, finalize the plan archive in the same invocation unless the user explicitly says not to.

Narrow exception:
- You may review multiple **adjacent** done phases together in one invocation only when all of the following are true:
  - they were implemented in the same session or same tightly coupled implementation burst
  - they form one cohesive feature slice rather than separate ship boundaries
  - they touch substantially the same files or code paths
  - later verification or integration testing clearly subsumes isolated per-phase review
  - splitting the review would be mostly repetitive overhead with little additional signal
- Do not use this exception for broad batching, convenience, or to skip meaningful review boundaries.
- If you use it, treat the grouped phases as one bounded review target and record the justification in both `review_notes` and `session_log.md`, including exactly which phases were covered.

Default selection rule:
1. If a phase already has `review_status: in review`, `claude-fixed`, or `codex-fixed`, resume that phase. **Only one phase may be in an active review state at a time.** If multiple phases have active review statuses, stop and surface the inconsistency — this indicates a prior session crashed mid-review. Resume the earliest one.
2. If a phase has `review_status: in disagreement`, it is eligible for re-review. Present the prior disagreement details from `review_notes` to the user and ask whether to re-run the review loop (which may resolve it with a fresh Codex invocation) or accept the current state and move on.
3. Otherwise select the earliest phase in order with:
   - `status: done`
   - `review_status` missing, or `review_status: not reviewed`

Do not automatically continue to the next phase after finishing one review group.
The user must invoke this skill again for the next phase or eligible adjacent-phase group.

## Preconditions

Before doing substantive work:
1. Resolve the plan slug (see above)
2. Read `.ai/plans/<slug>/final_plan.md`
3. Check the plan's status in `.ai/plans.md` — if not `active`, stop
4. Read `.ai/plans/<slug>/execution_state.md`
5. If execution state does not exist, stop and say review cannot proceed without execution state
6. Read `.ai/plans/<slug>/session_log.md` if it exists
7. Ensure the repo is a git repository and commits are possible
8. Run `git status --short` and check for dirty worktree:
   - If there are **no** uncommitted changes: proceed.
   - If there are uncommitted changes **only within the phase's touched files**: proceed, but note in chat that uncommitted changes exist in the review scope — Codex will review the working tree state, not the last commit.
   - If there are uncommitted changes **outside the phase scope**: stop and ask the user to commit or stash them first. Codex reviewing against a dirty worktree with out-of-scope changes produces unreliable findings. Do not proceed until the worktree is clean or the user explicitly approves.
   
   Do not accidentally sweep unrelated changes into a review-fix commit.

## Review metadata bootstrap

If the phase entries in `execution_state.md` do not yet contain review fields, add them for every phase entry in `## 3. Phase Tracker`.

Use these defaults:
- `review_status: not reviewed`
- `reviewed_on: not yet reviewed`
- `review_commit_claude: none`
- `review_commit_codex: none`
- `review_notes: none`

If the fields already exist, preserve them and update only the target phase unless you are normalizing obviously missing fields in other phases.

## Phase selection rules

- Review only one phase per invocation by default
- Exception: you may review one adjacent-phase group per invocation when the narrow exception above is satisfied
- A new review may only start on a phase with `status: done`. If the selected phase has any other status (`not started`, `in progress`, `blocked`, `cancelled`), refuse to review it and say why. This prevents reviewing incomplete work.
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
2. `.ai/plans/<slug>/session_log.md`
3. the definition of done and nearby implementation files

## Codex review strategy

Default to a hand-rolled `codex exec` review prompt, not `codex review`.

Reason:
- file scope is phase-specific
- the relevant context is the phase definition of done plus recorded touched files
- the review should stay bounded to one phase, not drift into a generic repo review

Only use `codex review` if the phase maps cleanly to an isolated git diff and file scope is obvious.

`codex review` is a generic repository diff review tool, not a plan-aware phase review tool. The available diff selectors are:
- `codex review --uncommitted` — review staged, unstaged, and untracked changes in the current working tree. Use this only when the worktree is cleanly scoped to the current phase and there are no unrelated changes.
- `codex review --base <branch>` — review the branch diff against a known base branch. Use this when the whole phase is represented by the current branch delta and that delta is not polluted by unrelated work.
- `codex review --commit <sha>` — review the changes introduced by one specific commit. Use this when the phase maps to a single isolated commit or a clearly reviewable fix commit.

Decision rule:
- If the phase needs plan context, fixed markdown sections in `review.md`, multi-pass review state, or precise file scoping, use the hand-rolled `codex exec` prompt.
- If the phase is cleanly represented by exactly one git diff shape above and you only need a bounded code review, `codex review` is acceptable.
- If the git situation is ambiguous (multiple relevant commits, unrelated branch drift, or mixed uncommitted changes), do not use `codex review`; use the hand-rolled `codex exec` prompt instead.

## Preferred Codex review command

Write a concise review brief that includes:
- phase number and name
- objective
- definition of done
- files in scope
- plan context: relevant accepted critiques, rejected critiques, and architectural decisions from `final_plan.md` that affect this phase — especially any that justify intentional breaking changes, scope decisions, or trade-offs
- test command(s): if `test_command` or `test_commands` is recorded for this phase in `execution_state.md`, include it so Codex can independently verify
- prior review state, if any
- current `review.md` contents when this is a re-review or final Codex decision
- instruction to focus on behavioral bugs, unmet definition of done, missing tests, regressions, and medium/high severity issues
- instruction to avoid style-only nits unless they hide real risk

**Important:** Before writing the Codex prompt, read the relevant phase section from `.ai/plans/<slug>/final_plan.md` (especially `## 4. Accepted Critiques`, `## 5. Rejected Critiques`, `## 8. Architecture / Solution Shape`, and the phase's entry in `## 12. Delivery Roadmap by Phases`). Extract the specific plan decisions that affect this phase and include them verbatim or summarized in the prompt under "Plan context". This prevents Codex from flagging intentional design decisions as bugs.

Then invoke Codex like this (substitute the resolved slug):

```bash
mkdir -p .ai/plans/<slug> && \
cat <<'EOF' | codex exec -C . --skip-git-repo-check \
  --output-last-message .ai/plans/<slug>/review.md -
You are reviewing phase <X>: <phase name>.

Review only the implementation relevant to this phase.

Phase objective:
<objective>

Definition of done:
<definition of done>

Files in scope:
<one file per line>

Plan context (from final_plan.md):
<Summarize the accepted critiques, rejected critiques, and architectural decisions
that are relevant to this phase. Include any that justify intentional breaking changes,
scope decisions, or trade-offs. Be specific — quote the plan where it matters.>

Test command:
<test command(s) from phase tracker, preserving order if multiple, or "not specified" if missing>

Prior review state:
<review status and prior notes>

Review instructions:
- Read .ai/plans/<slug>/final_plan.md for full context before raising findings — especially the accepted/rejected critiques and architecture sections
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

**Stdin note:** When the prompt is piped on stdin as shown above, that stdin stream is intentional. Do not also leave an extra interactive stdin source attached for prompt-argument invocations later in the flow.

**Timing note:** The `--output-last-message` flag writes `review.md` only when the Codex process exits, not during execution. Always wait for the command to complete before reading the output file. Do not run the Codex command in the background — run it synchronously so the file is guaranteed to exist when the next step begins.

## Simplified Codex fallback

If the preferred pipe-based command fails (e.g., `--output-last-message` not supported, pipe error, or older Codex version), try the simpler `codex exec "<prompt>"` form before falling back to a Claude subagent:

```bash
mkdir -p .ai/plans/<slug> && \
codex exec -C . --skip-git-repo-check --full-auto \
  "You are reviewing phase <X>: <phase name>.

Review only the implementation relevant to this phase.

Phase objective: <objective>
Definition of done: <definition of done>
Files in scope: <one file per line>

Plan context: Read .ai/plans/<slug>/final_plan.md for full context — especially accepted/rejected critiques and architecture sections.

Test command: <test command(s) or 'not specified'>
Prior review state: <review status and prior notes>

Review instructions:
- Focus on behavioral bugs, regressions, unmet definition of done, missing tests, and medium/high severity issues
- Do not flag intentional design decisions documented in the plan as bugs
- Stay scoped to this phase and these files
- Avoid style-only comments unless they hide real risk
- If test command(s) are provided, run them to independently verify
- Keep the output brief

Write your review as markdown to .ai/plans/<slug>/review.md using these sections:
# Phase Review
## 1. Review Target
## 2. Codex Initial Review
## 3. Claude Fix Pass
## 4. Codex Re-review
## 5. Codex Fix Pass
## 6. Claude Final Review
## 7. Final Outcome" </dev/null 2>&1
```

This form has Codex read the files itself and write the output file directly. The `</dev/null` redirect is intentional: it prevents Codex from trying to read extra interactive stdin and appending an unintended `<stdin>` block. After it finishes, verify `.ai/plans/<slug>/review.md` exists and is substantive.

## Claude subagent fallback rule

Codex has priority for this skill. Always attempt Codex first (preferred form, then simplified form). Never assume an earlier failure is still in effect.

If both Codex invocations fail (including `command not found` when Codex is not installed, usage limits, auth failures, or process errors):
- **Use a subagent for review instead of reviewing your own work directly.** Self-review has an inherent blind-spot problem — you are checking code you just orchestrated and will unconsciously anchor to your own reasoning. A subagent starts with a fresh context window and approaches the code as an independent reader.
- Spawn an Agent with `subagent_type: "general-purpose"` and a review prompt that includes:
  - The phase number, name, objective, and definition of done
  - The list of files in scope (one per line)
  - Plan context: relevant accepted/rejected critiques and architecture decisions from `final_plan.md`
  - Test command(s) if recorded
  - Clear instruction: "You are a skeptical code reviewer. You have not seen this code before. Read the listed files, compare against the definition of done, and find bugs, missing edge cases, unmet requirements, or regressions. Run the test command(s) if provided. Write your findings as markdown to `.ai/plans/<slug>/review.md` using the standard review structure (sections 1-7). Be concrete and direct. Do not flag style preferences — focus on behavioral correctness."
  - **Do not include** your implementation reasoning, session context, or why you made specific choices
- Prepend a provenance note to `review.md` stating this review was produced by a Claude subagent (not Codex) because Codex was unavailable, including the failure reason
- Note briefly in chat that Codex was unavailable and a Claude subagent produced the review instead — one line, not a conversation
- Continue the fix loop normally using the subagent's findings
- If a future invocation can reach Codex again, prefer Codex

## Workflow

Follow this loop exactly once for the selected phase.

### Step 0 — Archive stale review artifact

Before starting the review loop, check whether `.ai/plans/<slug>/review.md` already exists.

If it does, check whether it belongs to the current target phase (compare `## 1. Review Target` phase number).
- If it belongs to a **different phase**: archive it to `.ai/archive/` using the standard naming convention (`YYYYMMDD-<slug>-phase-NN-review.md`) before proceeding. This prevents the current review from reading stale findings from a previous phase.
- If it belongs to the **current phase** and `review_status` is `in review`, `claude-fixed`, or `codex-fixed`: this is a resumed review — keep it and continue from the recorded state.
- If it belongs to the **current phase** but `review_status` is `not reviewed` or missing: this is a leftover from an interrupted run — delete it and start fresh.

### Step 1 — Codex initial review

1. Set the target phase to `review_status: in review`
2. Update `execution_state.md`
3. Run the Codex review command
4. Read `.ai/plans/<slug>/review.md`
5. If Codex found no meaningful issues, document that briefly in:
   - `## 2. Codex Initial Review`
   - `## 7. Final Outcome`
   Then:
   - mark the phase `reviewed`
   - set `reviewed_on`
   - archive the review artifact after `review.md` contains the final archive path note
   - if that makes the whole plan implementation-complete and review-complete, archive the plan too
   - update execution state
   - stop
6. If Codex found meaningful issues, continue to Step 2

### Step 2 — Claude fix pass

Claude reads `review.md` and attempts to fix accepted findings in scope.

Rules:
- prioritize high and medium findings
- low findings may be documented without churn if they are not worth a fix pass
- do not broaden scope beyond the phase
- run the smallest relevant verification after changes

If Claude changes code:
- commit with prefix `Claude's fix of phase X code review`
- preferred format: `Claude's fix of phase X code review: <short summary>`
- create exactly one logical fix commit for the Claude pass, not a stream of micro-commits
- commit only after the accepted fix is in a coherent state and the smallest relevant verification has run
- record the commit SHA in `review_commit_claude`
- set `review_status: claude-fixed`

If Claude makes no code changes:
- do not create an empty commit
- do not create a commit for review notes, `review.md`, `execution_state.md`, or archive bookkeeping alone
- record `review_commit_claude: none`
- explain briefly in `## 3. Claude Fix Pass`

### Step 3 — Codex re-review and optional Codex fix

Codex reviews the post-Claude state again, using the same bounded phase context plus the current `review.md`.

If the meaningful problems are resolved:
- document that in `## 4. Codex Re-review`
- skip Codex fix
- go to Step 6

If medium/high problems from the review still persist and Codex agrees they should be fixed:
- Codex fixes them
- run the smallest relevant verification
- commit with a message that explicitly says it was fixed by Codex
- preferred format: `Codex fix of phase X code review: <short summary> (fixed by Codex)`
- create exactly one logical fix commit for this Codex pass, not multiple incremental cleanup commits
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
- keep this as one coherent final fix commit
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
- archiving the final review artifact after `review.md` contains the final archive path note
- if that makes the whole plan implementation-complete and review-complete, archive the plan too
- updating `execution_state.md`

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
1. **Mark linked todo items as done.** Check whether `.ai/plans/<slug>/final_plan.md` contains a `## 15. Todo References` section. If it does, read `.ai/todo.md` and mark each referenced item as done (move to the **Done** section with `[x]` and append `— YYYY-MM-DD`). If `.ai/todo.md` does not exist or a referenced item is not found (already removed or reworded), skip silently.
2. Record the final review archive path in `## 7. Final Outcome` in `review.md` and in `review_notes` in `execution_state.md`
3. Ensure the final review artifact is archived while the live plan directory still exists
4. Copy `.ai/plans/<slug>/` contents to `.ai/archive/<slug>/`
5. Update `.ai/plans.md`: set status to `completed`
6. Delete `.ai/plans/<slug>/` directory as the final filesystem step

Once the plan directory is deleted, the archived review snapshot becomes the canonical review artifact for that phase. Do not expect `.ai/plans/<slug>/review.md` to remain present after full plan archival.

If implementation is complete but review is not complete:
- do not archive the plan
- keep the plan active
- make `## 7. Final Outcome` say which phase still needs review next

If any phase remains `in disagreement`, do not archive the plan unless the user explicitly says to accept that state and archive anyway.

## Commit rules

- Commit only for accepted review-driven code fixes
- Do not commit on a time-based cadence or merely because a review invocation happened
- Use at most one Claude fix commit and one Codex fix commit per pass through the loop, unless Step 5 requires a final Codex fix commit
- Do not create a commit for review notes, `review.md`, `execution_state.md`, todo updates, or archive bookkeeping alone
- Exception: if this invocation finalizes the entire plan archive, stage and commit the finalization changes as one atomic commit with message `Archive completed plan <slug>`. That finalization commit should include the updated `.ai/plans.md`, any `.ai/todo.md` changes caused by linked todo completion, the archived `.ai/archive/<slug>/` snapshot, and the deletion of `.ai/plans/<slug>/`.
- Never create empty commits
- Never commit unrelated worktree changes
- Stage only files within the reviewed phase scope, plus the minimal `.ai/` state files that truthfully record the review result
- Stage only the intended review-fix files plus the relevant `.ai/` state files when appropriate
- If unrelated changes make safe staging unclear, stop and ask the user before committing
- Run the smallest relevant verification before each fix commit
- After each fix commit, record the commit SHA in `execution_state.md`

## Required structure for `.ai/plans/<slug>/review.md`

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
1. If `.ai/plans/<slug>/review.md` already exists from a different finished phase, archive it before overwriting
2. Create `.ai/archive/` first if it does not exist
3. When the current phase review finishes, archive the final markdown to `.ai/archive/`
4. Use filenames like:
   - `YYYYMMDD-<slug>-phase-01-review.md`
   - `YYYYMMDD-<slug>-phase-03-review-in-disagreement.md`
5. Record the archive path in:
   - `## 7. Final Outcome` in `review.md`
   - `review_notes` in `execution_state.md`

It is acceptable to keep `review.md` as the current active artifact after also archiving its final snapshot while the plan remains active. If the whole plan is archived in the same invocation, `review.md` will disappear with the plan directory and the archived snapshot becomes the source of truth.

## Execution state update rules

Before finishing, ensure the target phase entry in `execution_state.md` includes:
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
1. Ensure `.ai/plans/<slug>/review.md` exists and matches the selected phase, unless the plan itself was archived in this invocation
2. Ensure the review artifact contains all required sections in the live file or, if the plan was archived in this invocation, in the archived review snapshot
3. Ensure `execution_state.md` reflects the final review state truthfully
4. Ensure the final review artifact is archived in `.ai/archive/`
5. If the review finished the last required phase review for a fully implemented plan, ensure the plan is archived, `plans.md` is updated, and the archived review snapshot contains the final outcome
6. Then provide the short in-chat summary

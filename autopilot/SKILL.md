---
name: autopilot
description: Use this skill when the user wants fully autonomous execution and review of an active plan. Loops through all phases without user input — executing each phase, running Codex review, fixing issues, and making all decisions based on the plan, Claude memory, and repo documentation. Only stops when truly stuck on an external dependency or when the entire plan is done.
---

# Autopilot Skill

Your job is to take an active plan and drive it to completion autonomously. Execute every phase, review every phase, fix every issue, resolve every disagreement, and archive the plan when done. Do not stop to ask the user unless you literally cannot continue.

## When to use this skill

Use this skill when:
- `.ai/plans/<slug>/final_plan.md` exists with status `active`
- the user wants hands-off execution from current state to completion
- the user explicitly invokes `/autopilot`

Do not use this skill for:
- creating plans — use `/brainstorm`, `/quick-plan`, or `/evolve` first
- tasks without a `final_plan.md` — there is nothing to autopilot

## Pipeline Context

Two paths feed into execution:

**Full path:**
```
1. brainstorm → 2. brainstorm-critique → 3. brainstorm-synthesize → 4. execute-plan / autopilot → 5. evolve
```

**Quick path:**
```
1. quick-plan → (optional: quick-critique) → 2. execute-plan / autopilot → 3. evolve
```

`/autopilot` replaces the manual `/execute-plan` + `/execute-review` loop. It uses the same artifacts, same `execution_state.md` structure, same `session_log.md` format, same review loop, same archival rules. The only difference is that all decisions are made autonomously.

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

## Legacy layout detection

Before doing any work, check for a legacy (pre-namespace) layout:

If `.ai/final_plan.md` exists at root AND `.ai/plans.md` does not exist, this is a legacy layout.
Stop and suggest: "Run `/plan-migrate` to upgrade to the namespaced plan layout."
Do not proceed with the legacy layout.

## Plan slug resolution

1. If the user provided a slug explicitly (e.g., `/autopilot fix-sidebar-layout`), use it.
2. If not, read `.ai/plans.md`.
3. Filter to plans with status `active`.
4. If exactly one plan matches, use it silently.
5. If zero match, say so clearly and stop.
6. If multiple match, list them and ask the user to choose. This is the one question autopilot is allowed to ask before starting — it needs to know which plan to run.

## Core philosophy

**You are fully autonomous.** The user chose autopilot because they do not want to be involved in every decision. They trust you to make judgment calls.

When you face a decision, resolve it using this priority order:
1. **The plan itself** — `final_plan.md` is the primary source of truth. What does the plan say to do?
2. **Claude memory** — check your memory for user preferences, project context, and prior feedback that informs the decision.
3. **Repo documentation** — read `AGENTS.md`, `README.md`, `CLAUDE.md`, `ARCHITECTURE.md`, and other docs in the project for conventions and guidance.
4. **Codebase conventions** — look at existing code patterns and follow them.
5. **Best judgment** — if none of the above clearly resolves it, make the call that best serves the plan's intent and document your reasoning.

**Document every autonomous decision.** Every judgment call you make goes into `session_log.md` with your reasoning. This is how the user audits what happened after the fact.

## Preconditions

Before starting the loop:
1. Resolve the plan slug
2. Verify the plan's status is `active` in `.ai/plans.md`. If it is `brainstorming`, stop and tell the user to synthesize first. If `completed` or `abandoned`, stop and say so.
3. Read `.ai/plans/<slug>/final_plan.md`
4. Read `.ai/plans/<slug>/execution_state.md` if it exists. If it doesn't exist, create it now (extract phases from `final_plan.md`, include review metadata defaults: `review_status: not reviewed`, `reviewed_on: not yet reviewed`, `review_commit_claude: none`, `review_commit_codex: none`, `review_notes: none`) and **commit it immediately** with message `Initialize execution state for <slug>` — before touching any implementation files. This is the orphan-prevention rule: the committed state file ensures the plan is recoverable if the session crashes mid-implementation.
5. Read `.ai/plans/<slug>/session_log.md` if it exists
6. Read Claude memory for relevant project and user context
7. Read repo documentation (`AGENTS.md`, `README.md`, `CLAUDE.md`, etc.) for conventions
8. Inspect relevant codebase context
9. Run `git status --short` — if unrelated dirty changes exist, commit or stash them before starting to keep the worktree clean throughout the run
10. Brief the user: state how many phases remain, which phase you will start with, and that you will report back when done or if truly stuck. Keep this to 2-3 sentences.

Do not execute directly from `evolution_plan.md`. If an evolution proposal exists but `final_plan.md` has not been written, stop and tell the user to synthesize first.

## The autopilot loop

For each phase from the current active phase through the last phase:

### Step A — Execute the phase

Follow the same rules as `execute-plan`:

1. Identify the earliest non-done phase
2. Restate its objective, scope, definition of done, dependencies, and risk
3. Check whether prerequisites are actually satisfied in the codebase
4. Implement the phase — keep changes scoped, prefer completion over breadth
5. Verify completion honestly against the definition of done
6. Commit with format: `Execute plan <slug> phase N: <short description>`
7. Mark the phase `done` in `execution_state.md`
8. Append a session entry to `session_log.md`

If you cannot meet the definition of done, see the autonomous decision rules below.

### Step B — Review the phase

Immediately after marking a phase `done`, review it. Follow the same rules as `execute-review`:

1. Set `review_status: in review`
2. Run the Codex review command (same `codex exec` prompt as `execute-review`)
3. Read `review.md`
4. If clean: mark `reviewed`, archive review artifact, continue to next phase
5. If findings: run the full Claude fix → Codex re-review → optional Codex fix → Claude final review loop

Exception:
- If the just-completed phase and the next adjacent done phase(s) clearly satisfy `execute-review`'s narrow grouped-review exception, you may review that adjacent phase group together instead of one-by-one.
- When you do this, document the justification in both `review_notes` and `session_log.md`, including which phases were grouped and why separate reviews would have been redundant.

**The key difference from manual review: you resolve disagreements autonomously.**

### Step C — Move to the next phase

After review completes for the current phase, immediately start Step A for the next phase. Do not pause, do not ask.

### Step D — Finalize when all phases are done and reviewed

When every phase is `done` and `reviewed`:
1. Mark linked todo items as done (same rules as `execute-review`)
2. Archive the final review artifact
3. Copy `.ai/plans/<slug>/` to `.ai/archive/<slug>/`
4. Update `.ai/plans.md`: set status to `completed`
5. Delete `.ai/plans/<slug>/`
6. Stage and commit the finalization changes as one atomic commit with message `Archive completed plan <slug>`. Include `.ai/plans.md`, any `.ai/todo.md` changes, the archived `.ai/archive/<slug>/` snapshot, and the deletion of `.ai/plans/<slug>/`.
7. Report to the user (see reporting section)

## Autonomous decision rules

These are the situations where manual execution would stop and ask. Autopilot resolves them instead.

### Review disagreements

If Claude and Codex disagree on a finding:
- Read the plan's accepted critiques, rejected critiques, and architecture sections
- Read Claude memory for relevant user preferences
- Side with whichever position **aligns better with the plan's stated intent**
- If the plan does not clearly favor either position, apply this tie-breaker hierarchy:
  1. **Correctness over performance** — if one position prevents a bug or data loss, choose it even if the other is faster or cleaner
  2. **Existing behavior over new behavior** — prefer the option that preserves current working behavior, unless the plan explicitly requires changing it
  3. **Smaller diff over larger diff** — when both options are equally valid, the one that changes less code is safer to ship without user review
- Document **each individual disagreement** in `review_notes` in `execution_state.md` **and** in `session_log.md` with:
  - what the disagreement was about (the specific finding)
  - Claude's position
  - Codex's position
  - which side was chosen and why (referencing plan section, memory, or reasoning)
- The `review_notes` field in `execution_state.md` must indicate that a disagreement was resolved autonomously, so users auditing the phase tracker can see it without reading the session log. Use format: `disagreement resolved autonomously: <one-line summary of finding and resolution>`
- Mark the phase `reviewed` (not `in disagreement`) and continue

Never leave a phase `in disagreement` during autopilot. Always resolve it and move on.

### Codex unavailable

If Codex CLI fails (not installed, rate limit, quota, auth, process error):
- **Use a subagent for review instead of reviewing your own work directly.** Self-review has an inherent blind-spot problem — you are checking your own implementation and will unconsciously anchor to your own reasoning. A subagent starts with a fresh context window, has not seen your trade-offs or implementation decisions, and approaches the code as a genuinely independent reader.
- Spawn an Agent with `subagent_type: "general-purpose"` and a review prompt that includes:
  - The phase number, name, objective, and definition of done
  - The list of files in scope (one per line)
  - Plan context: relevant accepted/rejected critiques and architecture decisions from `final_plan.md`
  - Test command(s) if recorded
  - Clear instruction: "You are a skeptical code reviewer. You have not seen this code before. Read the listed files, compare against the definition of done, and find bugs, missing edge cases, unmet requirements, or regressions. Run the test command(s) if provided. Write your findings as markdown to `.ai/plans/<slug>/review.md` using the standard review structure (sections 1-7). Be concrete and direct. Do not flag style preferences — focus on behavioral correctness."
  - **Do not include** your implementation reasoning, session context, or why you made specific choices — the subagent should evaluate the code on its own merits
- Prepend a provenance note to `review.md` stating this review was produced by a Claude subagent (not Codex) because Codex was unavailable, including the failure reason
- Continue the fix loop: read the subagent's findings, fix accepted issues, then re-review (you may self-review the fixes since the initial blind-spot-breaking review has already surfaced the issues)
- Document in `session_log.md` that this phase was reviewed via Claude subagent without Codex and why
- On subsequent phases, attempt Codex again — do not assume it is still down

### Blocked phases

If a phase is blocked:
- Determine whether the blocker is something you can resolve:
  - **Missing code, missing tests, missing config that you can write:** resolve it yourself, document the deviation
  - **Dependency on a prior phase that is incomplete:** this should not happen in sequential execution; if it does, go back and finish the dependency
  - **External dependency you truly cannot resolve** (needs credentials, API keys, third-party service, hardware, human approval for deployment, access permissions): this is the one case where autopilot stops (see hard stops below)
- If you resolved the blocker yourself, document the resolution in `execution_state.md` and `session_log.md`

### Plan drift

If you discover during execution that the plan is materially wrong about something:
- If the fix is small and clearly correct (e.g., plan says file is at `src/auth.ts` but it is at `src/auth/index.ts`): adapt silently, document the deviation in `session_log.md`
- If the drift is larger but you can still achieve the plan's intent with a reasonable adjustment: make the adjustment, document it thoroughly in `execution_state.md` deviations section and `session_log.md`
- If the plan is fundamentally wrong and continuing would produce something the user clearly did not want: this is a hard stop (see below)

### Phase ordering

Default is strict sequential ordering. Only violate if:
- A small prerequisite from a later phase is needed to unblock the current phase — pull it forward, document why
- The plan itself is clearly wrong about ordering (e.g., phase 3 depends on phase 5's output) — reorder logically, document why

Use the same threshold as `execute-plan`: the ordering must be **clearly wrong**, not merely suboptimal.

## Hard stops

Autopilot stops **only** in these situations. These are cases where continuing would be irresponsible:

1. **External dependency that cannot be resolved.** You need credentials, API keys, access to a third-party service, hardware, or human approval for a deployment that you cannot perform. State exactly what is needed and what phase is blocked.

2. **Fundamentally broken plan.** The plan's core direction is wrong in a way that cannot be fixed by small adjustments. Continuing would produce something the user did not intend. State what is wrong and why you stopped.

3. **Catastrophic failure.** The codebase is in a state where tests are completely broken, the project does not compile, or you have introduced a regression that you cannot fix after a reasonable attempt. State what happened.

4. **Context limit approaching.** If you are running low on context and still have phases to complete, stop at the current phase boundary, commit all work, update all state files, and tell the user to re-invoke `/autopilot` to continue. The durable state in `execution_state.md` and `session_log.md` ensures you can pick up exactly where you left off.

When you hit a hard stop:
1. Update `execution_state.md` and `session_log.md` with the full situation **first**
2. Stage and commit state files together with any uncommitted implementation work in a single coherent commit. If implementation work is in a broken state, commit only the state files so the plan is recoverable. Use message: `Autopilot hard stop for <slug> at phase N: <reason>`
3. Report to the user clearly: what phase, what happened, what is needed to continue

The order matters: state files must be updated before the commit so they are included. Never commit code changes without also committing the current state files — this is how orphan plans happen.

**Everything else is your call.** If you are uncertain but the plan gives you enough to make a reasonable decision, make it and document it. That is what autopilot means.

## Execution rules

Follow the same implementation rules as `execute-plan`:

- Inspect relevant files before changing them
- Prefer minimal but complete changes
- Keep changes scoped to the current phase
- Validate with tests, builds, or local checks when appropriate
- Do not silently expand scope
- Protect working parts of the system
- Avoid rewrite enthusiasm

### Commit discipline

- Commit after each phase is implemented and verified (before review)
- Commit after review fixes (Claude fix commit, Codex fix commit — same format as `execute-review`)
- Commit plan finalization as one atomic archival commit when the plan completes: `Archive completed plan <slug>`
- Use clear messages tied to the phase: `Execute plan <slug> phase N: <short description>`
- Review fix format: `Claude's fix of phase N code review: <short summary>` / `Codex fix of phase N code review: <short summary> (fixed by Codex)`
- Never commit unrelated changes
- Never commit broken states

### State file maintenance

Keep durable state current throughout the run:

- Update `execution_state.md` after every phase status change (started, done, reviewed)
- Append to `session_log.md` after every phase completion and every review completion
- Record all autonomous decisions with reasoning in `session_log.md`
- Record all deviations from the plan in `execution_state.md` section 8

Use the same structures as `execute-plan` and `execute-review`:

**execution_state.md sections:** Plan Reference, Current Overall Status, Phase Tracker (with review metadata fields), Current Active Phase, Completed Work, Open Blockers, Next Session Starting Point, Deviations from Plan, Updated On

**session_log.md entry format:**
```md
## Session YYYY-MM-DD HH:MM (autopilot)
- plan: <slug>
- mode: autopilot
- active phase: N (or "N through M" if multiple phases covered)
- objective:
- actions taken:
- autonomous decisions:
- files touched:
- verification performed:
- commits:
- codex availability:
- status after session:
- blockers:
- hard stop reason: (none, or reason)
- next starting point:
```

This format is a superset of the `execute-plan` session log format, adding `mode`, `autonomous decisions`, `codex availability`, and `hard stop reason`. Both formats can coexist in the same `session_log.md` if a plan switches between manual and autopilot execution.

**Normalization rule:** When reading a `session_log.md` that contains entries from both formats, treat the `execute-plan` format as equivalent to an autopilot entry with `mode: manual`, `autonomous decisions: none`, `codex availability: n/a`, and `hard stop reason: none`. When writing entries, always use the autopilot superset format regardless of which skill is active — this ensures the log is uniform going forward without rewriting existing entries.

## Review rules

Follow the same review loop as `execute-review`, with these autopilot-specific adjustments:

- Always attempt Codex first for each phase review
- If Codex is unavailable, fall back to Claude review immediately without asking (document provenance)
- Resolve disagreements autonomously per the decision rules above
- Archive each phase review artifact to `.ai/archive/` using the same naming convention: `YYYYMMDD-<slug>-phase-NN-review.md`
- Do not leave `review.md` from a previous phase lying around — archive it before starting the next phase review

### Codex review command

Use the same `codex exec` prompt template as `execute-review`. Read the relevant phase section from `final_plan.md` before writing the prompt. Include plan context (accepted/rejected critiques, architecture decisions) so Codex does not flag intentional design decisions.

## Reporting

### During the run

Keep in-chat output minimal during autopilot. The user chose autopilot to avoid noise.

Report briefly at these points only:
- **Start:** "Starting autopilot for `<slug>`: N phases remaining, beginning at phase M."
- **Hard stop:** Full explanation of what happened and what is needed.
- **Done:** Final summary (see below).

Do not report after every phase. The session log captures the details.

### Final report

When autopilot completes the entire plan, provide a concise summary:

```
Autopilot complete for `<slug>`.

Phases: N executed, N reviewed, N archived
Commits: [list of commit SHAs with short messages]
Autonomous decisions: N (see session_log.md for details)
Codex availability: available for N/N reviews (or fallback details)
Deviations from plan: N (see execution_state.md section 8)
Plan status: completed, archived to .ai/archive/<slug>/
```

### After a hard stop

When autopilot stops before completion:

```
Autopilot stopped for `<slug>` at phase N.

Completed: phases 1-M executed and reviewed
Current phase: N — [status and what happened]
Reason: [clear explanation]
What is needed: [specific action required to continue]
To resume: run `/autopilot <slug>` after resolving the blocker
```

## Plan finalization

Same rules as `execute-review`:
1. Mark linked todo items as done
2. Record final review archive path
3. Archive final review artifact
4. Copy `.ai/plans/<slug>/` to `.ai/archive/<slug>/`
5. Update `.ai/plans.md`: set status to `completed`
6. Delete `.ai/plans/<slug>/`

## Style rules

- Be autonomous, not chatty
- Document decisions in files, not in chat
- Keep chat output to start, hard stops, and final report
- Write crisp, factual session log entries
- No motivational filler in any artifact
- No pretending partial work is finished

## File handling

Before finishing (whether done or hard-stopped):
1. Ensure `execution_state.md` is fully current
2. Ensure `session_log.md` has entries for all work done in this run
3. Ensure all review artifacts are archived
4. Ensure all commits are clean and atomic
5. Ensure `plans.md` reflects the current status
6. If plan completed: ensure archival is done and plan directory is deleted
7. Provide the final report or hard stop report in chat

---
name: quick-critique
description: Use this skill when an active plan's .ai/plans/<slug>/final_plan.md should be critiqued by Codex CLI as a skeptical external reviewer — especially for plans created via quick-plan that had no brainstorm-critique step. Produces .ai/plans/<slug>/codex_critique.md. Handles Codex usage limits and fallback the same way as brainstorm-critique.
---

# Quick Critique Skill

Your job is to use Codex CLI as the critique agent for an active plan's `final_plan.md`.

This skill is the quick-path counterpart of `brainstorm-critique`. Where `brainstorm-critique` reviews a brainstorm or evolution artifact before synthesis, this skill reviews the `final_plan.md` directly — typically after `/quick-plan` produced it without a prior critique step.

## When to use this skill

Use this skill when:
- `.ai/plans/<slug>/final_plan.md` exists with status `active`
- the plan was created via `quick-plan` (or any other path) without a prior Codex critique
- the user wants a skeptical external review before starting execution
- the critique should come from Codex, not from Claude alone

Do not use this skill for:
- critiquing a brainstorm artifact — use `brainstorm-critique` instead
- critiquing an evolution plan — use `brainstorm-critique` instead
- git diff review or code review
- bug fixing or direct implementation

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

**This skill's state responsibility:** Read `final_plan.md` from `.ai/plans/<slug>/`, write `.ai/plans/<slug>/codex_critique.md`. This skill does **not** read or modify plan state files (`execution_state.md`, `session_log.md`). It does **not** modify `final_plan.md`.

## Legacy layout detection

Before doing any work, check for a legacy (pre-namespace) layout:

If `.ai/final_plan.md` exists at root AND `.ai/plans.md` does not exist, this is a legacy layout.
Stop and suggest: "Run `/plan-migrate` to upgrade to the namespaced plan layout."
Do not proceed with the legacy layout.

## Plan slug resolution

Every invocation must resolve a plan slug before doing work.

1. If the user provided a slug explicitly (e.g., `/quick-critique fix-sidebar-layout`), use it.
2. If not, read `.ai/plans.md`.
3. Filter to plans with status `active` that have `final_plan.md` in their directory.
4. If exactly one plan matches, use it silently.
5. If zero match, say so clearly and stop.
6. If multiple match, list them and ask the user to choose.

## Primary objective

Create or overwrite:

`.ai/plans/<slug>/codex_critique.md`

using Codex CLI as the reviewing agent.

## Preconditions

Before starting:
1. Resolve the plan slug (see above)
2. Verify `.ai/plans/<slug>/final_plan.md` exists. If not, stop and say so.
3. If `.ai/plans/<slug>/execution_state.md` exists and has phases `in progress` or `done`, warn the user that execution has already started and ask whether they still want to critique the plan.
4. Ensure the `.ai/plans/<slug>/` directory exists

## Execution rule

Do not write the critique yourself unless Codex CLI is unavailable or the shell command fails.

Instead, invoke Codex CLI through the shell and save its output to `.ai/plans/<slug>/codex_critique.md`.

## Preferred shell command

Run this command (substitute the resolved slug):

```bash
mkdir -p .ai/plans/<slug> && \
cat .ai/plans/<slug>/final_plan.md | codex exec -C . --skip-git-repo-check \
  --output-last-message .ai/plans/<slug>/codex_critique.md \
  "You are a skeptical principal engineer and product critic.
Critique this plan rigorously, but calibrate to the actual project stage and scope.

This is a finalized plan (not a brainstorm), so focus your critique on whether the plan is ready for execution rather than on ideation-stage concerns.

Assume a solo-dev or small-team pre-launch context unless the plan explicitly says otherwise.
Do not assume enterprise scale, high traffic, many customers, strict compliance requirements, or complex operations unless stated.
Do not frame routine UI/layout work as major architecture risk unless it would realistically cause correctness, migration, or multi-session maintenance problems.
Be direct, but avoid melodramatic language or inflated severity.

Focus on:
1. weak assumptions
2. overengineering or underengineering
3. hidden costs
4. missing phases or gaps in the roadmap
5. unrealistic definitions of done
6. integration risk
7. missing edge cases
8. simpler alternatives

For each major point, indicate severity as one of:
- real blocker
- worth considering
- minor nit

Prefer short, concrete findings over long risk essays.
Include a brief final stance on which concerns should actually change the plan versus which ones can safely be ignored for now.

Return only markdown."
```

This form is preferred because `--output-last-message` writes the final assistant message directly to `.ai/plans/<slug>/codex_critique.md` instead of relying on raw stdout redirection.

## After execution

After Codex finishes:
1. Read `.ai/plans/<slug>/codex_critique.md`
2. Confirm it is substantive and not empty
3. Give a short in-chat summary of:
   - biggest concern raised
   - strongest confirmation of the plan
   - suggested next step: re-run `/quick-plan <slug>` to incorporate findings, or proceed with `/execute-plan` if no blockers

## Validation rules

The critique should be concrete and decision-useful.
It should not be empty, generic, or polite filler.
It should challenge assumptions and identify simplifications.
It should be calibrated to the actual stage of the project rather than defaulting to enterprise or large-scale assumptions.
It should separate true blockers from lower-priority concerns.

If the critique is weak or clearly failed, say so instead of pretending it succeeded.

## Fallback rule

Codex has priority for this skill. Always attempt the Codex critique first for each invocation. Never assume an earlier usage-limit failure is still in effect.

If Codex CLI is unavailable or the shell command fails in the current invocation:
- say clearly that Codex could not be invoked
- include the actual failure reason when known, for example usage limit, quota, rate limit, auth failure, or process error
- do not pretend Codex reviewed it
- ask whether Claude should produce a temporary critique instead

If the user explicitly approves a temporary Claude fallback:
- Claude may produce the critique for this invocation only
- write it to `.ai/plans/<slug>/codex_critique.md` so the downstream flow can continue
- prepend a clear provenance note stating that this file was generated by Claude as a temporary fallback because Codex failed in this invocation, including the failure reason if known
- keep the rest of the file as a real critique artifact, not filler

If the user does not explicitly approve the fallback:
- stop without creating or changing `codex_critique.md`

If a future invocation can reach Codex again, prefer Codex and overwrite the temporary Claude fallback critique with a real Codex critique.

## Re-planning flow

After the user reads the critique, they may choose to:
1. **Re-plan:** Run `/quick-plan <slug>` again. Quick-plan will read `codex_critique.md`, incorporate relevant findings into the updated `final_plan.md`, and then delete the stale `codex_critique.md`.
2. **Proceed anyway:** Run `/execute-plan <slug>` directly. The critique remains as documentation but does not block execution.

This skill does not enforce either path. It produces the critique and lets the user decide.

## Style rules

- Be honest about whether Codex actually ran
- Prefer concrete critique over soft wording
- Preserve the distinction between Claude orchestration and Codex critique
- Do not drift into code review semantics
- Avoid exaggerated language that makes routine work sound like major infrastructure risk

## File handling

Before finishing:
1. Ensure `.ai/plans/<slug>/codex_critique.md` exists if Codex succeeded or the user explicitly approved the temporary Claude fallback
2. Ensure it contains meaningful markdown and is not just whitespace
3. Ensure the critique clearly targets the `final_plan.md` content
4. If Claude fallback was used, ensure the provenance note is explicit and truthful
5. Then provide a short in-chat summary of the result

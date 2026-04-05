---
name: brainstorm-critique
description: Use this skill when .ai/claude_brainstorm.md exists and should be critiqued by Codex CLI as a skeptical external reviewer. Produces .ai/codex_critique.md.
---

# Brainstorm Critique Skill

Your job is to use Codex CLI as the critique agent for an existing brainstorm artifact.

## When to use this skill

Use this skill when:
- `.ai/claude_brainstorm.md` already exists
- the user wants a critique, second opinion, pressure test, or adversarial review
- the critique should come from Codex, not from Claude alone

Do not use this skill for:
- git diff review
- code review
- bug fixing
- generating the first brainstorm from scratch
- direct implementation

## Pipeline Context

This skill is **step 2 of 5** in a planning pipeline:

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

**This skill's state responsibility:** Read `.ai/claude_brainstorm.md`, write `.ai/codex_critique.md`. This skill does **not** read or modify plan state files (`final_plan.md`, `execution_state.md`).

## Primary objective

Create or overwrite:

`.ai/codex_critique.md`

using Codex CLI as the reviewing agent.

## Preconditions

Before starting:
1. Check whether `.ai/claude_brainstorm.md` exists
2. If it does not exist, say so clearly and stop
3. Ensure the `.ai` directory exists

## Execution rule

Do not write the critique yourself unless Codex CLI is unavailable or the shell command fails.

Instead, invoke Codex CLI through the shell and save its output to `.ai/codex_critique.md`.

## Preferred shell command

Run this command:

```bash
mkdir -p .ai && \
cat .ai/claude_brainstorm.md | codex exec -C . --skip-git-repo-check \
  --output-last-message .ai/codex_critique.md \
  "You are a skeptical principal engineer and product critic.
Critique this brainstorm aggressively.

Focus on:
1. weak assumptions
2. overengineering
3. hidden costs
4. migration risk
5. integration risk
6. missing edge cases
7. simpler alternatives

Return only markdown."
```

This form is preferred because `--output-last-message` writes the final assistant message directly to `.ai/codex_critique.md` instead of relying on raw stdout redirection.

## After execution

After Codex finishes:
1. Read `.ai/codex_critique.md`
2. Confirm it is substantive and not empty
3. Give a short in-chat summary of:
   - biggest weakness
   - strongest surviving direction

## Validation rules

The critique should be concrete and decision-useful.
It should not be empty, generic, or polite filler.
It should challenge assumptions and identify simplifications.

If the critique is weak or clearly failed, say so instead of pretending it succeeded.

## Fallback rule

If Codex CLI is unavailable or the shell command fails:
- say clearly that Codex could not be invoked
- do not pretend Codex reviewed it
- ask whether Claude should produce a temporary critique instead

## Style rules

- Be honest about whether Codex actually ran
- Prefer concrete critique over soft wording
- Preserve the distinction between Claude orchestration and Codex critique
- Do not drift into git diff review semantics

## File handling

Before finishing:
1. Ensure `.ai/codex_critique.md` exists if Codex succeeded
2. Ensure it contains meaningful markdown and is not just whitespace
3. Then provide a short in-chat summary of the result

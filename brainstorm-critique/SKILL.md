---
name: brainstorm-critique
description: Use this skill when a planning artifact in .ai/plans/<slug>/ should be critiqued by Codex CLI as a skeptical external reviewer. Supports both claude_brainstorm.md and evolution_plan.md as input and produces .ai/plans/<slug>/codex_critique.md.
---

# Brainstorm Critique Skill

Your job is to use Codex CLI as the critique agent for an existing planning artifact.

## When to use this skill

Use this skill when:
- `.ai/plans/<slug>/claude_brainstorm.md` already exists, or
- `.ai/plans/<slug>/evolution_plan.md` already exists
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

**This skill's state responsibility:** Read one planning input artifact from `.ai/plans/<slug>/` (`claude_brainstorm.md` or `evolution_plan.md`), write `.ai/plans/<slug>/codex_critique.md`. This skill does **not** read or modify plan state files (`final_plan.md`, `execution_state.md`).

## Legacy layout detection

Before doing any work, check for a legacy (pre-namespace) layout:

If `.ai/final_plan.md` exists at root AND `.ai/plans.md` does not exist, this is a legacy layout.
Stop and suggest: "Run `/plan-migrate` to upgrade to the namespaced plan layout."
Do not proceed with the legacy layout.

## Plan slug resolution

Every invocation must resolve a plan slug before doing work.

1. If the user provided a slug explicitly (e.g., `/brainstorm-critique auth-rewrite`), use it.
2. If not, read `.ai/plans.md`.
3. Filter to plans with status `brainstorming` that have a planning input artifact (`claude_brainstorm.md` or `evolution_plan.md`) in their directory.
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
2. Determine the critique input source:
   - **Standard path:** `.ai/plans/<slug>/claude_brainstorm.md`
   - **Evolution path:** `.ai/plans/<slug>/evolution_plan.md`
3. If both input files exist, stop and ask the user which artifact should be critiqued. Do not silently pick one.
4. If neither input file exists, say so clearly and stop.
5. Ensure the `.ai/plans/<slug>/` directory exists

## Execution rule

Do not write the critique yourself unless Codex CLI is unavailable or the shell command fails.

Instead, invoke Codex CLI through the shell and save its output to `.ai/plans/<slug>/codex_critique.md`.

## Preferred shell command

Run this command (substitute the resolved slug and input filename):

```bash
mkdir -p .ai/plans/<slug> && \
cat .ai/plans/<slug>/<input-file> | codex exec -C . --skip-git-repo-check \
  --output-last-message .ai/plans/<slug>/codex_critique.md \
  "You are a skeptical principal engineer and product critic.
Critique this planning artifact aggressively.

If the artifact is an evolution plan, critique it as a grounded v2 proposal rather than as greenfield brainstorming.

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

This form is preferred because `--output-last-message` writes the final assistant message directly to `.ai/plans/<slug>/codex_critique.md` instead of relying on raw stdout redirection.

## After execution

After Codex finishes:
1. Read `.ai/plans/<slug>/codex_critique.md`
2. Confirm it is substantive and not empty
3. Give a short in-chat summary of:
   - biggest weakness
   - strongest surviving direction or recommendation

## Validation rules

The critique should be concrete and decision-useful.
It should not be empty, generic, or polite filler.
It should challenge assumptions and identify simplifications.

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
- write it to `.ai/plans/<slug>/codex_critique.md` so the downstream pipeline can continue
- prepend a clear provenance note stating that this file was generated by Claude as a temporary fallback because Codex failed in this invocation, including the failure reason if known
- keep the rest of the file as a real critique artifact, not filler

If the user does not explicitly approve the fallback:
- stop without creating or changing `codex_critique.md`

If a future invocation can reach Codex again, prefer Codex and overwrite the temporary Claude fallback critique with a real Codex critique.

## Style rules

- Be honest about whether Codex actually ran
- Prefer concrete critique over soft wording
- Preserve the distinction between Claude orchestration and Codex critique
- Do not drift into git diff review semantics

## File handling

Before finishing:
1. Ensure `.ai/plans/<slug>/codex_critique.md` exists if Codex succeeded or the user explicitly approved the temporary Claude fallback
2. Ensure it contains meaningful markdown and is not just whitespace
3. Ensure the critique clearly matches the selected input artifact
4. If Claude fallback was used, ensure the provenance note is explicit and truthful
5. Then provide a short in-chat summary of the result

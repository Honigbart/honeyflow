# Claude Code Planning Skills

A set of skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that bring structured planning, execution, and review to your projects. Plans get critiqued by [Codex CLI](https://github.com/openai/codex) as an independent skeptical reviewer, and completed implementation phases go through a bounded Claude/Codex review loop before the plan is archived.

The goal is simple: think before you build, get a second opinion, execute with discipline, and review what you shipped.

## What's included

| Skill | Purpose |
|---|---|
| `/brainstorm` | Interactive ideation with Claude. Produces a structured 17-section artifact. |
| `/brainstorm-critique` | Sends the brainstorm to Codex CLI for a skeptical review. |
| `/brainstorm-synthesize` | Merges brainstorm + critique into a decisive `final_plan.md`. |
| `/quick-plan` | Creates `final_plan.md` directly for smaller, well-understood tasks. |
| `/quick-critique` | Sends a quick plan to Codex CLI for review. |
| `/execute-plan` | Phase-by-phase implementation with durable state tracking across sessions. |
| `/execute-review` | Post-implementation review per phase through a Claude/Codex loop. |
| `/evolve` | Takes a completed plan and proposes a grounded v2 direction. |
| `/todo` | Lightweight project todo list that integrates with the planning pipeline. |
| `/plan-migrate` | Migrates legacy single-plan layouts to the namespaced format. |

## Install

Clone the repo somewhere on your machine:

```bash
git clone git@github.com:Honigbart/honeyflow.git ~/honeyflow
```

Then symlink each skill into your Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills

for skill in brainstorm brainstorm-critique brainstorm-synthesize \
             quick-plan quick-critique execute-plan execute-review \
             evolve todo plan-migrate; do
  ln -s ~/honeyflow/$skill ~/.claude/skills/$skill
done
```

That's it. The skills will be available in your next Claude Code session.

## How it works

All plans live under `.ai/plans/<slug>/` in your project. Each plan gets its own directory with artifacts like `final_plan.md`, `execution_state.md`, `session_log.md`, and `review.md`. Completed plans are archived to `.ai/archive/<slug>/`.

There are two paths into the pipeline:

**Full path** for bigger, exploratory work:
```
/brainstorm → /brainstorm-critique → /brainstorm-synthesize → /execute-plan → /execute-review
```

**Quick path** for smaller, well-understood tasks:
```
/quick-plan → (optional: /quick-critique) → /execute-plan → /execute-review
```

Both paths produce the same `final_plan.md` structure, so execution and review work identically regardless of how the plan was created. After a plan is fully implemented and reviewed, `/evolve` can kick off the next version.

## Examples

### Full brainstorm flow

```
You:    /brainstorm
        I want to add a prompt template system to the API

Claude: [asks questions, discusses options with you]
Claude: [writes .ai/plans/prompt-templates/claude_brainstorm.md]

You:    /brainstorm-critique

Claude: [runs Codex CLI, writes codex_critique.md]
        "Codex thinks the versioning approach is overengineered for v1..."

You:    /brainstorm-synthesize

Claude: [merges brainstorm + critique into final_plan.md, 4 phases]
        "Direction: simple file-based templates, no DB. Biggest risk: ..."

You:    /execute-plan
Claude: [implements phase 1, updates execution_state.md, commits]

You:    /execute-plan
Claude: [implements phase 2, ...]

        ... (repeat until all phases done)

You:    /execute-review
Claude: [Codex reviews phase 1, Claude fixes, Codex re-reviews, archives]

        ... (repeat for each phase, then plan is archived)
```

### Quick plan flow

```
You:    /quick-plan add-rate-limiting
        Add rate limiting middleware to the API routes, 100 req/min per API key

Claude: [inspects codebase, writes final_plan.md with 2 phases]
        "2 phases: middleware + tests. Run /quick-critique or /execute-plan next."

You:    /execute-plan

Claude: [implements phase 1, commits]

You:    /execute-plan
Claude: [implements phase 2, commits, all phases done, awaiting review]

You:    /execute-review
Claude: [Codex reviews, clean, archives plan]
```

### Evolve flow

```
You:    /evolve prompt-templates
        The template system works but needs variable validation and a preview endpoint

Claude: [reads archived plan + current code, writes evolution_plan.md as prompt-templates-v2]
        "Recommended: add JSON Schema validation + preview route. 3 phases."

You:    /brainstorm-synthesize prompt-templates-v2

Claude: [synthesizes evolution plan into final_plan.md]

You:    /execute-plan
        ... (same execution + review cycle as above)
```

## Notes

**Codex CLI required for critiques and reviews.** The `/brainstorm-critique`, `/quick-critique`, and `/execute-review` skills invoke [Codex CLI](https://github.com/openai/codex) through the shell. If Codex is unavailable (rate limit, auth failure, quota), the skill will tell you the reason and ask if Claude should produce a temporary fallback critique instead. If you say yes, the fallback gets a provenance note so you know it wasn't Codex. A future invocation will prefer Codex again and can overwrite the fallback.

**Plans are durable across sessions.** The `execution_state.md` and `session_log.md` files track exactly where you left off. You can close your terminal, come back tomorrow, run `/execute-plan`, and it picks up from the right phase.

**Review gates completion.** A plan isn't archived just because implementation is done. Every completed phase must also pass the `/execute-review` Codex loop. If Claude and Codex disagree on a finding, the phase is marked `in disagreement` and you decide how to proceed.

**Todo integration.** If you maintain `.ai/todo.md` via `/todo`, brainstorm and quick-plan will pick up your Now/Next items as context. When a plan that references todo items is fully completed and reviewed, those items get auto-marked as done.

## License

MIT

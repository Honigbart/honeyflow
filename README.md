# Claude Code Planning Skills

A set of skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that bring structured planning, execution, and review to your projects. Plans get critiqued by [Codex CLI](https://github.com/openai/codex) as an independent skeptical reviewer, and completed implementation phases go through a bounded Claude/Codex review loop before the plan is archived. If you want extra local scrutiny, the critique and review skills can also add a local Ollama-based third voice.

The goal is simple: think before you build, get a second opinion, execute with discipline, and review what you shipped.

## What's included

| Skill | Purpose |
|---|---|
| `/brainstorm` | Interactive ideation with Claude. Produces a structured 17-section artifact. |
| `/brainstorm-critique` | Sends the brainstorm to Codex CLI for a skeptical review. |
| `/brainstorm-synthesize` | Merges brainstorm + critique into a decisive `final_plan.md`. |
| `/quick-plan` | Creates `final_plan.md` directly for smaller, well-understood tasks. |
| `/quick-critique` | Sends a quick plan to Codex CLI for review. Supports `--apply` to immediately re-run quick-plan with the critique incorporated. |
| `/execute-plan` | Phase-by-phase implementation with durable state tracking across sessions. |
| `/execute-review` | Post-implementation review per phase through a Claude/Codex loop. |
| `/quality-eval` | Durable qualitative evaluation for slow comparisons, output-quality checks, and fresh-session handoff via `.ai/evals/<slug>/`. |
| `/autopilot` | Fully autonomous execution + review of all phases. No user input needed. |
| `/evolve` | Takes a completed plan and proposes a grounded v2 direction. |
| `/follow-up` | Lists, starts, and resolves durable follow-on artifacts from active and archived plans via `.ai/follow_ups.md`. |
| `/todo` | Lightweight project todo list with priority buckets. Feeds context into planning. |
| `/plan-migrate` | Migrates plan layouts when the skill format changes. |

## Install

Clone the repo somewhere on your machine:

```bash
git clone git@github.com:Honigbart/honeyflow.git ~/honeyflow
```

Then symlink each skill into your Claude Code skills directory.

**Linux / macOS / WSL:**

```bash
mkdir -p ~/.claude/skills

for skill in brainstorm brainstorm-critique brainstorm-synthesize \
             quick-plan quick-critique execute-plan execute-review quality-eval \
             autopilot evolve follow-up todo plan-migrate; do
  ln -s ~/honeyflow/$skill ~/.claude/skills/$skill
done
```

**Windows (PowerShell, run as Administrator):**

```powershell
$skills = @("brainstorm","brainstorm-critique","brainstorm-synthesize",
            "quick-plan","quick-critique","execute-plan","execute-review","quality-eval",
            "autopilot","evolve","follow-up","todo","plan-migrate")

foreach ($skill in $skills) {
  New-Item -ItemType SymbolicLink `
    -Path "$env:USERPROFILE\.claude\skills\$skill" `
    -Target "$env:USERPROFILE\honeyflow\$skill"
}
```

The skills will be available in your next Claude Code session.

## Optional: Codex CLI

Three skills (`/brainstorm-critique`, `/quick-critique`, `/execute-review`) and `/autopilot` use [Codex CLI](https://github.com/openai/codex) as an independent reviewer. If Codex is installed, it runs the critique/review. If it's not installed (or hits a usage limit, auth failure, etc.), the skills fall back automatically to a Claude subagent — no manual intervention needed.

To install Codex CLI:

```bash
npm install -g @openai/codex
```

You'll need an `OPENAI_API_KEY` in your environment. See the [Codex CLI docs](https://github.com/openai/codex) for setup details.

**Without Codex CLI, the full pipeline still works.** You just get Claude-on-Claude review instead of Claude-vs-Codex review.

## Optional: Local Ollama Third Voice

If you want more eyes on plan critique and phase review, the skills can also run a **local Ollama reviewer** after the normal Codex pass.

This is deliberately a supplement, not a new primary gate:
- Codex remains the primary external reviewer.
- Ollama findings are advisory only.
- If `ollama` and the configured local model are available, the skills should attempt the Ollama pass.
- Missing Ollama, missing local model, or a local Ollama failure must not break the normal workflow.

The skills look for this local Ollama model alias:

- `local-reviewer:latest`

You can back that alias with Gemma, Qwen, or another instruction-following local model. The skills do **not** require Gemma specifically. They only require that this alias exists and that the backing model is good enough at critique/review-style instruction following.

The recommended shared Modelfile in this repo is:

- `ollama-models/Modelfile-gemma4-26b-reviewer`

This shared reviewer alias is preferred over separate plan/code aliases because it reduces duplicate model residency pressure while still letting the skills specialize behavior through task-specific prompts.

They use the [unsloth/gemma-4-26B-A4B-it-GGUF](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF) family as one strong default. A good starting point is:

- `gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf`

Hardware note:
- a 26B-class local model can require substantial VRAM and/or system RAM
- whether it runs well depends on your quant, context size, GPU offload, and Ollama setup
- do not assume a laptop or smaller GPU will handle the default example comfortably

If that is too heavy, use a smaller or more aggressively quantized variant, for example:

- `gemma-4-26B-A4B-it-UD-IQ4_NL.gguf`

You are also not restricted to Gemma 4. If you prefer a different local model family such as Qwen Coder, edit the `FROM ...` line in the Modelfile and keep the alias names the same when you run `ollama create`.

Gemma-based example setup:

```bash
cd ~/honeyflow/claude-skills
mkdir -p ollama-models/weights

huggingface-cli download unsloth/gemma-4-26B-A4B-it-GGUF \
  gemma-4-26B-A4B-it-UD-Q4_K_XL.gguf \
  --local-dir ollama-models/weights

cd ollama-models
ollama create local-reviewer -f Modelfile-gemma4-26b-reviewer
```

Notes:
- The `ollama-models/weights/` directory is gitignored on purpose. Keep local GGUF weights there without polluting the repo.
- If you use a different GGUF filename or quant, edit the `FROM ./weights/...` line in the Modelfile before running `ollama create`.
- If you want to use another Ollama base model entirely, you can also change the `FROM` line to something like an existing local Ollama model tag instead of a GGUF path.
  Example:
  `FROM qwen2.5-coder:14b`
- The skills expect this alias name by default:
  - `local-reviewer:latest`
- The backing base model is your choice. Gemma 4 is one option, not a requirement.
- `/plan-migrate` is not needed for this addition. `ollama_critique.md` and `ollama_review.md` are extra artifacts that appear only when the local Ollama reviewer is configured and actually runs.

## How it works

All state lives under `.ai/` in your project root:

```
.ai/
├── plans.md                        # index of all plans (slug, status, description)
├── follow_ups.md                   # durable registry of unresolved follow-on artifacts
├── todo.md                         # project todo list (Now / Next / Later / Done)
├── plans/
│   └── <slug>/                     # one directory per active plan
│       ├── final_plan.md           # the executable plan
│       ├── execution_state.md      # phase-by-phase progress tracker
│       ├── session_log.md          # chronological session history
│       ├── claude_brainstorm.md    # brainstorm artifact (full path only)
│       ├── codex_critique.md       # Codex critique output
│       ├── ollama_critique.md      # optional local Ollama critique output
│       ├── evolution_plan.md       # evolution proposal (evolve only)
│       ├── review.md               # active phase review artifact
│       ├── ollama_review.md        # optional local Ollama review artifact
│       └── superseded/             # optional snapshots before critique-driven overwrite
└── archive/                        # completed or abandoned plans
    └── <slug>/                     # full copy of the plan directory at completion
```

`todo.md` is global, not per-plan. It sits at `.ai/todo.md` and is shared across all plans. Plans reference specific todo items, and those references travel through the pipeline so they can be auto-completed when a plan is archived.

`follow_ups.md` is also global, but it solves a different problem. It is the durable working registry for unresolved `## 14. Follow-on Artifacts` coming from active or archived final plans. Unlike `todo.md`, it preserves source-plan provenance and can be picked up later by `/follow-up` without re-scanning every archived plan.

The registry is maintained by the bundled helper at `~/.claude/skills/follow-up/scripts/sync_follow_ups.py`. Planning and review skills should use that helper instead of hand-editing `follow_ups.md` whenever possible so IDs and section moves stay deterministic.

For qualitative validation that is not normal unit/integration testing, `/quality-eval` uses a separate durable area:

```
.ai/
└── evals/
    └── <slug>/
        ├── brief.md              # what to test and how
        ├── results.md            # rolling conclusions and recommendation
        └── runs/                 # optional raw outputs for long/slow comparisons
```

This is useful when a fresh session should continue a long-running output-quality check without reconstructing context from chat history.

There are two paths into the pipeline:

**Full path** for bigger, exploratory work:
```
/brainstorm → /brainstorm-critique → /brainstorm-synthesize → /execute-plan → /execute-review
```

**Quick path** for smaller, well-understood tasks:
```
/quick-plan → (optional: /quick-critique) → /execute-plan → /execute-review
```

**Autopilot** for hands-off execution (works with either path):
```
/quick-plan or /brainstorm-synthesize → /autopilot
```

All paths produce the same `final_plan.md` structure, so execution and review work identically regardless of how the plan was created. `/autopilot` replaces the manual `/execute-plan` + `/execute-review` loop when you want fully autonomous execution. After a plan is fully implemented and reviewed, `/evolve` can kick off the next version.

Follow-on artifacts are a separate loop:
```
/follow-up → (list | start | resolve)
```

`/follow-up start` can turn one preserved follow-on artifact into a new `/quick-plan` or `/brainstorm`, while keeping the source-plan link.

### Todo vs Follow-Ups

`/todo` maintains a lightweight task list at `.ai/todo.md` with three priority buckets: **Now**, **Next**, and **Later**. It's not just a standalone list though. When you run `/brainstorm` or `/quick-plan`, the skill reads your Now and Next items and uses them as context. If a plan addresses specific todo items, it tracks that reference all the way through: brainstorm notes it, synthesize carries it into the final plan, and when `/execute-review` archives a fully completed plan, the referenced todo items get auto-marked as done.

`/follow-up` is different. It works from `## 14. Follow-on Artifacts` in final plans and keeps a durable registry at `.ai/follow_ups.md` with source-plan provenance. Use it for deferred artifacts, broader-next-path items, or follow-on documents that should not be flattened into the simple Now/Next/Later todo list.

```
You:    /todo
        Add "fix rate limiting" to Now and "add webhook support" to Next

Claude: [updates .ai/todo.md]

You:    /quick-plan fix-rate-limiting
Claude: [reads todo, sees the Now item, references it in the plan]

        ... (execute + review cycle)

Claude: [archives plan, auto-marks "fix rate limiting" as done in todo.md]
```

### Follow-up flow

```
You:    /follow-up

Claude: [reads .ai/follow_ups.md]
        "Open: FU-003 API contracts for prompt templates (source: prompt-templates)"

You:    /follow-up start FU-003

Claude: [chooses quick-plan or brainstorm based on scope]
Claude: [creates a new linked plan and marks FU-003 as started]
```

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

You:    /quick-critique --apply add-rate-limiting

Claude: [runs Codex CLI, writes codex_critique.md]
Claude: [optionally runs local Ollama critique too]
Claude: [immediately re-runs quick-plan behavior for the same slug]
        "Plan tightened: Redis remains deferred, but multi-instance rollout caveat is now explicit."

You:    /execute-plan
Claude: [implements phase 1, commits]

You:    /execute-plan
Claude: [implements phase 2, commits, all phases done, awaiting review]

You:    /execute-review
Claude: [Codex reviews, clean, archives plan]
```

The `/quick-critique` step is optional. If the task is straightforward, go straight from `/quick-plan` to `/execute-plan`. If you already know you want to incorporate critique immediately, use `/quick-critique --apply` as the fast path.

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

### Autopilot flow

```
You:    /quick-plan add-rate-limiting
        Add rate limiting middleware to the API routes, 100 req/min per API key

Claude: [writes final_plan.md with 2 phases]

You:    /autopilot

Claude: "Starting autopilot for add-rate-limiting: 2 phases remaining, beginning at phase 1."

        [implements phase 1, commits]
        [runs Codex review on phase 1, clean, archives review]
        [implements phase 2, commits]
        [runs Codex review on phase 2, finds issue, Claude fixes, Codex re-reviews, clean]
        [archives plan to .ai/archive/add-rate-limiting/]

        "Autopilot complete for add-rate-limiting.
         Phases: 2 executed, 2 reviewed
         Commits: abc1234, def5678, ghi9012
         Autonomous decisions: 1 (see session_log.md)
         Plan status: completed"
```

Autopilot makes all decisions on its own. If Codex is unavailable, it falls back to Claude review automatically. If Claude and Codex disagree on a finding, it resolves the disagreement based on what the plan says and moves on. It only stops for things it truly cannot resolve (missing credentials, fundamentally broken plan, or running out of context).

## Notes

**Codex CLI required for critiques and reviews.** The `/brainstorm-critique`, `/quick-critique`, and `/execute-review` skills invoke [Codex CLI](https://github.com/openai/codex) through the shell. Unless a skill command explicitly overrides it, those Codex runs inherit the user's local Codex CLI configuration (for example `model` and reasoning settings from `~/.codex/config.toml`). If Codex is unavailable (rate limit, auth failure, quota), all skills fall back to a **Claude subagent** — a separate Claude instance with a fresh context window that has not seen the planning or implementation reasoning. This breaks the "checking your own homework" blind spot that makes self-review unreliable, whether reviewing plans or code. The subagent reads the artifacts independently, applies the same critique/review criteria, and writes findings without anchoring to the original author's reasoning. All fallback artifacts get a provenance note so you know it wasn't Codex. A future invocation will prefer Codex again.

**Local Ollama review is required when available, but still supplemental.** If `ollama` is installed and the local reviewer models exist, the critique and review skills should attempt to write `ollama_critique.md` or `ollama_review.md` on every applicable pass. Those artifacts are advisory only. They add signal, but they do not replace Codex and they must not block the workflow when the local Ollama run is unavailable or fails.

**Plans are durable across sessions.** The `execution_state.md` and `session_log.md` files track exactly where you left off. You can close your terminal, come back tomorrow, run `/execute-plan`, and it picks up from the right phase.

**Review gates completion.** A plan isn't archived just because implementation is done. Every completed phase must also pass the `/execute-review` Codex loop. If Claude and Codex disagree on a finding, the phase is marked `in disagreement` and you decide how to proceed.

**Archive location.** Completed plans currently archive to `.ai/archive/<slug>/`. A future version may move this to `.ai/plans/archive/<slug>/` to keep everything under one roof. When that happens, `/plan-migrate` will handle the transition.

**Recommended git policy for `.ai/`.** A good default is to version active workflow state but keep archived payloads local-only. In practice: track `.ai/plans.md`, `.ai/follow_ups.md`, `.ai/todo.md`, and active plan directories under `.ai/plans/<slug>/`, but ignore `.ai/archive/`. If `.ai/archive/` was previously tracked, remove it from the index once with `git rm -r --cached .ai/archive` and commit that change; the files stay on disk but stop creating churn in normal development. This is a git-tracking policy change only — it does **not** require `/plan-migrate`, because the on-disk `.ai/` layout stays the same. More generally: use `/plan-migrate` only when the artifact structure or directory layout changes, not when ignore rules or retention policy change.

**Updating the skills.** When the skill format changes (new artifact structure, renamed fields, directory layout changes), `/plan-migrate` acts as the migration engine. It detects outdated layouts in your project and upgrades them to the current format, similar to how database migrations work. Pull the latest skills, and if your `.ai/` layout needs updating, `/plan-migrate` will tell you.

## License

MIT

---
name: quality-eval
description: Use this skill when a feature, prompt, output, or UX flow needs qualitative validation that is not a normal unit/integration test — especially when a fresh session should pick up a durable eval brief and run multiple slow comparisons. Creates and maintains `.ai/evals/<slug>/` artifacts for eval planning, run logging, and conclusions.
---

# Quality Eval Skill

Your job is to create or run a durable qualitative evaluation.

This skill is for output quality, behavioral checks, prompt comparisons, model comparisons, UX judgment, and other validation that depends on looking at real results rather than only pass/fail tests.

It is especially useful when:
- the current session is getting full and you want a fresh session to continue
- each evaluation run is slow or expensive
- you need to compare multiple variants, models, prompts, or feature states
- output quality matters more than code coverage

Do not use this skill for:
- unit test authoring
- ordinary integration test setup
- broad exploratory brainstorming
- code review of an implementation diff

## Durable eval layout

Use `.ai/evals/<slug>/` for the eval bundle:

- `.ai/evals/<slug>/brief.md` — source of truth for what is being tested and how
- `.ai/evals/<slug>/results.md` — rolling summary of findings and recommendation
- `.ai/evals/<slug>/runs/` — optional raw run artifacts when outputs are long or worth preserving

Create `.ai/evals/` if it does not exist.

If the project already has a plan in `.ai/plans/<plan-slug>/`, you may reference it from the eval brief, but do not force the eval to live under the plan directory. This skill is intentionally broader than the plan pipeline.

## Modes

This skill has two modes.

### Mode 1 — Prepare

Use when the user wants to set up a durable eval brief now and run the actual validation later or in a fresh session.

Do this:
1. Resolve or derive an eval slug
2. Inspect only the context needed to understand the thing being validated
3. Write `.ai/evals/<slug>/brief.md`
4. If helpful, initialize `.ai/evals/<slug>/results.md` with an empty skeleton
5. Tell the user exactly how a fresh session should resume

### Mode 2 — Run or Resume

Use when `.ai/evals/<slug>/brief.md` already exists or the user explicitly wants the evaluation executed now.

Do this:
1. Read `.ai/evals/<slug>/brief.md`
2. Run the planned comparisons or scenarios
3. Save raw outputs under `.ai/evals/<slug>/runs/` when they are too long or too important to compress safely
4. Update `.ai/evals/<slug>/results.md`
5. End with a recommendation and exact next step

## Eval slug resolution

1. If the user provides a slug, use it
2. Otherwise derive one from the feature or question: kebab-case, 2-5 words, no dates
3. If `.ai/evals/<slug>/brief.md` already exists, treat this as resume unless the user explicitly wants a fresh eval

## Required brief structure

Write `.ai/evals/<slug>/brief.md` with these sections:

```markdown
# Quality Eval Brief

## 1. Eval Target
- slug
- thing being tested
- related feature / prompt / flow / artifact
- related plan or commit if relevant

## 2. Why This Eval Exists
- what decision this should unblock
- what uncertainty remains

## 3. Scope
- what is in scope
- what is out of scope

## 4. Setup Context
- minimal context a fresh session needs
- exact files, routes, commands, prompts, or entrypoints to use
- environment assumptions

## 5. Scenarios
- numbered list of concrete scenarios to run
- each scenario should say what to input, what to compare, and what “good” roughly looks like

## 6. Evaluation Criteria
- 3-7 concrete criteria
- use qualitative rubrics when needed: e.g. clarity, consistency, usefulness, tone calibration, correctness, trustworthiness

## 7. Run Budget
- expected number of runs
- variants to compare
- approximate cost/time if known
- stopping rule: what is enough evidence

## 8. Output Capture Rules
- what to save in `runs/`
- what to summarize in `results.md`

## 9. Recommendation Question
- the exact question the final recommendation must answer
```

Keep it tight. The point is handoff clarity, not essay writing.

## Required results structure

Write or update `.ai/evals/<slug>/results.md` with these sections:

```markdown
# Quality Eval Results

## 1. Eval Target
- slug
- date

## 2. Runs Completed
- list each scenario or comparison actually run
- include links or filenames for raw artifacts when saved

## 3. Findings
- concise findings grouped by criterion or scenario
- note patterns, not just anecdotes

## 4. Decision
- acceptable / mixed / not ready
- answer the recommendation question from the brief directly

## 5. Next Action
- exact next step
- rerun / refine prompt / ship / redesign / gather more evidence
```

## Run artifact rules

- If outputs are short, summarize directly in `results.md`
- If outputs are long, save them under `.ai/evals/<slug>/runs/`
- Use stable names like:
  - `01-baseline.md`
  - `02-variant-a.md`
  - `03-variant-b.md`
  - `04-scenario-edge-case.md`
- Prefer one file per run or per comparison unit
- If timing matters, record elapsed time in the run file or results summary

## Evaluation discipline

- Prefer a small number of high-signal scenarios over a large vague matrix
- Compare against a baseline whenever possible
- Do not silently change the criteria midway through the eval; if criteria change, note it in `results.md`
- Separate observed behavior from interpretation
- Do not declare “good” just because outputs are eloquent; judge against the stated criteria
- If evidence is mixed, say so plainly instead of forcing a binary verdict

## Fresh-session handoff rule

If the user’s goal is to continue in a fresh session, end the prepare step with one short instruction that a new session can follow, for example:

`Run /quality-eval <slug> to execute the brief in .ai/evals/<slug>/brief.md and update results.md.`

## File handling

Before finishing:
1. Ensure `.ai/evals/<slug>/brief.md` exists for any new eval
2. Ensure `.ai/evals/<slug>/results.md` exists after any actual run
3. Ensure raw outputs are stored if the summary would otherwise become lossy
4. Ensure the final recommendation answers the stated recommendation question

## Style rules

- Be concrete and operational
- Optimize for handoff clarity
- Keep the brief concise enough that a fresh session can load it quickly
- Do not drift into generic test philosophy

---
name: follow-up
description: Manage durable follow-on artifacts captured from active and archived final plans. Uses .ai/follow_ups.md as the working registry, can list unresolved items, start one as a new quick-plan or brainstorm, and resolve items as done, superseded, or dropped without rescanning every archived plan on each invocation.
---

# Follow-Up Skill

Your job is to manage durable follow-on artifacts captured from prior plans.

Use `.ai/follow_ups.md` as the authoritative working registry.
Do not scan all archives on every invocation unless the registry is missing or clearly stale.

## When to use this skill

Use this skill when:
- the user wants to see unresolved follow-on artifacts
- the user wants to turn a follow-on artifact into a new plan
- the user wants to resolve a follow-up as done, superseded, or dropped
- the user asks what deferred artifacts or next-path items still exist across plans

Do not use this skill for:
- normal Now/Next/Later task management — use `todo`
- direct implementation of a follow-up without creating or continuing a plan
- raw archive browsing when the registry already answers the question

## Files and states

Primary files:
- `.ai/follow_ups.md` — authoritative working registry
- `.ai/plans.md` — plan index
- `.ai/plans/<slug>/final_plan.md` — active source plans
- `.ai/archive/<slug>/final_plan.md` — archived source plans

Registry sections:
- `## Open`
- `## Started`
- `## Done`
- `## Superseded`
- `## Dropped`

Each entry uses this exact shape:

```markdown
### FU-001 — <descriptive title>
- source_plan: <slug>
- source_status: active|completed|abandoned
- linked_plan: none|<slug>
- notes: <short rationale or trigger>
```

## Source set

The registry is built from:
- active plans with `final_plan.md`
- archived plans with `final_plan.md`

Ignore:
- raw brainstorm artifacts
- critique artifacts
- evolution proposals that have not been promoted into `final_plan.md`

## Registry rebuild rule

If `.ai/follow_ups.md` does not exist, rebuild it before continuing.

Rebuild process:
1. Read `.ai/plans.md`
2. Collect active plans that have `.ai/plans/<slug>/final_plan.md`
3. Collect archived plans from `.ai/archive/<slug>/final_plan.md`
4. Read `## 14. Follow-on Artifacts` from each source plan
5. Create `.ai/follow_ups.md` with:
   - `# Follow-Ups`
   - `> Last updated: YYYY-MM-DD`
   - empty sections for `Open`, `Started`, `Done`, `Superseded`, `Dropped`
6. Add one `Open` entry per follow-on artifact using stable IDs in read order:
   - `source_status: active` for active plans
   - `source_status: completed` for archived plans
   - `linked_plan: none`
7. If a source plan says `None needed.` or has no follow-on bullets, add nothing for that plan

Normal usage after rebuild must read the registry, not re-scan all archives again.

## Modes

### 1. List mode

Default behavior when no explicit action is given.

Steps:
1. Ensure `.ai/follow_ups.md` exists (rebuild if missing)
2. Read `## Open` and `## Started`
3. Present a concise list with:
   - ID
   - title
   - source plan
   - source status
   - linked plan if any
   - notes

If no unresolved items exist, say so clearly.

### 2. Start mode

Use when the user wants to pick up one follow-up item.

Resolution:
1. Match by exact ID if provided
2. Otherwise match by unambiguous title
3. If ambiguous, list candidates and ask the user to choose

Before starting:
1. Ensure the item is in `## Open` or `## Started`
2. If it is already in `## Started` and `linked_plan` points to an existing active plan, do **not** create a duplicate; surface that linked plan and stop
3. Read the source plan's `final_plan.md` from `.ai/plans/<source_plan>/` or `.ai/archive/<source_plan>/`
4. Read the specific `## 14. Follow-on Artifacts` entry that produced this item when possible

Choosing workflow:
- Use `quick-plan` when the item is concrete, bounded, and implementable without broad ideation
- Use `brainstorm` when the item is ambiguous, strategic, product-heavy, or likely to need tradeoff discussion
- Record the chosen mode in chat briefly

Slug creation:
- derive a new slug from `<source-plan>-<normalized-title>`
- keep it distinct from the source slug
- if a matching active plan already exists, reuse it instead of creating a duplicate

State updates:
- move the entry to `## Started`
- set `linked_plan: <new-or-existing-slug>`
- keep `source_plan` and `source_status` unchanged
- keep the same `FU-###` ID
- update `Last updated`

Then continue by invoking the chosen planning workflow in the same invocation:
- `quick-plan` for bounded items
- `brainstorm` for broader items

The new plan must preserve provenance in its context summary or notes:
- this work came from follow-up `<FU-###>`
- source plan slug

### 3. Resolve mode

Use when the user wants to mark a follow-up as finished or no longer relevant.

Supported terminal states:
- `Done`
- `Superseded`
- `Dropped`

Rules:
- match the item by ID or unambiguous title
- preserve the same entry block and move it into the chosen section
- keep `source_plan`, `source_status`, and `linked_plan`
- update `notes` with a short reason if resolving as `Superseded` or `Dropped`
- update `Last updated`

Interpretation:
- `Done` — the follow-up was completed
- `Superseded` — it was replaced by a better or newer path
- `Dropped` — it is no longer worth doing

## Duplicate prevention

- Never create a second open/started entry with the same title and source plan
- If an item already exists in `Started` with a linked active plan, surface that plan instead of creating a duplicate
- If a source plan was revised and removed an open item, that belongs in `Superseded`, not deletion

## Style rules

- Be terse and registry-driven
- Preserve provenance
- Do not flatten these into `todo.md`
- Prefer stable IDs and minimal churn in the registry file

## File handling

Before finishing:
1. Ensure `.ai/follow_ups.md` exists
2. Ensure each touched entry preserves its `FU-###` ID
3. Ensure `Last updated` reflects the change date
4. If start mode was used, ensure `linked_plan` is truthful and non-duplicate
5. Then provide a short in-chat summary of what was listed, started, or resolved

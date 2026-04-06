---
name: todo
description: Manage a project-level todo list at .ai/todo.md. Use this skill when the user asks "what's next", wants to see open tasks, add/remove/reprioritize todos, or needs a starting point for brainstorming. The todo list lives in each project's .ai/ folder and integrates with the brainstorm pipeline.
---

# Todo Skill

Your job is to maintain and surface a lightweight, project-scoped todo list at `.ai/todo.md`.

## When to trigger this skill

**Automatically trigger** when the user:
- asks "what's next", "what should I work on", "what's left", "what's pending", "anything to do", or similar
- asks to add, remove, check off, or reprioritize a todo item
- says "/todo" explicitly

**Do not trigger** when:
- the user is clearly asking about a different kind of "next" (e.g., "what's the next step in this function")
- a more specific skill (execute-plan, evolve) already governs the workflow

## File location

The todo list lives at `.ai/todo.md` in the current project root.

If `.ai/` does not exist, create it.
If `.ai/todo.md` does not exist and the user asks "what's next", tell them there is no todo list yet and offer to create one.

## File format

```markdown
# Todo

> Last updated: YYYY-MM-DD

## Now
- [ ] High-priority item — short context if needed
- [ ] Another urgent item

## Next
- [ ] Medium-priority item
- [ ] Another medium item

## Later
- [ ] Low-priority or exploratory item
- [ ] Backlog idea

## Done
- [x] Completed item — YYYY-MM-DD
- [x] Another completed item — YYYY-MM-DD
```

### Format rules

- Use `- [ ]` for open items and `- [x]` for completed items.
- Each item is one line. Add a short `— context` suffix only when the item would be ambiguous without it.
- Keep three priority buckets: **Now**, **Next**, **Later**.
- Completed items move to **Done** with the completion date appended.
- Keep the **Done** section trimmed to the last 10 completed items. Older completed items can be removed silently.
- Update the `Last updated` timestamp whenever the file changes.

## Core behaviors

### Reading ("what's next")

1. Read `.ai/todo.md`.
2. Present the **Now** section items first, then **Next** as a secondary view.
3. Keep the response brief — just show the items, don't over-explain.
4. If the list is empty or all items are done, say so and ask if the user wants to add new items.

### Adding items

1. Ask which bucket (Now / Next / Later) if not obvious from context. Default to **Next** if ambiguous.
2. Append the item to the correct section.
3. Confirm briefly.

### Completing items

1. Move the item from its current bucket to **Done**.
2. Mark it `[x]` and append `— YYYY-MM-DD`.
3. Confirm briefly.

### Removing items

1. Remove the item entirely (no trace in Done).
2. Confirm briefly.

### Reprioritizing

1. Move items between buckets as requested.
2. Confirm the new placement briefly.

### Bulk operations

When the user describes multiple changes at once, apply them all in a single file write and confirm with a summary.

## Integration with the planning pipeline

The todo list participates in the planning → execute → review pipeline (all plans are namespaced under `.ai/plans/<slug>/`):

**Full path:**
1. **brainstorm** reads `.ai/todo.md` and uses **Now**/**Next** items as context. If the brainstorm addresses specific items, it lists them in a `## 17. Todo Context` section in `.ai/plans/<slug>/claude_brainstorm.md`.
2. **brainstorm-synthesize** carries those references into `.ai/plans/<slug>/final_plan.md` as `## 15. Todo References`.
3. **execute-review** (or **autopilot**), when it archives a fully completed and reviewed plan, reads `## 15. Todo References` from the plan's `final_plan.md` and marks those items as done in `.ai/todo.md`.

**Quick path:**
1. **quick-plan** reads `.ai/todo.md` and uses **Now**/**Next** items as context. If the plan addresses specific items, it lists them directly in `## 15. Todo References` in `.ai/plans/<slug>/final_plan.md`.
2. **execute-review** (or **autopilot**) marks those items as done when archiving, same as the full path.

Both paths end the same way: if a todo item is referenced in a plan's `## 15. Todo References` and the plan makes it through execution and review, the item gets auto-completed. No manual cleanup needed.

## Integration with execute-plan

When active plans exist (check `.ai/plans.md` for plans with status `active`):
- "What's next" should show active plan execution phases AND the todo list, so the user sees the full picture.
- For each active plan, read `.ai/plans/<slug>/execution_state.md` and show the current phase.
- If multiple plans are active, show all of them with their slugs as headers.
- Present execution phases first, then the todo list as additional context.

## Style rules

- Be terse. The todo list is a quick-reference tool, not a document.
- Don't add commentary or motivation to items unless the user provides it.
- Don't restructure or editorialize the list unless asked.
- When showing the list, use the file content directly — don't rephrase items.

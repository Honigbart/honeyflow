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

## Integration with the brainstorm pipeline

When the user wants to brainstorm and `.ai/todo.md` exists:
- The todo list can serve as input context for `brainstorm`. Items in **Now** and **Next** represent known priorities and desires.
- When `brainstorm-synthesize` produces a `final_plan.md`, the user may want to update the todo list to reflect the new plan. Suggest this but don't do it automatically.
- When `execute-plan` completes phases, suggest checking off related todo items.

This skill does **not** automatically modify the todo list based on other skills' outputs. It only suggests updates.

## Integration with execute-plan

When `execute-plan` is active (`.ai/execution_state.md` exists with an in-progress plan):
- "What's next" should show both the current execution phase AND the todo list, so the user sees the full picture.
- Present the execution phase first, then the todo list as additional context.

## Style rules

- Be terse. The todo list is a quick-reference tool, not a document.
- Don't add commentary or motivation to items unless the user provides it.
- Don't restructure or editorialize the list unless asked.
- When showing the list, use the file content directly — don't rephrase items.

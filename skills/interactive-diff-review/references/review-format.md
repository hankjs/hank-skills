# Review Format Reference

Loaded at Step 2. Defines how to display hunks, analyze them, and collect decisions.

---

## Hunk Display

Present each hunk with this header:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 Hunk [index] / [total]  —  [file path]
Type: [modified / added / deleted / renamed]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Then show the diff body in a fenced code block with `diff` syntax highlighting.

---

## Analysis Fields

For each hunk, provide these four fields. Labels and content must be in the **detected language**. English field names shown here for reference:

| Field | Description |
|-------|-------------|
| **Change Summary** | What this hunk does in 1-2 sentences |
| **Impact Scope** | Which functionality / module / API is affected |
| **Potential Risks** | Bugs, regressions, security, or performance concerns. Write "No obvious risks" if clean |
| **Suggestions** | Recommendations for improvement (optional, omit if none) |

### Analysis Quality Guidelines

- Read the full hunk carefully, including context lines (lines starting with ` `).
- If the hunk modifies error handling, always check completeness.
- If the hunk touches public API, note potential breaking changes.
- If the hunk adds dependencies or imports, note them.
- Keep analysis concise — 3-5 sentences total, not a paragraph per field.

---

## Decision Collection

Use `AskUserQuestion` with three options in the **detected language**:

| Option | Meaning | Action |
|--------|---------|--------|
| ✅ Accept | Passes review | Set `status = "accepted"`, move on |
| ❌ Reject | Fails review | Set `status = "rejected"`, ask for reason (see below) |
| ⏭️ Skip | Defer | Keep `status = "pending"`, revisit after first pass |

### Rejection Reason

If the user rejects a hunk, immediately ask:

> "Please describe the reason for rejection."

(In the detected language.) Store the response in the hunk's `reason` field.

---

## Running Tally

After each decision, show a one-line progress bar:

```
Progress: [reviewed] / [total] | ✅ [accepted] | ❌ [rejected] | ⏭️ [skipped]
```

---

## Skip Loop

After the first full pass, check for hunks with `status == "pending"`. If any exist:

1. Inform the user: "There are [N] skipped hunks remaining."
2. Loop through them again using the same display → analyze → decide flow.
3. In the skip loop, only offer ✅ Accept and ❌ Reject (no more skipping).

# Progress Template Reference

Loaded at Step 1 (creation) and Step 2 (updates). Defines the persistent progress document format.

The progress file (`diff-review-progress.md` in project root) acts as the **source of truth** for all review state. It survives context loss and enables review resumption.

All labels and content must be in the **detected language**. Technical terms (file paths, git commands, code) remain in English. The template below shows English placeholders — replace with the appropriate language.

---

## Full Template

```markdown
# Diff Review Progress

- **Date**: YYYY-MM-DD HH:MM
- **Diff Source**: staged / workspace / commit `<hash>`
- **Language**: zh / en / ...
- **Target Args**: (the original positional arguments passed to resolve_diff.py, for re-running)
- **Total Hunks**: N
- **Reviewed**: 0 / N
- **Phase**: parsing | reviewing | verified | completed

---

## Hunk 1 — `path/to/file.ts`

- **Type**: modified
- **Status**: pending
- **Header**: @@ -10,5 +10,7 @@

### Analysis

(empty until reviewed)

### Decision

(empty until reviewed)

` ``diff
(diff body)
`` `

---

## Hunk 2 — `path/to/file.ts`

...
```

---

## Field Reference

### Header Fields

| Field | Set At | Updated At | Description |
|-------|--------|------------|-------------|
| **Date** | Step 1 | — | Creation timestamp |
| **Diff Source** | Step 1 | — | `staged`, `workspace`, or `commit` + ref |
| **Language** | Step 1 | — | Detected language code |
| **Target Args** | Step 1 | — | Original CLI args for re-running scripts |
| **Total Hunks** | Step 1 | Step 3 (if new hunks found) | Total hunk count |
| **Reviewed** | Step 1 (0/N) | Step 2 (after each decision) | `reviewed / total` counter |
| **Phase** | Step 1 (`parsing`) | Steps 2-4 | Current workflow phase |

### Phase Values

| Phase | Meaning |
|-------|---------|
| `parsing` | Step 1 in progress — hunks being parsed |
| `reviewing` | Step 2 in progress — interactive review loop |
| `verified` | Step 3 passed — coverage confirmed |
| `completed` | Step 4 done — report generated |

### Hunk Fields

| Field | Set At | Updated At | Description |
|-------|--------|------------|-------------|
| **Type** | Step 1 | — | `modified`, `added`, `deleted`, `renamed`, `binary` |
| **Status** | Step 1 (`pending`) | Step 2 | `pending`, `✅ Accepted`, `❌ Rejected` |
| **Header** | Step 1 | — | The `@@` hunk header line |
| **Analysis** | — | Step 2 | Summary, impact, risks, suggestions |
| **Decision** | — | Step 2 | Accept/reject + rejection reason if applicable |
| **diff body** | Step 1 | — | The raw diff content in a fenced code block |

---

## Rules

1. **Creation**: Write the full progress file at the end of Step 1, with all hunks set to `pending`.
2. **Incremental updates**: After each hunk review in Step 2, use the Edit tool to update that hunk's section in-place. Update the `Reviewed` counter in the header at the same time.
3. **Source of truth**: Steps 3 and 4 read from the progress file, not from conversation context.
4. **Hunk section matching**: Each hunk section heading follows the format `## Hunk N — \`file/path\``. Use this pattern for Edit tool targeting.
5. **Phase transitions**: Update the Phase field when transitioning between steps.
6. **Cleanup**: The progress file remains after Step 4 (Phase = `completed`). It is only deleted on user request or when starting a fresh review (Step 0 restart).

---

## Update Examples

### After reviewing a hunk (Step 2)

Update the hunk's section — replace the Analysis, Decision, and Status fields:

```
- **Status**: ✅ Accepted

### Analysis

**Change Summary**: Adds input validation for email field.
**Impact Scope**: User registration form.
**Potential Risks**: No obvious risks.
**Suggestions**: —

### Decision

Accepted.
```

And update the header counter:

```
- **Reviewed**: 3 / 10
```

### After rejecting a hunk (Step 2)

```
- **Status**: ❌ Rejected

### Analysis

**Change Summary**: Removes error boundary wrapper.
**Impact Scope**: Global error handling.
**Potential Risks**: Unhandled errors will crash the app.
**Suggestions**: Keep the error boundary, fix the underlying issue instead.

### Decision

Rejected. Reason: Removing error boundary will cause unhandled crashes in production.
```

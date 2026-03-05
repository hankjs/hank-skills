# Progress Template Reference

Loaded at Step 1 (creation) and Step 2 (updates). Defines the persistent progress document format.

The review state is split into two file types:
- **Index file** (`.review/[review-name]/diff-review-progress.md`) — session metadata + chunk status table. Stays small (under 5 KB even for 500 hunks).
- **Chunk files** (`.review/[review-name]/chunk/[id].md`) — one file per hunk, holding the diff body, analysis, and decision.

Together they are the **source of truth** for all review state. They survive context loss and enable review resumption.

All labels and content must be in the **detected language**. Technical terms (file paths, git commands, code) remain in English. The templates below show English placeholders — replace with the appropriate language.

---

## Index File Template (diff-review-progress.md)

```markdown
# Diff Review Progress

- **Date**: YYYY-MM-DD HH:MM
- **Review Name**: [review-name]
- **Diff Source**: staged / workspace / commit `<hash>`
- **Language**: zh / en / ...
- **Target Args**: (the original positional arguments passed to resolve_diff.py, for re-running)
- **Total Hunks**: N
- **Reviewed**: 0 / N
- **Phase**: parsing | reviewing | verified | completed

## Chunks

| ID | File | Type | Status |
|----|------|------|--------|
| 001 | path/to/file.ts | modified | pending |
| 002 | path/to/other.ts | added | pending |
| 003 | path/to/login.ts | modified | pending |
```

**Chunk ID** is zero-padded index: `001`, `002`, ..., `999`. Matches the corresponding `chunk/[id].md` file.

---

## Chunk File Template (chunk/[id].md)

```markdown
# Chunk [ID] — `path/to/file.ts`

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
```

---

## Field Reference

### Index Header Fields

| Field | Set At | Updated At | Description |
|-------|--------|------------|-------------|
| **Date** | Step 1 | — | Creation timestamp |
| **Review Name** | Step 1.5 | — | Kebab-case slug identifying this review session |
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

### Index Chunk Table Columns

| Column | Set At | Updated At | Description |
|--------|--------|------------|-------------|
| **ID** | Step 1 | — | Zero-padded index: `001`, `002`, ... |
| **File** | Step 1 | — | File path from the diff |
| **Type** | Step 1 | — | `modified`, `added`, `deleted`, `renamed`, `binary` |
| **Status** | Step 1 (`pending`) | Step 2 | `pending`, `✅ Accepted`, `❌ Rejected` |

### Chunk File Fields

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

1. **Creation**: At the end of Step 1, write the index file (all rows `pending`) and one chunk file per hunk (N Write operations).
2. **Incremental updates**: After each hunk review in Step 2, use two Edit calls:
   - Edit `chunk/[id].md` — update Status, Analysis, Decision.
   - Edit `diff-review-progress.md` — update the status cell in the chunk table row + increment the `Reviewed` counter.
3. **Source of truth**: Steps 3 and 4 read from the index + chunk files, not from conversation context.
4. **Phase transitions**: Update the Phase field in the index when transitioning between steps.
5. **Cleanup**: The index and chunk files remain after Step 4 (Phase = `completed`). They are only deleted on user request, when starting a fresh review (Step 0 restart), or when `--archive` moves the entire directory to `.review/archive/[review-name]/`.

---

## Update Examples

### After reviewing a hunk (Step 2) — chunk file edit

Update `chunk/002.md` — replace the Status, Analysis, and Decision sections:

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

### After reviewing a hunk (Step 2) — index file edit

Update the status cell in the table row and the Reviewed counter:

```
| 002 | path/to/file.ts | modified | ✅ Accepted |
```

```
- **Reviewed**: 3 / 10
```

### After rejecting a hunk (Step 2) — chunk file edit

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

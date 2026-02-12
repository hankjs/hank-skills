# Report Template Reference

Loaded at Step 4. Defines the Markdown report structure.

All labels and content must be in the **detected language**. Technical terms (file paths, git commands, code) remain in English. The template below shows English placeholders — replace with the appropriate language.

---

## Full Template

```markdown
# Git Diff Review Report

- **Date**: YYYY-MM-DD HH:MM
- **Diff Source**: staged / workspace / commit `<hash>`
- **Total Hunks**: N
- **Accepted**: X
- **Rejected**: Y

---

## Overview

| # | File | Type | Status | Reason |
|---|------|------|--------|--------|
| 1 | path/to/file.ts | modified | ✅ Accepted | — |
| 2 | path/to/file.ts | modified | ❌ Rejected | Missing error handling |
| 3 | path/to/new.ts   | added    | ✅ Accepted | — |

---

## Detailed Review

### Hunk 1 — `path/to/file.ts`

**Status**: ✅ Accepted
**Type**: modified
**Change Summary**: [Claude's analysis summary]

` ``diff
[hunk diff content]
`` `

---

### Hunk 2 — `path/to/file.ts`

**Status**: ❌ Rejected
**Type**: modified
**Change Summary**: [Claude's analysis summary]
**Rejection Reason**: [User's reason]

` ``diff
[hunk diff content]
`` `

---

## Conclusion

- This review covered N hunks: X accepted, Y rejected.
- [If any rejected, summarize the key areas requiring changes.]
```

---

## Rules

1. **Order**: Follow original diff order — by file path, then by hunk index within file.
2. **Overview table**: Every hunk gets exactly one row. Status column uses ✅ / ❌ emoji.
3. **Detailed section**: Every hunk gets a subsection with status, type, summary, and diff.
4. **Rejected hunks**: Must include the `Rejection Reason` field with the user's stated reason.
5. **Accepted hunks**: Omit the `Rejection Reason` field entirely (do not show "— ").
6. **Binary hunks**: Include in overview table with note "Binary file". No diff block in detail section.
7. **Conclusion**: Summarize counts. If there are rejections, list the files/areas that need rework.

---

## Output

Save to: `diff-review-report.md` in the project root.

Present the report content directly to the user.

# Edge Cases Reference

Loaded at Step 1.4. Handle these conditions before entering the review loop.

---

## Empty Diff

**Condition**: `parse_hunks.py` returns `total == 0`, or `resolve_diff.py` returns an error.

**Action**: Inform the user that no changes were detected. Do **not** generate a report. Stop the workflow.

---

## Large Diff (>50 hunks)

**Condition**: `total > 50`

**Action**: Before entering the review loop, ask the user:

> "This diff contains [N] hunks. Would you like to review all of them, or filter by file path pattern first?"

If filtering, ask for a glob or substring pattern (e.g., `src/api/*`, `*.test.ts`). Apply the filter to the hunk list and only review matching hunks. Note the filter in the final report header.

---

## Binary Files

**Condition**: `type == "binary"`

**Action**: Auto-accept with a note: "Binary file, diff content not displayable." Include in the overview table but skip the interactive review for these hunks. No diff block in the detailed section.

---

## Merge Commits

**Condition**: User provides a merge commit hash.

**Detection**: Run `git cat-file -p <commit>` and check if there are multiple `parent` lines.

**Action**: Warn the user that this is a merge commit and the diff may be very large. Suggest diffing against a specific parent instead:

```bash
# List parents
git log --pretty=%P -n 1 <merge_commit>

# Diff against first parent (usually the branch being merged into)
git diff <merge_commit>^1 <merge_commit>
```

If the user confirms to proceed with the full merge diff, continue normally.

---

## File Renames

**Condition**: `type == "renamed"`

**Action**: Display both old and new paths clearly:

```
📄 Hunk [index] / [total]  —  [old_path] → [new_path]
Type: renamed
```

If the file also has content changes (not a pure rename), note this in the analysis. If it's a pure rename with no content diff, auto-accept with a note.

---

## Non-UTF-8 / Encoding Issues

**Condition**: Diff contains bytes that can't be decoded as UTF-8.

**Action**: Show what is displayable and add a note: "This hunk contains non-UTF-8 content. Some characters may be displayed as escape sequences." Let the user decide normally.

---

## No Git Repository

**Condition**: `resolve_diff.py` fails because the current directory is not a git repo.

**Action**: Report the error to the user. Suggest `cd` into the correct directory or provide the repo path. Stop the workflow.

---

## Detached HEAD / Shallow Clone

**Condition**: `resolve_diff.py` fails on commit-based diff due to shallow clone or detached HEAD.

**Action**: Report the specific git error. For shallow clones, suggest:

```bash
git fetch --unshallow
```

For detached HEAD with no commit history, fall back to workspace diff if changes exist.

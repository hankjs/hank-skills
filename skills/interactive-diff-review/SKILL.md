---
name: interactive-diff-review
description: "Supports commands: [commit|commit_a commit_b] [--verify] [--apply] [--commit] [--archive] Interactive git diff review skill. Parses git diff output into individual hunks, presents each hunk to the user with analysis for accept/reject decisions, verifies complete coverage, and generates a Markdown review report. "
---

# Git Diff Review Skill

Interactive hunk-by-hunk code review. Resume → Parse → Review → Verify → Report → Apply → Commit.

---

## Commands

Parse `$ARGUMENTS` to determine the command and diff target:

| Command | Usage | Description |
|---------|-------|-------------|
| `review` | `/interactive-diff-review [target]` | **Default**. Full interactive review: parse → review → report |
| `--verify` | `/interactive-diff-review --verify` | Check report exists, matches current diff, and all hunks passed |
| `--apply` | `/interactive-diff-review --apply` | Fix code based on rejected hunks' review suggestions |
| `--commit` | `/interactive-diff-review --commit` | Generate and execute git commit (requires `--verify` pass first) |
| `--archive` | `/interactive-diff-review --archive [review-name]` | Archive a completed review — move progress file to `.review/archive/` |

**Target** is optional: `<commit>`, `<commit_a> <commit_b>`, or omit for auto-detect (staged → workspace).

Commands can be combined: `/interactive-diff-review --apply --commit` will apply fixes then commit if verify passes.

### Command Routing

1. Parse `$ARGUMENTS` — extract command flags and remaining positional args (diff target).
2. If no command flag is present → default to `review`.
3. Route to the corresponding section below.

---

## Workflow Checklist

Copy this checklist and check off items as you complete them:

```
Diff Review Progress:
- [ ] Step 0: Check for Existing Progress
  - [ ] 0.1 Scan .review/ for existing progress files (diff-review-progress.md inside subdirs)
  - [ ] 0.2 If found, parse index header and count pending vs reviewed hunks
  - [ ] 0.3 Ask user: Resume or Restart?
  - [ ] 0.4 If resume → skip to Step 2 (pending hunks only)
  - [ ] 0.5 If restart → delete .review/[review-name]/ directory, continue to Step 1
- [ ] Step 1: Resolve & Parse
  - [ ] 1.1 Run resolve_diff.py to get diff + language
  - [ ] 1.2 Verify no error, inform user of diff source + language
  - [ ] 1.3 Run parse_hunks.py to split into hunks
  - [ ] 1.4 Handle edge cases ⚠️ Load references/edge-cases.md
  - [ ] 1.5 Generate review-name slug from diff content summary
  - [ ] 1.6 Write index + hunk files ⚠️ Load references/progress-template.md
      - Write .review/[review-name]/diff-review-progress.md (index: metadata + hunk table)
      - Write .review/[review-name]/hunk/[id].md for each hunk
- [ ] Step 2: Interactive Review ⚠️ CORE LOOP
  - [ ] Load references/review-format.md
  - [ ] 2.1 Display hunk (index/total, file, type, diff body) — read hunk/[id].md
  - [ ] 2.2 Provide analysis (summary, impact, risks, suggestions)
  - [ ] 2.3 Collect decision via ask_user_input (Accept / Reject / Skip)
  - [ ] 2.4 If rejected, ask reason (open-ended text follow-up)
  - [ ] 2.5 Update hunk file (status, analysis, decision) + update index row + reviewed counter
  - [ ] 2.6 Show running tally, advance to next hunk
  - [ ] 2.7 Repeat 2.1–2.6 until all hunks done
  - [ ] 2.8 Loop back for any skipped hunks
- [ ] Step 3: Coverage Verification ⚠️ REQUIRED
  - [ ] 3.1 Re-run resolve_diff.py + parse_hunks.py
  - [ ] 3.2 Read index to enumerate hunk IDs; read each hunk file for file + header + body
  - [ ] 3.3 If new/changed hunks → write new hunk files, append rows to index, review them (back to Step 2)
  - [ ] 3.4 Confirm full coverage, set Phase to "verified" in index
- [ ] Step 4: Generate Report
  - [ ] Load references/report-template.md
  - [ ] 4.1 Read index for ordered hunk list + metadata; read each hunk/[id].md for hunk details
  - [ ] 4.2 Build Markdown report (detected language, diff order)
  - [ ] 4.3 Save to .review/[review-name]-report.md
  - [ ] 4.4 Set Phase to "completed" in index
  - [ ] 4.5 Present to user
```

---

## Step 0: Check for Existing Progress

Before starting any review work, check if a progress file already exists.

### 0.1 Check for progress file

Scan `.review/` for subdirectories containing a `diff-review-progress.md` file.

- If **none found** → proceed to Step 1.
- If **one found** → continue to 0.2 with that file.
- If **multiple found** → list them to the user and ask which to resume (or start fresh).

### 0.2 Parse progress state

Read `.review/[review-name]/diff-review-progress.md` and extract:
- **Review Name**: the slug identifying this review session
- **Phase**: current workflow phase
- **Reviewed counter**: `X / N`
- **Pending hunks**: count of hunks with `Status: pending`
- **Diff Source** and **Target Args**: for context

### 0.3 Ask user

Present the state to the user and ask:

- If there are **pending hunks** (Phase = `reviewing`):
  > "Found an existing review in progress — `[review-name]` (X/N hunks reviewed, diff source: ...). Resume or restart?"
  - **Resume**: Skip to Step 2, only iterate through pending hunks.
  - **Restart**: Delete progress file and directory, proceed to Step 1.

- If **all hunks are reviewed** (Phase = `verified` or `completed`):
  > "Found a completed review — `[review-name]` (N/N hunks reviewed). Regenerate the report, or restart a fresh review?"
  - **Regenerate**: Skip to Step 4.
  - **Restart**: Delete progress file and directory, proceed to Step 1.

- If **Phase = `parsing`** (interrupted during Step 1):
  > "Found an incomplete progress file (parsing was interrupted). Restarting fresh."
  - Delete progress file and directory, proceed to Step 1.

### 0.4 Resume flow

When resuming, read `.review/[review-name]/diff-review-progress.md` (the index) to get the hunk table. Filter to only rows with `Status: pending`. Enter Step 2 with these hunk IDs — each hunk's data is in `hunk/[id].md`. Previously reviewed hunks are preserved.

### 0.5 Restart flow

Delete the entire `.review/[review-name]/` directory (which contains the index file and the `hunk/` subdirectory) and proceed to Step 1 from scratch.

---

## Step 1: Resolve & Parse

### 1.1 Run resolver

```bash
python scripts/resolve_diff.py                       # auto: staged → workspace
python scripts/resolve_diff.py <commit>              # single commit
python scripts/resolve_diff.py <commit_a> <commit_b> # commit range
```

Returns JSON: `{ source, ref, language, diff, error }`

### 1.2 Verify & inform

If `error` is non-null → report to user and **stop**.
Otherwise tell the user which diff source was resolved and what language was detected.

### 1.3 Save diff & run parser

Extract the `diff` field from Step 1.1's JSON output and write it to a temporary file, then parse:

```bash
# Write the diff field to a temp file (agent should use Write tool or shell redirect)
# e.g. write resolve output's .diff value to /tmp/diff.txt

python scripts/parse_hunks.py --file /tmp/diff.txt
```

Returns JSON: `{ total, hunks: [{ index, file, header, body, type, status, reason }] }`

### 1.4 Edge cases

Load `references/edge-cases.md` and handle accordingly.

### 1.5 Generate review name

After parsing hunks, generate a short slug (`[review-name]`) that describes the nature of the changes:

- Read the file paths and hunk types from parse output.
- Produce a kebab-case slug of 2–5 words summarizing the change (e.g., `fix-user-auth-validation`, `add-payment-api-endpoints`, `refactor-db-connection-pool`).
- The slug must be filesystem-safe: lowercase letters, digits, hyphens only. No spaces or special characters.
- If the diff is too ambiguous, fall back to `review-YYYY-MM-DD`.

### 1.6 Write progress files

Load `references/progress-template.md` for the format specification.

Create the `.review/[review-name]/hunk/` directory structure if needed, then write:

1. **Index file** — `.review/[review-name]/diff-review-progress.md`:
   - Header metadata (date, review name, diff source, language, target args, total hunks, reviewed = 0/N, phase = `reviewing`)
   - Hunk table with one row per hunk: ID (zero-padded, e.g. `001`), file, type, status = `pending`

2. **Hunk files** — `.review/[review-name]/hunk/[id].md` for each hunk (N Write operations):
   - Header fields: type, status = `pending`, hunk header (`@@` line)
   - Empty Analysis and Decision sections
   - Raw diff body in a fenced code block

Set Phase to `reviewing` in the index (parsing is complete, ready for review loop).

---

## Step 2: Interactive Review

**Before starting this step**, load `references/review-format.md` for display format, analysis fields, and decision collection details.

All UI text uses the **detected language** from Step 1. Technical terms remain in English.

Loop through each hunk (or pending hunks only if resuming): display → analyze → collect decision → **update files** → show tally → next.

### Per-hunk updates (two Edit calls)

After each hunk decision (2.3/2.4):

**Edit 1 — hunk file** `.review/[review-name]/hunk/[id].md`:
1. **Update Status** — change `pending` to `✅ Accepted` or `❌ Rejected`.
2. **Fill in Analysis** — replace the empty Analysis section with the summary, impact, risks, and suggestions.
3. **Fill in Decision** — replace the empty Decision section with the accept/reject decision and rejection reason if applicable.

**Edit 2 — index file** `.review/[review-name]/diff-review-progress.md`:
1. **Update the hunk's status cell** in the table row (e.g., `pending` → `✅ Accepted`).
2. **Update the Reviewed counter** — increment the `Reviewed: X / N` line in the header.

The index + hunk files together are the source of truth — if context is lost, the review can resume from them.

After the first pass, loop back for any skipped hunks.

---

## Step 3: Coverage Verification

1. Re-run `resolve_diff.py` + `parse_hunks.py` with same arguments as Step 1 (read **Target Args** from index if needed).
2. Read `.review/[review-name]/diff-review-progress.md` (the index) to enumerate all hunk IDs. Read each `hunk/[id].md` to get `file + header + body` for hash-matching.
3. Compare new hunks against existing hunk entries by `file + header + body`.
4. New/changed hunks found → write new `hunk/[id].md` files, append new rows to the index table, update Total Hunks, then go back to Step 2 for those hunks only.
5. Confirm full coverage. Set Phase to `verified` in the index. Only proceed to Step 4 when all hunks are decided.

---

## Step 4: Generate Report

**Before starting this step**, load `references/report-template.md` for the full template.

1. Read `.review/[review-name]/diff-review-progress.md` (the index) for the ordered hunk list and session metadata. Then read each `hunk/[id].md` for hunk data, analysis, and decisions.
2. Build the report in the **detected language** (technical terms in English), ordered by original diff sequence.
3. Save to `.review/[review-name]-report.md` and present to user.
4. Set Phase to `completed` in the index.

---

## Command: `--verify`

Validates that the review is complete and current.

1. Scan `.review/` for a `[review-name]-report.md`. If none → error: "No report found. Run `review` first."
2. If multiple reports exist, prompt user to specify which review name.
3. Re-run `resolve_diff.py` + `parse_hunks.py` with same target args (read from matching progress file) to get current hunks.
4. Parse the report's Overview table to extract reviewed hunks (file + type + status).
5. Compare:
   - Every current hunk has a matching entry in the report (by file path + hunk header + body hash).
   - No extra entries in report that don't exist in current diff (stale entries).
6. Check that all hunks have status ✅ Accepted (no ❌ Rejected, no missing).
7. Output result:
   - **PASS**: "Verification passed. All N hunks reviewed and accepted. Ready to commit."
   - **FAIL — unreviewed hunks**: List the unmatched hunks.
   - **FAIL — rejected hunks**: List the rejected hunks with their reasons.
   - **FAIL — stale report**: Report doesn't match current diff. Suggest re-running `review`.

---

## Command: `--apply`

Fixes code based on review suggestions for rejected hunks.

1. Locate `.review/[review-name]-report.md`. If not found → error: "No report found. Run `review` first."
2. Parse the report to find all ❌ Rejected hunks and their rejection reasons + analysis suggestions.
3. For each rejected hunk (in diff order):
   a. Read the relevant file and locate the code region from the hunk.
   b. Based on the rejection reason and the review analysis, generate a fix.
   c. Apply the fix using Edit tool.
   d. Show the user what was changed and why.
4. After all fixes applied, inform the user:
   - "Applied fixes for N rejected hunks. Run `--verify` or re-run `review` to confirm."

**Note**: `--apply` does NOT re-run the review. The user should run `review` again or `--verify` after applying.

---

## Command: `--commit`

Generates and executes a git commit. Requires verification to pass first.

1. Run the `--verify` flow internally (same as above).
2. If verify **FAILS** → stop and show the failure reason. Do not commit.
3. If verify **PASSES**:
   a. Parse `.review/[review-name]-report.md` to build a commit message:
      - Subject line: summarize the changes (max 72 chars), in detected language.
      - Body: list the key changes from the report overview (accepted hunks grouped by file).
   b. Show the proposed commit message to the user for confirmation.
   c. On user approval:
      - `git add -A` (or stage the specific files from the review).
      - `git commit` with the message.
   d. Show the commit result.

---

## Command: `--archive`

Archives a completed review by moving the progress file to `.review/archive/`.

**Usage**: `/interactive-diff-review --archive [review-name]`

- If `[review-name]` is omitted → scan `.review/` for progress files with Phase = `completed`. If exactly one, use it. If multiple, list them and ask the user to specify.

### Steps

1. Locate `.review/[review-name]/diff-review-progress.md` (the index).
   - If not found → error: "No progress file found for `[review-name]`."
2. Check Phase in the index:
   - If Phase ≠ `completed` → warn: "Review `[review-name]` is not yet completed (Phase: `X`). Archive anyway?" — require user confirmation to proceed.
3. Create `.review/archive/` directory if it does not exist.
4. Move the entire `.review/[review-name]/` directory → `.review/archive/[review-name]/`
   (preserves the index file and all `hunk/` files in the archive).
5. Inform the user:
   > "Archived: `.review/archive/[review-name]/`"
   > "Report remains at: `.review/[review-name]-report.md`"

---

## Parameter Reference

| Parameter | Type | Description |
|-----------|------|-------------|
| (none) | — | Default `review` command, auto-detect diff source |
| `<commit>` | string | Commit hash, short hash, tag, or ref |
| `<commit_a> <commit_b>` | string | Commit range |
| `--verify` | flag | Run verification check on existing report |
| `--apply` | flag | Apply fixes for rejected hunks |
| `--commit` | flag | Verify + generate git commit |
| `--archive [review-name]` | flag + optional string | Archive completed review to `.review/archive/` |

---

## Language

- Detected from `git log --oneline -10` by `resolve_diff.py`.
- All UI, analysis, and report use detected language; technical terms stay English.
- Mixed-language commits → most frequent wins.
- No history → fall back to user's conversation language.

---

## File Structure

```
git-diff-review/
├── SKILL.md                          # This file — workflow orchestration
├── scripts/
│   ├── resolve_diff.py               # Diff source + language detection
│   └── parse_hunks.py                # Unified diff → structured hunks
└── references/
    ├── review-format.md              # Step 2: display, analysis, decisions
    ├── report-template.md            # Step 4: Markdown report template
    ├── progress-template.md          # Steps 1-2: progress document format
    └── edge-cases.md                 # Step 1.4: edge case handling
```

### Generated Files (`.review/` directory in project root)

```
.review/[review-name]/
├── diff-review-progress.md        ← index only (metadata + hunk status table)
└── hunk/
    ├── 001.md                     ← hunk 1 data
    ├── 002.md                     ← hunk 2 data
    └── ...
.review/[review-name]-report.md    ← final report (unchanged)
.review/archive/[review-name]/     ← archived (whole directory moved here)
```

| File | Created By | Purpose |
|------|-----------|---------|
| `.review/[review-name]/diff-review-progress.md` | Step 1 | Index: session metadata + hunk status table (stays small) |
| `.review/[review-name]/hunk/[id].md` | Step 1 | Per-hunk data: diff body, analysis, decision |
| `.review/[review-name]-report.md` | Step 4 | Final review report |
| `.review/archive/[review-name]/` | `--archive` | Archived review directory (index + all hunk files) |

**Review name** (`[review-name]`): a kebab-case slug auto-generated from the diff content at Step 1.5 (e.g., `fix-auth-login-flow`, `add-payment-endpoints`). Ties the index, hunk files, report, and archive together.

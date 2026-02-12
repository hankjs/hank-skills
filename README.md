# hank-skills

A collection of custom skills for Claude Code.

## Skills

| Skill | Description |
|-------|-------------|
| [interactive-diff-review](skills/interactive-diff-review/SKILL.md) | Interactive git diff code review. Parses diff → presents each hunk with analysis → collects Accept/Reject decisions → verifies coverage → generates a Markdown review report. |

## Structure

```
hank-skills/
├── README.md
└── skills/
    └── interactive-diff-review/
        ├── SKILL.md              # Skill definition & workflow
        ├── scripts/
        │   ├── resolve_diff.py   # Diff source resolution + language detection
        │   └── parse_hunks.py    # Unified diff → structured hunks
        └── references/
            ├── review-format.md  # Review display format & analysis fields
            ├── report-template.md# Review report template
            └── edge-cases.md     # Edge case handling
```

## Installation

```bash
# Install a specific skill
npx skills add https://github.com/hankjs/hank-skills --skill interactive-diff-review
```

## Usage

Invoke via `/interactive-diff-review` in Claude Code:

```bash
/interactive-diff-review                        # Auto-detect: staged → workspace
/interactive-diff-review <commit>               # Specific commit
/interactive-diff-review <commit_a> <commit_b>  # Commit range
```

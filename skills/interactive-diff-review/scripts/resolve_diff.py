#!/usr/bin/env python3
"""
Resolve the git diff source and detect commit language.

Usage:
    python resolve_diff.py                      # auto-detect: staged → workspace
    python resolve_diff.py <commit>             # diff a single commit
    python resolve_diff.py <commit_a> <commit_b> # diff a commit range

Output (JSON to stdout):
{
    "source": "staged" | "workspace" | "commit",
    "ref": "<commit hash or null>",
    "language": "en" | "zh" | "ja" | ...,
    "diff": "<full diff text>",
    "error": null
}
"""

import json
import re
import subprocess
import sys
from collections import Counter


def run(cmd: list[str]) -> tuple[int, str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip()


def detect_language(text: str) -> str:
    """Heuristic language detection from commit messages."""
    if not text:
        return "en"

    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    jp = len(re.findall(r"[\u3040-\u309f\u30a0-\u30ff]", text))
    kr = len(re.findall(r"[\uac00-\ud7af]", text))
    latin = len(re.findall(r"[a-zA-Z]", text))

    counts = Counter({"zh": cjk, "ja": cjk + jp, "ko": kr, "en": latin})
    # Japanese needs kana to distinguish from Chinese
    if jp > 0:
        counts["ja"] = cjk + jp
    else:
        counts.pop("ja", None)

    best = counts.most_common(1)
    if not best or best[0][1] == 0:
        return "en"
    return best[0][0]


def resolve():
    args = sys.argv[1:]
    output = {"source": None, "ref": None, "language": "en", "diff": "", "error": None}

    # Language detection
    _, log_text = run(["git", "log", "--oneline", "-10"])
    output["language"] = detect_language(log_text)

    # Resolve diff source
    if len(args) == 2:
        # commit range
        commit_a, commit_b = args
        rc, diff = run(["git", "diff", commit_a, commit_b])
        if rc != 0:
            output["error"] = f"Failed to diff {commit_a}..{commit_b}"
        else:
            output["source"] = "commit"
            output["ref"] = f"{commit_a}..{commit_b}"
            output["diff"] = diff

    elif len(args) == 1:
        # single commit
        commit = args[0]
        # Try parent~1 first; fall back to --root for initial commit
        rc, diff = run(["git", "diff", f"{commit}~1", commit])
        if rc != 0:
            rc, diff = run(["git", "diff-tree", "-p", "--root", commit])
        if rc != 0:
            output["error"] = f"Failed to diff commit {commit}"
        else:
            output["source"] = "commit"
            output["ref"] = commit
            output["diff"] = diff

    else:
        # auto-detect: staged → workspace
        _, staged_stat = run(["git", "diff", "--cached", "--stat"])
        if staged_stat:
            _, diff = run(["git", "diff", "--cached"])
            output["source"] = "staged"
            output["diff"] = diff
        else:
            _, workspace_stat = run(["git", "diff", "--stat"])
            if workspace_stat:
                _, diff = run(["git", "diff"])
                output["source"] = "workspace"
                output["diff"] = diff
            else:
                output["error"] = "No changes detected (no staged or workspace diff)."

    json.dump(output, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    resolve()

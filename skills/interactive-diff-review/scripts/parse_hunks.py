#!/usr/bin/env python3
"""
Parse a unified diff into individual hunk blocks.

Usage:
    echo "<diff text>" | python parse_hunks.py
    python parse_hunks.py < diff.txt
    python parse_hunks.py --file diff.txt

Output (JSON to stdout):
{
    "total": 5,
    "hunks": [
        {
            "index": 1,
            "file": "src/main.ts",
            "header": "@@ -10,6 +10,8 @@ function main()",
            "body": " context\n-old\n+new\n context",
            "type": "modified",
            "status": "pending",
            "reason": null
        },
        ...
    ]
}
"""

import json
import re
import sys


def detect_change_type(file_header_lines: list[str]) -> str:
    """Detect the type of change from diff metadata lines."""
    text = "\n".join(file_header_lines)
    if "new file mode" in text:
        return "added"
    if "deleted file mode" in text:
        return "deleted"
    if "rename from" in text or "rename to" in text:
        return "renamed"
    if "Binary files" in text:
        return "binary"
    return "modified"


def parse_file_path(diff_line: str) -> str:
    """Extract the b/ side file path from a diff --git line."""
    match = re.match(r"diff --git a/.+ b/(.+)", diff_line)
    return match.group(1) if match else "unknown"


def parse(diff_text: str) -> dict:
    lines = diff_text.split("\n")
    hunks = []
    index = 0

    current_file = None
    current_type = "modified"
    file_header_lines: list[str] = []
    in_hunk = False
    hunk_header = ""
    hunk_body_lines: list[str] = []

    def flush_hunk():
        nonlocal index, in_hunk
        if in_hunk and current_file:
            index += 1
            hunks.append({
                "index": index,
                "file": current_file,
                "header": hunk_header,
                "body": "\n".join(hunk_body_lines),
                "type": current_type,
                "status": "pending",
                "reason": None,
            })
        in_hunk = False
        hunk_body_lines.clear()

    for line in lines:
        # New file header
        if line.startswith("diff --git "):
            flush_hunk()
            current_file = parse_file_path(line)
            file_header_lines = [line]
            current_type = "modified"
            continue

        # Metadata lines between "diff --git" and first "@@"
        if current_file and not in_hunk and not line.startswith("@@"):
            file_header_lines.append(line)
            # Check for binary
            if "Binary files" in line:
                current_type = "binary"
                index += 1
                hunks.append({
                    "index": index,
                    "file": current_file,
                    "header": "",
                    "body": line,
                    "type": "binary",
                    "status": "pending",
                    "reason": None,
                })
            continue

        # Hunk header
        if line.startswith("@@"):
            flush_hunk()
            current_type = detect_change_type(file_header_lines)
            if current_type == "binary":
                continue
            hunk_header = line
            in_hunk = True
            continue

        # Hunk body
        if in_hunk:
            hunk_body_lines.append(line)

    # Flush last hunk
    flush_hunk()

    return {"total": len(hunks), "hunks": hunks}


def main():
    if "--file" in sys.argv:
        idx = sys.argv.index("--file")
        filepath = sys.argv[idx + 1]
        with open(filepath, "r") as f:
            diff_text = f.read()
    else:
        diff_text = sys.stdin.read()

    result = parse(diff_text)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

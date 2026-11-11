#!/usr/bin/env python3
"""Check local AGENTS.md files for a small set of mechanical problems."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, List, Optional, Tuple

DEFAULT_LIMIT = 32 * 1024
MAX_READ = 1024 * 1024
SKIP_DIRS = {".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__"}
BIDI_CONTROLS = frozenset("\u061c\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069")
CONFLICT_MARKER = re.compile(r"^(?:<{7}(?: |$)|={7}$|>{7}(?: |$)|\|{7}(?: |$))")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")


def finding(path: str, code: str, message: str, line: Optional[int] = None) -> dict:
    result: dict[str, Any] = {"path": path, "code": code, "message": message}
    if line is not None:
        result["line"] = line
    return result


def inspect_file(path: Path, root: Path, limit: int) -> Tuple[List[dict], bool]:
    relative = path.relative_to(root).as_posix()
    issues: List[dict] = []
    if path.is_symlink():
        return [finding(relative, "symlink", "Symbolic link skipped; inspect its target separately.")], False
    try:
        size = path.stat().st_size
        if size > limit:
            issues.append(finding(relative, "size", f"File exceeds the configured {limit}-byte advisory limit."))
        if size > MAX_READ:
            issues.append(finding(relative, "read_limit", "File exceeds the 1 MiB scan limit and was not read."))
            return issues, True
        with path.open("rb") as stream:
            raw = stream.read(MAX_READ + 1)
        if len(raw) > MAX_READ:
            issues.append(finding(relative, "read_limit", "File grew beyond the 1 MiB scan limit and was not analyzed."))
            return issues, True
    except OSError as exc:
        return issues + [finding(relative, "read_error", f"Could not read file: {exc.strerror or type(exc).__name__}.")], True
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return issues + [finding(relative, "encoding", "File is not valid UTF-8.")], False
    if not content.strip():
        issues.append(finding(relative, "empty", "File contains no instructions."))
    seen: dict[str, int] = {}
    fence_char: Optional[str] = None
    fence_len = 0
    for number, line in enumerate(content.splitlines(), 1):
        if any(char in BIDI_CONTROLS for char in line):
            issues.append(finding(relative, "bidi_control", "Line contains an invisible bidirectional text control.", number))
        fence = FENCE.match(line)
        if fence:
            marker = fence.group(1)
            if fence_char is None:
                fence_char, fence_len = marker[0], len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_len:
                fence_char, fence_len = None, 0
            continue
        if fence_char is not None:
            continue
        if CONFLICT_MARKER.match(line):
            issues.append(finding(relative, "merge_marker", "Possible unresolved merge-conflict marker.", number))
        normalized = " ".join(line.split()).casefold()
        if len(normalized) < 30 or normalized.startswith("#"):
            continue
        if normalized in seen:
            issues.append(finding(relative, "duplicate_line", f"Long line repeats line {seen[normalized]} in this file.", number))
        else:
            seen[normalized] = number
    return issues, False


def scan(root: Path, limit: int) -> Tuple[List[str], List[dict], bool]:
    files: List[str] = []
    issues: List[dict] = []
    had_error = False

    def on_error(exc: OSError) -> None:
        nonlocal had_error
        had_error = True
        issues.append(finding(".", "walk_error", f"Could not list a directory: {exc.strerror or type(exc).__name__}."))

    for directory, names, filenames in os.walk(root, topdown=True, followlinks=False, onerror=on_error):
        names[:] = sorted(name for name in names if name not in SKIP_DIRS and not (Path(directory) / name).is_symlink())
        if "AGENTS.md" not in filenames:
            continue
        path = Path(directory) / "AGENTS.md"
        files.append(path.relative_to(root).as_posix())
        file_issues, failed = inspect_file(path, root, limit)
        issues.extend(file_issues)
        had_error = had_error or failed
    return files, issues, had_error


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Check local AGENTS.md files without sending their contents anywhere.")
    parser.add_argument("root", nargs="?", default=".", help="Directory to scan (default: current directory)")
    parser.add_argument("--json", action="store_true", help="Print a machine-readable report")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_LIMIT, help="Advisory size threshold (default: 32768 bytes)")
    args = parser.parse_args(argv)
    if args.max_bytes < 1:
        parser.error("--max-bytes must be positive")
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        parser.error("root must be an existing directory")
    files, issues, had_error = scan(root, args.max_bytes)
    report = {"schema_version": 1, "files_scanned": files, "findings": issues, "incomplete": had_error}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Scanned {len(files)} AGENTS.md file(s); found {len(issues)} issue(s).")
        for issue in issues:
            location = issue["path"] + (f":{issue['line']}" if "line" in issue else "")
            print(f"{location}: {issue['code']}: {issue['message']}")
        if had_error:
            print("Scan incomplete; review the errors above.")
    return 2 if had_error else 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())

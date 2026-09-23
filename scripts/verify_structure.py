#!/usr/bin/env python3
"""Structural checks for this repo, complementing verify_citations.py.

Checks:
  1. Every relative markdown link in docs/ and README.md resolves to a real file.
  2. Every docs/**/*.md file is reachable from README.md.
  3. Code fences are balanced in every markdown file.
  4. Every mermaid block is non-empty and opens with a recognised diagram keyword.

Usage:
    python3 scripts/verify_structure.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
README = ROOT / "README.md"

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^```", re.M)
MERMAID_RE = re.compile(r"```mermaid\n(.*?)```", re.S)

MERMAID_KEYWORDS = (
    "flowchart", "graph", "sequenceDiagram", "gantt", "classDiagram",
    "stateDiagram", "erDiagram", "journey", "pie", "mindmap", "timeline",
)


def markdown_files():
    return [README] + sorted(DOCS.rglob("*.md"))


def check_links(errors):
    for md in markdown_files():
        text = md.read_text()
        for target in LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            resolved = (md.parent / path_part).resolve()
            if not resolved.exists():
                errors.append(
                    f"broken link in {md.relative_to(ROOT)}: {target}"
                )


def check_reachability(errors):
    reachable = set()
    queue = [README]
    seen = set()
    while queue:
        md = queue.pop()
        if md in seen:
            continue
        seen.add(md)
        for target in LINK_RE.findall(md.read_text()):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            path_part = target.split("#", 1)[0]
            if not path_part.endswith(".md"):
                continue
            resolved = (md.parent / path_part).resolve()
            if resolved.exists():
                reachable.add(resolved)
                queue.append(resolved)
    for md in DOCS.rglob("*.md"):
        if md.resolve() not in reachable:
            errors.append(
                f"unreachable from README: {md.relative_to(ROOT)}"
            )


def check_fences(errors):
    for md in markdown_files():
        count = len(FENCE_RE.findall(md.read_text()))
        if count % 2 != 0:
            errors.append(
                f"unbalanced code fences ({count}) in {md.relative_to(ROOT)}"
            )


def check_mermaid(errors):
    total = 0
    for md in markdown_files():
        for block in MERMAID_RE.findall(md.read_text()):
            total += 1
            body = block.strip()
            if not body:
                errors.append(f"empty mermaid block in {md.relative_to(ROOT)}")
                continue
            if not body.startswith(MERMAID_KEYWORDS):
                errors.append(
                    f"mermaid block in {md.relative_to(ROOT)} starts with "
                    f"unrecognised keyword: {body.splitlines()[0][:40]!r}"
                )
    return total


def main() -> int:
    errors: list[str] = []
    check_links(errors)
    check_reachability(errors)
    check_fences(errors)
    diagrams = check_mermaid(errors)

    n_docs = len(list(DOCS.rglob("*.md")))
    print(f"info: {n_docs} doc file(s), {diagrams} mermaid diagram(s) checked")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return 1
    print("structure OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

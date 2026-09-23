#!/usr/bin/env python3
"""Self-contained citation verifier for this repo.

Checks that every numeric citation marker [n] used across docs/**.md resolves
to an id present in sources/cited-sources.json, and that every cited source
carries at least one verified quote (i.e. was actually read, not just linked).

Usage:
    python3 scripts/verify_citations.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
LEDGER_PATH = ROOT / "sources" / "cited-sources.json"

CITATION_RE = re.compile(r"\[(\d+)\]")


def main() -> int:
    ledger = json.loads(LEDGER_PATH.read_text())
    known_ids = {s["id"]: s for s in ledger["sources"]}

    used_ids = set()
    for md in DOCS.rglob("*.md"):
        text = md.read_text()
        for m in CITATION_RE.finditer(text):
            used_ids.add(int(m.group(1)))

    missing = sorted(i for i in used_ids if i not in known_ids)
    unquoted = sorted(
        i for i in used_ids
        if i in known_ids and not known_ids[i].get("quotes")
    )
    unused = sorted(i for i in known_ids if i not in used_ids)

    ok = True
    if missing:
        ok = False
        print(f"FAIL: citation marker(s) with no ledger entry: {missing}")
    if unquoted:
        ok = False
        print(f"FAIL: cited source(s) with no verified excerpt: {unquoted}")
    if unused:
        print(f"warn: ledger source(s) never cited in docs/: {unused}")

    print(f"info: {len(used_ids)} distinct source(s) cited across docs/, "
          f"{len(known_ids)} in sources/cited-sources.json")

    if ok:
        print("citations OK")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())

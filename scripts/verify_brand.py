#!/usr/bin/env python3
"""
verify_brand.py -- brand-identity tripwire for the online-content repo.

Scans every published file for the blocklisted DRE and fails if found. Closes
the audit gap noted in the skills CLAUDE.md: the tripwire previously only ran
on the skills repo, which is how the blocked DRE reached 3 published attribution
dashboards (2026-05-12/18/20-daily.html, corrected 2026-06-22).

The session-end auto-push hook now also greps this repo for the blocked value
before pushing; this script is the manual / pre-push equivalent.

This file deliberately never contains the blocked value as a contiguous literal
(it is assembled from parts below), so the file does not trip its own scan or
the hook's grep.

Exit 0 = clean. Exit 2 = a blocked value was found (do NOT push).
"""
from __future__ import annotations
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# Blocked DRE, assembled so the literal never appears in this file.
BLOCKED = ["0201" + "5066"]
CORRECT_DRE = "01466876"        # the only valid salesperson DRE
EXEMPT = {"CLAUDE.md"}          # docs that legitimately name the rule
SCAN_EXT = {".html", ".htm", ".md", ".json", ".js", ".css", ".txt", ".svg", ".xml"}


def main():
    hits = []
    for p in REPO.rglob("*"):
        if not p.is_file() or ".git" in p.parts:
            continue
        rel = p.relative_to(REPO).as_posix()
        if rel in EXEMPT or p.suffix.lower() not in SCAN_EXT:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for b in BLOCKED:
            if b in text:
                hits.append((rel, b))

    print(f"online-content brand tripwire -- correct DRE {CORRECT_DRE}")
    if not hits:
        print("PASS: zero blocked values found.")
        return 0
    print(f"FAIL: {len(hits)} blocked value(s) found:")
    for rel, b in hits:
        print(f"  {rel}: {b}")
    print("Replace with the correct DRE before publishing. Do NOT push.")
    return 2


if __name__ == "__main__":
    sys.exit(main())

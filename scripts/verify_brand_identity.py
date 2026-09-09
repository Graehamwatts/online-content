#!/usr/bin/env python3
"""
verify_brand_identity.py -- brand tripwire for the online-content repo.

The Skills repo has had a tripwire since April 2026. This repo did not, which is
exactly how 243 published files drifted back to the former brokerage and stayed
that way until a client-facing page was spotted showing an Intero logo above a
Compass byline (2026-09-09).

Reads the same single source of truth the Skills repo uses:
    ../Skills/skills/shared-references/identity.json

Run before every push:
    python scripts/verify_brand_identity.py

Exit 0 = clean, 1 = blocked value found, 2 = could not read identity.json.

DELIBERATE EXCEPTIONS (see ALLOW below): a third party's @intero.com email
address is that person's real contact detail, not Graeham's branding, and the
"Intero (origin)" MLS syndication chip in the 2026 weekly seller reports is a
true statement about where that listing's feed originated at the time. Rewriting
either one would falsify a record rather than fix a brand.
"""
from __future__ import annotations
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDENTITY = os.path.normpath(os.path.join(
    REPO, "..", "Skills", "skills", "shared-references", "identity.json"))

# Substrings that legitimately survive a sweep. Anything matching is not a hit.
ALLOW = [
    re.compile(r"[A-Za-z0-9._%+-]+@intero\.com", re.I),   # third-party contacts
    re.compile(r"Intero \(origin\)"),                      # true syndication history
]

SKIP_DIRS = {".git", "__pycache__", "node_modules"}
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".mov", ".woff",
            ".woff2", ".ttf", ".otf", ".ico", ".zip", ".xlsx", ".docx"}
# This file names the blocked values in order to warn about them.
SELF = os.path.relpath(os.path.abspath(__file__), REPO).replace("\\", "/")
EXEMPT_FILES = {SELF, "CLAUDE.md", "scripts/build_content_dashboard.py"}


def main() -> int:
    if not os.path.exists(IDENTITY):
        print("FAIL: identity source-of-truth not found at %s" % IDENTITY)
        return 2

    with open(IDENTITY, encoding="utf-8") as fh:
        identity = json.load(fh)

    blocked = identity["_blocked_values"]
    dre_values = blocked.get("dre_blocklist", [])
    brand_values = blocked.get("brand_blocklist", [])
    # Also block the wrong licensed entity for California. identity.json records
    # that "Compass Real Estate" is the licensed name for ID/ME/NH/VT/WY, and
    # that using the wrong one can fine both the agent and Compass.
    brand_values = list(brand_values) + ["Compass Real Estate"]
    correct = identity["identity"]

    print("Brand tripwire -- online-content")
    print("  source of truth : %s" % IDENTITY)
    print("  correct DRE     : %s" % correct["dre"])
    print("  correct brokerage: %s" % correct["brokerage"])
    print("  blocklist       : %s" % (dre_values + brand_values))
    print()

    specs = [(v, False) for v in dre_values] + [(v, True) for v in brand_values]
    failures: list[tuple[str, list[str]]] = []

    for value, ci in specs:
        pat = re.compile(re.escape(value), re.I if ci else 0)
        hits: list[str] = []
        for dirpath, dirnames, filenames in os.walk(REPO):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fn in filenames:
                path = os.path.join(dirpath, fn)
                rel = os.path.relpath(path, REPO).replace("\\", "/")
                if rel in EXEMPT_FILES:
                    continue
                ext = os.path.splitext(fn)[1].lower()
                if ext in SKIP_EXT:
                    continue
                try:
                    if ext == ".pdf":
                        text = open(path, "rb").read().decode("latin-1", "ignore")
                    else:
                        text = open(path, encoding="utf-8", newline="").read()
                except (OSError, UnicodeDecodeError):
                    continue
                for m in pat.finditer(text):
                    window = text[max(0, m.start() - 40):m.end() + 40]
                    if any(a.search(window) for a in ALLOW):
                        continue
                    line = text.count("\n", 0, m.start()) + 1
                    hits.append("%s:%d" % (rel, line))
                    break
        if hits:
            failures.append((value, hits))

    if not failures:
        print("PASS: zero blocked values in published content.")
        return 0

    print("FAIL: blocked values found in published content:")
    for value, hits in failures:
        print("\n  %r in %d file(s):" % (value, len(hits)))
        for h in hits:
            print("    - %s" % h)
    print()
    print("Fix: replace with the correct values from identity.json.")
    print("     Brokerage in DRE/legal contexts: %s" % correct["brokerage"])
    print("     Footers and contact strips     : %s" % correct["brand_line"])
    return 1


if __name__ == "__main__":
    sys.exit(main())

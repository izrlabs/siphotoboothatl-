#!/usr/bin/env python3
"""Run after you've copied your WordPress uploads folder into static/assets/uploads/ (keeping the year/month folders).
Rewrites image links that point at the old WordPress site so they use your own copies instead."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
OLD = re.compile(r"https://siphotoboothatl\.com/wp-content/uploads/([^\"'\s)]+)")
changed = missing = 0
for f in list((ROOT / "static").rglob("*.html")) + list((ROOT / "posts").glob("*.md")):
    t = f.read_text(encoding="utf-8")
    def fix(m):
        global missing
        if (ROOT / "static/assets/uploads" / m.group(1)).exists():
            return "/assets/uploads/" + m.group(1)
        missing += 1
        return m.group(0)
    n = OLD.sub(fix, t)
    if n != t:
        f.write_text(n, encoding="utf-8"); changed += 1
print(f"updated {changed} file(s); {missing} image link(s) still point at the old site (file not found in static/assets/uploads)")

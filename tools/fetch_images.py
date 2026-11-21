#!/usr/bin/env python3
"""Fetch or generate site images listed in tools/images.json into static/assets/img/*.webp.
Runs on the GitHub runner (open internet). Skips files that already exist."""
import io, json, sys, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "static" / "assets" / "img"
items = json.loads((ROOT / "tools" / "images.json").read_text(encoding="utf-8"))
made = 0
for i, it in enumerate(items):
    dest = OUT / (it["file"] + ".webp")
    if dest.exists():
        continue
    if it.get("url"):
        url = it["url"]
    else:
        q = urllib.parse.quote(it["prompt"])
        url = f"https://image.pollinations.ai/prompt/{q}?width=1344&height=896&model=flux&nologo=true&seed={1000+i}"
    data = None
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; si-site-build)"})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            Image.open(io.BytesIO(data)).verify()
            break
        except Exception as e:
            print("retry", it["file"], attempt, e, flush=True)
            data = None
            time.sleep(8 * (attempt + 1))
    if not data:
        print("FAILED", it["file"], flush=True); continue
    im = Image.open(io.BytesIO(data)).convert("RGB")
    im.thumbnail((1400, 1400))
    im.save(dest, "WEBP", quality=82)
    made += 1
    print("saved", dest.name, im.size, flush=True)
    time.sleep(4)
print("new images:", made)

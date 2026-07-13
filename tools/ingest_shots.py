#!/usr/bin/env python3
"""Ingest game screenshots dropped into game-named subfolders at the repo root.

Usage: python3 tools/ingest_shots.py
  - scans repo-root subfolders whose names match a game (fuzzy: case/space/punctuation-insensitive)
  - converts each image found to assets/games/<slug>/shot-N.jpg (max 1200px tall, q85)
  - then run: python3 tools/build_site.py  (cards/pages pick the shots up automatically)
Originals are left in place — delete the drop folders once the site looks right.
"""
import os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUGS = {
    "orbcrash": "orbcrash", "squishfall": "squishfall", "gatefall": "gatefall",
    "kingdomblackjack": "kingdom-blackjack", "kingdomsweeper": "kingdom-sweeper",
    "ksweeper": "kingdom-sweeper", "kblackjack": "kingdom-blackjack",
    "spellbashtd": "spellbash-td", "spellbash": "spellbash",
    "spiteandsteel": "spite-and-steel", "spitesteel": "spite-and-steel", "sands": "spite-and-steel",
    "looseleaflabyrinth": "looseleaf-labyrinth", "looseleaf": "looseleaf-labyrinth",
    "youcannotgoback": "you-cannot-go-back", "ycgb": "you-cannot-go-back",
    "shorewooddays": "shorewood-days", "shorewood": "shorewood-days",
    "yahikono": "yahiko-no", "yahiko": "yahiko-no",
    "rats": "rats", "resurrectedasthesystem": "rats",
    "unearth": "unearth", "localmyth": "local-myth",
}
EXTS = (".png", ".jpg", ".jpeg", ".webp", ".heic")

def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())

found_any = False
for entry in sorted(os.listdir(ROOT)):
    path = os.path.join(ROOT, entry)
    if not os.path.isdir(path) or entry.startswith((".", "_")) or entry in ("assets", "games", "play", "tools", "build"):
        continue
    slug = SLUGS.get(norm(entry))
    if not slug:
        continue
    imgs = sorted(f for f in os.listdir(path) if f.lower().endswith(EXTS))
    if not imgs:
        continue
    found_any = True
    outdir = os.path.join(ROOT, "assets", "games", slug)
    os.makedirs(outdir, exist_ok=True)
    print(f"{entry}/ -> {slug} ({len(imgs)} images)")
    for i, f in enumerate(imgs, 1):
        dest = os.path.join(outdir, f"shot-{i}.jpg")
        subprocess.run(["sips", "-Z", "1200", "-s", "format", "jpeg",
                        "-s", "formatOptions", "85", os.path.join(path, f),
                        "--out", dest], check=True, capture_output=True)
        print(f"  {f} -> assets/games/{slug}/shot-{i}.jpg")

if not found_any:
    print("No game-named drop folders with images found at repo root.")
    sys.exit(1)
print("\nDone. Now run: python3 tools/build_site.py  (then review & push)")

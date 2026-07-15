# iPhone install framework

Private, over-the-air install links for PushPop games. Dev-signed builds — they
install only on iPhones registered to the developer profile (team `P725B32RWV`).
Not linked from the public site; reach them at:

- **My iPhone (16 Pro Max):** https://pushpopgames.com/install/
- **KC Phone:** https://pushpopgames.com/install/kc/

Open in **Safari** on the phone and tap a game to install/update it.

## Publish or update ONE game

```
tools/build_ios_install.sh <slug> "<project_dir>" "<Display Name>" <bundle_id>
python3 tools/gen_install_pages.py
git add -A && git commit -m "iPhone build: <slug>" && git push
```

`build_ios_install.sh` exports the game from Godot, archives + signs a `.ipa`
(team `P725B32RWV`, automatic signing via the Mac's managed profiles), writes
`manifest.plist`, grabs the icon, and uploads all three to the GitHub release
`install-<slug>` (`--clobber`, so the install link never changes). It records
the game in `builds.json`.

`gen_install_pages.py` rebuilds the install pages for every phone in
`audiences.json` from `builds.json`.

## Files

- `builds.json` — one entry per published game (written by the build script).
- `audiences.json` — the phones we publish for; each gets its own folder of
  install pages. Same underlying builds (a dev build installs on any registered
  phone). If a phone ever needs its OWN signed build, add a `tag_suffix` to its
  audience and point its builds at `install-<slug><suffix>` releases.

## Notes

- The `.ipa` files live in GitHub releases, never in this repo.
- Bundle IDs must match each game's iOS export preset (`com.pushpop*`).
- Team is always `P725B32RWV`. Never switch teams or delete+reinstall (wipes
  on-device saves). See `~/.claude/CLAUDE.md`.

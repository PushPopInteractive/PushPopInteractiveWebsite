#!/bin/zsh
# ============================================================
# Build ONE PushPop Godot game as a signed iPhone app (.ipa) and publish it
# to an over-the-air install link that never changes. Reusable framework —
# run once per game; future updates re-run the same command (the link is stable).
#
#   tools/build_ios_install.sh <slug> "<project_dir>" "<Display Name>" <bundle_id> [--scheme NAME]
#
# e.g.
#   tools/build_ios_install.sh orbcrash /Users/openclaw/Orbcrash "Orbcrash" com.pushpopinteractive.orbcrash
# Portrait-only games: prefix the command with IOS_ORIENTATION=portrait.
#
# What it does:
#   1. Godot exports the game -> a fresh Xcode project (+ the orientation fix).
#   2. xcodebuild archives it and exports a development-signed .ipa
#      (team P725B32RWV — the ONLY team; never switch. See ~/.claude/CLAUDE.md).
#   3. Writes manifest.plist and grabs the app icon.
#   4. Uploads .ipa + icon.png + manifest.plist to the GitHub release
#      tagged install-<slug> in this website repo (--clobber = stable link).
#   5. Then run:  python3 tools/gen_install_pages.py   (builds the install pages)
#
# The install link only works on iPhones registered to the developer profile
# (your own phones) — it is development-signed, not App Store distribution.
# ============================================================
set -uo pipefail

SLUG="${1:?usage: build_ios_install.sh <slug> <project_dir> <Display Name> <bundle_id> [--scheme NAME]}"
PROJDIR="${2:?missing project dir}"
DISPLAY="${3:?missing display name}"
BUNDLE="${4:?missing bundle id}"
SCHEME=""
[[ "${5:-}" == "--scheme" ]] && SCHEME="${6:-}"

TEAM="P725B32RWV"                         # the only team, always
REPO="PushPopInteractive/PushPopInteractiveWebsite"
TAG="install-$SLUG"
GODOT="${GODOT:-/Users/openclaw/Applications/Godot-4.6.3.app/Contents/MacOS/Godot}"
WEBROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$PROJDIR/build/ios_ota"
DD="$WORK/dd"
rm -rf "$WORK"; mkdir -p "$WORK"
cd "$PROJDIR"

echo "==> [1/5] Godot export -> Xcode project"
XCPROJ_DIR="$PROJDIR/build/ios"
mkdir -p "$XCPROJ_DIR"
# Godot's auto-archive step exits non-zero without signing configured; that's
# expected. We only need the regenerated .xcodeproj.
"$GODOT" --headless --path . --export-debug "iOS" "$XCPROJ_DIR/$SLUG.xcodeproj" >"$WORK/export.log" 2>&1 || true
XCPROJ="$(ls -d "$XCPROJ_DIR"/*.xcodeproj 2>/dev/null | head -1)"
if [[ -z "$XCPROJ" || ! -d "$XCPROJ" ]]; then
  echo "!! No .xcodeproj produced. Last export log lines:"; tail -25 "$WORK/export.log"; exit 1
fi
# Godot names the scheme after the lowercased project, not the .xcodeproj file —
# ask xcodebuild for the real scheme rather than assuming.
if [[ -z "$SCHEME" ]]; then
  SCHEME="$(xcodebuild -list -project "$XCPROJ" -json 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); print((d["project"]["schemes"] or [""])[0])' 2>/dev/null)"
  [[ -z "$SCHEME" ]] && SCHEME="$(basename "$XCPROJ" .xcodeproj)"
fi
echo "    project: $XCPROJ  (scheme: $SCHEME)"

# Godot 4.6 writes one fixed orientation and often gets it wrong. Most PushPop
# builds use free rotation, but rhythm layouts such as Neonomaly: Pulse must
# remain portrait-only.
PLIST="$(ls "$XCPROJ_DIR"/*/*-Info.plist 2>/dev/null | head -1)"
if [[ -f "$PLIST" ]]; then
  if [[ "${IOS_ORIENTATION:-free}" == "portrait" ]]; then
    ORIENTS='["UIInterfaceOrientationPortrait"]'
  else
    ORIENTS='["UIInterfaceOrientationPortrait","UIInterfaceOrientationLandscapeLeft","UIInterfaceOrientationLandscapeRight"]'
  fi
  for key in UISupportedInterfaceOrientations "UISupportedInterfaceOrientations~ipad"; do
    /usr/bin/plutil -replace "$key" -json "$ORIENTS" "$PLIST" >/dev/null 2>&1 || true
  done
fi

echo "==> [2/5] Archive + export signed .ipa (team $TEAM)"
# Rely on the team's Xcode-managed profiles already on this Mac (no Apple ID
# session): plain automatic signing, no -allowProvisioningUpdates (that flag
# fails with "No Accounts"). Same signing path the other Pushpop apps ship with.
# Version stamping: Godot leaves $(MARKETING_VERSION)/$(CURRENT_PROJECT_VERSION)
# unexpanded, so every build shipped as the same version+build number and iOS
# refused to replace an already-installed app ("installs" but keeps the old
# binary). Stamp a real version and an always-increasing build number.
MKT_VERSION="$(grep -E '^application/short_version=' "$PROJDIR/export_presets.cfg" 2>/dev/null | head -1 | sed -E 's/.*"([^"]*)".*/\1/')"
[[ -z "$MKT_VERSION" ]] && MKT_VERSION="0.1"
BUILD_NUM="$(date +%s)"   # monotonic: every build is newer than the last
echo "    stamping version $MKT_VERSION build $BUILD_NUM"

xcodebuild -project "$XCPROJ" -scheme "$SCHEME" -configuration Debug \
  -sdk iphoneos -archivePath "$WORK/$SLUG.xcarchive" -derivedDataPath "$DD" \
  -allowProvisioningUpdates \
  DEVELOPMENT_TEAM="$TEAM" CODE_SIGN_STYLE=Automatic PRODUCT_BUNDLE_IDENTIFIER="$BUNDLE" \
  MARKETING_VERSION="$MKT_VERSION" CURRENT_PROJECT_VERSION="$BUILD_NUM" \
  archive 2>&1 | grep -viE "^ *ld: warning|ignoring file|auto-linked|implicit file" | tail -12
if [[ ! -d "$WORK/$SLUG.xcarchive" ]]; then
  echo "!! Archive failed — see output above."; exit 2
fi

cat > "$WORK/ExportOptions.plist" <<PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>method</key><string>development</string>
  <key>teamID</key><string>$TEAM</string>
  <key>signingStyle</key><string>automatic</string>
  <key>compileBitcode</key><false/>
  <key>stripSwiftSymbols</key><true/>
</dict></plist>
PLISTEOF

xcodebuild -exportArchive -archivePath "$WORK/$SLUG.xcarchive" \
  -exportPath "$WORK/ipa" -exportOptionsPlist "$WORK/ExportOptions.plist" 2>&1 | tail -8
IPA="$(ls "$WORK/ipa"/*.ipa 2>/dev/null | head -1)"
if [[ -z "$IPA" ]]; then
  echo "!! No .ipa exported — see output above."; exit 3
fi
IPANAME="$(basename "$IPA")"
echo "    ipa: $IPA ($(du -h "$IPA" | cut -f1))"

echo "==> [3/5] Version + icon"
VERSION="$MKT_VERSION"
echo "    version: $VERSION (build $BUILD_NUM)"
ICON="$WEBROOT/assets/games/$SLUG/icon.png"      # the web icon we already ship
if [[ ! -f "$ICON" ]]; then
  # fall back to the largest icon inside the built app
  APPICON="$(ls "$WORK/$SLUG.xcarchive/Products/Applications/"*.app/*.png 2>/dev/null | head -1)"
  ICON="${APPICON:-}"
fi
cp "$ICON" "$WORK/icon.png"

echo "==> [4/5] manifest.plist"
BASEURL="https://github.com/$REPO/releases/download/$TAG"
cat > "$WORK/manifest.plist" <<MANEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict><key>items</key><array><dict>
  <key>assets</key><array>
    <dict><key>kind</key><string>software-package</string><key>url</key><string>$BASEURL/$IPANAME</string></dict>
    <dict><key>kind</key><string>display-image</string><key>url</key><string>$BASEURL/icon.png</string></dict>
    <dict><key>kind</key><string>full-size-image</string><key>url</key><string>$BASEURL/icon.png</string></dict>
  </array>
  <key>metadata</key><dict>
    <key>bundle-identifier</key><string>$BUNDLE</string>
    <key>bundle-version</key><string>$VERSION</string>
    <key>kind</key><string>software</string>
    <key>title</key><string>$DISPLAY</string>
  </dict>
</dict></array></dict></plist>
MANEOF

echo "==> [5/5] Publish to release $TAG (stable link)"
if ! gh release view "$TAG" -R "$REPO" >/dev/null 2>&1; then
  gh release create "$TAG" -R "$REPO" --prerelease --title "$DISPLAY — iPhone build" \
    --notes "Development install build for registered iPhones. Bundle $BUNDLE, v$VERSION." >/dev/null
fi
gh release upload "$TAG" "$IPA" "$WORK/icon.png" "$WORK/manifest.plist" --clobber -R "$REPO" >/dev/null
# record metadata for the page generator
python3 - "$WEBROOT" "$SLUG" "$DISPLAY" "$BUNDLE" "$VERSION" "$IPANAME" "$TAG" <<'PY'
import json, os, sys
webroot, slug, display, bundle, version, ipaname, tag = sys.argv[1:8]
reg = os.path.join(webroot, "install", "builds.json")
os.makedirs(os.path.dirname(reg), exist_ok=True)
data = json.load(open(reg)) if os.path.exists(reg) else {}
data[slug] = {"display": display, "bundle": bundle, "version": version, "ipa": ipaname, "tag": tag}
with open(reg, "w") as f:
    json.dump(data, f, indent=2, sort_keys=True)
    f.write("\n")
print("    registry updated:", reg)
PY

echo ""
echo "==> Done. Now run:  python3 tools/gen_install_pages.py  (then commit & push)"
echo "    Install link:   https://pushpopgames.com/install/  (index; no per-game pages)"

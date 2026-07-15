#!/usr/bin/env python3
"""Generate the private iPhone install pages from install/builds.json.

builds.json is written by tools/build_ios_install.sh (one entry per game that
has a published build). audiences.json lists the phones we publish for; each
gets its OWN folder of install pages so you can bookmark one index per phone:

  install/index.html            + install/<slug>/index.html          -> main phone
  install/<aud>/index.html      + install/<aud>/<slug>/index.html     -> each extra phone

The builds are the same underlying dev-signed IPAs (a dev build installs on ANY
iPhone registered to the developer profile); the separate folders are per-phone
install indexes. If a phone ever needs its OWN signed build, give its audience a
"tag_suffix" and point its builds at install-<slug><suffix> releases.

These pages are NOT linked from the public site. Reach them at pushpopgames.com/install/.
Run:  python3 tools/gen_install_pages.py
"""
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "PushPopInteractive/PushPopInteractiveWebsite"
INSTALL = os.path.join(ROOT, "install")

DEFAULT_AUDIENCES = [
    {"folder": "", "label": "My iPhone (16 Pro Max)"},
    {"folder": "kc", "label": "KC Phone"},
]


def esc(s):
    return html.escape(str(s), quote=True)


def rel_prefix(folder):
    # depth from install/<folder>/<slug>/ back to site root
    return "/"


def game_page(slug, b, aud):
    manifest = b.get("manifest_url") or f"https://github.com/{REPO}/releases/download/{b.get('tag', 'install-'+slug) + aud.get('tag_suffix', '')}/manifest.plist"
    itms = f"itms-services://?action=download-manifest&amp;url={manifest}"
    home = f"/install/{aud['folder']}/".replace("//", "/")
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>{esc(b['display'])} — Install ({esc(aud['label'])})</title>
<style>
  body{{margin:0;font-family:-apple-system,system-ui,sans-serif;background:#0a0a14;color:#f2f0ff;
       display:flex;min-height:100vh;align-items:center;justify-content:center;text-align:center}}
  .card{{padding:2rem;max-width:22rem}}
  img{{width:112px;height:112px;border-radius:24px;box-shadow:0 8px 30px rgba(0,0,0,.45)}}
  h1{{font-size:1.35rem;margin:1.2rem 0 .2rem}}
  .aud{{opacity:.55;font-size:.8rem;text-transform:uppercase;letter-spacing:.08em}}
  p{{opacity:.82;font-size:.95rem;line-height:1.45}}
  a.btn{{display:block;margin-top:1.4rem;padding:1rem;border-radius:14px;
        background:linear-gradient(100deg,#ff5a3c,#ffb43c 55%,#ff3c8c);
        color:#1a0c06;font-weight:800;text-decoration:none;font-size:1.05rem}}
  .warn{{margin-top:1.3rem;padding:.8rem 1rem;border-radius:12px;background:#3a2a12;
        border:1px solid #7a5a1e;color:#ffd591;font-size:.9rem;line-height:1.4;display:none}}
  .warn.show{{display:block}}
  small{{display:block;margin-top:1rem;opacity:.55;font-size:.8rem}}
  a.back{{color:#7d7a96;font-size:.85rem;display:inline-block;margin-top:1.4rem}}
</style></head><body>
<div class="card">
  <img src="/assets/games/{esc(slug)}/icon.png" alt="">
  <div class="aud">{esc(aud['label'])}</div>
  <h1>{esc(b['display'])}</h1>
  <p>Tap Install to put this build on the phone. Version {esc(b.get('version','0.1.0'))}.</p>
  <div id="notsafari" class="warn">⚠️ iPhone install links only work in <b>Safari</b>.
    Copy this page's link, open <b>Safari</b>, paste it, and tap Install there.</div>
  <a class="btn" href="{itms}">Install on iPhone</a>
  <small>Safari only, on Wi-Fi. Installs on registered iPhones only.</small>
  <a class="back" href="{home}">← All builds</a>
</div>
<script>
  var ua = navigator.userAgent;
  var isSafari = /Safari/.test(ua) && !/CriOS|FxiOS|EdgiOS|Brave|Chrome|OPT\\//.test(ua) && !navigator.brave;
  if (!isSafari) document.getElementById('notsafari').classList.add('show');
</script>
</body></html>
"""


def index_page(builds, aud, audiences):
    rows = ""
    for slug in sorted(builds, key=lambda s: builds[s]["display"].lower()):
        b = builds[slug]
        manifest = b.get("manifest_url") or f"https://github.com/{REPO}/releases/download/{b.get('tag', 'install-'+slug) + aud.get('tag_suffix', '')}/manifest.plist"
        itms = f"itms-services://?action=download-manifest&amp;url={manifest}"
        rows += f"""
    <a class="row" href="{itms}">
      <img src="/assets/games/{esc(slug)}/icon.png" alt="">
      <span class="name">{esc(b['display'])}</span>
      <span class="tap">Install ›</span>
    </a>"""
    # links to the other phones' indexes
    switch = ""
    others = [a for a in audiences if a["folder"] != aud["folder"]]
    if others:
        def href(a):
            return f"/install/{a['folder']}/" if a["folder"] else "/install/"
        links = " · ".join(f'<a href="{href(a)}">{esc(a["label"])}</a>' for a in others)
        switch = f'<p class="switch">Other phone: {links}</p>'
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>PushPop — iPhone builds ({esc(aud['label'])})</title>
<style>
  body{{margin:0;font-family:-apple-system,system-ui,sans-serif;background:#0a0a14;color:#f2f0ff;
       -webkit-font-smoothing:antialiased}}
  .wrap{{max-width:34rem;margin:0 auto;padding:2rem 1.1rem 4rem}}
  h1{{font-size:1.5rem;margin:.2rem 0}}
  .aud{{opacity:.55;font-size:.8rem;text-transform:uppercase;letter-spacing:.08em}}
  p.sub{{opacity:.7;font-size:.92rem;line-height:1.45;margin:.3rem 0 1.4rem}}
  p.switch{{font-size:.85rem;margin:.2rem 0 1.4rem}}
  p.switch a{{color:#4c9aff}}
  a.row{{display:flex;align-items:center;gap:.9rem;padding:.7rem .8rem;border-radius:14px;
        background:#14142299;border:1px solid #ffffff14;text-decoration:none;color:#f2f0ff;
        margin-bottom:.6rem}}
  a.row:active{{background:#ffffff12}}
  a.row img{{width:52px;height:52px;border-radius:12px}}
  .name{{font-weight:700;flex:1}}
  .tap{{font-weight:800;font-size:.85rem;color:#ffb43c}}
  .empty{{opacity:.6;font-size:.95rem;padding:2rem 0}}
  .warn{{margin:0 0 1.2rem;padding:.8rem 1rem;border-radius:12px;background:#3a2a12;
        border:1px solid #7a5a1e;color:#ffd591;font-size:.88rem;line-height:1.4;display:none}}
  .warn.show{{display:block}}
</style></head><body>
<div class="wrap">
  <div class="aud">{esc(aud['label'])}</div>
  <h1>PushPop — iPhone builds</h1>
  <p class="sub">Private install links. Tap a game to install or update it. Not for public distribution.</p>
  <div id="notsafari" class="warn">⚠️ iPhone install links only work in <b>Safari</b>.
    Copy this page's link, open <b>Safari</b>, paste it, and tap there.</div>
  {switch}
  {rows if rows else '<div class="empty">No builds published yet. Run tools/build_ios_install.sh for a game.</div>'}
</div>
<script>
  var ua = navigator.userAgent;
  var isSafari = /Safari/.test(ua) && !/CriOS|FxiOS|EdgiOS|Brave|Chrome|OPT\\//.test(ua) && !navigator.brave;
  if (!isSafari) document.getElementById('notsafari').classList.add('show');
</script>
</body></html>
"""


def main():
    builds = json.load(open(os.path.join(INSTALL, "builds.json"))) if os.path.exists(os.path.join(INSTALL, "builds.json")) else {}
    apath = os.path.join(INSTALL, "audiences.json")
    audiences = json.load(open(apath)) if os.path.exists(apath) else DEFAULT_AUDIENCES
    if not os.path.exists(apath):
        os.makedirs(INSTALL, exist_ok=True)
        json.dump(audiences, open(apath, "w"), indent=2)

    total = 0
    for aud in audiences:
        adir = os.path.join(INSTALL, aud["folder"]) if aud["folder"] else INSTALL
        os.makedirs(adir, exist_ok=True)
        with open(os.path.join(adir, "index.html"), "w") as f:
            f.write(index_page(builds, aud, audiences))
        for slug, b in builds.items():
            gdir = os.path.join(adir, slug)
            os.makedirs(gdir, exist_ok=True)
            with open(os.path.join(gdir, "index.html"), "w") as f:
                f.write(game_page(slug, b, aud))
            total += 1
    print(f"wrote {len(audiences)} audience index(es) + {total} game page(s)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Deploy a Godot web-demo export into play/<slug>/ with cache-proof names.

Usage: python3 tools/deploy_demo.py <slug> <export_dir>
  e.g. python3 tools/deploy_demo.py orbcrash /Users/openclaw/Orbcrash/build/web_demo

- Renames every file to <slug>-<pck-sha8>.* (index.html keeps its name) and
  rewrites all references, so browsers/CDNs can never serve a stale mix.
- Injects a visual-viewport shim: iOS browsers hide part of the canvas behind
  collapsing toolbars; window.innerHeight lies about it and toolbar moves don't
  fire window.resize. The shim makes the engine see the *visible* viewport and
  relays visualViewport changes to the engine's resize path.
"""
import hashlib, os, shutil, sys

SHIM = """<script>
// visual-viewport shim: see tools/deploy_demo.py
(function () {
	var vv = window.visualViewport;
	if (!vv) return;
	var ow = Object.getOwnPropertyDescriptor(window, 'innerWidth')  || Object.getOwnPropertyDescriptor(Window.prototype, 'innerWidth');
	var oh = Object.getOwnPropertyDescriptor(window, 'innerHeight') || Object.getOwnPropertyDescriptor(Window.prototype, 'innerHeight');
	var realW = function () { return (vv.width  > 0) ? Math.round(vv.width)  : ow.get.call(window); };
	var realH = function () { return (vv.height > 0) ? Math.round(vv.height) : oh.get.call(window); };
	// portrait game: on wide windows, cap the canvas to a centered ~19:9 phone column
	var capW  = function () { return Math.min(realW(), Math.round(realH() * 0.475)); };
	try {
		Object.defineProperty(window, 'innerWidth',  { get: capW });
		Object.defineProperty(window, 'innerHeight', { get: realH });
	} catch (e) {}
	var style = document.createElement('style');
	style.textContent = 'body{display:flex;justify-content:center;align-items:flex-start;background:#0a0a14;}#canvas{margin:0 auto;}';
	document.addEventListener('DOMContentLoaded', function () { document.head.appendChild(style); });
	var relay = function () { window.dispatchEvent(new Event('resize')); };
	vv.addEventListener('resize', relay);
	vv.addEventListener('scroll', relay);
	[400, 1200, 2500].forEach(function (t) { setTimeout(relay, t); });
})();
</script>
"""

def main():
    slug, src = sys.argv[1], sys.argv[2]
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dst = os.path.join(root, "play", slug)
    os.makedirs(dst, exist_ok=True)

    sha = hashlib.sha1(open(f"{src}/index.pck", "rb").read()).hexdigest()[:8]
    base = f"{slug}-{sha}"

    for f in os.listdir(dst):
        os.remove(os.path.join(dst, f))

    html = open(f"{src}/index.html").read()
    for f in sorted(os.listdir(src)):
        if f == "index.html":
            continue
        new = base + f[len("index"):]
        shutil.copy2(f"{src}/{f}", f"{dst}/{new}")
        html = html.replace(f, new)
    html = html.replace('"executable":"index"', f'"executable":"{base}"')
    html = html.replace("'executable':'index'", f"'executable':'{base}'")
    assert "<head>" in html
    html = html.replace("<head>", "<head>\n" + SHIM, 1)
    open(f"{dst}/index.html", "w").write(html)
    print(f"deployed {slug} as {base} (shim injected)")

if __name__ == "__main__":
    main()

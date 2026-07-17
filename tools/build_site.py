#!/usr/bin/env python3
"""One-shot generator for the PushPop Interactive site."""
import os, html, hashlib

ROOT = "/Users/openclaw/PushpopInteractiveWebsite"
SITE = "https://pushpopgames.com"
EMAIL = "pushpopinteractive@gmail.com"

GAMES = [
    dict(
        slug="neonomaly", name="Neonomaly", status="dev",
        media="cover",
        tagline="Dive the sim. Overload the Core.",
        one="A neon arcade shmup in the Life Force tradition — learnable waves, squadron wipes that drop power-ups, and a dive toward the simulation's Core.",
        tags=["Shmup", "Arcade", "Cyberpunk Neon"],
        desc=[
            "Neonomaly is a neon arcade shoot-'em-up built the old way — Life Force and Salamander, not bullet hell. Waves are scripted and learnable: fewer, faster bullets, squadrons you wipe for power-ups, and a loadout you fight to keep because death takes it away.",
            "You're a star captain flying inside the simulation, behind the matrix. Descend layer by layer toward the Core — the sim's brain — and overload it, while the grid bleeds from cyan to red the deeper you go.",
        ],
        shots=[],
    ),
    dict(
        slug="orbcrash", name="Orbcrash", status="soon",
        media="cover",
        tagline="Merge. Burst. Chain. Repeat.",
        one="A juicy, colorful match-roguelike — squish jelly orbs until the whole board erupts.",
        tags=["Match Roguelike", "Chain Reactions", "Fully Offline"],
        desc=[
            "Orbcrash is a juicy, colorful match-roguelike. Slide squishy jelly orbs together so colors merge and grow, burst them in glorious cascades, and buy game-changing Charms between rounds to beat each round's rising target.",
            "One burst sets off the next. Stack your Charms into wild, run-defining combos, fill the meter, and unleash the screen-clearing ORBFALL — a cascade that sweeps the whole board.",
            "No accounts, no ads, no internet required. Your progress stays on your device.",
        ],
        shots=["shot-title.jpg", "shot-gameplay.jpg", "shot-shop.jpg"],
    ),
    dict(
        slug="squishfall", name="Squishfall", status="dev",
        media="cover",
        tagline="Drop. Absorb. Overload.",
        one="Drop squishy orbs into the tank — same colors absorb, grow unstable, and burst the pile into chain reactions.",
        tags=["Physics Puzzle", "Chain Reactions", "Arcade"],
        desc=[
            "Squishfall is a physics puzzler about beautiful overreactions. Drop squishy colored orbs into the tank and watch same colors absorb each other, swelling into unstable masses that wobble on the edge of catastrophe.",
            "When a mass finally bursts, it clears space, collapses the pile, and sets off juicy chain reactions that ripple through the whole tank. Every drop is a small decision; every burst is a payoff.",
        ],
        shots=[],
    ),
    dict(
        slug="gatefall", name="GateFall", status="dev",
        media="cover",
        tagline="Five gates. Every drop, transformed.",
        one="A falling-brick puzzle roguelike — drop irregular bricks through card gates that transform them mid-fall.",
        tags=["Puzzle Roguelike", "Falling Bricks", "Card Gates"],
        desc=[
            "GateFall is a falling-brick puzzle roguelike. Every brick you drop falls through one of five card gates — and the gate transforms what passes through it: shape, material, behavior.",
            "Line clears, materials, and enclosed holes all feed your cards' combo engines. Route the right brick through the right gate, and the board stops being a puzzle and starts being a machine.",
        ],
        shots=[],
    ),
    dict(
        slug="kingdom-blackjack", name="Kingdom Blackjack", status="dev",
        media="cover",
        tagline="Twenty-one, drawn steel.",
        one="Blackjack reimagined as a fantasy battler — commanders, relics, and the bravest question in cards: Rally or Charge?",
        tags=["Card Battler", "Roguelike", "Fantasy"],
        desc=[
            "Kingdom Blackjack takes the most familiar card game in the world and marches it onto a fantasy battlefield. Face down enemy commanders where every hand is an exchange of blows — and going bust hurts more than your pride.",
            "Build around commander kits with their own styles, stack relics that bend the rules of the table, and manage armor, status effects, and damage-over-time while you decide, again and again, whether to Rally or Charge.",
        ],
        shots=["splash.jpg"],
    ),
    dict(
        slug="kingdom-sweeper", name="Kingdom Sweeper", status="dev",
        media="pad",
        tagline="Sweep the field. Bend the odds.",
        one="A fantasy minesweeper roguelike — bank Glory to meet each quota, then stack charm cards to cheat fate.",
        tags=["Minesweeper Roguelike", "Charm Cards", "Fantasy"],
        desc=[
            "Kingdom Sweeper is minesweeper the way a court wizard would play it. Sweep the field tile by tile, bank Glory to meet each round's quota, and try not to wake what's sleeping under the flags.",
            "Between rounds, recruit Balatro-style charm cards that bend the odds in your favor — then push deeper, where the quotas get greedier and the fields get meaner.",
        ],
        shots=[],
    ),
    dict(
        slug="spellbash-td", name="Spellbash TD", status="dev",
        media="pad",
        tagline="Free placement. True 3D. 50+ levels.",
        one="A fantasy tower defense on hand-authored 3D maps where roads duck under bridges and cross back over.",
        tags=["Tower Defense", "True-3D Maps", "50+ Level Campaign"],
        desc=[
            "Spellbash TD is a fantasy tower defense with free tower placement on true-3D, hand-authored maps — roads duck under bridges and cross back over them, and your kill zones have to respect it.",
            "Fight through a 50+ level campaign with 11 towers with branching upgrades and gem sockets, 37 enemy types, six-color light zones, and 28 commander loadouts to shape how you hold the line.",
        ],
        shots=[],
    ),
    dict(
        slug="spellbash", name="Spellbash", status="dev",
        media="cover",
        tagline="One wizard becomes an army.",
        one="A multiplier-gate lane runner done right — sprint the lane, stack casters through power gates, blast the horde.",
        tags=["Lane Runner", "Roguelike Meta", "Fantasy"],
        desc=[
            "You know the fake-ad soldier game? Spellbash is that game, real, fantasy, and actually fun. Sprint your wizard down the lane, pass the right power gates, and grow a crowd of casters auto-blasting the monster horde ahead.",
            "A roguelike meta layer wraps every run, so the choices between gates matter as much as the reflexes during them.",
        ],
        shots=[],
    ),
    dict(
        slug="spite-and-steel", name="Spite & Steel", status="dev",
        media="cover",
        tagline="Every wound feeds the grudge.",
        one="A fantasy card battler of gold, mana, and lanes — with Spite that grows when your commander bleeds.",
        tags=["Card Battler", "Duel vs AI", "Fantasy"],
        desc=[
            "Spite & Steel is a fantasy card battler fought as a duel of commanders. You and your opponent recruit allies, stockpile gold, channel fleeting mana, and position your forces between front and rear lanes.",
            "And then there's Spite — a grudge that only grows when the enemy draws your commander's blood. Nurse it well and it repays every drop.",
        ],
        shots=[],
    ),
    dict(
        slug="looseleaf-labyrinth", name="Looseleaf Labyrinth", status="dev",
        media="cover",
        tagline="A dungeon drawn in pencil.",
        one="A solo D&D-like dungeon crawl played on a living pencil-and-paper tabletop. Roll the d20. Pick a tab. Pretend it matters.",
        tags=["Dungeon Crawler", "Tabletop", "Solo RPG"],
        desc=[
            "Looseleaf Labyrinth is a solo D&D-like dungeon crawler played on a living pencil-and-paper tabletop. The dungeon is sketched in graphite on looseleaf, the d20 rattles in a real dice tray, and your fate is an eraser smudge away.",
            "Delve through hand-drawn modules like The Graphite Depths, manage your character sheet like it's due Monday, and enjoy a dungeon master with a very dry sense of humor.",
        ],
        shots=[],
    ),
    dict(
        slug="you-cannot-go-back", name="You Cannot Go Back", status="dev",
        media="cover",
        tagline="The world forgets. You do not.",
        one="A forward-only journey. There is no backtracking — you only get to choose how to continue.",
        tags=["Adventure", "Forward-Only", "Atmospheric"],
        desc=[
            "You Cannot Go Back is built on a single, unbreakable rule: the player never goes backward. The world only opens forward, and everything you pass is gone for good.",
            "There is no backtracking because life has no backtracking. The world forgets. You do not.",
        ],
        shots=["titlescreen.jpg"],
    ),
    dict(
        slug="shorewood-days", name="Shorewood Days", status="dev",
        media="pad",
        tagline="Slow days. Small mysteries.",
        one="A cozy beach-house life & mystery game set in the seaside village of Shorewood.",
        tags=["Cozy", "Life Sim", "Mystery"],
        desc=[
            "Shorewood Days is a cozy beach-house life game set in the seaside village of Shorewood — slow mornings, salt air, neighbors with routines worth learning.",
            "But Shorewood keeps its secrets the way small towns do: politely, and not forever. Settle in, and start noticing.",
        ],
        shots=[],
    ),
    dict(
        slug="yahiko-no", name="Yahiko, NO!", status="dev",
        media="cover",
        tagline="The cat is not sorry.",
        one="A cozy, chaotic domestic-disaster arcade roguelike. Mom catches, Yahiko the Siamese weaponizes gravity.",
        tags=["Arcade Roguelike", "Cozy Chaos", "Cat Physics"],
        desc=[
            "Yahiko, NO! is a cozy, chaotic domestic-disaster arcade roguelike. Mom scrambles to catch the good objects and dodge the bad ones while Yahiko the Siamese calmly, methodically weaponizes gravity from the shelf above.",
            "Between rooms, redecorate the shelves to bend the rules of the chaos — because you can't stop Yahiko. You can only plan around him.",
        ],
        shots=[],
    ),
    dict(
        slug="rats", name="Resurrected as the System?!", status="dev",
        media="cover",
        tagline="You're not the hero. You're the System.",
        one="An 8-bit, NES-era RPG with a twist: you were isekai'd as the System itself. Recruit heroes. Manage them. Nag them to victory.",
        tags=["Retro RPG", "8-Bit", "Isekai"],
        desc=[
            "Resurrected as the System?! (RATS) is an 8-bit, NES-era style RPG in the vein of classic Final Fantasy — except you weren't reborn as the hero. You were reborn as the System itself.",
            "You have no body. You cannot swing a sword. What you can do is recruit adventurers, manage their gear and gold, and talk them into defeating the Demon King. Somehow, that's harder.",
        ],
        shots=[],
    ),
    dict(
        slug="unearth", name="Unearth", status="dev",
        media="cover",
        tagline="Descend into the dark.",
        one="A low-poly dungeon delver — torchlight, tumbled stone, and something purple glowing at the bottom of the stairs.",
        tags=["Dungeon Delver", "Low-Poly", "Action"],
        desc=[
            "Unearth is a low-poly dungeon delver about going down. Torch in hand, you descend room by handcrafted room through shifting biomes of tumbled stone — toward the purple glow that should probably be left alone.",
            "Unearth is early in development, and we're excited about where it's headed.",
        ],
        shots=[],
    ),
    dict(
        slug="local-myth", name="Local Myth", status="dev",
        media="blur",
        tagline="An AI dungeon master of your very own.",
        one="Solo RPG adventures run by an AI dungeon master — private on your own machine, or in the cloud when you roam.",
        tags=["AI Dungeon Master", "Solo RPG", "Mac & iPhone"],
        desc=[
            "Local Myth is a solo RPG adventure engine for Mac and iPhone. An AI dungeon master runs your table through a three-role pipeline: an Archivist keeps your canon straight, a Director shapes each scene, and a Narrator streams the story onto the page as it's written.",
            "Pick the brain behind the screen — run everything privately on your own machine, free and offline, or switch to the cloud and adventure anywhere. Campaign templates, table-talk with the DM, a living canon you can inspect, generated scene art, and voices that read the tale aloud.",
        ],
        shots=[],
    ),
]

STATUS = {
    "soon": ("Coming Soon", "soon"),
    "dev": ("In Development", "dev"),
}

def discovered_shots(slug):
    """shot-*.jpg/png files in the game's asset folder, sorted by name."""
    import glob
    d = f"{ROOT}/assets/games/{slug}"
    return sorted(os.path.basename(p) for p in glob.glob(f"{d}/shot-*.jpg") + glob.glob(f"{d}/shot-*.png"))


def esc(s):
    return html.escape(s, quote=True)


def asset_version(path):
    """Short content hash so browsers immediately pick up regenerated assets."""
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:10]

def head(title, desc, canon, og_image, css_prefix=""):
    style_version = asset_version(f"{ROOT}/style.css")
    script_version = asset_version(f"{ROOT}/site.js")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{og_image}">
<meta property="og:url" content="{canon}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#0a0a14">
<link rel="icon" href="/assets/favicon.png">
<link rel="apple-touch-icon" href="/assets/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Nunito:ital,wght@0,400;0,600;0,700;0,800;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css?v={style_version}">
<script src="/site.js?v={script_version}" defer></script>
</head>
<body>
"""

def nav(active=""):
    def cls(k):
        return ' class="active"' if k == active else ""
    return f"""
<nav class="nav">
  <a class="brand" href="/">
    <img src="/assets/favicon.png" alt="">
    <span>PushPop <em>Interactive</em></span>
  </a>
  <div class="links">
    <a href="/#games"{cls('games')}>Games</a>
    <a href="/#about"{cls('about')}>About</a>
    <a href="/support.html"{cls('support')}>Support</a>
    <a href="/privacy.html"{cls('privacy')}>Privacy</a>
  </div>
</nav>
"""

def footer():
    return f"""
<footer>
  <div class="foot-inner">
    <div class="pp"><img src="/assets/pushpop_logo.png" alt="PushPop Interactive logo"></div>
    <div class="flinks">
      <a href="/#games">Games</a> ·
      <a href="/support.html">Support</a> ·
      <a href="/privacy.html">Privacy</a> ·
      <a href="mailto:{EMAIL}">Contact</a>
    </div>
    <div class="fine">© 2026 PushPop Interactive. All rights reserved.<br>All games designed &amp; built in-house.</div>
  </div>
</footer>
</body>
</html>
"""

def media(g, big=False):
    """Card / hero media block. Modes: cover, blur, pad, icon."""
    slug, mode = g["slug"], g["media"]
    base = f"/assets/games/{slug}"
    hero_ext = "png" if os.path.exists(f"{ROOT}/assets/games/{slug}/hero.png") else "jpg"
    hero = f"{base}/hero.{hero_ext}"
    icon = f"{base}/icon.png"
    size = "big" if big else ""
    if mode == "cover":
        return f'<div class="media {size}"><img class="cover" src="{hero}" alt="{esc(g["name"])} key art" loading="lazy"></div>'
    if mode == "blur":
        return (f'<div class="media {size}"><img class="blurbg" src="{hero}" alt="" aria-hidden="true" loading="lazy">'
                f'<img class="contain" src="{hero}" alt="{esc(g["name"])} key art" loading="lazy"></div>')
    if mode == "pad":
        return f'<div class="media pad {size}"><img class="contain" src="{hero}" alt="{esc(g["name"])} logo" loading="lazy"></div>'
    # icon-only
    return (f'<div class="media {size}"><img class="blurbg" src="{icon}" alt="" aria-hidden="true" loading="lazy">'
            f'<img class="appicon" src="{icon}" alt="{esc(g["name"])} app icon" loading="lazy"></div>')

def badge(g):
    label, k = STATUS[g["status"]]
    return f'<span class="badge {k}">{label}</span>'

def chips(g):
    return '<div class="chips">' + "".join(f"<span>{esc(t)}</span>" for t in g["tags"]) + "</div>"

# ---------- index ----------

def has_demo(slug):
    return (os.path.exists(f"{ROOT}/play/{slug}/index.html")
            or os.path.exists(f"{ROOT}/play/{slug}.html"))


def build_index():
    cards = ""
    # playable games first (stable: curated order preserved within each group)
    ordered = [g for g in GAMES if has_demo(g["slug"])] + [g for g in GAMES if not has_demo(g["slug"])]
    for g in ordered:
        try_btn = ""
        if os.path.exists(f"{ROOT}/play/{g['slug']}/index.html"):
            try_btn = f"""
          <a class="try-btn" href="/play/{g['slug']}/">\u25b6 Try it now!</a>"""
        elif os.path.exists(f"{ROOT}/play/{g['slug']}.html"):
            try_btn = f"""
          <a class="try-btn" href="/play/{g['slug']}.html">\u25b6 Try it now!</a>"""
        shots = discovered_shots(g["slug"])[:3]
        shots_row = ""
        if len(shots) >= 2:
            from PIL import Image
            with Image.open(f"{ROOT}/assets/games/{g['slug']}/{shots[0]}") as im:
                landscape = im.width > im.height
            cls = "card-shots landscape" if landscape else "card-shots"
            imgs = "".join(f'<img src="/assets/games/{g["slug"]}/{s}" alt="" loading="lazy">' for s in shots)
            shots_row = f"""
          <div class="{cls}">{imgs}</div>"""
        cards += f"""
      <div class="card">
        <a class="card-hit" href="/games/{g['slug']}.html" aria-label="{esc(g['name'])}"></a>
        <div class="media-wrap">{media(g)}{badge(g)}</div>
        <div class="card-body">
          <h3>{esc(g['name'])}</h3>
          <p>{esc(g['one'])}</p>{shots_row}
          {chips(g)}{try_btn}
        </div>
      </div>"""

    body = f"""{nav()}
<header class="hero">
  <div class="hero-inner">
    <img class="hero-logo" src="/assets/pushpop_logo.png" alt="PushPop Interactive" width="360">
    <h1>Juicy little games,<br><span class="grad">made with far too much care.</span></h1>
    <p class="sub">PushPop Interactive is an indie game studio making bright, tactile,
    delightfully juicy games for iPhone and iPad. No ads. No accounts. No nonsense — just games.</p>
    <div class="hero-cta">
      <a class="btn" href="#games">Browse the games</a>
      <a class="btn ghost" href="mailto:{EMAIL}">Say hello</a>
    </div>
  </div>
</header>

<section id="games">
  <div class="wrap wide">
    <p class="eyebrow">The catalog</p>
    <h2 class="section-title">{len(GAMES)} games &amp; counting</h2>
    <p class="section-sub">Everything below is headed to the App Store. Some are nearly there, some are still in the oven — all of them are being made with far too much care.</p>
    <div class="grid">{cards}
    </div>
  </div>
</section>

<section id="about">
  <div class="wrap narrow">
    <p class="eyebrow">The studio</p>
    <h2 class="section-title">Small studio. Big juice.</h2>
    <div class="about-card">
      <p>PushPop Interactive is an indie studio with a stubborn streak. Every title on this
      page — the design, the code, the art direction, the sound of an orb going
      <em>splorch</em> — is made in-house, and fussed over far longer than anyone would call
      reasonable.</p>
      <p>The house style: games that feel <strong>tactile</strong> and <strong>generous</strong>.
      Screens you want to touch, systems that reward one more run, and zero of the stuff that
      makes mobile games feel gross. Our games ship with <strong>no ads, no accounts, and no
      tracking</strong> — your progress lives on your device and nowhere else.</p>
      <p>Built with ❤️ (and Godot) for iPhone and iPad.</p>
    </div>
  </div>
</section>

<section id="contact">
  <div class="wrap narrow center">
    <p class="eyebrow">Get in touch</p>
    <h2 class="section-title">We read every message</h2>
    <p class="section-sub">Questions, bug reports, fan mail, cat photos — all welcome.</p>
    <a class="btn" href="mailto:{EMAIL}">📬 {EMAIL}</a>
  </div>
</section>
{footer()}"""
    return head(
        "PushPop Interactive — Juicy indie games for iPhone & iPad",
        "PushPop Interactive is an indie game studio making bright, tactile, delightfully juicy games for iOS — including Orbcrash, Squishfall, Kingdom Blackjack, and more.",
        f"{SITE}/", f"{SITE}/assets/pushpop_logo.png",
    ) + body

# ---------- game pages ----------

def build_game(g):
    label, _k = STATUS[g["status"]]
    try_row = ""
    if os.path.exists(f"{ROOT}/play/{g['slug']}/index.html"):
        try_row = f"""<div class="try-row"><a class="btn" href="/play/{g['slug']}/">\u25b6 Try it now \u2014 playable sneak peek</a></div>
"""
    elif os.path.exists(f"{ROOT}/play/{g['slug']}.html"):
        try_row = f"""<div class="try-row"><a class="btn" href="/play/{g['slug']}.html">\u25b6 Try it now \u2014 playable sneak peek</a></div>
"""
    prose = "".join(f"\n      <p>{esc(p)}</p>" for p in g["desc"])
    page_shots = discovered_shots(g["slug"]) or g["shots"]
    g = dict(g, shots=page_shots)
    shots = ""
    if g["shots"]:
        imgs = "".join(
            f'\n        <img src="/assets/games/{g["slug"]}/{s}" alt="{esc(g["name"])} screenshot" loading="lazy">'
            for s in g["shots"])
        shots = f"""
    <h2 class="shots-title">From the game</h2>
    <div class="shots">{imgs}
    </div>"""

    status_line = ("Orbcrash is coming soon to the App Store." if g["status"] == "soon"
                   else f"{g['name']} is in development at PushPop Interactive — it isn't on the App Store just yet.")

    body = f"""{nav('games')}
<header class="game-hero">
  {media(g, big=True)}
</header>

<div class="wrap page">
  <a class="crumb" href="/#games">← All games</a>
  <div class="title-row">
    <h1>{esc(g['name'])}</h1>
    {badge(g)}
  </div>
  <p class="tagline">{esc(g['tagline'])}</p>
  {chips(g)}
  {try_row}
  <div class="prose">{prose}
  </div>
  {shots}

  <div class="cta-card">
    <h2>{'Want to know the moment it lands?' if g['status']=='soon' else 'Curious about ' + esc(g['name']) + '?'}</h2>
    <p>{esc(status_line)} Questions, feedback, or just want a launch heads-up? Drop us a line — we read every message.</p>
    <div class="cta-row">
      <a class="btn" href="mailto:{EMAIL}?subject={esc(g['name'])}">📬 Email the studio</a>
      <a class="btn ghost" href="/support.html">Support &amp; FAQ</a>
    </div>
  </div>
</div>
{footer()}"""
    og_ext = "png" if os.path.exists(f"{ROOT}/assets/games/{g['slug']}/hero.png") else "jpg"
    og = (f"{SITE}/assets/games/{g['slug']}/hero.{og_ext}" if g["media"] != "icon"
          else f"{SITE}/assets/games/{g['slug']}/icon.png")
    return head(
        f"{g['name']} — PushPop Interactive",
        f"{g['name']}: {g['one']}",
        f"{SITE}/games/{g['slug']}.html", og,
    ) + body

# ---------- support ----------

def build_support():
    game_links = "".join(
        f'\n      <a class="mini" href="/games/{g["slug"]}.html"><img src="/assets/games/{g["slug"]}/icon.png" alt="" loading="lazy"><span>{esc(g["name"])}</span></a>'
        for g in GAMES if os.path.exists(f"{ROOT}/assets/games/{g['slug']}/icon.png"))
    body = f"""{nav('support')}
<div class="wrap page">
  <p class="eyebrow">PushPop Interactive</p>
  <h1>Support</h1>
  <p class="updated">We're a small studio and we read every message.</p>

  <div class="content-card">
    <h2>Get in touch</h2>
    <p>Need help with any PushPop game, found a bug, or have feedback or ideas?
    Email us and we'll get back to you as soon as we can. Mentioning which game
    you're writing about helps us help you faster.</p>
    <a class="big-email" href="mailto:{EMAIL}">📬 {EMAIL}</a>
  </div>

  <div class="content-card">
    <h2>Our games</h2>
    <div class="minis">{game_links}
    </div>
  </div>

  <div class="content-card faq">
    <h2>Frequently asked</h2>
    <details>
      <summary>How is my game progress saved?</summary>
      <p>Progress is saved locally on your device. It isn't uploaded anywhere, so it stays private to you. Deleting the app removes it.</p>
    </details>
    <details>
      <summary>Do your games need an internet connection?</summary>
      <p>No. PushPop games play fully offline — no accounts, no ads, no connection required.</p>
    </details>
    <details>
      <summary>When is [game] coming out?</summary>
      <p>Orbcrash is coming soon to the App Store, and the rest of the catalog is in active development. Email us if you'd like a heads-up when a specific game launches.</p>
    </details>
    <details>
      <summary>I found a bug — what should I include?</summary>
      <p>Let us know what happened, what you expected, which game and your device model and iOS version. A screenshot or screen recording helps a lot.</p>
    </details>
    <details>
      <summary>Can I request a feature?</summary>
      <p>Absolutely. Some of our favorite ideas came from players. No promises — but every suggestion gets read.</p>
    </details>
  </div>
</div>
{footer()}"""
    return head(
        "Support — PushPop Interactive",
        "Get help with any PushPop Interactive game. Contact the studio, report bugs, and read frequently asked questions.",
        f"{SITE}/support.html", f"{SITE}/assets/pushpop_logo.png",
    ) + body

# ---------- privacy ----------

def build_privacy():
    body = f"""{nav('privacy')}
<div class="wrap page">
  <p class="eyebrow">PushPop Interactive</p>
  <h1>Privacy Policy</h1>
  <p class="updated">Last updated July 2026 · Applies to all PushPop Interactive apps, including Orbcrash</p>

  <div class="content-card">
    <h2>The short version</h2>
    <p><strong>PushPop Interactive games do not collect, store, transmit, or share any personal data.</strong> None at all.</p>

    <h2>No tracking, no accounts, no ads</h2>
    <p>Our apps have no accounts, no analytics, no advertising, and no tracking of any kind.
    They do not connect to the internet, so nothing you do in our apps ever leaves your device.</p>

    <h2>Your game progress</h2>
    <p>Your game progress is saved only in local storage on your own device. If you delete an app, that data is removed with it.</p>

    <h2>Nothing to request or delete</h2>
    <p>Because we collect no data, there is nothing to request, export, delete, or opt out of.</p>

    <h2>Changes to this policy</h2>
    <p>If a future game ever works differently, we'll update this page and say so plainly before it ships.</p>

    <h2>Questions?</h2>
    <p>If you have any questions about this policy, contact us at
      <a class="big-email" href="mailto:{EMAIL}">📬 {EMAIL}</a>
    </p>
  </div>
</div>
{footer()}"""
    return head(
        "Privacy Policy — PushPop Interactive",
        "PushPop Interactive games collect no personal data of any kind. No tracking, no accounts, no ads.",
        f"{SITE}/privacy.html", f"{SITE}/assets/pushpop_logo.png",
    ) + body

# ---------- 404 ----------

def build_404():
    body = f"""{nav()}
<div class="wrap page center" style="padding-top:96px;">
  <h1 style="font-size:64px;">4🫧4</h1>
  <p class="tagline">That page burst, chained, and vanished.</p>
  <p><a class="btn" href="/">Back to the studio</a></p>
</div>
{footer()}"""
    return head("Page not found — PushPop Interactive",
                "That page burst, chained, and vanished.",
                f"{SITE}/404.html", f"{SITE}/assets/pushpop_logo.png") + body

# ---------- write ----------

os.makedirs(f"{ROOT}/games", exist_ok=True)
with open(f"{ROOT}/index.html", "w") as f: f.write(build_index())
with open(f"{ROOT}/support.html", "w") as f: f.write(build_support())
with open(f"{ROOT}/privacy.html", "w") as f: f.write(build_privacy())
with open(f"{ROOT}/404.html", "w") as f: f.write(build_404())
for g in GAMES:
    with open(f"{ROOT}/games/{g['slug']}.html", "w") as f: f.write(build_game(g))
print("wrote", 4 + len(GAMES), "pages")

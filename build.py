#!/usr/bin/env python3
"""Builds the portfolio website from site.json and apps.json.

Run:  python3 build.py
It writes index.html and one page per app in products/<id>/index.html.
Do not edit those generated pages by hand. Edit site.json or apps.json, then run this again.
Screenshots: put image files in assets/screenshots/<app id>/ and they appear on that app's page.
"""
import html
import json
import os
import urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")


def load(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as f:
        return json.load(f)


SITE = load("site.json")
APPS = load("apps.json")


def esc(text):
    return html.escape(text or "", quote=True)


def digits(number):
    return "".join(c for c in (number or "") if c.isdigit())


def whatsapp_link(message):
    num = digits(SITE.get("whatsapp"))
    if not num:
        return ""
    return "https://wa.me/%s?text=%s" % (num, urllib.parse.quote(message))


def contact_buttons(message):
    out = []
    wa = whatsapp_link(message)
    if wa:
        out.append('<a class="btn" href="%s">Message us on WhatsApp</a>' % esc(wa))
    if SITE.get("email"):
        subject = urllib.parse.quote(message)
        out.append('<a class="btn alt" href="mailto:%s?subject=%s">Send an email</a>' % (esc(SITE["email"]), subject))
    if SITE.get("linkedin"):
        out.append('<a class="btn alt" href="%s">LinkedIn</a>' % esc(SITE["linkedin"]))
    return "".join(out)


def layout(title, description, body, root, path):
    name = esc(SITE["name"])
    url = SITE["site_url"].rstrip("/") + "/" + path
    image = SITE["site_url"].rstrip("/") + "/assets/share.png"
    has_image = os.path.exists(os.path.join(ROOT, "assets", "share.png"))
    og_image = ('<meta property="og:image" content="%s">\n<meta name="twitter:card" content="summary_large_image">' % esc(image)) if has_image else ""
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<meta property="og:type" content="website">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:url" content="%(url)s">
%(og_image)s
<link rel="stylesheet" href="%(root)sstyle.css">
</head>
<body>
<header class="top"><div class="wrap">
<a class="brand" href="%(root)sindex.html">%(name)s</a>
<nav><a href="%(root)sindex.html#products">Products</a><a href="%(root)sindex.html#contact">Contact</a></nav>
</div></header>
<main class="wrap">
%(body)s
</main>
<footer><div class="wrap">
<p>%(name)s &middot; %(location)s</p>
<p>%(tagline)s</p>
</div></footer>
</body>
</html>
""" % {
        "title": esc(title), "desc": esc(description), "url": esc(url), "og_image": og_image,
        "root": root, "name": name, "body": body, "location": esc(SITE["location"]),
        "tagline": esc(SITE["tagline"]),
    }


def tile(app, big=False):
    return '<div class="tile%s">%s</div>' % (" big" if big else "", esc(app["name"][:1]))


def contact_block(message):
    buttons = contact_buttons(message)
    if buttons:
        return "<p>Ask for a demonstration or tell us about your business.</p><p>%s</p>" % buttons
    return '<p class="note">Contact details will be added here soon.</p>'


def build_home():
    cards = []
    for app in APPS:
        cards.append(
            '<a class="card" href="products/%s/index.html">%s<div class="cat">%s</div><h3>%s</h3><p>%s</p><span class="badge">%s</span></a>'
            % (esc(app["id"]), tile(app), esc(app["category"]), esc(app["name"]), esc(app["tagline"]), esc(app["status"]))
        )
    body = """
<section class="hero">
<h1>%(name)s</h1>
<p class="tag">%(tagline)s</p>
<p class="lead">%(intro)s</p>
</section>

<h2>What we do</h2>
<p>%(about)s</p>

<h2 id="products">Our products</h2>
<div class="grid">
%(cards)s
</div>

<h2 id="contact">Contact</h2>
%(contact)s
""" % {
        "name": esc(SITE["name"]), "tagline": esc(SITE["tagline"]), "intro": esc(SITE["intro"]),
        "about": esc(SITE["about"]), "cards": "\n".join(cards),
        "contact": contact_block("Hello, I would like to know more about your products."),
    }
    page = layout(SITE["name"] + ": practical software from Zambia", SITE["intro"], body, "", "")
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)


def screenshots(app_id, root):
    folder = os.path.join(ROOT, "assets", "screenshots", app_id)
    if not os.path.isdir(folder):
        return []
    files = sorted(f for f in os.listdir(folder) if f.lower().endswith(IMG_EXT))
    return ["%sassets/screenshots/%s/%s" % (root, app_id, urllib.parse.quote(f)) for f in files]


def build_app(app):
    root = "../../"
    shots = screenshots(app["id"], root)
    features = "".join("<li>%s</li>" % esc(x) for x in app["features"])
    sections = []
    sections.append("<h2>Who it is for</h2><p>%s</p>" % esc(app["audience"]))
    sections.append("<h2>What it does</h2><ul class=\"feat\">%s</ul>" % features)
    if app.get("why"):
        sections.append("<h2>Why it matters</h2><p>%s</p>" % esc(app["why"]))

    if shots:
        imgs = "".join('<img src="%s" alt="%s screenshot" loading="lazy">' % (esc(s), esc(app["name"])) for s in shots)
        sections.append('<h2>Screenshots</h2><div class="shots">%s</div>' % imgs)
    else:
        sections.append('<h2>Screenshots</h2><p class="note">Screenshots coming soon.</p>')

    if app.get("video_url"):
        sections.append('<h2>Demo video</h2><video controls preload="none" src="%s"></video>' % esc(app["video_url"]))

    get = []
    if app.get("apk"):
        get.append('<a class="btn" href="%s">Download the Android app (APK)</a>' % esc(app["apk"]))
    if app.get("demo_url"):
        get.append('<a class="btn alt" href="%s">Open the live demo</a>' % esc(app["demo_url"]))
    if get:
        sections.append("<h2>Try it</h2><p>%s</p>" % "".join(get))
    else:
        sections.append('<h2>Try it</h2><p class="note">A verified download is not published yet. Contact us to see a demonstration.</p>')

    sections.append("<h2>Enquiries</h2>" + contact_block("Hello, I would like to know more about %s." % app["name"]))

    body = """
<p class="crumb"><a href="../../index.html#products">&larr; All products</a></p>
<section class="hero">
%(tile)s
<h1>%(name)s</h1>
<p class="tag">%(tagline)s</p>
<p class="lead">%(summary)s</p>
<span class="badge">%(status)s</span>
</section>
%(sections)s
""" % {
        "tile": tile(app, big=True), "name": esc(app["name"]), "tagline": esc(app["tagline"]),
        "summary": esc(app["summary"]), "status": esc(app["status"]), "sections": "\n".join(sections),
    }
    folder = os.path.join(ROOT, "products", app["id"])
    os.makedirs(folder, exist_ok=True)
    page = layout("%s | %s" % (app["name"], SITE["name"]), app["summary"], body, root, "products/%s/index.html" % app["id"])
    with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)


def build_share_image():
    """Makes the picture shown when a link is shared (1200 x 630). Skipped if Pillow is missing."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return
    os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
    img = Image.new("RGB", (1200, 630), "#0f766e")
    d = ImageDraw.Draw(img)

    def font(size, bold=False):
        names = ["DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"]
        for n in names:
            for base in ("/usr/share/fonts/truetype/dejavu/", "/usr/share/fonts/dejavu/", ""):
                try:
                    return ImageFont.truetype(base + n, size)
                except OSError:
                    continue
        return ImageFont.load_default()

    d.text((80, 200), SITE["name"], font=font(88, True), fill="white")
    d.text((80, 330), SITE["tagline"], font=font(34), fill="#d7f0ec")
    d.text((80, 520), SITE["location"], font=font(30), fill="#d7f0ec")
    img.save(os.path.join(ROOT, "assets", "share.png"), optimize=True)


if __name__ == "__main__":
    build_share_image()
    build_home()
    for a in APPS:
        build_app(a)
    print("Built home page and %d product pages." % len(APPS))

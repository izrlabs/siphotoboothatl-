#!/usr/bin/env python3
"""Builds the site: copies static/ pages and generates the blog from posts/*.md.
Posts dated in the future are skipped until that date, so a batch can be uploaded in advance."""
import datetime, html, json, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_site"
SITE = "https://siphotoboothatl.com"
TODAY = datetime.date.today()

def load_posts():
    posts = []
    for f in sorted((ROOT / "posts").glob("*.md")):
        raw = f.read_text(encoding="utf-8")
        m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
        if not m:
            print("skip (no front matter):", f.name); continue
        meta = {}
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1); meta[k.strip()] = v.strip()
        body = m.group(2).strip()
        if not body.lstrip().startswith("<"):
            import markdown
            body = markdown.markdown(body, extensions=["extra"])
        date = datetime.date.fromisoformat(meta["date"])
        if date > TODAY:
            print("scheduled, not yet live:", f.name, date); continue
        posts.append(dict(slug=f.stem, title=meta["title"], date=date, category=meta.get("category", "Blog"),
                          desc=meta.get("description", ""), image=meta.get("image", ""), body=body))
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts

def fmt(d):
    return d.strftime("%B ") + str(d.day) + d.strftime(", %Y")

def abs_img(u):
    return SITE + u if u.startswith('/') else u


def esc(s): return html.escape(s, quote=True)

LAYOUT = (ROOT / "tools" / "layout.html").read_text(encoding="utf-8")
BIZ = json.loads((ROOT / "tools" / "business-schema.json").read_text(encoding="utf-8"))
HEAD_A, FOOT = LAYOUT.split("<!--SI_CONTENT-->")

def page(title, desc, canonical, body, og_image, og_type="website", extra_schema=None):
    head = "".join([
        f"<title>{esc(title)}</title>\n",
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500;600;700&display=swap">\n',
        '<link rel="stylesheet" href="/assets/main.css?ver=4.8">\n<link rel="stylesheet" href="/assets/pink.css?ver=4">\n',
        f'<meta name="description" content="{esc(desc)}">\n',
        '<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">\n',
        '<meta name="author" content="SI Photo Booth Atlanta">\n',
        f'<meta property="og:type" content="{og_type}">\n<meta property="og:title" content="{esc(title)}">\n',
        f'<meta property="og:description" content="{esc(desc)}">\n<meta property="og:url" content="{canonical}">\n',
        f'<meta property="og:image" content="{esc(abs_img(og_image))}">\n<meta property="og:site_name" content="SI Photo Booth Atlanta">\n',
        '<meta name="twitter:card" content="summary_large_image">\n',
        f'<meta name="twitter:title" content="{esc(title)}">\n<meta name="twitter:description" content="{esc(desc)}">\n<meta name="twitter:image" content="{esc(abs_img(og_image))}">\n',
        '<script type="application/ld+json">' + json.dumps(BIZ, ensure_ascii=False) + '</script>\n',
    ] + ['<script type="application/ld+json">' + json.dumps(s, ensure_ascii=False) + '</script>\n' for s in (extra_schema or [])])
    top = re.sub(r'<link rel="canonical" href="[^"]*"/>', f'<link rel="canonical" href="{canonical}"/>', HEAD_A)
    top = top.replace("<!--SI_HEAD-->", head)
    return top + body + FOOT

def breadcrumb(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}

ROSE_LINK = '<link rel="stylesheet" href="/assets/rose.css?ver=2">\n'
PHONE = "(943) 255-2632"; PHONE_TEL = "+19432552632"

def rose_page(title, desc, canonical, body, og_image, og_type="website", extra_schema=None):
    html_ = page(title, desc, canonical, '<div class="rose">' + body + '</div>', og_image, og_type, extra_schema)
    return html_.replace('<link rel="stylesheet" href="/assets/pink.css?ver=4">\n', '<link rel="stylesheet" href="/assets/pink.css?ver=4">\n' + ROSE_LINK, 1)

def slugify(t):
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", t).lower()).strip("-")

def add_toc(body):
    heads = []
    def sub(m):
        txt = re.sub(r"<[^>]+>", "", m.group(2)); sid = slugify(txt)[:60]; heads.append((sid, txt))
        return f'<h2 id="{sid}">{m.group(2)}</h2>'
    body = re.sub(r"<h2([^>]*)>(.*?)</h2>", sub, body, flags=re.S)
    toc = "".join(f'<a href="#{i}">{html.escape(t)}</a>' for i, t in heads)
    return body, toc

def faq_schema(body):
    m = re.search(r"<h2[^>]*>[^<]*(?:Frequently Asked|FAQ)[^<]*</h2>(.*?)(?=<h2|$)", body, re.S | re.I)
    if not m: return None
    qs = re.findall(r"<h3[^>]*>(.*?)</h3>\s*(.*?)(?=<h3|$)", m.group(1), re.S)
    items = [{"@type": "Question", "name": re.sub(r"<[^>]+>", "", q).strip(),
              "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", a)).strip()}} for q, a in qs]
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": items} if items else None

def words(body): return len(re.sub(r"<[^>]+>", " ", body).split())

def aside(toc, who="this guide"):
    return ('<aside class="rose-aside">'
            f'<div class="rose-card rose-toc"><h4>In {who}</h4>{toc}</div>'
            '<div class="rose-card rose-cta"><h4>Get your free quote</h4><p>Tell us your date, city and ZIP. We reply with a clear, all-in price.</p>'
            '<a class="rose-btn" href="/contact/">Get a Quote</a>'
            f'<small>Or call <a href="tel:{PHONE_TEL}" style="color:#fff;">{PHONE}</a></small></div></aside>')

def band(h="Ready to book your photo booth?"):
    return ('<section class="rose-band"><h2>' + h + '</h2><p>Open-air, glam, enclosed and 360 video booths across Atlanta and metro Georgia. '
            'Setup, teardown and a friendly attendant are always included.</p>'
            '<div class="rose-btns" style="justify-content:center;"><a class="rose-btn" href="/contact/">Get a Free Quote</a>'
            f'<a class="rose-btn alt" href="tel:{PHONE_TEL}">Call {PHONE}</a></div></section>')

def post_cards(items):
    return "".join(f'<a class="rose-post" href="/{p["slug"]}/"><img src="{esc(p["image"])}" alt="{esc(p["title"])}" loading="lazy"><div>'
                   f'<span class="rose-pill">{esc(p["category"])}</span><h3>{esc(p["title"])}</h3><p>{esc(p["desc"])}</p></div></a>' for p in items)

def blog_index(posts):
    hero = ('<section class="rose-hero"><div class="rose-hero-in"><div class="rose-crumbs"><a href="/">Home</a> / Blog</div>'
            '<span class="rose-pill">The SI Journal</span><h1>Photo Booth Ideas, Pricing &amp; Planning Guides for Atlanta</h1>'
            '<p class="rose-lead">In-depth guides for weddings, quinceañeras, corporate events and parties across Atlanta, written by the team that runs the booths.</p></div></section>')
    body = hero + '<section class="rose-related"><div class="rose-grid">' + post_cards(posts) + '</div></section>' + band()
    return rose_page("Photo Booth Blog Atlanta | Guides, Pricing & Ideas | SI Photo Booth",
                "In-depth photo booth guides for Atlanta weddings, quinceañeras, corporate events and parties: pricing, backdrops, timelines and ideas from SI Photo Booth.",
                f"{SITE}/blog/", body, posts[0]["image"] if posts and posts[0]["image"] else f"{SITE}/assets/img/fun-group-photo-booth-atlanta.webp",
                extra_schema=[breadcrumb([("Home", SITE + "/"), ("Blog", SITE + "/blog/")])])

def post_page(p, posts=()):
    body_html, toc = add_toc(p["body"])
    mins = max(3, round(words(p["body"]) / 220))
    hero = ('<section class="rose-hero"><div class="rose-hero-in"><div class="rose-crumbs"><a href="/">Home</a> / <a href="/blog/">Blog</a></div>'
            f'<span class="rose-pill">{esc(p["category"])}</span><h1>{esc(p["title"])}</h1>'
            f'<div class="rose-meta"><span>By the SI Photo Booth team</span><span>&bull;</span><span>{fmt(p["date"])}</span><span>&bull;</span><span>{mins} min read</span></div></div></section>')
    feat = f'<div class="rose-feature"><img src="{esc(p["image"])}" alt="{esc(p["title"])}"></div>' if p["image"] else ""
    rel = [q for q in posts if q["slug"] != p["slug"]]
    rel = [q for q in rel if q["category"] == p["category"]][:3] + [q for q in rel if q["category"] != p["category"]]
    rel = rel[:3]
    related = '<section class="rose-related"><h2>Keep reading</h2><div class="rose-grid">' + post_cards(rel) + '</div></section>' if rel else ""
    body = hero + feat + '<div class="rose-wrap"><article class="rose-article">' + body_html + '</article>' + aside(toc) + '</div>' + band() + related
    url = f'{SITE}/{p["slug"]}/'
    blog = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "description": p["desc"],
            "datePublished": p["date"].isoformat(), "dateModified": p["date"].isoformat(), "mainEntityOfPage": url,
            "wordCount": words(p["body"]),
            "author": {"@type": "Organization", "name": "SI Photo Booth"},
            "publisher": {"@type": "Organization", "name": "SI Photo Booth"}}
    if p["image"]: blog["image"] = abs_img(p["image"])
    schemas = [blog, breadcrumb([("Home", SITE + "/"), ("Blog", SITE + "/blog/"), (p["title"], url)])]
    fq = faq_schema(p["body"])
    if fq: schemas.append(fq)
    return rose_page(f'{p["title"]} | SI Photo Booth Atlanta', p["desc"], url, body,
                p["image"] or f"{SITE}/assets/img/fun-group-photo-booth-atlanta.webp", "article", schemas)

def load_cities():
    out = []
    for f in sorted((ROOT / "cities").glob("*.md")):
        raw = f.read_text(encoding="utf-8")
        m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
        meta = {}
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1); meta[k.strip()] = v.strip()
        body = m.group(2).strip()
        if not body.lstrip().startswith("<"):
            import markdown
            body = markdown.markdown(body, extensions=["extra"])
        out.append(dict(slug=f.stem, city=meta["city"], state=meta.get("state", "GA"), title=meta["title"], desc=meta["description"],
                        image=meta.get("image", "/assets/img/wedding-photo-booth-atlanta.webp"), lead=meta.get("lead", ""), body=body))
    return out

def city_page(c, cities):
    body_html, toc = add_toc(c["body"])
    hero = ('<section class="rose-hero"><div class="rose-hero-in"><div class="rose-crumbs"><a href="/">Home</a> / Service areas / ' + esc(c["city"]) + '</div>'
            f'<span class="rose-pill">{esc(c["city"])}, {esc(c["state"])}</span><h1>{esc(c["title"])}</h1>'
            f'<p class="rose-lead">{esc(c["lead"])}</p>'
            '<div class="rose-btns"><a class="rose-btn" href="/contact/">Get a Free Quote</a>'
            f'<a class="rose-btn alt" href="tel:{PHONE_TEL}">Call {PHONE}</a></div></div></section>')
    feat = f'<div class="rose-feature"><img src="{esc(c["image"])}" alt="Photo booth rental in {esc(c["city"])}, {esc(c["state"])} by SI Photo Booth"></div>'
    others = "".join(f'<a href="/{o["slug"]}/">{esc(o["city"])}</a>' for o in cities if o["slug"] != c["slug"])
    near = f'<section class="rose-related" style="padding-bottom:30px;"><h2>We also serve</h2><div class="rose-cities">{others}<a href="/contact/">Anywhere in metro Atlanta</a></div></section>'
    body = hero + feat + '<div class="rose-wrap"><article class="rose-article">' + body_html + '</article>' + aside(toc, "this page") + '</div>' + band(f"Book your {c['city']} photo booth") + near
    url = f'{SITE}/{c["slug"]}/'
    local = dict(BIZ); local = {"@context": "https://schema.org", "@type": "LocalBusiness", "name": "SI Photo Booth", "url": url,
        "telephone": PHONE, "image": abs_img(c["image"]), "priceRange": BIZ.get("priceRange", "$$"),
        "address": BIZ.get("address"), "areaServed": {"@type": "City", "name": f'{c["city"]}, {c["state"]}'},
        "description": c["desc"]}
    schemas = [local, breadcrumb([("Home", SITE + "/"), ("Service areas", SITE + "/#areas"), (c["city"], url)])]
    fq = faq_schema(c["body"])
    if fq: schemas.append(fq)
    return rose_page(c["title"] + " | SI Photo Booth", c["desc"], url, body, c["image"], "website", schemas)

def apply_base_path():
    """While previewing on github.io/<repo>/, prefix root-relative links. Unset BASE_PATH once the real domain is connected."""
    import os
    base = os.environ.get("BASE_PATH", "").rstrip("/")
    if not base: return
    pat = re.compile(r'((?:href|src|action)=")/(?!/)')
    pat2 = re.compile(r"(url\(['\"]?|openLb\(')/(?!/)")
    for f in OUT.rglob("*.html"):
        t = f.read_text(encoding="utf-8")
        t = pat.sub(lambda m: m.group(1) + base + "/", t)
        t = pat2.sub(lambda m: m.group(1) + base + "/", t)
        f.write_text(t, encoding="utf-8")
    print("applied BASE_PATH", base)

def main():
    if OUT.exists(): shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)
    posts = load_posts()
    (OUT / "blog").mkdir(exist_ok=True)
    (OUT / "blog" / "index.html").write_text(blog_index(posts), encoding="utf-8")
    for p in posts:
        d = OUT / p["slug"]; d.mkdir(exist_ok=True)
        (d / "index.html").write_text(post_page(p, posts), encoding="utf-8")
    cities = load_cities() if (ROOT / "cities").exists() else []
    for c in cities:
        d = OUT / c["slug"]; d.mkdir(exist_ok=True)
        (d / "index.html").write_text(city_page(c, cities), encoding="utf-8")
    urls = [("/", "1.0", "weekly"), ("/services/", "0.9", "monthly"), ("/contact/", "0.9", "monthly"), ("/gallery/", "0.8", "monthly"),
            ("/about/", "0.7", "monthly"), ("/blog/", "0.8", "weekly")]
    urls += [(f"/{d.name}/", "0.8", "monthly") for d in sorted((ROOT / "static").iterdir()) if d.is_dir() and d.name.startswith("photo-booth-rental-") and d.name not in {c["slug"] for c in cities}]
    urls += [(f'/{c["slug"]}/', "0.9", "monthly") for c in cities]
    urls += [(f'/{p["slug"]}/', "0.6", "monthly") for p in posts]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f"<url><loc>{SITE}{u}</loc><changefreq>{c}</changefreq><priority>{pr}</priority></url>\n" for u, pr, c in urls) + "</urlset>\n"
    (OUT / "sitemap.xml").write_text(xml, encoding="utf-8")
    apply_base_path()
    print(f"built {len(posts)} live post(s), {len(urls)} URLs -> {OUT}")

if __name__ == "__main__":
    main()

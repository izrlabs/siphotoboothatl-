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

def esc(s): return html.escape(s, quote=True)

LAYOUT = (ROOT / "tools" / "layout.html").read_text(encoding="utf-8")
BIZ = json.loads((ROOT / "tools" / "business-schema.json").read_text(encoding="utf-8"))
HEAD_A, FOOT = LAYOUT.split("<!--SI_CONTENT-->")

def page(title, desc, canonical, body, og_image, og_type="website", extra_schema=None):
    head = "".join([
        f"<title>{esc(title)}</title>\n",
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500;600;700&display=swap">\n',
        '<link rel="stylesheet" href="/assets/main.css?ver=4.7">\n',
        f'<meta name="description" content="{esc(desc)}">\n',
        '<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">\n',
        '<meta name="author" content="SI Photo Booth Atlanta">\n',
        f'<meta property="og:type" content="{og_type}">\n<meta property="og:title" content="{esc(title)}">\n',
        f'<meta property="og:description" content="{esc(desc)}">\n<meta property="og:url" content="{canonical}">\n',
        f'<meta property="og:image" content="{esc(og_image)}">\n<meta property="og:site_name" content="SI Photo Booth Atlanta">\n',
        '<meta name="twitter:card" content="summary_large_image">\n',
        f'<meta name="twitter:title" content="{esc(title)}">\n<meta name="twitter:description" content="{esc(desc)}">\n<meta name="twitter:image" content="{esc(og_image)}">\n',
        '<script type="application/ld+json">' + json.dumps(BIZ, ensure_ascii=False) + '</script>\n',
    ] + ['<script type="application/ld+json">' + json.dumps(s, ensure_ascii=False) + '</script>\n' for s in (extra_schema or [])])
    top = re.sub(r'<link rel="canonical" href="[^"]*"/>', f'<link rel="canonical" href="{canonical}"/>', HEAD_A)
    top = top.replace("<!--SI_HEAD-->", head)
    return top + body + FOOT

def breadcrumb(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}

def blog_index(posts):
    cards = []
    for i, p in enumerate(posts):
        img = f'<img src="{esc(p["image"])}" alt="{esc(p["title"])}" loading="lazy" style="width:100%;height:100%;object-fit:cover;">' if p["image"] else ""
        meta = (f'<div style="display:flex;gap:12px;margin-bottom:14px;align-items:center;"><span class="post-cat">{esc(p["category"])}</span>'
                f'<span style="color:rgba(255,255,255,.2);">•</span><span style="font-size:10px;color:rgba(255,255,255,.3);">{fmt(p["date"])}</span></div>')
        if i == 0:
            cards.append(f'<a href="/{p["slug"]}/" class="blog-featured" style="text-decoration:none;">'
                         f'<div class="blog-featured-img" style="aspect-ratio:16/10;">{img}</div>'
                         f'<div style="padding:clamp(28px,3vw,52px);display:flex;flex-direction:column;justify-content:center;">{meta}'
                         f'<h2 class="post-title" style="font-size:clamp(20px,2.2vw,30px);margin:0 0 14px;">{esc(p["title"])}</h2>'
                         f'<p class="post-excerpt">{esc(p["desc"])}</p></div></a>')
        else:
            cards.append(f'<a href="/{p["slug"]}/" class="blog-card" style="margin-bottom:24px;">'
                         f'<div style="aspect-ratio:16/10;overflow:hidden;">{img}</div>'
                         f'<div style="padding:22px 24px 28px;">{meta}<h3 class="post-title" style="font-size:19px;margin:0 0 10px;">{esc(p["title"])}</h3>'
                         f'<p class="post-excerpt">{esc(p["desc"])}</p></div></a>')
    body = ('<div class="page-hero"><div class="page-hero-bg" style="background-image:url(\'https://images.unsplash.com/photo-1504196606672-aef5c9cefc92?w=1600&q=80\');"></div>'
            '<div class="page-hero-overlay"></div><div class="page-hero-inner"><span class="sec-label">Journal</span>'
            '<h1 class="page-h1">Stories &amp; Insights</h1><p class="page-sub">Tips, trends, and behind-the-scenes moments from premier event photography.</p></div></div>'
            '<section class="sec"><div class="sec-inner">' + "".join(cards) + "</div></section>")
    return page("Photo Booth Blog Atlanta | Tips, Ideas & Inspiration | SI Photo Booth",
                "Photo booth tips, event inspiration and behind-the-scenes from SI Photo Booth — Atlanta's premier photo booth rental company serving weddings, corporate events & more.",
                f"{SITE}/blog/", body, posts[0]["image"] if posts and posts[0]["image"] else f"{SITE}/wp-content/uploads/2026/04/fun-group-photo-booth-atlanta.jpeg",
                extra_schema=[breadcrumb([("Home", SITE + "/"), ("Blog", SITE + "/blog/")])])

def post_page(p):
    img = (f'<div style="border-radius:16px;overflow:hidden;margin-bottom:44px;"><img src="{esc(p["image"])}" alt="{esc(p["title"])}" '
           f'style="width:100%;aspect-ratio:16/9;object-fit:cover;"></div>') if p["image"] else ""
    body = ('<div style="background:var(--bg);min-height:100vh;padding-top:100px;">'
            '<article style="max-width:780px;margin:0 auto;padding:40px clamp(20px,4vw,60px) 100px;">'
            '<a href="/blog/" style="color:var(--gold);font-size:12px;letter-spacing:.06em;display:inline-block;margin-bottom:40px;">&larr; Back to Journal</a>'
            f'<div style="display:flex;gap:14px;margin-bottom:20px;align-items:center;"><span class="post-cat">{esc(p["category"])}</span>'
            f'<span style="color:rgba(255,255,255,.2);">•</span><span style="font-size:10px;color:rgba(255,255,255,.3);">{fmt(p["date"])}</span></div>'
            f'<h1 style="font-family:var(--fd);font-size:clamp(28px,4.5vw,44px);font-weight:700;color:#F0EBE1;line-height:1.2;margin:0 0 32px;letter-spacing:-.025em;">{esc(p["title"])}</h1>'
            f'{img}<div style="font-size:16px;color:rgba(255,255,255,.6);line-height:1.9;" class="post-content">{p["body"]}</div></article></div>')
    url = f'{SITE}/{p["slug"]}/'
    blog = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "description": p["desc"],
            "datePublished": p["date"].isoformat(), "mainEntityOfPage": url,
            "author": {"@type": "Organization", "name": "SI Photo Booth"},
            "publisher": {"@type": "Organization", "name": "SI Photo Booth"}}
    if p["image"]: blog["image"] = p["image"]
    return page(f'{p["title"]} | SI Photo Booth Atlanta', p["desc"], url, body,
                p["image"] or f"{SITE}/wp-content/uploads/2026/04/fun-group-photo-booth-atlanta.jpeg", "article",
                [blog, breadcrumb([("Home", SITE + "/"), ("Blog", SITE + "/blog/"), (p["title"], url)])])

def apply_base_path():
    """While previewing on github.io/<repo>/, prefix root-relative links. Unset BASE_PATH once the real domain is connected."""
    import os
    base = os.environ.get("BASE_PATH", "").rstrip("/")
    if not base: return
    pat = re.compile(r'((?:href|src|action)=")/(?!/)')
    for f in OUT.rglob("*.html"):
        t = f.read_text(encoding="utf-8")
        f.write_text(pat.sub(lambda m: m.group(1) + base + "/", t), encoding="utf-8")
    print("applied BASE_PATH", base)

def main():
    if OUT.exists(): shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)
    posts = load_posts()
    (OUT / "blog").mkdir(exist_ok=True)
    (OUT / "blog" / "index.html").write_text(blog_index(posts), encoding="utf-8")
    for p in posts:
        d = OUT / p["slug"]; d.mkdir(exist_ok=True)
        (d / "index.html").write_text(post_page(p), encoding="utf-8")
    urls = [("/", "1.0", "weekly"), ("/services/", "0.9", "monthly"), ("/contact/", "0.9", "monthly"), ("/gallery/", "0.8", "monthly"),
            ("/about/", "0.7", "monthly"), ("/blog/", "0.8", "weekly")]
    urls += [(f"/{d.name}/", "0.8", "monthly") for d in sorted((ROOT / "static").iterdir()) if d.is_dir() and d.name.startswith("photo-booth-rental-")]
    urls += [(f'/{p["slug"]}/', "0.6", "monthly") for p in posts]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
        f"<url><loc>{SITE}{u}</loc><changefreq>{c}</changefreq><priority>{pr}</priority></url>\n" for u, pr, c in urls) + "</urlset>\n"
    (OUT / "sitemap.xml").write_text(xml, encoding="utf-8")
    apply_base_path()
    print(f"built {len(posts)} live post(s), {len(urls)} URLs -> {OUT}")

if __name__ == "__main__":
    main()

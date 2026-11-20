# SI Photo Booth — static site

Rebuilt from the WordPress theme and export of siphotoboothatl.com. Hosted free on GitHub Pages.

## Folders
- `static/`  — the pages (home, services, gallery, about, contact, 7 city pages), CSS/JS, CNAME, robots.txt
- `posts/`   — one file per blog post (`.md`). Add a file here to publish a post.
- `tools/`   — `build.py` (builds the site), `localize-images.py`, layout files
- `.github/workflows/deploy.yml` — builds and publishes automatically on every upload and once a day

## Publishing a blog post
Create `posts/my-post-slug.md`:

    ---
    title: Your Post Title
    date: 2026-12-01
    category: Weddings
    description: One or two sentences shown on the blog page and in Google.
    image: https://...link to the featured photo...
    ---
    Post text in Markdown (or plain HTML).

A post with a future `date` stays hidden and goes live automatically on that day.
The file name becomes the page address: `posts/my-post-slug.md` -> siphotoboothatl.com/my-post-slug/

## First-time setup
1. Create a free GitHub repository and upload everything in this folder (including `.github`).
2. Repository Settings -> Pages -> Source: **GitHub Actions**.
3. Open `static/contact/index.html`, replace `YOUR_FORM_ID` with your Formspree form ID.
4. Check the site at the github.io address GitHub shows. Only then point your domain at GitHub (Settings -> Pages -> Custom domain).
5. Before cancelling WordPress hosting: copy `wp-content/uploads` into `static/assets/uploads/`, then run `python tools/localize-images.py`.

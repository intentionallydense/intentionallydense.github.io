# Architecture

Personal site built with Jekyll, hosted on GitHub Pages.

## File/module map

- `_config.yml` — Site config, collections, permalink settings
- `_layouts/default.html` — Base HTML layout (head, nav, main wrapper)
- `_layouts/post.html` — Layout for blog posts
- `_layouts/project.html` — Layout for writing items (article-style, 640px max-width)
- `_layouts/project-app.html` — Layout for artifacts (900px max-width, relaxed image constraints)
- `_writing/` — Writing collection (essays, writeups). Each file becomes a `/writing/:slug/` page
- `_artifacts/` — Artifacts collection (interactive tools). Each file becomes an `/artifacts/:slug/` page
- `_posts/` — Blog post collection (photo posts, short notes)
- `.github/workflows/post-from-issue.yml` — GitHub Action to create posts from issues (paste photos + caption, label "post")
- `assets/css/style.css` — Global styles
- `mokoudb/emotes/` — Mokou emote image files
- `mokoudb/tags.json` — Tag data for mokou_search (loaded at runtime via fetch)
- `index.html` — Homepage
- `writing.html` — Writing listing page
- `artifacts.html` — Artifacts listing page
- `posts.html` — Posts listing page

## Key decisions

- **Writing vs artifacts**: Two top-level sections. Writing is chronological, text-driven (essays, writeups). Artifacts is a curated set of interactive things. Writeups about artifacts go in writing and link to the artifact.
- **project-app layout**: Wider layout for interactive artifacts. Overrides `article img` constraints so galleries/tools render properly.
- **mokou_search assets stay in `/mokoudb/`**: Emotes and tags.json remain at their original paths; the artifact page fetches them with absolute paths. Avoids moving hundreds of image files.
- **Post from issue workflow**: GitHub Action creates posts from labeled issues. Photos pasted into issues are downloaded from GitHub's CDN and committed to `assets/images/`.

## Data flow

- Jekyll builds static HTML from layouts + collections
- mokou_search loads `/mokoudb/tags.json` at runtime via fetch, images served from `/mokoudb/emotes/`
- Posts can be created via GitHub Issues → GitHub Action → commit to `_posts/`

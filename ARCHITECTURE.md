# Architecture

Personal site built with Jekyll, hosted on GitHub Pages.

## File/module map

- `_config.yml` — Site config, collections, permalink settings
- `_layouts/default.html` — Base HTML layout (head, nav, main wrapper)
- `_layouts/post.html` — Layout for blog posts
- `_layouts/project.html` — Layout for standard article-style projects (640px max-width)
- `_layouts/project-app.html` — Layout for interactive/app-style projects (900px max-width, no `<article>` wrapper)
- `_projects/` — Project collection. Each file becomes a `/projects/:slug/` page
- `_posts/` — Blog post collection
- `assets/css/style.css` — Global styles
- `mokoudb/emotes/` — Mokou emote image files
- `mokoudb/tags.json` — Tag data for mokou_search (loaded at runtime via fetch)
- `index.html` — Homepage
- `projects.html` — Projects listing page
- `posts.html` — Posts listing page

## Key decisions

- **project-app layout**: Created for interactive projects that need more width and shouldn't have `article img` constraints (max-width: 600px, max-height: 400px) applied. Reusable for future app-style projects.
- **mokou_search assets stay in `/mokoudb/`**: Emotes and tags.json remain at their original paths; the project page fetches them with absolute paths. Avoids moving hundreds of image files.
- **No separate nav link for mokou_search**: Accessible via the projects page instead of a dedicated nav entry.

## Data flow

- Jekyll builds static HTML from layouts + collections
- mokou_search loads `/mokoudb/tags.json` at runtime via fetch, images served from `/mokoudb/emotes/`

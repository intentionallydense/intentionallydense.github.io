A minimal personal site with notes and projects.

## Setup

1. Create a new repo on GitHub named `yourusername.github.io`
2. Push this folder to that repo
3. Go to repo Settings → Pages → make sure it's set to deploy from main branch
4. Your site will be live at `https://yourusername.github.io`

## Adding content

### Posts (short posts)

Create a file in `_posts/` with this format:

```markdown
---
date: 2025-01-20
---
Your short thought goes here.
```

Filename can be anything, like `2025-01-20-whatever.md`

### Projects (longer posts)

Create a file in `_projects/` like:

```markdown
---
title: Project Name
description: One-line summary
date: 2025-01-01
---

Full content here. Markdown works.
```

### Images

Put images in `assets/images/` and reference them in your markdown:

```markdown
![alt text](/assets/images/your-image.png)
```

Works in both posts and projects.

## Local preview

If you want to preview locally:

```
gem install bundler jekyll
bundle exec jekyll serve
```

Then open `http://localhost:4000`

## Customization

- Edit `_config.yml` to change your site title
- Edit `assets/css/style.css` for styling
- Edit layouts in `_layouts/` for structure

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a minimal Jekyll static site hosted on GitHub Pages. It features a personal portfolio/blog with two main content types: posts (short notes) and projects (longer descriptions).

## Development Commands

```bash
# Install dependencies
bundle install

# Run local development server
bundle exec jekyll serve
# Site available at http://localhost:4000

# Build site (output to _site/)
bundle exec jekyll build
```

## Architecture

### Content Organization

**Two Jekyll Collections:**
- **Posts** (`_posts/`): Short notes/thoughts with date-based naming (`YYYY-MM-DD-slug.md`)
- **Projects** (`_projects/`): Longer project descriptions with frontmatter-based dating

**URL Structure:**
- Posts: `/posts/slug/`
- Projects: `/projects/slug/`
- Automatic permalink generation configured in `_config.yml`

### Layout Hierarchy

```
default.html (base layout with nav and header)
├── post.html (shows date in YYYY-MM-DD format)
└── project.html (shows date in "Month YYYY" format)
```

All layouts automatically applied via `_config.yml` defaults - no need to specify in frontmatter.

### Styling System

**Dual Font Architecture:**
- Header/navigation/dates: Monospace (`"SF Mono", Monaco, Consolas`)
- Content text: Sans-serif (`Helvetica, Arial`)
- Achieved through class-specific font-family overrides on `.intro`, `.note-content`, `.project-item`

Single CSS file (`assets/css/style.css`) with no preprocessors or build tools.

### Key Patterns

**Adding New Posts:**
1. Create `_posts/YYYY-MM-DD-title.md`
2. Add frontmatter with `date: YYYY-MM-DD`
3. Write content in Markdown
4. Automatically appears in `/posts/` listing (reverse chronological)

**Adding New Projects:**
1. Create `_projects/slug.md`
2. Add frontmatter: `title`, `description`, `date`
3. Write content in Markdown
4. Automatically appears in `/projects/` listing

**Image References:**
- Store in `assets/images/`
- Reference with absolute paths: `/assets/images/filename.jpg`
- Profile picture on homepage: floated right, 150x200px

## Deployment

Automatic deployment via GitHub Pages from `main` branch. Jekyll builds automatically on push - no manual build step required.

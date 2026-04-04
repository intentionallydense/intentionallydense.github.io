#!/usr/bin/env python3
"""
Publish Obsidian notes to Jekyll.

Scans the vault's "7. website/" folder for markdown files with
`published: true` frontmatter, converts Obsidian syntax to Jekyll,
copies images, and commits to the right collection.

Frontmatter fields:
    published: true          (required)
    date: 2026-03-28 14:30   (required for posts, optional for writing)
    slug: my-slug            (optional — derived from filename if omitted)
    type: post               (optional — "post" (default) or "writing")
    title: My Title          (required for writing, ignored for posts)
    description: About...    (optional, passed through for writing)

Usage:
    python3 publish.py              # dry run
    python3 publish.py --go         # publish
    python3 publish.py --go --push  # publish and git push
"""
# Used by: zsh alias `publish` (in nix-config modules/home/zsh/default.nix)
# Depends on: Obsidian vault at ~/Documents/Obsidian/magnesium/

import argparse
import hashlib
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

VAULT_PATH = Path.home() / "Documents/Obsidian/magnesium"
WEBSITE_DIR = VAULT_PATH / "7. website"
JEKYLL_ROOT = Path(__file__).resolve().parent
POSTS_DIR = JEKYLL_ROOT / "_posts"
WRITING_DIR = JEKYLL_ROOT / "_writing"
IMAGES_DIR = JEKYLL_ROOT / "assets/images"

# Obsidian wiki-link images: ![[file.jpg]] or ![[file.jpg|alt text]]
WIKI_IMAGE_RE = re.compile(r"!\[\[([^\]|]+?)(?:\|([^\]]*))?\]\]")
# Standard markdown images (local only, not http): ![alt](path)
MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\((?!https?://)([^)]+)\)")
# Obsidian comments: %%...%%
COMMENT_RE = re.compile(r"%%.*?%%", re.DOTALL)
# Non-image wiki-links: [[page]] or [[page|display]]
WIKILINK_RE = re.compile(r"\[\[([^\]|]+?)(?:\|([^\]]*))?\]\]")


def parse_frontmatter(text):
    """Split YAML frontmatter from body. Returns (dict, body_str)."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end].strip()
    body = text[end + 3 :].strip()
    meta = {}
    for line in raw.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            val = val.strip().strip("'\"")
            # Handle booleans
            if val.lower() == "true":
                val = True
            elif val.lower() == "false":
                val = False
            meta[key.strip()] = val
    return meta, body


def slugify(name):
    """Convert a name to a URL-safe slug."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def sanitize_image_name(name):
    """Lowercase, replace spaces with hyphens, keep safe chars only."""
    name = name.lower().replace(" ", "-")
    return re.sub(r"[^a-z0-9._-]", "", name)


def find_image(name, note_path):
    """Find an image file by name, searching outward from the note's location."""
    search_dirs = [
        note_path.parent / "images",
        note_path.parent,
        WEBSITE_DIR / "images",
        WEBSITE_DIR,
        VAULT_PATH,
    ]
    for d in search_dirs:
        # Direct match
        candidate = d / name
        if candidate.is_file():
            return candidate
        # Recursive search in this directory
        for match in d.rglob(name):
            if match.is_file():
                return match
    return None


MAX_IMAGE_WIDTH = 1600  # Cap width for oversized camera photos; 2.5x site width for retina


def copy_image(src, dest_name, dry_run):
    """Copy image to assets/images/, resizing if too wide. Returns True if copied."""
    dest = IMAGES_DIR / dest_name
    if dest.exists():
        # On macOS (case-insensitive FS), dest.exists() matches files with different casing.
        # Detect case mismatches so git tracks the lowercase name we actually reference.
        actual_name = dest.resolve().name
        needs_case_fix = actual_name != dest_name
        if not needs_case_fix:
            if hashlib.md5(src.read_bytes()).digest() == hashlib.md5(dest.read_bytes()).digest():
                return False
        if needs_case_fix and not dry_run:
            # Two-step rename required on case-insensitive filesystems
            tmp = dest.with_suffix(".tmp-rename")
            dest.rename(tmp)
            tmp.rename(dest)
            print(f"  Case fix: {actual_name} → {dest_name}")
            if hashlib.md5(src.read_bytes()).digest() == hashlib.md5(dest.read_bytes()).digest():
                return True  # Renamed but content unchanged, skip re-copy
    if not dry_run:
        shutil.copy2(src, dest)
        # Resize with sips (macOS built-in) if wider than MAX_IMAGE_WIDTH
        try:
            result = subprocess.run(
                ["sips", "-g", "pixelWidth", str(dest)],
                capture_output=True, text=True,
            )
            for line in result.stdout.splitlines():
                if "pixelWidth" in line:
                    width = int(line.split(":")[-1].strip())
                    if width > MAX_IMAGE_WIDTH:
                        subprocess.run(
                            ["sips", "--resampleWidth", str(MAX_IMAGE_WIDTH), str(dest)],
                            capture_output=True,
                        )
                        print(f"  Resized: {dest_name} ({width}px → {MAX_IMAGE_WIDTH}px)")
                    break
        except FileNotFoundError:
            pass  # sips not available (non-macOS), skip resize
    return True


def convert_body(body, note_path, dry_run):
    """Convert Obsidian syntax to Jekyll markdown. Copies images as a side effect."""
    copied_images = []

    def replace_wiki_image(m):
        filename = m.group(1).strip()
        alt = m.group(2) or ""
        src = find_image(filename, note_path)
        if src is None:
            print(f"  WARNING: image not found: {filename}")
            return m.group(0)
        dest_name = sanitize_image_name(src.name)
        if copy_image(src, dest_name, dry_run):
            copied_images.append(dest_name)
        return f"\n\n![{alt}](/assets/images/{dest_name})\n\n"

    def replace_md_image(m):
        alt = m.group(1)
        rel_path = m.group(2).strip()
        src = (note_path.parent / rel_path).resolve()
        if not src.is_file():
            src = find_image(Path(rel_path).name, note_path)
        if src is None:
            print(f"  WARNING: image not found: {rel_path}")
            return m.group(0)
        dest_name = sanitize_image_name(src.name)
        if copy_image(src, dest_name, dry_run):
            copied_images.append(dest_name)
        return f"\n\n![{alt}](/assets/images/{dest_name})\n\n"

    body = COMMENT_RE.sub("", body)
    body = WIKI_IMAGE_RE.sub(replace_wiki_image, body)
    body = MD_IMAGE_RE.sub(replace_md_image, body)
    # Non-image wiki-links → plain text (use display text if present)
    body = WIKILINK_RE.sub(lambda m: m.group(2) or m.group(1), body)
    # Collapse excessive blank lines (from image spacing) to exactly two
    body = re.sub(r"\n{3,}", "\n\n", body)

    return body.strip(), copied_images


def find_published_notes():
    """Scan 7. website/ for markdown files with published: true."""
    notes = []
    if not WEBSITE_DIR.is_dir():
        print(f"Notes directory not found: {WEBSITE_DIR}")
        return notes
    for md in WEBSITE_DIR.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)
        if meta.get("published") is True:
            notes.append((md, meta, body))
    return notes


def make_output(meta, body, note_path, dry_run):
    """Generate Jekyll content and output path. Returns (dest_dir, filename, content, images)."""
    note_type = meta.get("type", "post")
    slug = meta.get("slug", "") or slugify(note_path.stem)

    # Convert body (shared across types)
    converted, images = convert_body(body, note_path, dry_run)

    if note_type == "writing":
        # Writing collection: slug.md in _writing/, keeps title + description + date
        filename = f"{slug}.md"
        fm_lines = []
        if meta.get("title"):
            fm_lines.append(f"title: {meta['title']}")
        if meta.get("description"):
            fm_lines.append(f"description: {meta['description']}")
        if meta.get("date"):
            fm_lines.append(f"date: {meta['date']}")
        frontmatter = "\n".join(fm_lines)
        content = f"---\n{frontmatter}\n---\n{converted}\n"
        return WRITING_DIR, filename, content, images

    else:
        # Post (default): YYYY-MM-DD-slug.md in _posts/, only date in frontmatter
        date_str = meta.get("date", "")
        if not date_str:
            mtime = datetime.fromtimestamp(note_path.stat().st_mtime)
            date_str = mtime.strftime("%Y-%m-%d %H:%M:00")
            print(f"  WARNING: no date in frontmatter, using mtime: {date_str}")
        date_prefix = date_str.strip().split(" ")[0]
        filename = f"{date_prefix}-{slug}.md"
        content = f"---\ndate: {date_str}\n---\n{converted}\n"
        return POSTS_DIR, filename, content, images


def main():
    parser = argparse.ArgumentParser(description="Publish Obsidian notes to Jekyll")
    parser.add_argument("--go", action="store_true", help="Actually publish (default is dry run)")
    parser.add_argument("--push", action="store_true", help="Git push after committing")
    args = parser.parse_args()
    dry_run = not args.go

    if dry_run:
        print("DRY RUN (pass --go to publish)\n")

    notes = find_published_notes()
    if not notes:
        print("No published notes found in 7. website/")
        return

    changed = []
    all_images = []

    for note_path, meta, body in notes:
        rel = note_path.relative_to(WEBSITE_DIR)
        note_type = meta.get("type", "post")
        print(f"{'[DRY] ' if dry_run else ''}Processing ({note_type}): {rel}")

        dest_dir, filename, content, images = make_output(meta, body, note_path, dry_run)
        all_images.extend(images)

        dest = dest_dir / filename
        if dest.exists() and dest.read_text(encoding="utf-8") == content:
            print(f"  Unchanged: {filename}")
            continue

        print(f"  {'Would write' if dry_run else 'Writing'}: {dest_dir.name}/{filename}")
        if images:
            print(f"  Images: {', '.join(images)}")

        if not dry_run:
            dest.write_text(content, encoding="utf-8")
        changed.append(filename)

    # Summary
    print(f"\n{'Would publish' if dry_run else 'Published'}: {len(changed)} item(s)")
    if not changed:
        return

    if dry_run:
        return

    # Git commit
    slugs = ", ".join(p.replace(".md", "").split("-", 3)[-1] for p in changed)
    subprocess.run(
        ["git", "add", "_posts/", "_writing/", "assets/images/"],
        cwd=JEKYLL_ROOT, check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", f"publish: {slugs}"],
        cwd=JEKYLL_ROOT,
        check=True,
    )
    print(f"Committed: publish: {slugs}")

    if args.push:
        subprocess.run(["git", "push"], cwd=JEKYLL_ROOT, check=True)
        print("Pushed to remote")


if __name__ == "__main__":
    main()

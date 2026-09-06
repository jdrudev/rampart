"""Synchronize explicitly labelled Confluence pages into content/blog."""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

from .client import ConfluenceClient
from .transform import page_to_markdown

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "content" / "blog"


def slugify(title: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return value[:80].rstrip("-")


def sync() -> None:
    client = ConfluenceClient(
        os.environ["CONFLUENCE_BASE_URL"],
        os.environ["CONFLUENCE_EMAIL"],
        os.environ["CONFLUENCE_API_TOKEN"],
        os.environ.get("CONFLUENCE_CLOUD_ID"),
    )
    print(f"Using Confluence API endpoint: {client.api_base_url}")
    pages = client.list_published_pages(
        "portfolio-public",
        os.environ.get("CONFLUENCE_SPACE", "Portfolio"),
        os.environ.get("CONFLUENCE_CONTENT_TYPE", "page"),
    )
    desired: set[str] = set()
    for page in pages:
        slug = slugify(page.title)
        desired.add(slug)
        article_dir = CONTENT / slug
        article_dir.mkdir(parents=True, exist_ok=True)
        (article_dir / "index.md").write_text(page_to_markdown(page), encoding="utf-8")
    for article_dir in CONTENT.iterdir():
        if article_dir.is_dir() and article_dir.name not in desired:
            shutil.rmtree(article_dir)
    print(f"Synced {len(pages)} portfolio-public article(s).")


if __name__ == "__main__":
    sync()
"""Synchronize explicitly labelled Confluence pages into content/blog."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from .client import ConfluenceClient
from .transform import page_to_markdown

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "content" / "blog"


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
    existing = {path.name for path in CONTENT.iterdir() if path.is_dir()} if CONTENT.exists() else set()
    if not pages and existing and os.environ.get("CONFLUENCE_ALLOW_EMPTY_SYNC", "false").lower() != "true":
        raise RuntimeError(
            "Confluence returned zero published pages while local content exists. "
            "Refusing to delete content; set CONFLUENCE_ALLOW_EMPTY_SYNC=true only for intentional removal."
        )
    for page in pages:
        print(f"Processing Confluence page {page.page_id}: {page.title}")
        article_dir = CONTENT / page.page_id
        desired.add(page.page_id)
        assets_dir = article_dir / "assets"
        article_dir.mkdir(parents=True, exist_ok=True)
        if assets_dir.exists():
            shutil.rmtree(assets_dir)
        (article_dir / "index.md").write_text(page_to_markdown(page), encoding="utf-8")
    for article_dir in CONTENT.iterdir():
        if article_dir.is_dir() and article_dir.name not in desired:
            shutil.rmtree(article_dir)
    print(f"Synced {len(pages)} portfolio-public article(s).")


if __name__ == "__main__":
    try:
        sync()
    except (KeyError, RuntimeError, ValueError) as error:
        print(f"Confluence sync failed: {error}")
        raise SystemExit(1)
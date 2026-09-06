from dataclasses import dataclass


@dataclass(frozen=True)
class ConfluencePage:
    page_id: str
    title: str
    body_html: str
    updated_at: str
    labels: tuple[str, ...]
    source_url: str
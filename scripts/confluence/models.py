from dataclasses import dataclass


@dataclass(frozen=True)
class ConfluencePage:
    page_id: str
    title: str
    body_html: str
    updated_at: str
    labels: tuple[str, ...]
    source_url: str


@dataclass(frozen=True)
class ConfluenceAttachment:
    attachment_id: str
    filename: str
    media_type: str
    download_url: str
    file_size: int
    fallback_download_url: str | None = None
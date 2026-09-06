"""Conservative HTML-to-Markdown conversion for the first Confluence slice."""

from html.parser import HTMLParser
import re

from .models import ConfluenceAttachment, ConfluencePage


class _MarkdownParser(HTMLParser):
    def __init__(self, attachments: dict[str, ConfluenceAttachment]) -> None:
        super().__init__()
        self.output: list[str] = []
        self.stack: list[str] = []
        self.attachments = attachments

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "ri:attachment":
            filename = dict(attrs).get("ri:filename")
            attachment = self.attachments.get(filename or "")
            if attachment:
                self.output.append(f"\n![{attachment.filename}](./assets/{attachment.filename})\n")
        elif tag in {"h1", "h2", "h3", "h4"}:
            self.output.append("\n" + "#" * int(tag[1]) + " ")
        elif tag == "li":
            self.output.append("\n- ")
        elif tag == "br":
            self.output.append("\n")
        self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"p", "h1", "h2", "h3", "h4", "li", "blockquote"}:
            self.output.append("\n")
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_data(self, data: str) -> None:
        self.output.append(data)


def page_to_markdown(page: ConfluencePage, attachments: list[ConfluenceAttachment] | None = None) -> str:
    parser = _MarkdownParser({attachment.filename: attachment for attachment in attachments or []})
    parser.feed(page.body_html)
    body = re.sub(r"\n{3,}", "\n\n", "".join(parser.output)).strip()
    tags = [label for label in page.labels if label != "portfolio-public"]
    tag_lines = "\n".join(f"  - {tag!r}" for tag in tags) or "  []"
    return f"---\ntitle: {page.title!r}\ndescription: Generated from Confluence.\ndate: {page.updated_at[:10]}\nupdated: {page.updated_at[:10]}\ntags:\n{tag_lines}\nconfluence_id: {page.page_id!r}\nsource_url: {page.source_url!r}\n---\n\n{body}\n"
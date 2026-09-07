"""Convert Confluence storage XHTML into readable, safe Markdown."""

from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from html.parser import HTMLParser
import re
from urllib.parse import urlparse

from .models import ConfluencePage


@dataclass
class _Node:
    name: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list["_Node | str"] = field(default_factory=list)


class _DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Node("root")
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = _Node(tag.lower(), {key.lower(): value or "" for key, value in attrs})
        self.stack[-1].children.append(node)
        if node.name not in {"br", "hr", "img", "meta", "input", "source"}:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if self.stack[-1].name == tag.lower():
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].name == tag.lower():
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)

    def unknown_decl(self, data: str) -> None:
        if data.startswith("CDATA["):
            self.stack[-1].children.append(data[6:])


UNSUPPORTED_MACROS = {"ac:structured-macro", "ac:macro"}
BLOCK_NODES = {"p", "div", "section", "article", "blockquote", "ul", "ol", "pre", "table", "ac:task-list"}


def _plain(node: _Node | str) -> str:
    if isinstance(node, str):
        return re.sub(r"\s+", " ", node)
    return "".join(_plain(child) for child in node.children)


def _safe_url(value: str) -> str | None:
    parsed = urlparse(value)
    if parsed.scheme in {"", "http", "https", "mailto"} and not value.startswith("//"):
        return value
    return None


def _inline(node: _Node | str) -> str:
    if isinstance(node, str):
        return node.replace("\\", "\\\\").replace("`", "\\`")
    if node.name in UNSUPPORTED_MACROS:
        return f"> Confluence macro omitted: `{node.attrs.get('ac:name', 'unknown')}`"
    content = "".join(_inline(child) for child in node.children)
    if node.name in {"strong", "b"}:
        return f"**{content.strip()}**"
    if node.name in {"em", "i"}:
        return f"*{content.strip()}*"
    if node.name == "u":
        return f"<u>{content.strip()}</u>"
    if node.name in {"del", "s", "strike"}:
        return f"~~{content.strip()}~~"
    if node.name == "code":
        return f"`{content.strip()}`"
    if node.name == "a":
        href = _safe_url(node.attrs.get("href", ""))
        return f"[{content.strip()}]({href})" if href else content
    if node.name == "br":
        return "  \n"
    if node.name == "img":
        source = _safe_url(node.attrs.get("src", ""))
        return f"![{node.attrs.get('alt', '').strip()}]({source})" if source else ""
    if node.name in {"ac:task-id", "ac:task-status"}:
        return ""
    return content


def _table_rows(node: _Node) -> list[list[_Node]]:
    rows: list[list[_Node]] = []
    for child in node.children:
        if not isinstance(child, _Node):
            continue
        if child.name == "tr":
            rows.append([cell for cell in child.children if isinstance(cell, _Node) and cell.name in {"th", "td"}])
        else:
            rows.extend(_table_rows(child))
    return rows


def _render_children(node: _Node) -> str:
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, _Node) and (child.name in BLOCK_NODES or child.name.startswith("h") or child.name.startswith("ac:")):
            parts.append(_render_block(child))
        elif isinstance(child, str) and child.strip():
            parts.append(child.strip())
        elif isinstance(child, _Node):
            parts.append(_inline(child).strip())
    return "\n\n".join(part for part in parts if part)


def _simple_table(node: _Node) -> str | None:
    rows = _table_rows(node)
    if not rows or not rows[0] or any("colspan" in cell.attrs or "rowspan" in cell.attrs for row in rows for cell in row):
        return None
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        return None
    values = [[_inline(cell).strip().replace("|", "\\|").replace("\n", " ") for cell in row] for row in rows]
    lines = ["| " + " | ".join(values[0]) + " |", "| " + " | ".join("---" for _ in values[0]) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in values[1:])
    return "\n".join(lines)


def _sanitized_html(node: _Node) -> str:
    allowed = {"table", "thead", "tbody", "tfoot", "tr", "th", "td", "p", "br", "strong", "em", "u", "code", "pre", "blockquote", "a", "img"}
    if node.name not in allowed:
        return "".join(_sanitized_html(child) if isinstance(child, _Node) else escape(child) for child in node.children)
    attrs: list[str] = []
    for key in ("href", "src", "alt", "colspan", "rowspan"):
        value = node.attrs.get(key)
        if value and (key not in {"href", "src"} or _safe_url(value)):
            attrs.append(f' {key}="{escape(value, quote=True)}"')
    content = "".join(_sanitized_html(child) if isinstance(child, _Node) else escape(child) for child in node.children)
    if node.name in {"br", "img"}:
        return f"<{node.name}{''.join(attrs)} />"
    return f"<{node.name}{''.join(attrs)}>{content}</{node.name}>"


def _render_block(node: _Node) -> str:
    if node.name in UNSUPPORTED_MACROS:
        macro = node.attrs.get("ac:name", "unknown")
        body = _render_children(node).strip()
        if macro in {"info", "note", "success", "warning", "error", "danger", "tip"}:
            kind = "success" if macro == "tip" else "error" if macro == "danger" else macro
            return f'<div class="callout callout-{kind}"><strong>{kind.title()}</strong>\n\n{body}</div>'
        if macro in {"code", "noformat"}:
            return f"```\n{_plain(node).strip()}\n```"
        if macro == "expand":
            return f'<details class="expand"><summary>{_inline(node).strip() or "Details"}</summary>\n\n{body}\n\n</details>'
        return f"> Confluence macro omitted: `{macro}`\n\n{body}" if body else f"> Confluence macro omitted: `{macro}`"
    if node.name == "ac:task-list":
        tasks = []
        for child in node.children:
            if isinstance(child, _Node) and child.name == "ac:task":
                status = next((item for item in child.children if isinstance(item, _Node) and item.name == "ac:task-status"), None)
                body = next((item for item in child.children if isinstance(item, _Node) and item.name == "ac:task-body"), None)
                checked = _plain(status).strip().lower() in {"complete", "completed", "done"} if status else False
                tasks.append(f"- [{'x' if checked else ' '}] {_inline(body).strip() if body else _inline(child).strip()}")
        return "\n".join(tasks)
    if node.name.startswith("ac:"):
        return _render_children(node)
    if node.name in {"p", "div", "section", "article"}:
        if any(isinstance(child, _Node) and (child.name in BLOCK_NODES or child.name.startswith("h")) for child in node.children):
            return _render_children(node)
        return _inline(node).strip()
    if node.name.startswith("h") and len(node.name) == 2 and node.name[1].isdigit():
        level = min(int(node.name[1]) + 1, 6)
        return f"{'#' * level} {_inline(node).strip()}"
    if node.name == "blockquote":
        return "\n".join(f"> {line}" for line in _inline(node).strip().splitlines())
    if node.name in {"ul", "ol"}:
        lines: list[str] = []
        index = 1
        for child in node.children:
            if isinstance(child, _Node) and child.name == "li":
                marker = f"{index}." if node.name == "ol" else "-"
                lines.append(f"{marker} {_inline(child).strip()}")
                index += 1
        return "\n".join(lines)
    if node.name == "pre":
        return f"```\n{_plain(node).strip()}\n```"
    if node.name == "table":
        return _simple_table(node) or _sanitized_html(node)
    return _inline(node).strip()


def _body_to_markdown(html: str) -> str:
    parser = _DocumentParser()
    parser.feed(html)
    blocks: list[str] = []
    for child in parser.root.children:
        if isinstance(child, str):
            if child.strip():
                blocks.append(re.sub(r"\s+", " ", child).strip())
        else:
            rendered = _render_block(child)
            if rendered:
                blocks.append(rendered)
    return re.sub(r"\n{3,}", "\n\n", "\n\n".join(blocks)).strip()


def page_to_markdown(page: ConfluencePage) -> str:
    tags = [label for label in page.labels if label != "portfolio-public"]
    tag_lines = "\n".join(f"  - {tag!r}" for tag in tags) or "  []"
    body = _body_to_markdown(page.body_html)
    return f"---\ntitle: {page.title!r}\ndescription: Generated from Confluence.\ndate: {page.updated_at[:10]}\nupdated: {page.updated_at[:10]}\ntags:\n{tag_lines}\nconfluence_id: {page.page_id!r}\nsource_url: {page.source_url!r}\n---\n\n{body}\n"
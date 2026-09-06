"""Small Confluence Cloud REST client with bounded retries and no secret logging."""

from __future__ import annotations

import base64
import json
import time
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from .models import ConfluenceAttachment, ConfluencePage


class ConfluenceClient:
    def __init__(self, base_url: str, email: str, token: str, timeout: int = 20) -> None:
        value = "".join(base_url.split())
        if "://" not in value:
            value = f"https://{value}"
        parsed = urlsplit(value)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("CONFLUENCE_BASE_URL must be an HTTPS hostname or URL")
        self.base_url = value.rstrip("/")
        self.timeout = timeout
        credentials = base64.b64encode(f"{email.strip()}:{token.strip()}".encode()).decode()
        self.headers = {"Authorization": f"Basic {credentials}", "Accept": "application/json"}

    def _get(self, path: str, params: str = "") -> dict:
        url = f"{self.base_url}{path}{'?' + params if params else ''}"
        for attempt in range(3):
            try:
                request = Request(url, headers=self.headers)
                with urlopen(request, timeout=self.timeout) as response:
                    return json.load(response)
            except HTTPError as error:
                if error.code == 401:
                    raise RuntimeError(
                        "Confluence authentication failed (401). "
                        "Use the exact Atlassian account email with an Atlassian API token; "
                        "OAuth access tokens are not supported by this Basic-auth client."
                    ) from error
                if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                    raise RuntimeError(f"Confluence request failed with HTTP {error.code}") from error
            except URLError as error:
                if attempt == 2:
                    raise RuntimeError("Confluence request failed") from error
            time.sleep(2**attempt)
        raise RuntimeError("Confluence request failed")

    def list_blog_posts(self, label: str, space: str = "Portfolio") -> list[ConfluencePage]:
        pages: list[ConfluencePage] = []
        start = 0
        while True:
            cql = f'space = "{space}" AND type = "blogpost" AND label = "{label}"'
            params = urlencode({"cql": cql, "expand": "body.storage,version,metadata.labels", "limit": "50", "start": str(start)})
            payload = self._get("/wiki/rest/api/content/search", params)
            for result in payload.get("results", []):
                labels = tuple(item["name"] for item in result.get("metadata", {}).get("labels", {}).get("results", []))
                pages.append(ConfluencePage(result["id"], result["title"], result.get("body", {}).get("storage", {}).get("value", ""), result.get("version", {}).get("when", ""), labels, f"{self.base_url}/wiki{result.get('_links', {}).get('webui', '')}"))
            if len(payload.get("results", [])) < 50:
                return pages
            start += 50

    def get_attachments(self, page_id: str) -> list[ConfluenceAttachment]:
        payload = self._get(f"/wiki/rest/api/content/{page_id}/child/attachment", "limit=200")
        return [ConfluenceAttachment(item["id"], item["title"], item.get("metadata", {}).get("mediaType", ""), f"{self.base_url}{item['_links']['download']}", item.get("extensions", {}).get("fileSize", 0)) for item in payload.get("results", [])]
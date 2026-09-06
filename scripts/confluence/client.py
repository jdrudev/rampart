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


def _read_error_body(error: HTTPError, limit: int = 500) -> str:
    """Return the API's own error detail instead of guessing a root cause from the status code alone."""
    try:
        return error.read().decode("utf-8", errors="replace")[:limit]
    except Exception:
        return "<no response body>"


class ConfluenceClient:
    def __init__(self, base_url: str, email: str, token: str, cloud_id: str | None = None, timeout: int = 20) -> None:
        value = "".join(base_url.split())
        if "://" not in value:
            value = f"https://{value}"
        parsed = urlsplit(value)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("CONFLUENCE_BASE_URL must be an HTTPS hostname or URL")
        self.base_url = value.rstrip("/")
        self.timeout = timeout
        resolved_cloud_id = cloud_id.strip() if cloud_id and cloud_id.strip() else self._resolve_cloud_id()
        self.api_base_url = f"https://api.atlassian.com/ex/confluence/{resolved_cloud_id}"
        credentials = base64.b64encode(f"{email.strip()}:{token.strip()}".encode()).decode()
        self.headers = {"Authorization": f"Basic {credentials}", "Accept": "application/json"}
        self.bearer_headers = {"Authorization": f"Bearer {token.strip()}", "Accept": "application/octet-stream"}

    def _resolve_cloud_id(self) -> str:
        try:
            request = Request(f"{self.base_url}/_edge/tenant_info", headers={"Accept": "application/json"})
            with urlopen(request, timeout=self.timeout) as response:
                cloud_id = json.load(response).get("cloudId")
        except (HTTPError, URLError, ValueError, json.JSONDecodeError) as error:
            raise ValueError("Unable to resolve Confluence Cloud ID from CONFLUENCE_BASE_URL") from error
        if not isinstance(cloud_id, str) or not cloud_id.strip():
            raise ValueError("Confluence tenant metadata did not include a Cloud ID")
        return cloud_id.strip()

    def _get(self, path: str, params: str = "") -> dict:
        url = f"{self.api_base_url}{path}{'?' + params if params else ''}"
        for attempt in range(3):
            try:
                request = Request(url, headers=self.headers)
                with urlopen(request, timeout=self.timeout) as response:
                    return json.load(response)
            except HTTPError as error:
                if error.code in (401, 403):
                    body = _read_error_body(error)
                    raise RuntimeError(
                        f"Confluence request failed with HTTP {error.code} for {path}. Response body: {body}"
                    ) from error
                if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                    body = _read_error_body(error)
                    raise RuntimeError(
                        f"Confluence request failed with HTTP {error.code} for {path}. Response body: {body}"
                    ) from error
            except URLError as error:
                if attempt == 2:
                    raise RuntimeError(f"Confluence network request failed: {error.reason}") from error
            time.sleep(2**attempt)
        raise RuntimeError("Confluence request failed")

    def list_published_pages(self, label: str, space: str = "Portfolio", content_type: str = "page") -> list[ConfluencePage]:
        pages: list[ConfluencePage] = []
        start = 0
        while True:
            cql = f'space = "{space}" AND type = "{content_type}" AND label = "{label}"'
            params = urlencode({"cql": cql, "expand": "body.storage,version,metadata.labels", "limit": "50", "start": str(start)})
            payload = self._get("/wiki/rest/api/content/search", params)
            for result in payload.get("results", []):
                labels = tuple(item["name"] for item in result.get("metadata", {}).get("labels", {}).get("results", []))
                pages.append(ConfluencePage(result["id"], result["title"], result.get("body", {}).get("storage", {}).get("value", ""), result.get("version", {}).get("when", ""), labels, f"{self.base_url}/wiki{result.get('_links', {}).get('webui', '')}"))
            if len(payload.get("results", [])) < 50:
                return pages
            start += 50

    def get_attachments(self, page_id: str) -> list[ConfluenceAttachment]:
        attachments: list[ConfluenceAttachment] = []
        start = 0
        while True:
            payload = self._get(f"/wiki/api/v2/pages/{page_id}/attachments", urlencode({"limit": "50", "start": str(start)}))
            results = payload.get("results", [])
            attachments.extend(ConfluenceAttachment(item["id"], item["title"], item.get("mediaType", ""), item.get("downloadLink", f"{self.api_base_url}/wiki/api/v2/attachments/{item['id']}/download"), item.get("fileSize", 0)) for item in results)
            if len(results) < 50:
                return attachments
            start += 50

    def download_attachment(self, attachment: ConfluenceAttachment) -> bytes:
        request = Request(attachment.download_url, headers=self.bearer_headers)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return response.read(10 * 1024 * 1024 + 1)
        except HTTPError as error:
            body = _read_error_body(error)
            raise RuntimeError(f"Attachment download failed with HTTP {error.code}. Response body: {body}") from error
        except URLError as error:
            raise RuntimeError(f"Attachment download failed: {error.reason}") from error
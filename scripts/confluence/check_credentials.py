"""Check Confluence credentials and Portfolio blog-post access without changing content."""

from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .client import ConfluenceClient

ROOT = Path(__file__).resolve().parents[2]


def load_dotenv(path: Path = ROOT / ".env") -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(name, value)


def request(base_url: str, email: str, token: str, path: str, params: dict[str, str]) -> dict:
    credentials = base64.b64encode(f"{email.strip()}:{token.strip()}".encode()).decode()
    url = f"{base_url}{path}?{urlencode(params)}"
    request = Request(url, headers={"Authorization": f"Basic {credentials}", "Accept": "application/json"})
    with urlopen(request, timeout=20) as response:
        return json.load(response)


def download_request(url: str, email: str, token: str) -> bytes:
    request = Request(url, headers={"Authorization": f"Bearer {token.strip()}", "Accept": "application/octet-stream"})
    with urlopen(request, timeout=20) as response:
        return response.read(1)


def report_http_error(check: str, error: HTTPError) -> None:
    try:
        body = error.read().decode("utf-8", errors="replace")[:500]
    except Exception:
        body = "<no response body>"
    print(f"{check}: FAIL (HTTP {error.code})", file=sys.stderr, flush=True)
    print(f"Response body: {body}", file=sys.stderr, flush=True)


def main() -> int:
    load_dotenv()
    missing = [name for name in ("CONFLUENCE_BASE_URL", "CONFLUENCE_EMAIL", "CONFLUENCE_API_TOKEN") if not os.environ.get(name)]
    if missing:
        print(f"Missing environment variable(s): {', '.join(missing)}", file=sys.stderr, flush=True)
        return 2

    try:
        client = ConfluenceClient(
            os.environ["CONFLUENCE_BASE_URL"],
            os.environ["CONFLUENCE_EMAIL"],
            os.environ["CONFLUENCE_API_TOKEN"],
            os.environ.get("CONFLUENCE_CLOUD_ID"),
        )
    except ValueError as error:
        print(f"Configuration error: {error}", file=sys.stderr, flush=True)
        return 2

    email = os.environ["CONFLUENCE_EMAIL"]
    token = os.environ["CONFLUENCE_API_TOKEN"]
    print(f"Testing Confluence tenant: {client.base_url}", flush=True)
    print(f"Testing API endpoint: {client.api_base_url}", flush=True)

    space = os.environ.get("CONFLUENCE_SPACE", "Portfolio")
    content_type = os.environ.get("CONFLUENCE_CONTENT_TYPE", "page")
    checks_failed = False

    try:
        identity = request(client.api_base_url, email, token, "/wiki/rest/api/user/current", {})
        print(f"Identity: PASS ({identity.get('displayName', 'account authenticated')})", flush=True)
    except HTTPError as error:
        report_http_error("Identity", error)
        return 1
    except URLError as error:
        print(f"Identity: FAIL (network error: {error.reason})", file=sys.stderr, flush=True)
        return 1
    except Exception as error:
        print(f"Identity: FAIL (unexpected {type(error).__name__}: {error})", file=sys.stderr, flush=True)
        return 1

    try:
        spaces = request(client.api_base_url, email, token, "/wiki/rest/api/space", {"limit": "1"})
        print(f"Space API: PASS ({len(spaces.get('results', []))} sample result(s))", flush=True)
    except HTTPError as error:
        report_http_error("Space API", error)
        checks_failed = True
    except URLError as error:
        print(f"Space API: FAIL (network error: {error.reason})", file=sys.stderr, flush=True)
        checks_failed = True
    except Exception as error:
        print(f"Space API: FAIL (unexpected {type(error).__name__}: {error})", file=sys.stderr, flush=True)
        checks_failed = True

    try:
        content = request(client.api_base_url, email, token, "/wiki/rest/api/content/search", {"cql": f'type = "{content_type}"', "limit": "1"})
        print(f"Content API ({content_type}): PASS ({len(content.get('results', []))} sample result(s))", flush=True)
    except HTTPError as error:
        report_http_error(f"Content API ({content_type})", error)
        checks_failed = True
    except URLError as error:
        print(f"Content API ({content_type}): FAIL (network error: {error.reason})", file=sys.stderr, flush=True)
        checks_failed = True
    except Exception as error:
        print(f"Content API ({content_type}): FAIL (unexpected {type(error).__name__}: {error})", file=sys.stderr, flush=True)
        checks_failed = True

    cql = f'space = "{space}" AND type = "{content_type}" AND label = "portfolio-public"'
    try:
        payload = request(client.api_base_url, email, token, "/wiki/rest/api/content/search", {"cql": cql, "limit": "50", "expand": "body.storage,version,history,metadata.labels"})
        results = payload.get("results", [])
        if not results:
            print(f"Publication query: FAIL (0 matching {content_type}(s) in {space})", file=sys.stderr, flush=True)
            print('Check the space, content type, and exact "portfolio-public" label.', file=sys.stderr, flush=True)
            checks_failed = True
        else:
            print(f"Publication query: PASS ({len(results)} matching {content_type}(s) in {space})", flush=True)
            for result in results:
                print(f"- {result.get('title', '<untitled>')} [{result.get('id', 'no-id')}]")
            for result in results:
                page_id = result.get("id")
                if not page_id:
                    continue
                try:
                    attachments = request(client.api_base_url, email, token, f"/wiki/api/v2/pages/{page_id}/attachments", {"limit": "1"})
                    print(f"Attachments API ({page_id}): PASS ({len(attachments.get('results', []))} sample result(s))", flush=True)
                    if attachments.get("results"):
                        attachment = attachments["results"][0]
                        download_url = f"{client.api_base_url}/wiki/api/v2/attachments/{attachment['id']}/download"
                        try:
                            download_request(download_url, email, token)
                            print(f"Attachment download ({page_id}): PASS", flush=True)
                        except HTTPError as error:
                            report_http_error(f"Attachment download ({page_id})", error)
                            checks_failed = True
                except HTTPError as error:
                    report_http_error(f"Attachments API ({page_id})", error)
                    checks_failed = True
                except URLError as error:
                    print(f"Attachments API ({page_id}) Bearer: FAIL (network error: {error.reason})", file=sys.stderr, flush=True)
                    checks_failed = True
                except Exception as error:
                    print(f"Attachments API ({page_id}): FAIL (unexpected {type(error).__name__}: {error})", file=sys.stderr, flush=True)
                    checks_failed = True
    except HTTPError as error:
        report_http_error("Publication query", error)
        checks_failed = True
    except URLError as error:
        print(f"Publication query: FAIL (network error: {error.reason})", file=sys.stderr, flush=True)
        checks_failed = True
    except Exception as error:
        print(f"Publication query: FAIL (unexpected {type(error).__name__}: {error})", file=sys.stderr, flush=True)
        checks_failed = True

    return 1 if checks_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
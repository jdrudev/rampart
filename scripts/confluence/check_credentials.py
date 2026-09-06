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


def report_http_error(check: str, error: HTTPError) -> None:
    if error.code == 401:
        print(f"{check}: FAIL (401 Unauthorized)", file=sys.stderr)
        print("The email/token pair is not accepted. Use an Atlassian API token with its exact account email.", file=sys.stderr)
    elif error.code == 403:
        print(f"{check}: FAIL (403 Forbidden)", file=sys.stderr)
        print("The account is authenticated but lacks the permission required by this endpoint.", file=sys.stderr)
    else:
        print(f"{check}: FAIL (HTTP {error.code})", file=sys.stderr)


def main() -> int:
    load_dotenv()
    missing = [name for name in ("CONFLUENCE_BASE_URL", "CONFLUENCE_EMAIL", "CONFLUENCE_API_TOKEN") if not os.environ.get(name)]
    if missing:
        print(f"Missing environment variable(s): {', '.join(missing)}", file=sys.stderr)
        return 2

    try:
        client = ConfluenceClient(os.environ["CONFLUENCE_BASE_URL"], os.environ["CONFLUENCE_EMAIL"], os.environ["CONFLUENCE_API_TOKEN"])
    except ValueError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 2

    email = os.environ["CONFLUENCE_EMAIL"]
    token = os.environ["CONFLUENCE_API_TOKEN"]
    print(f"Testing Confluence tenant: {client.base_url}")

    space = os.environ.get("CONFLUENCE_SPACE", "Portfolio")
    checks_failed = False

    try:
        identity = request(client.base_url, email, token, "/wiki/rest/api/user/current", {})
        print(f"Identity: PASS ({identity.get('displayName', 'account authenticated')})")
    except HTTPError as error:
        report_http_error("Identity", error)
        return 1
    except URLError as error:
        print(f"Identity: FAIL (network error: {error.reason})", file=sys.stderr)
        return 1

    try:
        spaces = request(client.base_url, email, token, "/wiki/rest/api/space", {"limit": "1"})
        print(f"Space API: PASS ({len(spaces.get('results', []))} sample result(s))")
    except HTTPError as error:
        report_http_error("Space API", error)
        checks_failed = True

    try:
        content = request(client.base_url, email, token, "/wiki/rest/api/content/search", {"cql": 'type = "blogpost"', "limit": "1"})
        print(f"Blog Post API: PASS ({len(content.get('results', []))} sample result(s))")
    except HTTPError as error:
        report_http_error("Blog Post API", error)
        checks_failed = True

    cql = f'space = "{space}" AND type = "blogpost" AND label = "portfolio-public"'
    try:
        payload = request(client.base_url, email, token, "/wiki/rest/api/content/search", {"cql": cql, "limit": "50", "expand": "body.storage,version,history,metadata.labels"})
        results = payload.get("results", [])
        if not results:
            print(f"Publication query: FAIL (0 matching blog post(s) in {space})", file=sys.stderr)
            print('Check the space, content type, and exact "portfolio-public" label.', file=sys.stderr)
            checks_failed = True
        else:
            print(f"Publication query: PASS ({len(results)} matching blog post(s) in {space})")
            for result in results:
                print(f"- {result.get('title', '<untitled>')} [{result.get('id', 'no-id')}]")
    except HTTPError as error:
        report_http_error("Publication query", error)
        checks_failed = True

    return 1 if checks_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
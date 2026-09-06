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

    try:
        spaces = request(client.base_url, email, token, "/wiki/rest/api/space", {"limit": "1"})
        print(f"Authentication: PASS (accessible spaces response received; {len(spaces.get('results', []))} sample result(s))")
    except HTTPError as error:
        if error.code == 401:
            print("Authentication: FAIL (401 Unauthorized)", file=sys.stderr)
            print("Use the exact Atlassian account email with an Atlassian API token.", file=sys.stderr)
        elif error.code == 403:
            print("Authentication: PASS, permissions: FAIL (403 Forbidden)", file=sys.stderr)
            print("The token is valid but the account cannot read Confluence spaces.", file=sys.stderr)
        else:
            print(f"Authentication check failed with HTTP {error.code}", file=sys.stderr)
        return 1
    except URLError as error:
        print(f"Network check failed: {error.reason}", file=sys.stderr)
        return 1

    space = os.environ.get("CONFLUENCE_SPACE", "Portfolio")
    cql = f'space = "{space}" AND type = "blogpost" AND label = "portfolio-public"'
    try:
        payload = request(client.base_url, email, token, "/wiki/rest/api/content/search", {"cql": cql, "limit": "50", "expand": "body.storage,version,history,metadata.labels"})
    except HTTPError as error:
        if error.code == 403:
            print("Portfolio query: FAIL (403 Forbidden)", file=sys.stderr)
            print("The account authenticated but lacks permission to read the Portfolio content.", file=sys.stderr)
        else:
            print(f"Portfolio query failed with HTTP {error.code}", file=sys.stderr)
        return 1

    results = payload.get("results", [])
    if not results:
        print(f"Portfolio query: FAIL (0 matching blog post(s) in {space})", file=sys.stderr)
        print('Check the space, content type, and exact "portfolio-public" label.', file=sys.stderr)
        return 1

    print(f"Portfolio query: PASS ({len(results)} matching blog post(s) in {space})")
    for result in results:
        print(f"- {result.get('title', '<untitled>')} [{result.get('id', 'no-id')}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
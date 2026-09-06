"""Validate generated Markdown frontmatter without requiring the frontend toolchain."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
BLOG = ROOT / "content" / "blog"
REQUIRED = ("title", "description", "date")


def validate() -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    for path in sorted(BLOG.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            errors.append(f"{path}: missing frontmatter")
            continue
        frontmatter = text.split("---\n", 2)[1]
        for field in REQUIRED:
            if not re.search(rf"^{field}:\s*.+$", frontmatter, re.MULTILINE):
                errors.append(f"{path}: missing required field '{field}'")
        match = re.search(r'^confluence_id:\s*["\']?([^"\'\n]+)', frontmatter, re.MULTILINE)
        if match and match.group(1) in seen_ids:
            errors.append(f"{path}: duplicate confluence_id '{match.group(1)}'")
        if match:
            seen_ids.add(match.group(1))
    return errors


if __name__ == "__main__":
    failures = validate()
    if failures:
        print("Content validation failed:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        raise SystemExit(1)
    print("Content validation passed.")
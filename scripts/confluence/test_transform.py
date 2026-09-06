import unittest

from .models import ConfluencePage
from .transform import page_to_markdown


def _page(body: str) -> ConfluencePage:
    return ConfluencePage("1", "Test", body, "2026-09-06T00:00:00Z", ("portfolio-public", "security"), "https://example.test")


class TransformTests(unittest.TestCase):
    def test_inline_formatting_and_simple_table(self) -> None:
        markdown = page_to_markdown(_page(
            "<p><strong>bold</strong> <em>italic</em> <u>underline</u></p>"
            "<table><tbody><tr><th>Name</th><th>Status</th></tr>"
            "<tr><td>Rampart</td><td><strong>Active</strong></td></tr></tbody></table>"
        ))

        self.assertIn("**bold** *italic* <u>underline</u>", markdown)
        self.assertIn("| Name | Status |\n| --- | --- |\n| Rampart | **Active** |", markdown)
        self.assertNotIn("portfolio-public", markdown)
        self.assertIn("  - 'security'", markdown)

    def test_complex_table_is_sanitized_html(self) -> None:
        markdown = page_to_markdown(_page(
            '<table><tr><th colspan="2">Status</th></tr>'
            '<tr><td><a href="javascript:alert(1)">Unsafe</a></td><td>Pass</td></tr></table>'
        ))

        self.assertIn('<th colspan="2">Status</th>', markdown)
        self.assertIn("Unsafe", markdown)
        self.assertNotIn("javascript:", markdown)

    def test_unsupported_macro_is_visible(self) -> None:
        markdown = page_to_markdown(_page('<p><ac:structured-macro ac:name="jira">hidden</ac:structured-macro></p>'))

        self.assertIn("> Confluence macro omitted: `jira`", markdown)


if __name__ == "__main__":
    unittest.main()
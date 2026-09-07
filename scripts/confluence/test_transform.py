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

    def test_nested_headings_tasks_and_panels_are_normalized(self) -> None:
        markdown = page_to_markdown(_page(
            '<div><h1>Section</h1><h2>Detail</h2></div>'
            '<ac:task-list><ac:task><ac:task-status>complete</ac:task-status>'
            '<ac:task-body>Done task</ac:task-body></ac:task>'
            '<ac:task><ac:task-status>incomplete</ac:task-status>'
            '<ac:task-body>Open task</ac:task-body></ac:task></ac:task-list>'
            '<ac:structured-macro ac:name="warning"><ac:rich-text-body>'
            '<p>Read this carefully.</p></ac:rich-text-body></ac:structured-macro>'
        ))

        self.assertIn("## Section\n\n### Detail", markdown)
        self.assertIn("- [x] Done task", markdown)
        self.assertIn("- [ ] Open task", markdown)
        self.assertIn('<div class="callout callout-warning">', markdown)
        self.assertIn("Read this carefully.", markdown)

    def test_code_macro_becomes_copyable_code_block_source(self) -> None:
        markdown = page_to_markdown(_page(
            '<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">javascript</ac:parameter>'
            '<ac:parameter ac:name="theme">Midnight</ac:parameter><ac:plain-text-body>'
            '<![CDATA[print("hello")]]></ac:plain-text-body></ac:structured-macro>'
        ))

        self.assertIn('```\nprint("hello")\n```', markdown)

    def test_confluence_layout_containers_preserve_nested_blocks(self) -> None:
        markdown = page_to_markdown(_page(
            '<ac:layout><ac:layout-section><ac:layout-cell>'
            '<h1>Wrapped heading</h1><ul><li>First item</li></ul>'
            '<table><tr><th>Format</th><th>Result</th></tr>'
            '<tr><td>Bold</td><td><strong>Pass</strong></td></tr></table>'
            '</ac:layout-cell></ac:layout-section></ac:layout>'
        ))

        self.assertIn("## Wrapped heading", markdown)
        self.assertIn("- First item", markdown)
        self.assertIn("| Format | Result |", markdown)

    def test_decision_list_removes_ids_and_keeps_status_icon(self) -> None:
        markdown = page_to_markdown(_page(
            '<ac:decision-list><ac:decision><ac:decision-id>778f191b</ac:decision-id>'
            '<ac:decision-status>DECIDED</ac:decision-status><ac:decision-body>Use this.</ac:decision-body></ac:decision>'
            '<ac:decision><ac:decision-id>153a0472</ac:decision-id>'
            '<ac:decision-status>UNDECIDED</ac:decision-status><ac:decision-body>Decide later.</ac:decision-body></ac:decision></ac:decision-list>'
        ))

        self.assertIn('<span class="decision-icon">✓</span>', markdown)
        self.assertIn('<span class="decision-icon">□</span>', markdown)
        self.assertIn("Use this.", markdown)
        self.assertIn("Decide later.", markdown)
        self.assertNotIn("778f191b", markdown)
        self.assertNotIn("153a0472", markdown)


if __name__ == "__main__":
    unittest.main()
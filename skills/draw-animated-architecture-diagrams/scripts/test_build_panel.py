"""Check standalone embedding, hostile closing tags and required page order."""
import json
import re
import tempfile
import unittest
from pathlib import Path

from build_panel import SKILL, build


class BuildPanelTest(unittest.TestCase):
    """Use temporary outputs so validation never edits a delivered diagram."""

    def test_example_and_checker(self):
        """The example must round-trip through the embedded config unchanged."""
        source = SKILL / 'examples/example-config.json'
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'diagram.html'
            self.assertEqual(build(source, output), 3)
            page = output.read_text(encoding='utf-8')
            blob = re.search(r'type="application/json">(.*?)</script>', page, re.S)[1]
            self.assertEqual(json.loads(blob), json.loads(source.read_text(encoding='utf-8')))
            self.assertTrue((output.parent / 'check-panel.js').exists())
            self.assertNotIn('<!--LIVE_CONFIG-->', page)

    def test_text_cannot_close_config_script(self):
        """Treat titles and notes as text even when they contain closing tags."""
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder) / 'input.json', Path(folder) / 'out.html'
            value = '</script><script>alert("x")</script> 中文'
            config = {'title': value, 'subtitle': 'Example', 'sourceNote': 'Teaching example', 'pages': [{'overview': True}]}
            source.write_text(json.dumps(config), encoding='utf-8')
            build(source, output)
            page = output.read_text(encoding='utf-8')
            self.assertNotIn(value, page)
            blob = re.search(r'type="application/json">(.*?)</script>', page, re.S)[1]
            self.assertEqual(json.loads(blob)['title'], value)

    def test_overview_required(self):
        """Reject an input that cannot provide the default overview entry."""
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder) / 'input.json', Path(folder) / 'out.html'
            source.write_text(json.dumps({'title': 'Demo', 'pages': []}), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'overview'):
                build(source, output)
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()

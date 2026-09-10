import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_site import render


class BuildSiteTests(unittest.TestCase):
    def test_generated_page_contains_filters_and_data(self):
        page = render([{"year": "2024", "title": "A DBMS Test", "venue": "SIGMOD", "url": "https://example.com"}])
        self.assertIn('id="search"', page)
        self.assertIn("A DBMS Test", page)
        self.assertIn("All years (1)", page)
        self.assertIn("SIGMOD (1)", page)
        self.assertIn("Showing 1 of", page.replace("${found.length}", "1"))
        self.assertIn("prefers-reduced-motion", page)

    def test_venue_filter_uses_fixed_order_and_includes_zero_counts(self):
        page = render([{"year": "2024", "title": "A DBMS Test", "venue": "SIGMOD", "url": "https://example.com"}])
        self.assertIn("AAAI (0)", page)
        self.assertIn("WWW (0)", page)
        positions = [page.index(f'>{venue} (') for venue in ("AAAI", "ACL", "SIGMOD", "WWW", "Other")]
        self.assertEqual(positions, sorted(positions))

    def test_embedded_json_escapes_script_close(self):
        page = render([{"year": "2024", "title": "</script>", "venue": "Other", "url": "https://example.com"}])
        script_data = page.split("const papers=", 1)[1].split(";", 1)[0]
        self.assertNotIn("</script>", script_data)


if __name__ == "__main__":
    unittest.main()

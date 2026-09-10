import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_dataset import validate


class DatasetValidationTests(unittest.TestCase):
    def test_same_title_in_different_years_is_valid(self):
        papers = [
            {"year": "2021", "title": "A Reused Title", "venue": "SIGMOD", "url": "https://example.com/one"},
            {"year": "2025", "title": "A Reused Title", "venue": "ICDE", "url": "https://example.com/two"},
        ]
        self.assertEqual(validate(papers), [])

    def test_same_title_and_year_is_rejected(self):
        paper = {"year": "2024", "title": "Duplicate", "venue": "SIGMOD", "url": "https://example.com"}
        self.assertTrue(any("duplicate" in error for error in validate([paper, paper])))


if __name__ == "__main__":
    unittest.main()

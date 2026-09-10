import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from paper_utils import deduplicate, normalize_venue, preferred_url, title_key


class PaperUtilsTests(unittest.TestCase):
    def test_title_identity_ignores_punctuation(self):
        self.assertEqual(title_key("SQLancer: Testing DBMSs."), title_key("SQLancer — Testing DBMSs"))

    def test_venue_alias(self):
        self.assertEqual(normalize_venue("Proceedings of the VLDB Endowment"), "VLDB")

    def test_new_venue_aliases_and_removed_venues(self):
        self.assertEqual(normalize_venue("Advances in Neural Information Processing Systems"), "NeurIPS")
        self.assertEqual(normalize_venue("The VLDB Journal"), "VLDBJ")
        self.assertEqual(normalize_venue("Network and Distributed System Security Symposium"), "Other")
        self.assertEqual(normalize_venue("Transactions of the Association for Computational Linguistics"), "Other")

    def test_doi_wins_url_selection(self):
        self.assertEqual(preferred_url({"doi": "10.1/example", "url": "https://arxiv.org/abs/1"}), "https://doi.org/10.1/example")

    def test_deduplicates_title_variants(self):
        records = [
            {"title": "Testing Database Systems.", "year": "2022", "venue": "Other", "url": "https://example.com/a"},
            {"title": "Testing Database Systems", "year": "2022", "venue": "SIGMOD", "url": "https://example.com/b"},
        ]
        result = deduplicate(records)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["venue"], "SIGMOD")

    def test_merges_arxiv_and_published_title_variants(self):
        records = [
            {"title": "SQLaser: Detecting DBMS Logic Bugs with Clause-Guided Fuzzing", "year": "2024", "venue": "ArXiv", "url": "https://arxiv.org/abs/1"},
            {"title": "SQLaser: Detecting Database Management System Logic Bugs with Clause-Guided Fuzzing", "year": "2025", "venue": "TSE", "doi": "10.1/sqlaser"},
        ]
        result = deduplicate(records)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["venue"], "TSE")
        self.assertEqual(result[0]["year"], "2025")

    def test_same_title_with_conflicting_publication_identity_is_not_merged(self):
        records = [
            {"title": "A Reused Paper Title", "year": "2021", "venue": "SIGMOD", "doi": "10.1/first"},
            {"title": "A Reused Paper Title", "year": "2025", "venue": "ICDE", "doi": "10.1/second"},
        ]
        self.assertEqual(len(deduplicate(records)), 2)

    def test_publisher_doi_replaces_arxiv_doi(self):
        records = [
            {"title": "Testing DBMS", "abstract": "long " * 100, "year": "2024", "venue": "ArXiv", "doi": "10.48550/arxiv.1"},
            {"title": "Testing DBMS", "year": "2025", "venue": "TSE", "doi": "10.1/published"},
        ]
        paper = deduplicate(records)[0]
        self.assertEqual(paper["doi"], "10.1/published")
        self.assertEqual(paper["url"], "https://doi.org/10.1/published")

    def test_fuzzy_titles_with_conflicting_dois_are_not_merged(self):
        records = [
            {"title": "Testing Database Systems with Generated Queries", "year": "2024", "venue": "SIGMOD", "doi": "10.1/first"},
            {"title": "Testing Database Systems using Generated Queries", "year": "2024", "venue": "SIGMOD", "doi": "10.1/second"},
        ]
        self.assertEqual(len(deduplicate(records)), 2)

    def test_exact_titles_with_conflicting_same_year_dois_are_not_merged(self):
        records = [
            {"title": "Identical Title", "year": "2024", "venue": "SIGMOD", "doi": "10.1/first"},
            {"title": "Identical Title", "year": "2024", "venue": "SIGMOD", "doi": "10.1/second"},
        ]
        self.assertEqual(len(deduplicate(records)), 2)


if __name__ == "__main__":
    unittest.main()

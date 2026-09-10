import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from relevance import assess


class RelevanceTests(unittest.TestCase):
    def test_accepts_dbms_fuzzing(self):
        result = assess({"title": "Finding Logic Bugs in Database Systems via SQL Fuzzing"})
        self.assertTrue(result["relevant"])
        self.assertEqual(result["confidence"], "high")

    def test_accepts_combined_method_and_context(self):
        result = assess({"title": "Metamorphic Testing of Query Engines"})
        self.assertTrue(result["relevant"])

    def test_rejects_compiler_fuzzing(self):
        result = assess({"title": "Differential Testing of LLVM Compilers"})
        self.assertFalse(result["relevant"])

    def test_rejects_smart_contracts(self):
        result = assess({"title": "Transaction Fuzzing for Smart Contracts", "abstract": "A differential testing oracle."})
        self.assertFalse(result["relevant"])

    def test_rejects_dataframe_system_under_test(self):
        result = assess({"title": "Detecting Bugs in DataFrame Systems via Transferred DBMS Test Cases"})
        self.assertFalse(result["relevant"])

    def test_allows_machine_learning_as_testing_technique(self):
        result = assess({"title": "Query Generation for Database Testing Via Machine Learning"})
        self.assertTrue(result["relevant"])


if __name__ == "__main__":
    unittest.main()

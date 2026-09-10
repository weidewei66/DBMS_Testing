import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from config import CANONICAL_VENUES, VENUE_ORDER


class ConfigTests(unittest.TestCase):
    def test_venue_order_matches_reference_project(self):
        self.assertEqual(
            VENUE_ORDER,
            (
                "AAAI", "ACL", "ASE", "ArXiv", "CVPR", "FSE", "ICCV", "ICDE",
                "ICML", "ICSE", "IJCAI", "ISSTA", "KDD", "NeurIPS", "SIGIR",
                "SIGMOD", "TKDE", "TOSEM", "TSE", "VLDB", "VLDBJ", "WWW",
            ),
        )
        self.assertEqual(CANONICAL_VENUES, VENUE_ORDER + ("Other",))
        self.assertNotIn("NDSS", CANONICAL_VENUES)


if __name__ == "__main__":
    unittest.main()

"""Project configuration for DBMS Testing paper collection."""

from datetime import datetime, timezone

START_YEAR = 2020
CURRENT_YEAR = datetime.now(timezone.utc).year

# DBLP stream keys. Conference XML is discovered from each stream index so
# colocated workshops are not silently mistaken for the main venue.
CONFERENCES = {
    "AAAI": "aaai",
    "ACL": "acl",
    "ASE": "kbse",
    "CVPR": "cvpr",
    "FSE": "sigsoft",
    "ICCV": "iccv",
    "ICDE": "icde",
    "ICML": "icml",
    "ICSE": "icse",
    "IJCAI": "ijcai",
    "ISSTA": "issta",
    "KDD": "kdd",
    "NeurIPS": "nips",
    "SIGIR": "sigir",
    "SIGMOD": "sigmod",
    "VLDB": "vldb",
    "WWW": "www",
}

JOURNALS = {
    "TKDE": "IEEE Transactions on Knowledge and Data Engineering",
    "VLDBJ": "The VLDB Journal",
    "TSE": "IEEE Transactions on Software Engineering",
    "TOSEM": "ACM Transactions on Software Engineering and Methodology",
}

JOURNAL_KEYS = {
    "TKDE": ("tkde", -1988),
    "VLDBJ": ("vldb", -1991),
    "TSE": ("tse", -1974),
    "TOSEM": ("tosem", -1991),
}

VENUE_ORDER = (
    "AAAI",
    "ACL",
    "ASE",
    "ArXiv",
    "CVPR",
    "FSE",
    "ICCV",
    "ICDE",
    "ICML",
    "ICSE",
    "IJCAI",
    "ISSTA",
    "KDD",
    "NeurIPS",
    "SIGIR",
    "SIGMOD",
    "TKDE",
    "TOSEM",
    "TSE",
    "VLDB",
    "VLDBJ",
    "WWW",
)

CANONICAL_VENUES = VENUE_ORDER + ("Other",)

VENUE_ALIASES = {
    "aaai conference on artificial intelligence": "AAAI",
    "association for the advancement of artificial intelligence": "AAAI",
    "annual meeting of the association for computational linguistics": "ACL",
    "computer vision and pattern recognition": "CVPR",
    "international conference on computer vision": "ICCV",
    "international conference on machine learning": "ICML",
    "international joint conference on artificial intelligence": "IJCAI",
    "knowledge discovery and data mining": "KDD",
    "neural information processing systems": "NeurIPS",
    "advances in neural information processing systems": "NeurIPS",
    "international acm sigir conference": "SIGIR",
    "special interest group on information retrieval": "SIGIR",
    "the web conference": "WWW",
    "world wide web conference": "WWW",
    "proceedings of the acm on management of data": "SIGMOD",
    "acm sigmod": "SIGMOD",
    "international conference on management of data": "SIGMOD",
    "sigmod": "SIGMOD",
    "proceedings of the vldb endowment": "VLDB",
    "very large data bases": "VLDB",
    "vldb": "VLDB",
    "international conference on data engineering": "ICDE",
    "icde": "ICDE",
    "international conference on software engineering": "ICSE",
    "icse": "ICSE",
    "foundations of software engineering": "FSE",
    "joint meeting on european software engineering conference": "FSE",
    "automated software engineering": "ASE",
    "international symposium on software testing and analysis": "ISSTA",
    "ieee transactions on knowledge and data engineering": "TKDE",
    "the vldb journal": "VLDBJ",
    "ieee transactions on software engineering": "TSE",
    "acm transactions on software engineering and methodology": "TOSEM",
    "nips": "NeurIPS",
    "arxiv": "ArXiv",
}

OPENALEX_QUERIES = (
    '"database testing"',
    '"DBMS testing"',
    '"SQL fuzzing"',
    '"database fuzzing"',
    '"query optimizer" testing',
    '"database system" "differential testing"',
    '"database system" "metamorphic testing"',
    'DBMS fuzzer',
    'SQL logic bug',
    'transaction bug database testing',
)

ARXIV_QUERIES = OPENALEX_QUERIES

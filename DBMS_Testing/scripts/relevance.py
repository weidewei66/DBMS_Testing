"""Explainable DBMS Testing relevance rules."""

import re

STRONG = {
    "database-testing": r"\bdatabase testing\b",
    "dbms-testing": r"\b(?:dbms|database(?: management)? system)s?\b.{0,35}\b(?:test|testing|fuzz|fuzzer|bug)",
    "sql-fuzzing": r"\bsql\b.{0,24}\b(?:fuzz|fuzzer|testing|test generation)",
    "optimizer-testing": r"\bquery optimi[sz]er\b.{0,40}\b(?:test|validation|bug|fuzz)",
    "db-fuzzer": r"\b(?:database|dbms|sql)\s+(?:system\s+)?fuzz(?:er|ing)?\b",
}

METHODS = {
    "fuzzing": r"\bfuzz(?:er|ing|ed)?\b",
    "differential-testing": r"\bdifferential (?:test|testing)\b",
    "metamorphic-testing": r"\bmetamorphic (?:test|testing)\b",
    "test-oracle": r"\b(?:test oracle|oracle construction|oracle-based|metamorphic oracle)\b",
    "query-partitioning": r"\bquery partitioning\b",
    "bug-finding": r"\b(?:bug|fault|defect)(?:s)? (?:finding|detection|discovery)\b|\b(?:find|finding|detect|detecting|discover|discovering)(?:\s+\w+){0,3}\s+(?:bug|fault|defect)s?\b",
    "validation": r"\b(?:test|testing|validation|verification)\b",
}

CONTEXT = {
    "dbms": r"\b(?:dbms|database management system)s?\b",
    "sql": r"\bsql\b",
    "database-system": r"\bdatabase system(?:s)?\b",
    "query-engine": r"\b(?:query|execution|storage) engines?\b",
    "query-optimizer": r"\bquery optimi[sz]er\b",
    "transaction": r"\b(?:database )?transaction(?:s)?\b",
    "relational": r"\brelational database(?:s)?\b",
    "graph-dbms": r"\b(?:graph database|gdbms)\b",
}

EXCLUSIONS = {
    "smart-contract": r"\b(?:smart contract|blockchain|ethereum|dapp)s?\b",
    "ml-system": r"\b(?:testing|fuzzing|validation) (?:of |for )?(?:deep learning|machine learning|neural network|image caption)(?: system| model)?s?\b|\b(?:deep learning|machine learning|neural network|image caption)(?: system| model)?s?\b.{0,24}\b(?:testing|fuzzing|validation)\b",
    "web-application": r"\b(?:web application|browser|frontend)\b",
    "compiler-only": r"\b(?:compiler|jvm|wasm|llvm)\b",
    "data-quality": r"\b(?:data quality|data cleaning|missing data)\b",
    "non-paper-entry": r"\b(?:workshop on testing|international workshop on testing)\b",
    "byzantine-fault": r"\bbyzantine fault\b",
    "application-system-test": r"\b(?:automated system test generation|IT testing)\b",
    "software-development": r"\bcomputer software development\b",
    "dataframe-system": r"\b(?:test|testing|detecting bugs in|fuzzing)\b.{0,40}\bdataframe systems?\b",
}


def matches(patterns, text):
    return [name for name, pattern in patterns.items() if re.search(pattern, text, re.I | re.S)]


def assess(record):
    title = str(record.get("title") or "")
    abstract = str(record.get("abstract") or "")
    text = f"{title}. {abstract}"
    title_strong = matches(STRONG, title)
    title_methods = matches(METHODS, title)
    title_context = matches(CONTEXT, title)
    strong = matches(STRONG, text)
    methods = matches(METHODS, text)
    context = matches(CONTEXT, text)
    exclusions = matches(EXCLUSIONS, text)
    decisive_title_methods = [item for item in title_methods if item != "validation"]
    title_evidence = bool(title_strong or (decisive_title_methods and title_context))
    body_evidence = bool(strong or (methods and context))
    score = 6 * len(title_strong) + 3 * len(title_methods) + 3 * len(title_context) + len(methods) + len(context) - 5 * len(exclusions)
    relevant = body_evidence and not exclusions
    confidence = "high" if relevant and title_evidence else "medium" if relevant else "low"
    return {
        "relevant": relevant,
        "confidence": confidence,
        "score": score,
        "matches": {
            "title_strong": title_strong,
            "title_methods": title_methods,
            "title_context": title_context,
            "strong": strong,
            "methods": methods,
            "context": context,
            "exclusions": exclusions,
        },
    }

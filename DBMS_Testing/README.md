# DBMS Testing Paper Summary

An automatically maintained paper index for research on testing database management systems. It collects venue records from DBLP and preprints from arXiv, then uses OpenAlex to enrich matching records with abstracts and identifiers. It applies explainable relevance rules, cleans and deduplicates metadata, validates the result, and builds a static paper-style website.

## Website

The generated site is in [`web/index.html`](web/index.html). It displays only year, linked title, and venue, with title search plus year and venue filters.

The venue filter follows the reference project's fixed order: AAAI, ACL, ASE, ArXiv, CVPR, FSE, ICCV, ICDE, ICML, ICSE, IJCAI, ISSTA, KDD, NeurIPS, SIGIR, SIGMOD, TKDE, TOSEM, TSE, VLDB, VLDBJ, and WWW. Relevant papers from other sources are grouped under `Other`; all counts are regenerated from the current dataset on every build, including zero-count venues.

## Current snapshot

<!-- snapshot:start -->
| Year | Papers |
| --- | ---: |
| 2020 | 1 |
| 2021 | 1 |
| 2022 | 4 |
| 2023 | 6 |
| 2024 | 5 |
| 2025 | 15 |
| 2026 | 15 |
| **Total** | **47** |
<!-- snapshot:end -->

## Pipeline

```bash
python scripts/fetch_papers.py --from-year 2020
python scripts/process_papers.py
python scripts/validate_dataset.py
python scripts/update_readme.py
python scripts/build_site.py
python -m unittest discover -s tests -v
```

The fetcher uses only Python's standard library. Set `OPENALEX_EMAIL` to identify automated OpenAlex requests and receive polite-pool service. Bounded source caches remain in `data/raw/`; the internally auditable collection is `data/curated/canonical.json`; the public projection is `data/curated/papers.json`; borderline and rejected candidates are recorded in `data/reports/relevance-audit.json`.

## Relevance policy

A paper qualifies when it contains an unambiguous DBMS-testing phrase, or when it combines a testing method (for example fuzzing, differential testing, metamorphic testing, or a test oracle) with DBMS context. Explicit exclusions prevent similarly worded work about compilers, smart contracts, ML systems, Web applications, and data cleaning from entering the public index.

The rule definitions and their explanations live in [`scripts/relevance.py`](scripts/relevance.py). No LLM or paid API is required.

## Automation

The GitHub Actions workflow runs daily at 01:00 Asia/Shanghai and may also be started manually. A scheduled run refreshes candidates, validates that the collection has not been corrupted or unexpectedly truncated, rebuilds the static site, commits legitimate data changes, and deploys `web/` to GitHub Pages.

Optional repository variable:

```text
OPENALEX_EMAIL
```

## Disclaimer

This is a navigation aid maintained by automated collection and rule-based screening. Coverage and classification can be imperfect. Review `data/reports/relevance-audit.json` when tuning rules or investigating a missing paper.


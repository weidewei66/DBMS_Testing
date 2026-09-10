#!/usr/bin/env python3
"""Fail closed when curated data is malformed or unexpectedly truncated."""

import argparse
import json
from collections import Counter
from pathlib import Path

from config import CANONICAL_VENUES, CURRENT_YEAR, START_YEAR
from paper_utils import title_key, valid_url

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "curated" / "papers.json"
CANONICAL = ROOT / "data" / "curated" / "canonical.json"
SITE = ROOT / "web" / "index.html"


def validate(papers):
    errors, seen = [], set()
    for index, paper in enumerate(papers):
        missing = {key for key in ("year", "title", "venue", "url") if not paper.get(key)}
        if missing:
            errors.append(f"record {index}: missing {sorted(missing)}")
        year = int(paper.get("year") or 0)
        if not START_YEAR <= year <= CURRENT_YEAR:
            errors.append(f"record {index}: invalid year {year}")
        if paper.get("venue") not in CANONICAL_VENUES:
            errors.append(f"record {index}: invalid venue {paper.get('venue')}")
        if not valid_url(paper.get("url")):
            errors.append(f"record {index}: invalid URL")
        key = (str(paper.get("year")), title_key(paper.get("title")))
        if key in seen:
            errors.append(f"record {index}: duplicate title {paper.get('title')}")
        seen.add(key)
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline")
    parser.add_argument("--max-drop", type=float, default=0.35)
    args = parser.parse_args()
    papers = json.loads(DATA.read_text(encoding="utf-8"))
    errors = validate(papers)
    canonical = json.loads(CANONICAL.read_text(encoding="utf-8"))
    if len(canonical) != len(papers):
        errors.append(f"canonical/public count mismatch: {len(canonical)} != {len(papers)}")
    for index, record in enumerate(canonical):
        for field in ("title", "year", "venue", "url", "sources", "relevance"):
            if field not in record:
                errors.append(f"canonical record {index}: missing {field}")
    if SITE.exists():
        site = SITE.read_text(encoding="utf-8")
        marker = f'<strong>{len(papers)}</strong>papers on file'
        if marker not in site.replace("\n", ""):
            errors.append("generated HTML count does not match public dataset")
    if args.baseline and Path(args.baseline).exists():
        old = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
        if old and len(papers) < len(old) * (1 - args.max_drop):
            errors.append(f"paper count dropped from {len(old)} to {len(papers)}")
        old_ids = {title_key(paper.get("title")) for paper in old}
        new_ids = {title_key(paper.get("title")) for paper in papers}
        retained = len(old_ids & new_ids) / len(old_ids) if old_ids else 1.0
        if retained < 0.65:
            errors.append(f"only {retained:.1%} of baseline paper identities were retained")
        old_years, new_years = Counter(paper.get("year") for paper in old), Counter(paper.get("year") for paper in papers)
        for year, count in old_years.items():
            if count >= 3 and new_years[year] < count * 0.5:
                errors.append(f"year {year} dropped from {count} to {new_years[year]}")
        old_other = sum(paper.get("venue") == "Other" for paper in old) / len(old) if old else 0
        new_other = sum(paper.get("venue") == "Other" for paper in papers) / len(papers) if papers else 0
        if abs(new_other - old_other) > 0.20:
            errors.append(f"Other venue share shifted from {old_other:.1%} to {new_other:.1%}")
    if errors:
        raise SystemExit("dataset validation failed:\n- " + "\n- ".join(errors))
    print(f"validated {len(papers)} papers")


if __name__ == "__main__":
    main()

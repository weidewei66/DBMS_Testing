#!/usr/bin/env python3
"""Normalize, deduplicate, screen, and publish paper records."""

import json
from pathlib import Path

from config import CURRENT_YEAR, START_YEAR
from paper_utils import deduplicate, merge_records, normalize_doi, title_key, valid_url
from relevance import assess

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SEED_DIR = ROOT / "data" / "seed"
CURATED = ROOT / "data" / "curated" / "papers.json"
CANONICAL = ROOT / "data" / "curated" / "canonical.json"
AUDIT = ROOT / "data" / "reports" / "relevance-audit.json"


def load_records():
    records, enrichment = [], []
    paths = [path for path in sorted(RAW.glob("*.json")) if path.name != "openalex.json"]
    paths = sorted(SEED_DIR.glob("*.json")) + paths
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        records.extend(payload.values() if isinstance(payload, dict) else payload)
    openalex = RAW / "openalex.json"
    if openalex.exists():
        payload = json.loads(openalex.read_text(encoding="utf-8"))
        enrichment.extend(payload.values() if isinstance(payload, dict) else payload)
    by_doi = {normalize_doi(item.get("doi")): item for item in enrichment if normalize_doi(item.get("doi"))}
    title_groups = {}
    for item in enrichment:
        key = (str(item.get("year") or ""), title_key(item.get("title")))
        if key[1]:
            title_groups.setdefault(key, []).append(item)
    by_title = {}
    for key, items in title_groups.items():
        dois = {normalize_doi(item.get("doi")) for item in items if normalize_doi(item.get("doi"))}
        if len(dois) <= 1:
            by_title[key] = items[0]
    enriched = []
    for record in records:
        match = by_doi.get(normalize_doi(record.get("doi"))) or by_title.get(
            (str(record.get("year") or ""), title_key(record.get("title")))
        )
        enriched.append(merge_records(record, match) if match else record)
    return enriched


def main():
    assessed, canonical, published, withheld = [], [], [], []
    for record in deduplicate(load_records()):
        decision = assess(record)
        item = {**record, "relevance": decision}
        assessed.append(item)
        year = int(record.get("year") or 0)
        complete = START_YEAR <= year <= CURRENT_YEAR and record.get("title") and record.get("venue") and valid_url(record.get("url"))
        if decision["relevant"] and decision["confidence"] == "high" and complete:
            canonical.append(item)
            published.append({key: record[key] for key in ("year", "title", "venue", "url")})
        else:
            withheld.append(item)
    published.sort(key=lambda paper: (-int(paper["year"]), paper["title"].casefold()))
    canonical.sort(key=lambda paper: (-int(paper["year"]), paper["title"].casefold()))
    CURATED.parent.mkdir(parents=True, exist_ok=True)
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    CURATED.write_text(json.dumps(published, indent=2, ensure_ascii=False), encoding="utf-8")
    CANONICAL.write_text(json.dumps(canonical, indent=2, ensure_ascii=False), encoding="utf-8")
    AUDIT.write_text(json.dumps({"summary": {"candidates": len(assessed), "published": len(published), "withheld": len(withheld)}, "withheld": withheld}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"candidates={len(assessed)} published={len(published)} withheld={len(withheld)}")


if __name__ == "__main__":
    main()

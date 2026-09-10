#!/usr/bin/env python3
"""Fetch broad DBMS Testing candidates from OpenAlex and arXiv."""

import argparse
import json
import os
import re
import tempfile
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from config import ARXIV_QUERIES, CONFERENCES, CURRENT_YEAR, JOURNAL_KEYS, OPENALEX_QUERIES, START_YEAR
from paper_utils import clean_text

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def request(url, params=None, attempts=3):
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    headers = {"User-Agent": "DBMS-Testing-Paper-Summary/1.0 (academic index; GitHub Actions)"}
    last = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=45) as response:
                return response.read()
        except Exception as exc:
            last = exc
            time.sleep(2 ** attempt)
    safe_url = urllib.parse.urlsplit(url)._replace(query="").geturl()
    raise RuntimeError(f"request failed after {attempts} attempts: {safe_url}: {last}")


def abstract_from_index(index):
    words = []
    for word, positions in (index or {}).items():
        words.extend((position, word) for position in positions)
    return clean_text(" ".join(word for _, word in sorted(words)))


def openalex_record(work):
    location = work.get("primary_location") or {}
    source = location.get("source") or {}
    doi = work.get("doi") or ""
    return {
        "title": work.get("title") or work.get("display_name") or "",
        "abstract": abstract_from_index(work.get("abstract_inverted_index")),
        "year": str(work.get("publication_year") or ""),
        "venue": source.get("display_name") or "Other",
        "doi": doi,
        "url": doi or location.get("landing_page_url") or work.get("id") or "",
        "openalex_id": work.get("id") or "",
        "source": "OpenAlex",
    }


def fetch_openalex(query, from_year, to_year, per_query, polite_email=""):
    params = {
        "search": query,
        "filter": f"from_publication_date:{from_year}-01-01,to_publication_date:{to_year}-12-31",
        "per-page": str(min(per_query, 200)),
        "sort": "publication_date:desc",
        "select": "id,doi,title,display_name,publication_year,primary_location,abstract_inverted_index",
    }
    if polite_email:
        params["mailto"] = polite_email
    payload = json.loads(request("https://api.openalex.org/works", params).decode("utf-8"))
    return [openalex_record(work) for work in payload.get("results", [])]


def fetch_arxiv(query, max_results):
    params = {
        "search_query": "all:" + query,
        "start": "0",
        "max_results": str(max_results),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    root = ET.fromstring(request("https://export.arxiv.org/api/query", params).decode("utf-8"))
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    records = []
    for item in root.findall("atom:entry", ns):
        identifier = clean_text(item.findtext("atom:id", "", ns))
        published = clean_text(item.findtext("atom:published", "", ns))
        records.append({
            "title": clean_text(item.findtext("atom:title", "", ns)),
            "abstract": clean_text(item.findtext("atom:summary", "", ns)),
            "year": published[:4],
            "venue": "ArXiv",
            "url": identifier,
            "arxiv_id": identifier.rsplit("/", 1)[-1],
            "source": "arXiv",
        })
    return records


def fetch_dblp_venue(venue, key, year, journal_offset=None):
    if journal_offset is None:
        base = f"https://dblp.org/db/conf/{key}/"
        slug = re.sub(r"[^a-z0-9]+", "", venue.casefold())
        urls = [f"{base}{key}{year}.xml", f"{base}{slug}{year}.xml"]
        try:
            index = request(base + "index.html").decode("utf-8")
            for href in re.findall(r'href="([^"]+\.html)"', index, re.I):
                if str(year) in href:
                    urls.append(urllib.parse.urljoin(base, href[:-5] + ".xml"))
        except Exception:
            pass
    else:
        urls = [f"https://dblp.org/db/journals/{key}/{key}{year + journal_offset}.xml"]
    records = []
    errors = []
    for url in dict.fromkeys(urls):
        try:
            root = ET.fromstring(request(url).decode("utf-8"))
        except Exception as exc:
            errors.append(str(exc))
            continue
        for node in root.iter():
            if node.tag not in {"inproceedings", "article"}:
                continue
            node_year = clean_text(node.findtext("year") or year)
            if node_year != str(year):
                continue
            title_node = node.find("title")
            title = clean_text("".join(title_node.itertext()) if title_node is not None else "")
            if not title:
                continue
            ee = clean_text(node.findtext("ee"))
            doi = clean_text(node.findtext("doi"))
            records.append({
                "title": title,
                "abstract": "",
                "year": node_year,
                "venue": venue,
                "booktitle": clean_text(node.findtext("booktitle")) or venue,
                "doi": doi,
                "url": ee or (f"https://doi.org/{doi}" if doi else ""),
                "source": "DBLP",
                "dblp_key": node.attrib.get("key", ""),
            })
        if records:
            break
    if not records:
        raise RuntimeError(f"empty DBLP result for {venue} {year}: {'; '.join(errors[-2:])}")
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-year", type=int, default=START_YEAR)
    parser.add_argument("--to-year", type=int, default=CURRENT_YEAR)
    parser.add_argument("--per-query", type=int, default=100)
    parser.add_argument("--arxiv-results", type=int, default=50)
    parser.add_argument("--sleep", type=float, default=0.5)
    parser.add_argument("--source", choices=("all", "dblp", "openalex", "arxiv"), default="all")
    args = parser.parse_args()
    if args.from_year < START_YEAR or args.to_year < args.from_year:
        parser.error("invalid year range")

    RAW.mkdir(parents=True, exist_ok=True)
    records_by_source, failures = {"OpenAlex": [], "arXiv": []}, []
    statuses = []
    if args.source in {"all", "dblp"}:
        dblp_units = [(venue, key, None) for venue, key in CONFERENCES.items()]
        dblp_units.extend((venue, spec[0], spec[1]) for venue, spec in JOURNAL_KEYS.items())
        for venue, key, journal_offset in dblp_units:
            for year in range(args.from_year, args.to_year + 1):
                slug = re.sub(r"[^a-z0-9]+", "-", venue.casefold()).strip("-")
                output = RAW / f"dblp-{slug}-{year}.json"
                try:
                    fresh = fetch_dblp_venue(venue, key, year, journal_offset)
                except Exception as exc:
                    failures.append({"source": "DBLP", "unit": venue, "year": year, "error": str(exc)})
                    statuses.append({"source": "DBLP", "unit": venue, "year": year, "status": "stale-cache-retained" if output.exists() else "unavailable"})
                    time.sleep(args.sleep)
                    continue
                time.sleep(args.sleep)
                with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=RAW, delete=False, suffix=".tmp") as handle:
                    json.dump(fresh, handle, indent=2, ensure_ascii=False)
                    temporary = Path(handle.name)
                os.replace(temporary, output)
                statuses.append({"source": "DBLP", "unit": venue, "year": year, "status": "refreshed", "records": len(fresh)})
    email = os.environ.get("OPENALEX_EMAIL", "")
    if args.source in {"all", "openalex"}:
        for query in OPENALEX_QUERIES:
            try:
                records_by_source["OpenAlex"].extend(fetch_openalex(query, args.from_year, args.to_year, args.per_query, email))
            except Exception as exc:
                failures.append({"source": "OpenAlex", "query": query, "error": str(exc)})
            time.sleep(args.sleep)
    if args.source in {"all", "arxiv"}:
        for query in ARXIV_QUERIES:
            try:
                records_by_source["arXiv"].extend(fetch_arxiv(query, args.arxiv_results))
            except Exception as exc:
                failures.append({"source": "arXiv", "query": query, "error": str(exc)})
            time.sleep(max(args.sleep, 1.0))

    for source, fresh in records_by_source.items():
        if args.source not in {"all", source.casefold()}:
            continue
        output = RAW / f"{source.casefold()}.json"
        source_failures = [item for item in failures if item["source"] == source]
        fresh = [record for record in fresh if args.from_year <= int(record.get("year") or 0) <= args.to_year]
        if source_failures:
            statuses.append({"source": source, "status": "stale-cache-retained" if output.exists() else "unavailable", "failures": len(source_failures)})
            continue
        old = json.loads(output.read_text(encoding="utf-8")) if output.exists() else []
        retained = [record for record in old if not args.from_year <= int(record.get("year") or 0) <= args.to_year]
        combined = retained + fresh
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=RAW, delete=False, suffix=".tmp") as handle:
            json.dump(combined, handle, indent=2, ensure_ascii=False)
            temporary = Path(handle.name)
        os.replace(temporary, output)
        statuses.append({"source": source, "status": "refreshed", "records": len(fresh), "cache_records": len(combined)})
    report = ROOT / "data" / "reports" / "fetch.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps({"range": [args.from_year, args.to_year], "sources": statuses, "failures": failures}, indent=2), encoding="utf-8")
    available = any(RAW.glob("*.json"))
    print(f"sources={statuses}; failures={len(failures)}")
    if not available:
        raise SystemExit("no source cache available; preserving existing curated data")


if __name__ == "__main__":
    main()

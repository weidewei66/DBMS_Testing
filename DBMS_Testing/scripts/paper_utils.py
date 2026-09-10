"""Normalization and conservative record merging."""

import html
import re
import unicodedata
from difflib import SequenceMatcher
from urllib.parse import urlparse

from config import CANONICAL_VENUES, VENUE_ALIASES


def clean_text(value):
    value = html.unescape(str(value or ""))
    value = unicodedata.normalize("NFKC", value)
    return re.sub(r"\s+", " ", value).strip()


def clean_title(value):
    return clean_text(value).rstrip(".")


def title_key(value):
    value = clean_title(value).casefold()
    return re.sub(r"[^a-z0-9]+", "", value)


def comparison_title(value):
    value = clean_title(value).casefold()
    value = re.sub(r"database management systems?\s*\(dbmss?\)", "database management system", value)
    value = re.sub(r"\bdbmss?\b", "database management systems", value)
    value = value.replace("database management systems", "database management system")
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def normalize_doi(value):
    value = clean_text(value).casefold()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value)
    return value.removeprefix("doi:").strip()


def is_arxiv_doi(value):
    return normalize_doi(value).startswith("10.48550/arxiv.")


def normalize_venue(value, url=""):
    raw = clean_text(value)
    if raw in CANONICAL_VENUES:
        return raw
    text = raw.casefold()
    if "arxiv.org" in str(url).casefold() or "arxiv" in text:
        return "ArXiv"
    for alias, venue in sorted(VENUE_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if alias in text:
            return venue
    return "Other"


def valid_url(value):
    parsed = urlparse(str(value or ""))
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def preferred_url(record):
    doi = normalize_doi(record.get("doi"))
    if doi:
        return f"https://doi.org/{doi}"
    candidates = record.get("urls") or [record.get("url", "")]
    candidates = [clean_text(url) for url in candidates if valid_url(url)]
    if not candidates:
        return ""
    priorities = ("dl.acm.org", "ieeexplore.ieee.org", "usenix.org", "ndss-symposium.org", "dblp.org", "arxiv.org")
    return sorted(candidates, key=lambda url: next((i for i, domain in enumerate(priorities) if domain in url), 99))[0]


def normalize_record(record):
    out = dict(record)
    out["title"] = clean_title(out.get("title"))
    out["abstract"] = clean_text(out.get("abstract"))
    out["year"] = str(out.get("year") or "")[:4]
    out["doi"] = normalize_doi(out.get("doi"))
    out["venue"] = normalize_venue(out.get("venue") or out.get("booktitle") or out.get("journal"), out.get("url"))
    out["url"] = preferred_url(out)
    out["sources"] = sorted(set(out.get("sources") or ([out.get("source")] if out.get("source") else [])))
    return out


def identity_keys(record):
    keys = []
    if record.get("doi"):
        keys.append("doi:" + normalize_doi(record["doi"]))
    if record.get("arxiv_id"):
        keys.append("arxiv:" + clean_text(record["arxiv_id"]).casefold())
    if record.get("title"):
        keys.append("title:" + title_key(record["title"]))
    return keys


def merge_records(first, second):
    first, second = normalize_record(first), normalize_record(second)
    primary, secondary = (first, second) if len(first.get("abstract", "")) >= len(second.get("abstract", "")) else (second, first)
    merged = dict(primary)
    for key, value in secondary.items():
        if not merged.get(key) and value:
            merged[key] = value
    merged["sources"] = sorted(set(first.get("sources", [])) | set(second.get("sources", [])))
    rank = lambda venue: 3 if venue not in {"Other", "ArXiv"} else 2 if venue == "ArXiv" else 1
    if rank(first["venue"]) == rank(second["venue"]):
        venue_record = second if second.get("doi") and not first.get("doi") else first
    else:
        venue_record = first if rank(first["venue"]) > rank(second["venue"]) else second
    merged["venue"] = venue_record["venue"]
    if venue_record.get("year"):
        merged["year"] = venue_record["year"]
    dois = [normalize_doi(item.get("doi")) for item in (first, second) if normalize_doi(item.get("doi"))]
    if dois:
        merged["doi"] = next((doi for doi in dois if not is_arxiv_doi(doi)), dois[0])
    merged["url"] = preferred_url({**merged, "urls": [first.get("url", ""), second.get("url", "")]})
    return normalize_record(merged)


def deduplicate(records):
    papers, index = [], {}
    for raw in records:
        record = normalize_record(raw)
        identifier_keys = [key for key in identity_keys(record) if not key.startswith("title:")]
        existing = next((index[key] for key in identifier_keys if key in index), None)
        if existing is None:
            exact_title = "title:" + title_key(record.get("title"))
            candidate = index.get(exact_title)
            if candidate is not None:
                other = papers[candidate]
                left_year, right_year = int(record.get("year") or 0), int(other.get("year") or 0)
                compatible_year = left_year == right_year or abs(left_year - right_year) <= 1 and (
                    "ArXiv" in {record.get("venue"), other.get("venue")} or record.get("venue") == other.get("venue")
                )
                left_doi, right_doi = normalize_doi(record.get("doi")), normalize_doi(other.get("doi"))
                compatible_doi = not (left_doi and right_doi and left_doi != right_doi) or is_arxiv_doi(left_doi) or is_arxiv_doi(right_doi)
                if compatible_year and compatible_doi:
                    existing = candidate
        if existing is None:
            candidate_title = comparison_title(record.get("title"))
            candidate_year = int(record.get("year") or 0)
            for position, paper in enumerate(papers):
                paper_year = int(paper.get("year") or 0)
                compatible_year = candidate_year == paper_year or (
                    abs(candidate_year - paper_year) <= 2 and "ArXiv" in {record.get("venue"), paper.get("venue")}
                )
                left_doi, right_doi = normalize_doi(record.get("doi")), normalize_doi(paper.get("doi"))
                compatible_doi = not (left_doi and right_doi and left_doi != right_doi) or is_arxiv_doi(left_doi) or is_arxiv_doi(right_doi)
                if compatible_year and compatible_doi and SequenceMatcher(None, candidate_title, comparison_title(paper.get("title"))).ratio() >= 0.92:
                    existing = position
                    break
        if existing is None:
            existing = len(papers)
            papers.append(record)
        else:
            papers[existing] = merge_records(papers[existing], record)
        for key in identity_keys(papers[existing]):
            index[key] = existing
    return papers

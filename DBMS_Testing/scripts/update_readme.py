#!/usr/bin/env python3
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
papers = json.loads((ROOT / "data" / "curated" / "papers.json").read_text(encoding="utf-8"))
counts = Counter(paper["year"] for paper in papers)
rows = "\n".join(f"| {year} | {counts[year]} |" for year in sorted(counts))
block = f"<!-- snapshot:start -->\n| Year | Papers |\n| --- | ---: |\n{rows}\n| **Total** | **{len(papers)}** |\n<!-- snapshot:end -->"
path = ROOT / "README.md"
text = path.read_text(encoding="utf-8")
text = re.sub(r"<!-- snapshot:start -->.*?<!-- snapshot:end -->", block, text, flags=re.S)
path.write_text(text, encoding="utf-8")


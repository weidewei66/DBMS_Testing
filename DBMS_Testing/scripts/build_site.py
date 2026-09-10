#!/usr/bin/env python3
"""Build the standalone academic-archive paper browser."""

import html
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from config import VENUE_ORDER

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "curated" / "papers.json"
OUTPUT = ROOT / "web" / "index.html"


def options(values, counts, label, total):
    return f'<option value="">{label} ({total})</option>' + "".join(
        f'<option value="{html.escape(value)}">{html.escape(value)} ({counts[value]})</option>' for value in values
    )


def render(papers):
    years = sorted({paper["year"] for paper in papers}, reverse=True)
    venues = list(VENUE_ORDER) + ["Other"]
    year_counts = Counter(paper["year"] for paper in papers)
    venue_counts = Counter(paper["venue"] for paper in papers)
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    payload = json.dumps(papers, ensure_ascii=False).replace("</", "<\\/")
    return TEMPLATE.replace("__PAPERS__", payload).replace("__TOTAL__", str(len(papers))).replace(
        "__UPDATED__", updated
    ).replace("__YEAR_OPTIONS__", options(years, year_counts, "All years", len(papers))).replace(
        "__VENUE_OPTIONS__", options(venues, venue_counts, "All venues", len(papers))
    )


TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="A curated index of DBMS testing research since 2020.">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='4' fill='%23f4eedf'/%3E%3Cpath d='M14 15h22c10 0 16 6 16 17S46 49 36 49H14zm9 8v18h11c6 0 9-3 9-9s-3-9-9-9z' fill='%23263f55'/%3E%3C/svg%3E">
<title>DBMS Testing Paper Summary</title>
<style>
:root{--paper:#f7f3e8;--paper-deep:#eee7d8;--ink:#24272b;--muted:#70747a;--blue:#214f73;--red:#a44b3e;--rule:rgba(48,52,56,.18);--font:"Segoe UI",Arial,sans-serif}
*{box-sizing:border-box}html{min-height:100%;background:var(--paper);scroll-behavior:smooth}body{min-height:100vh;margin:0;color:var(--ink);font-family:var(--font);font-size:16px;line-height:1.5;background:var(--paper)}
body:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.09;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.7' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.16'/%3E%3C/svg%3E")}
.paper{position:relative;width:100%;min-height:100vh;margin:0;padding:clamp(36px,5vw,72px) clamp(24px,6vw,96px) 80px;background:transparent}
.kicker{font-size:12px;font-weight:600;letter-spacing:.12em;color:var(--red);text-transform:uppercase}.masthead{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:48px;align-items:end;padding-bottom:32px;border-bottom:1px solid var(--ink)}
h1{margin:10px 0 12px;font-size:clamp(38px,5vw,68px);font-weight:650;letter-spacing:-.035em;line-height:1.02}.dek{max-width:760px;margin:0;color:#565b60;font-size:16px}
.folio{text-align:right;font-size:12px;line-height:1.65;color:var(--muted)}.folio strong{display:block;font-size:38px;font-weight:600;line-height:1;color:var(--ink)}
.tools{position:sticky;top:0;z-index:5;display:grid;grid-template-columns:minmax(280px,1fr) minmax(180px,230px) minmax(200px,260px) auto;gap:12px;margin:0 -12px 36px;padding:16px 12px;background:rgba(247,243,232,.96);border-bottom:1px solid var(--rule);backdrop-filter:blur(8px)}
input,select,button{height:44px;border:1px solid rgba(51,55,59,.32);border-radius:4px;background:rgba(255,255,255,.42);color:var(--ink);font:14px var(--font)}input,select{padding:0 13px}input::placeholder{color:#7a7e82}button{padding:0 18px;font-weight:600;cursor:pointer}button:hover,button:focus-visible{background:var(--ink);color:var(--paper)}input:focus-visible,select:focus-visible,button:focus-visible,a:focus-visible{outline:2px solid var(--red);outline-offset:2px}
.results{grid-column:1/-1;font-size:12px;color:var(--muted)}.year{display:grid;grid-template-columns:150px minmax(0,1fr);gap:32px;margin:0 0 44px;animation:rise .45s both}.year-label{position:sticky;top:100px;align-self:start;margin:0;font-size:30px;font-weight:650;line-height:1.15}.year-count{display:block;margin-top:6px;color:var(--muted);font-size:13px;font-weight:400}.year-label:after{content:"";display:block;width:34px;margin-top:12px;border-top:3px solid var(--red)}
.paper-list{border-top:1px solid var(--rule)}.entry{display:grid;grid-template-columns:minmax(0,1fr) 150px;gap:28px;align-items:baseline;padding:15px 4px;border-bottom:1px solid var(--rule)}.title{color:var(--blue);font-size:17px;font-weight:600;line-height:1.38;text-decoration:none;text-underline-offset:3px}.title:hover{text-decoration:underline}.venue{text-align:right;font-size:12px;font-weight:600;color:var(--muted)}
.empty{display:none;padding:80px 10px;text-align:center;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}.empty strong{display:block;font-size:26px;font-weight:600}.empty span{font-size:13px;color:var(--muted)}footer{display:flex;justify-content:space-between;gap:20px;margin-top:72px;padding-top:18px;border-top:1px solid var(--ink);font-size:12px;color:var(--muted)}
@keyframes rise{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
@media(max-width:900px){.paper{padding:34px 20px 60px}.masthead{grid-template-columns:1fr;gap:24px}.folio{text-align:left}.tools{grid-template-columns:1fr 1fr;margin:0 -8px 30px;padding:12px 8px}.tools input{grid-column:1/-1}.tools button{grid-column:1/-1}.year{display:block}.year-label{position:static;margin-bottom:14px}.entry{grid-template-columns:1fr;gap:7px}.venue{text-align:left}.title{font-size:16px}footer{display:block}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.year{animation:none}}
</style>
</head>
<body>
<main class="paper">
  <header class="masthead">
    <div><div class="kicker">Research index · 2020—present</div><h1>DBMS Testing<br>Paper Summary</h1><p class="dek">An automatically maintained catalogue of research that tests database management systems—the engines, optimizers, transactions and semantics beneath the query.</p></div>
    <div class="folio"><strong>__TOTAL__</strong>papers on file<br>revised __UPDATED__</div>
  </header>
  <section class="tools" aria-label="Paper filters">
    <input id="search" type="search" placeholder="Search paper titles…" aria-label="Search paper titles">
    <select id="year" aria-label="Filter by year">__YEAR_OPTIONS__</select>
    <select id="venue" aria-label="Filter by venue">__VENUE_OPTIONS__</select>
    <button id="clear" type="button">Clear</button>
    <div class="results" id="count" aria-live="polite"></div>
  </section>
  <div id="catalogue"></div>
  <div class="empty" id="empty"><strong>No papers found.</strong><span>Try a broader title, year, or venue.</span></div>
  <footer><span>DBMS Testing Paper Summary</span><span>Collected automatically · screened by explicit rules</span></footer>
</main>
<script>
const papers=__PAPERS__;
const els={q:document.querySelector('#search'),year:document.querySelector('#year'),venue:document.querySelector('#venue'),clear:document.querySelector('#clear'),count:document.querySelector('#count'),catalogue:document.querySelector('#catalogue'),empty:document.querySelector('#empty')};
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function render(){const q=els.q.value.trim().toLocaleLowerCase();const found=papers.filter(p=>(!q||p.title.toLocaleLowerCase().includes(q))&&(!els.year.value||p.year===els.year.value)&&(!els.venue.value||p.venue===els.venue.value));const groups=Object.groupBy?Object.groupBy(found,p=>p.year):found.reduce((a,p)=>((a[p.year]??=[]).push(p),a),{});els.catalogue.innerHTML=Object.keys(groups).sort((a,b)=>b-a).map((year,i)=>`<section class="year" style="animation-delay:${Math.min(i*45,240)}ms"><h2 class="year-label">${esc(year)}<span class="year-count">${groups[year].length} ${groups[year].length===1?'paper':'papers'}</span></h2><div class="paper-list">${groups[year].map(p=>`<article class="entry"><a class="title" href="${esc(p.url)}" target="_blank" rel="noopener noreferrer">${esc(p.title)}</a><span class="venue">${esc(p.venue)}</span></article>`).join('')}</div></section>`).join('');els.count.textContent=`Showing ${found.length} of ${papers.length} papers`;els.empty.style.display=found.length?'none':'block'}
[els.q,els.year,els.venue].forEach(el=>el.addEventListener('input',render));els.clear.addEventListener('click',()=>{els.q.value=els.year.value=els.venue.value='';render();els.q.focus()});render();
</script>
</body>
</html>'''


def main():
    papers = json.loads(DATA.read_text(encoding="utf-8"))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render(papers), encoding="utf-8")
    print(f"built {OUTPUT} with {len(papers)} papers")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Canonical content-dashboard builder. THE ONLY thing allowed to write the weekly
blogs/videos/research HTML. The weekly task produces ONLY a data JSON and runs
this; it never hand-writes HTML and never names a template path or version.

Why this exists: the dashboards used to be free-written as raw HTML by an LLM
every week, which drifted to stale layouts and shipped broken buttons
(onclick="cp("...")" quote collisions). Here, the LLM writes DATA, Jinja2
(autoescape ON) renders MARKUP, copy prompts live in a JSON map keyed by id
(never in an HTML attribute), and a fail-closed validator blocks any broken or
stale output from being published.

Usage:
    python build_content_dashboard.py --input data/weekly-topics/2026-06-29.json --out <dist_dir>

Exit 0 = three valid pages written. Exit 1 = nothing written / validation failed.
"""
import argparse, hashlib, json, re, sys, datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from jinja2 import Environment, FileSystemLoader, select_autoescape

REPO = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO / "templates" / "content_dashboard"
TEMPLATE_NAME = "dashboard.html.j2"
TEMPLATE_ID = "gw-content-dashboard"
TEMPLATE_VERSION = "1.0.0"
SCHEMA = "weekly-topics.v1"
DRE = "01466876"
BLOCKED_DRE = "02015066"
STAGES = ["BOFU", "MOFU", "TOFU"]

# Raw-telemetry vocabulary that must never appear in human-facing copy (title/humanWhy).
TELEMETRY = re.compile(
    r"\b(GSC|Search Console|GA4|WoW|CTR|SERP|impr/7d|impr\b|impressions|"
    r"position\s+\d+(\.\d+)?|r/[A-Za-z0-9_]+|\d+\s+comments?)\b", re.I)


class BuildError(Exception):
    pass


def fail(msg):
    raise BuildError(msg)


def validate_data(d):
    """Schema + content gates on the DATA, before any rendering."""
    if not isinstance(d, dict) or "topics" not in d or "week" not in d:
        fail("data must be an object with 'week' and 'topics'")
    week = d["week"]
    for k in ("label", "monday"):
        if not week.get(k):
            fail(f"week.{k} required")
    topics = d["topics"]
    if len(topics) != 21:
        fail(f"expected exactly 21 topics, got {len(topics)}")
    seen = set()
    for i, t in enumerate(topics):
        where = f"topic[{i}] ({t.get('id','?')})"
        for k in ("id", "stage", "title", "humanWhy", "internalSignal", "day", "scores"):
            if not t.get(k):
                fail(f"{where}: missing '{k}'")
        if t["id"] in seen:
            fail(f"{where}: duplicate id")
        seen.add(t["id"])
        if t["stage"] not in STAGES:
            fail(f"{where}: stage must be one of {STAGES}")
        for field in ("title", "humanWhy"):
            m = TELEMETRY.search(t[field])
            if m:
                fail(f"{where}: raw telemetry '{m.group(0)}' leaked into human-facing {field} "
                     f"(put metrics in internalSignal instead)")
        for s in t["scores"]:
            if not isinstance(s.get("value"), int):
                fail(f"{where}: score '{s.get('label')}' must be an integer")
        blob = json.dumps(t, ensure_ascii=False)
        if BLOCKED_DRE in blob:
            fail(f"{where}: blocklisted DRE {BLOCKED_DRE} present")
        # page-specific prompt presence
        if not (t.get("blog") or {}).get("prompt"):
            fail(f"{where}: blog.prompt required")
        for vk in ("scriptPrompt", "productionPrompt"):
            if not (t.get("video") or {}).get(vk):
                fail(f"{where}: video.{vk} required")
    picks = [t for t in topics if t.get("pick")]
    if not (1 <= len(picks) <= 8):
        fail(f"unreasonable number of ⭐ picks: {len(picks)}")
    return d


DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
STAGE_ORDER = {s: i for i, s in enumerate(STAGES)}  # BOFU, MOFU, TOFU left-to-right


def sections_for(topics):
    """One section per day (Mon..Sun) — matches the team's day-by-day workflow:
    each day offers a BOFU/MOFU/TOFU choice, ⭐ pick marked, pick one to publish."""
    by_day = {}
    for t in topics:
        by_day.setdefault(t["day"], []).append(t)
    out = []
    seen_order = DAY_ORDER + [d for d in by_day if d not in DAY_ORDER]
    for day in seen_order:
        group = by_day.get(day)
        if not group:
            continue
        group.sort(key=lambda t: STAGE_ORDER.get(t["stage"], 9))
        date = group[0].get("date", "")
        out.append({"label": f"{day}" + (f" · {date}" if date else ""), "topics": group})
    return out


def prompts_for(page_type, topics):
    m = {}
    for t in topics:
        if page_type == "blogs":
            m[f"{t['id']}:blog"] = t["blog"]["prompt"]
            if t["blog"].get("searchAtlasBrief"):
                m[f"{t['id']}:brief"] = t["blog"]["searchAtlasBrief"]
        elif page_type == "videos":
            m[f"{t['id']}:script"] = t["video"]["scriptPrompt"]
            m[f"{t['id']}:production"] = t["video"]["productionPrompt"]
    return m


def validate_output(html, page_type, prompt_map, n_topics):
    """Fail-closed checks on the RENDERED html (Fugu's blocklist)."""
    # isolate the COPY_PROMPTS data island so legit text inside prompts can't trip the scans
    body = re.sub(r'<script id="COPY_PROMPTS"[^>]*>.*?</script>', "", html, flags=re.S)
    if re.search(r"\son[a-z]+\s*=", body, re.I):
        fail(f"{page_type}: inline event handler (on*=) found in markup")
    if re.search(r"\bcp\s*\(", body):
        fail(f"{page_type}: legacy broken copy pattern 'cp(' found")
    if "javascript:" in body:
        fail(f"{page_type}: javascript: URI found")
    if not html.rstrip().endswith("</html>"):
        fail(f"{page_type}: output truncated (no closing </html>)")
    if html.count("<html") != 1 or html.count("<body") != 1:
        fail(f"{page_type}: malformed document (html/body count)")
    if f'templateSha256={SHA}' not in html:
        fail(f"{page_type}: provenance stamp missing/mismatched")
    cards = html.count("data-topic-card")
    if cards != n_topics:
        fail(f"{page_type}: expected {n_topics} cards, rendered {cards}")
    # every copy button id resolves in the embedded map
    m = re.search(r'<script id="COPY_PROMPTS"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        fail(f"{page_type}: COPY_PROMPTS data island missing")
    try:
        embedded = json.loads(m.group(1))
    except Exception as e:
        fail(f"{page_type}: COPY_PROMPTS is not valid JSON ({e})")
    for cid in re.findall(r'data-copy-id="([^"]+)"', html):
        if cid not in embedded:
            fail(f"{page_type}: button id '{cid}' has no prompt in the map")
    # telemetry must not reach blogs/videos human pages
    if page_type in ("blogs", "videos"):
        for why in re.findall(r'<p class="card-why">(.*?)</p>', html, re.S):
            mt = TELEMETRY.search(why)
            if mt:
                fail(f"{page_type}: telemetry '{mt.group(0)}' rendered in a card")
        if "internalSignal" in html or 'class="signal-panel"' in html:
            fail(f"{page_type}: internal signal leaked onto a human-facing page")


def main():
    global SHA
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    tpl_path = TEMPLATE_DIR / TEMPLATE_NAME
    if not tpl_path.exists():
        print(f"::error::canonical template not found at {tpl_path}", file=sys.stderr); sys.exit(1)
    SHA = hashlib.sha256(tpl_path.read_bytes()).hexdigest()[:16]

    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
        validate_data(data)
    except BuildError as e:
        print(f"::error::data validation failed — {e}", file=sys.stderr); sys.exit(1)
    except Exception as e:
        print(f"::error::could not load/parse {args.input}: {e}", file=sys.stderr); sys.exit(1)

    now = datetime.datetime.now(ZoneInfo("America/Los_Angeles")).isoformat(timespec="seconds")
    prov = {"template_id": TEMPLATE_ID, "version": TEMPLATE_VERSION, "sha256": SHA,
            "schema": SCHEMA, "generated_at": now}
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)),
                      autoescape=select_autoescape(["j2", "html"]))
    tpl = env.get_template(TEMPLATE_NAME)

    pages = {
        "blogs":    ("Content Topics — Blogs",   "21 topics for the blog + SEO team, grouped by funnel stage."),
        "videos":   ("Content Topics — Videos",  "21 topics for Peter & Ellie, with per-format treatments and ready-to-copy prompts."),
        "research": ("Content Topics — Research", "The evidence behind every pick: convergence signals and the raw data per topic."),
    }
    topics = data["topics"]
    out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    try:
        for page_type, (title, subtitle) in pages.items():
            pmap = prompts_for(page_type, topics)
            prompts_json = json.dumps(pmap, ensure_ascii=False).replace("</", "<\\/")
            html = tpl.render(page_type=page_type, page_title=title, page_subtitle=subtitle,
                              week=data["week"], topic_count=len(topics), dre=DRE, prov=prov,
                              sections=sections_for(topics), prompts_json=prompts_json)
            validate_output(html, page_type, pmap, len(topics))
            (out_dir / f"{page_type}.html").write_text(html, encoding="utf-8")
            written.append(page_type)
    except BuildError as e:
        print(f"::error::build/validation failed — {e}. NOTHING published.", file=sys.stderr)
        for p in written:
            (out_dir / f"{p}.html").unlink(missing_ok=True)
        sys.exit(1)

    print(f"OK — wrote {', '.join(p+'.html' for p in written)} to {out_dir} (template v{TEMPLATE_VERSION}, sha {SHA})")


if __name__ == "__main__":
    main()

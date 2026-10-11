"""Re-read title, channel, views and likes for each analyzed short, ONE page per request.

Batch reads (8 pages per request) mixed up pages, so this re-checks every video on its own.
usage: python research/recheck_views.py research/viral-shorts
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import viral_study as vs  # noqa: E402

out = Path(sys.argv[1])
analyses = json.loads((out / "analyses.json").read_text())
path = out / "views.json"
views = json.loads(path.read_text()) if path.exists() else {}
vs.KEY = vs.key()
vs.MODELS[:] = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]
for n, url in enumerate(analyses, 1):
    if url in views:
        continue
    try:
        text = vs.ask([{"text": (
            f"Read {url} and report ONLY what is literally on that page as JSON: "
            '{"title": ..., "channel": ..., "views": "e.g. 1.2M views or not shown", '
            '"likes": "e.g. 371K or not shown", "uploaded": "..."}')}], tools=[{"url_context": {}}])
        row = vs.parse_json(text) or {}
    except RuntimeError as e:
        print(f"[{n}] failed: {e}", flush=True)
        continue
    if isinstance(row, list):
        row = row[0] if row else {}
    row["views_n"] = vs.views_num(row.get("views")) if "not" not in str(row.get("views")) else 0
    row["likes_n"] = vs.views_num(row.get("likes")) if "not" not in str(row.get("likes")) else 0
    views[url] = row
    path.write_text(json.dumps(views, indent=1, ensure_ascii=False))
    print(f"[{n}/{len(analyses)}] {row.get('views')} | {row.get('likes')} | {str(row.get('title'))[:60]}", flush=True)
print("[done]", len(views), flush=True)

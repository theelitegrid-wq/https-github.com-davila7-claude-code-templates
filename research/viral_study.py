"""Study ~100 viral YouTube Shorts across niches with Gemini (free tier).

1. candidates: real search results with view counts via yt-dlp ("ytsearch"), needs youtube.com
               network access; fallback --source gemini lets Gemini propose videos (it often
               invents IDs, so most get dropped at verification)
2. verify:     Gemini URL-context reads each video page -> real title, channel, view count
3. select:     most-viewed verified videos per niche
4. analyze:    Gemini watches each video and returns a structured breakdown

Needs GEMINI_API_KEY (env or ~/.config/watch/.env). Resumable: results are cached in OUT/.
usage: python research/viral_study.py [--per-niche 7] [--out research/viral]
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

MODELS = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash"]  # override with --models

NICHES = {
    "3d-what-happens-if": "3D animated 'what happens if' shorts about the body, injuries, survival (Zack D. Films style)",
    "3d-physics-what-if": "3D physics/destruction 'what if' simulations (Jake Fellman style)",
    "human-body-3d": "human body / medical 3D animation explainers",
    "space-scale": "space, universe and size-comparison shorts",
    "animated-history": "animated history stories and facts",
    "scary-facts-horror": "creepy facts and short horror stories",
    "reddit-stories": "Reddit stories narrated over gameplay footage",
    "animal-facts": "animal and nature facts",
    "psychology-facts": "psychology and life facts",
    "money-business": "money, business and rich-people stories",
    "satisfying": "oddly satisfying, hydraulic press, 3D satisfying renders",
    "how-it-works": "how things work / engineering animations",
    "survival-scenarios": "how to survive extreme situations",
    "mystery-unsolved": "mysteries, unsolved cases, strange places",
    "movie-recaps": "movie and TV recaps / explained",
    "tech-ai-facts": "technology and AI facts",
}

SEEDS = {
    "human-body-3d": ["https://www.youtube.com/shorts/3D-zndsxCDA", "https://www.youtube.com/shorts/aZvtcdltNMg",
                      "https://www.youtube.com/shorts/VVGaYQOBfRU", "https://www.youtube.com/shorts/gs9IqxEgMpE"],
    "space-scale": ["https://www.youtube.com/shorts/YnD-MD5DSng", "https://www.youtube.com/shorts/OdLeE-XgejU",
                    "https://www.youtube.com/shorts/hTvn0s-1i8M", "https://www.youtube.com/shorts/uXf6ndiYAPg"],
    "scary-facts-horror": ["https://www.youtube.com/shorts/YKh23n34omA", "https://www.youtube.com/shorts/X5MapFYALiw",
                           "https://www.youtube.com/shorts/ul951wnTuFs", "https://www.youtube.com/shorts/BNVx_86R0VQ"],
    "survival-scenarios": ["https://www.youtube.com/watch?v=vRJQ6RLWv9Y"],
    "reddit-stories": ["https://www.youtube.com/watch?v=MkH-hoXaMrw"],
}

ANALYSIS_Q = """You are a top YouTube Shorts strategist. Watch this video and return ONLY a JSON object:
{
 "topic": "...",
 "hook_words": "exact spoken/on-screen words of the first 3 seconds",
 "hook_type": "question | shocking claim | visual shock | story cold-open | countdown | other",
 "length_s": number,
 "structure": ["beat 1", "beat 2", "..."],
 "cut_count": number,
 "avg_shot_s": number,
 "camera": {"wide": pct, "medium": pct, "close": pct},
 "visual_style": "3D render | 2D animation | stock footage | gameplay | live action | AI images | screen/text | mixed",
 "characters": "who/what is on screen and how realistic",
 "captions": {"type": "word-by-word | phrase | none | title only", "size": "small|medium|large",
              "position": "top|middle|lower third|bottom", "pct_of_runtime": pct},
 "voice": "human | AI/TTS | none; tone",
 "words_per_minute": number,
 "music_sfx": "...",
 "ending": "loop | question | cliffhanger | punchline | CTA | abrupt",
 "retention_tricks": ["..."],
 "emotion": "curiosity | fear | disgust | awe | humor | satisfaction | other",
 "why_it_works": "2 sentences",
 "production_difficulty": 1-5,
 "faceless": true/false,
 "makeable_with_free_3d_pipeline": "yes | partial | no - one line why"
}"""


def key():
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"]
    cfg = Path.home() / ".config/watch/.env"
    for line in cfg.read_text().splitlines():
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("GEMINI_API_KEY not set")


KEY = None
_last = [0.0]


def ask(parts, tools=None, json_out=False, tries=8, gap=7.0):
    body = {"contents": [{"parts": parts}]}
    if tools:
        body["tools"] = tools
    if json_out and not tools:
        body["generationConfig"] = {"responseMimeType": "application/json"}
    err = None
    for i in range(tries):
        wait = gap - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        model = MODELS[i % len(MODELS)]
        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            data=json.dumps(body).encode(), headers={"x-goog-api-key": KEY, "Content-Type": "application/json"})
        _last[0] = time.time()
        try:
            d = json.load(urllib.request.urlopen(req, timeout=300))
            return "".join(p.get("text", "") for p in d["candidates"][0]["content"]["parts"])
        except urllib.error.HTTPError as e:
            err = f"{model} HTTP {e.code}: {e.read()[:200]!r}"
            time.sleep(min(90, 10 * (i + 1)))
        except Exception as e:  # timeouts, malformed responses
            err = f"{model} {e}"
            time.sleep(10)
    raise RuntimeError(err)


def parse_json(text):
    m = re.search(r"(\{.*\}|\[.*\])", text, re.S)
    return json.loads(m.group(1)) if m else None


def vid(url):
    m = re.search(r"(?:shorts/|v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
    return m.group(1) if m else None


def views_num(text):
    if not text:
        return 0
    t = str(text).replace(",", "").lower()
    m = re.search(r"([\d.]+)\s*([kmb])?", t)
    if not m:
        return 0
    n = float(m.group(1))
    return int(n * {"k": 1e3, "m": 1e6, "b": 1e9}.get(m.group(2) or "", 1))


def load(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def main():
    global KEY
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-niche", type=int, default=7)
    ap.add_argument("--out", default="research/viral")
    ap.add_argument("--source", choices=["ytdlp", "gemini", "file"], default="ytdlp")
    ap.add_argument("--urls", help="for --source file: JSON {niche: [video ids or urls]}")
    ap.add_argument("--models", help="comma-separated Gemini models to rotate through")
    ap.add_argument("--search", type=int, default=40, help="search results per niche (ytdlp)")
    args = ap.parse_args()
    KEY = key()
    if args.models:
        MODELS[:] = args.models.split(",")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # 1. candidates
    cand_path = out / "candidates.json"
    ver_path = out / "verified.json"
    cands = load(cand_path, {})
    verified = load(ver_path, {})
    for niche, desc in NICHES.items():
        if niche in cands:
            continue
        if args.source == "file":
            continue
        if args.source == "ytdlp":
            # Real search results with real view counts; no verification step needed.
            query = f"ytsearch{args.search}:{desc} #shorts"
            proc = subprocess.run(["yt-dlp", "--flat-playlist", "--dump-json", "--no-warnings", query],
                                  capture_output=True, text=True)
            rows = [json.loads(l) for l in proc.stdout.splitlines() if l.strip()]
            cands[niche] = []
            for r in rows:
                if not r.get("id") or (r.get("duration") or 0) > 180:
                    continue
                u = f"https://www.youtube.com/watch?v={r['id']}"
                cands[niche].append(u)
                verified[u] = {"exists": True, "title": r.get("title"), "channel": r.get("channel"),
                               "views": r.get("view_count"), "views_n": r.get("view_count") or 0,
                               "uploaded": r.get("upload_date"), "niche": niche}
            ver_path.write_text(json.dumps(verified, indent=1))
            if not rows:
                sys.exit("yt-dlp search returned nothing (is youtube.com reachable?); try --source gemini")
        else:
            text = ask([{"text": (
                f"List 16 real, very viral YouTube Shorts (millions of views) in this niche: {desc}. "
                "Prefer the biggest faceless channels in the niche. Only include videos you are confident exist, "
                'with their real 11-character IDs. Return JSON: [{"url": "https://www.youtube.com/shorts/ID", '
                '"channel": "...", "title": "..."}]')}], json_out=True)
            items = parse_json(text) or []
            urls = [i.get("url", "") for i in items if isinstance(i, dict)] + SEEDS.get(niche, [])
            cands[niche] = sorted({f"https://www.youtube.com/watch?v={vid(u)}" for u in urls if vid(u)})
        cand_path.write_text(json.dumps(cands, indent=1))
        print(f"[candidates] {niche}: {len(cands[niche])}", flush=True)

    if args.source == "file":
        for niche, ids in json.loads(Path(args.urls).read_text()).items():
            cands.setdefault(niche, [f"https://www.youtube.com/watch?v={vid(i) or i}" for i in ids])
        cand_path.write_text(json.dumps(cands, indent=1))

    # 2. verify (8 pages per request; ytdlp candidates are already verified)
    todo = [(n, u) for n, us in cands.items() for u in us if u not in verified]
    for i in range(0, len(todo), 8):
        batch = todo[i:i + 8]
        listing = "\n".join(u for _, u in batch)
        try:
            text = ask([{"text": (
                "Read each of these YouTube pages and report ONLY what is literally on each page. Return a JSON "
                'array, one object per URL: {"url": ..., "exists": true/false, "title": ..., "channel": ..., '
                '"views": "e.g. 12M views or not shown", "likes": "e.g. 371K or not shown", '
                '"uploaded": "..."}\n' + listing)}],
                tools=[{"url_context": {}}])
            rows = parse_json(text) or []
        except RuntimeError as e:
            print("[verify] batch failed:", e, flush=True)
            continue
        by_id = {vid(r.get("url", "")): r for r in rows if isinstance(r, dict)}
        for niche, u in batch:
            r = by_id.get(vid(u)) or {"exists": False}
            r["niche"] = niche
            r["views_n"] = views_num(r.get("views"))
            r["likes_n"] = views_num(r.get("likes"))
            verified[u] = r
        ver_path.write_text(json.dumps(verified, indent=1))
        ok = sum(1 for _, u in batch if verified[u].get("exists") and verified[u].get("title"))
        print(f"[verify] {i + len(batch)}/{len(todo)} ({ok}/{len(batch)} real)", flush=True)

    # 3. select
    picks = []
    for niche in cands:
        rows = [(u, r) for u, r in verified.items()
                if r.get("niche") == niche and r.get("exists") and r.get("title")]
        rows.sort(key=lambda x: (x[1].get("views_n", 0), x[1].get("likes_n", 0)), reverse=True)
        picks += [(niche, u, r) for u, r in rows[:args.per_niche]]
    print(f"[select] {len(picks)} videos", flush=True)

    # 4. analyze
    res_path = out / "analyses.json"
    results = load(res_path, {})
    for n, (niche, u, r) in enumerate(picks, 1):
        if u in results:
            continue
        try:
            text = ask([{"fileData": {"fileUri": u}}, {"text": ANALYSIS_Q}], json_out=True)
            a = parse_json(text)
        except RuntimeError as e:
            print(f"[analyze] {n}/{len(picks)} failed: {e}", flush=True)
            continue
        if not a:
            continue
        results[u] = {"niche": niche, "title": r.get("title"), "channel": r.get("channel"),
                      "views": r.get("views"), "views_n": r.get("views_n"), "likes": r.get("likes"),
                      "likes_n": r.get("likes_n"), "uploaded": r.get("uploaded"),
                      "analysis": a}
        res_path.write_text(json.dumps(results, indent=1, ensure_ascii=False))
        print(f"[analyze] {n}/{len(picks)} {niche}: {str(r.get('title'))[:60]}", flush=True)
    print(f"[done] {len(results)} analyses in {res_path}", flush=True)


if __name__ == "__main__":
    main()

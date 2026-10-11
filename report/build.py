"""Build report/index.html from the study data and the rendered test video.

usage: python report/build.py [--video studio/out/mariana-trench.mp4]
"""
import argparse
import json
import re
import statistics as st
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STUDY = ROOT / "research" / "viral-shorts"

NICHES = [
    ("\"What if\" hypotheticals: body and physics", "Most top performers in the study; curiosity hook; endless topics.", "Strong"),
    ("Space and scale", "Top short in the sample was a universe size comparison; awe emotion.", "Strong"),
    ("Survival scenarios", "Question hook plus \"would I survive?\" comments drive engagement.", "Strong"),
    ("Deadly and weird animals", "\"Deadliest animal\" format performs; cute-vs-deadly contrast.", "Medium"),
    ("Inside the human body (as \"what if\")", "Fits our scenes; plain explainers did poorly, so frame them as hypotheticals.", "Strong"),
    ("History: what if you lived then", "Strong genre on YouTube; needs period characters and sets.", "Medium"),
    ("Mysteries and strange places", "Storytelling genre with strong retention; needs atmosphere scenes.", "Medium"),
    ("How it works (3D cutaways)", "Sample shorts were slow (~89 wpm, 4 s shots) and weak; needs machine models.", "Medium"),
    ("Psychology facts", "Crowded; sample shorts performed poorly; template risk.", "Weak"),
    ("Money stories", "Mostly live-action interviews; hard to make in 3D.", "Weak"),
]
IDEAS = [
    ("What if you don't sleep for 11 days?", "Body", "Rendered (test 1)"),
    ("What if you fell into the Mariana Trench?", "Survival", "Rendered (this test)"),
    ("What happens to your body in space without a suit?", "Body / space", "Next"),
    ("What if the Moon disappeared tonight?", "Space", "Next"),
    ("What if you got struck by lightning?", "Survival / body", "Next"),
    ("What if your heart stopped for 60 seconds?", "Body", "Next"),
    ("What if you stood next to a black hole?", "Space", "Next"),
    ("What if a mosquito bit you in 1347?", "History / animals", "Next"),
    ("What if you fell through thin ice?", "Survival", "Next"),
    ("What if Earth were twice as big?", "Space", "Next (Kurzgesagt did it; use a different angle)"),
]


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def channel_lists():
    text = (ROOT / "research" / "channels.md").read_text()
    part1, part2 = text.split("## Part 2")[0], text.split("## Part 2")[1]
    names = lambda t: [m.group(1).replace("**", "").strip()
                       for m in re.finditer(r"^\| \d+ \| ([^|]+) \|", t, re.M)]
    return names(part1), names(part2)


def video_specs(path):
    out = subprocess.run(["python3", str(ROOT / ".claude/skills/style-study/scripts/metrics.py"), str(path),
                          "--out", str(ROOT / "report" / ".metrics")], capture_output=True, text=True).stdout
    m = json.loads(out[: out.rindex("}") + 1])
    plan = json.loads((ROOT / "studio" / "public" / "plan.json").read_text())
    words = sum(len(s["narration"].split()) for s in plan["scenes"])
    wpm = words / m["duration"] * 60
    hook = len(plan["scenes"][0]["narration"].split())
    rows = [
        ("Length", f"{m['duration']:.0f} s", "45–60 s", 45 <= m["duration"] <= 60),
        ("Average shot", f"{m['shot_seconds']['mean']:.1f} s", "2–3 s", 1.8 <= m["shot_seconds"]["mean"] <= 3.2),
        ("Cuts per minute", f"{m['cuts_per_minute']:.0f}", "20–30", 18 <= m["cuts_per_minute"] <= 34),
        ("Voice pace", f"{wpm:.0f} wpm", "~150 wpm", 135 <= wpm <= 165),
        ("Hook length", f"{hook} words", "≤10 words", hook <= 10),
        ("Loudness", f"{m['loudness_lufs']:.0f} LUFS", "−14 to −16", m["loudness_lufs"] is not None and -17 <= m["loudness_lufs"] <= -12),
        ("Frame", m["aspect"], "1080×1920 vertical", m["aspect"].startswith("1080x1920")),
    ]
    return [{"label": a, "ours": b, "target": c, "ok": bool(d)} for a, b, c, d in rows]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", default=str(ROOT / "studio/out/mariana-trench.mp4"))
    args = ap.parse_args()
    analyses = json.loads((STUDY / "analyses.json").read_text())
    views = json.loads((STUDY / "views.json").read_text()) if (STUDY / "views.json").exists() else {}

    videos = []
    for url, r in analyses.items():
        a = r["analysis"][0] if isinstance(r["analysis"], list) else r["analysis"]
        v = views.get(url, {})
        title = v.get("title") if v.get("title") and "not" not in str(v.get("title")).lower() else r.get("title")
        videos.append({
            "url": url, "title": title or url, "channel": v.get("channel") or r.get("channel") or "",
            "niche": r["niche"].split(" (")[0], "views": v.get("views_n") or 0, "likes": v.get("likes_n") or 0,
            "hook": a.get("hook_type"), "length": num(a.get("length_s")), "shot": num(a.get("avg_shot_s")),
            "why": a.get("why_it_works"),
        })
    A = [r["analysis"][0] if isinstance(r["analysis"], list) else r["analysis"] for r in analyses.values()]
    count = lambda key: Counter(str(x.get(key) or "other").split(";")[0][:24] for x in A).most_common(6)
    caps = Counter(str((x.get("captions") or {}).get("type")) for x in A).most_common(5)
    creators, faceless = channel_lists()
    data = {
        "videos": videos,
        "counts": {"hook": count("hook_type"), "emotion": count("emotion"), "ending": count("ending"), "captions": caps},
        "specs": video_specs(args.video),
        "niches": [{"name": a, "why": b, "fit": c} for a, b, c in NICHES],
        "ideas": IDEAS, "creators": creators, "faceless": faceless,
        "medians": {k: st.median([v for v in (num(x.get(k)) for x in A) if v]) for k in ("length_s", "avg_shot_s", "words_per_minute")},
    }
    html = (ROOT / "report" / "template.html").read_text().replace(
        "__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    (ROOT / "report" / "index.html").write_text(html)
    print("videos", len(videos), "with views", sum(1 for v in videos if v["views"]),
          "| specs", [(s["label"], s["ours"], s["ok"]) for s in data["specs"]])


if __name__ == "__main__":
    main()

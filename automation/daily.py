"""Daily pipeline: pick a fresh topic -> write script -> render with MoneyPrinterTurbo -> upload to YouTube.

Writer: Claude (CLAUDE_CODE_OAUTH_TOKEN, your Claude subscription) or Gemini free tier (GEMINI_API_KEY).
Footage: Pexels (PEXELS_API_KEY, free). Voice: Edge TTS (free). Upload: YouTube Data API (free).
"""
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "automation"
ENGINE = ROOT / "vendor" / "MoneyPrinterTurbo"
HISTORY = HERE / "history.json"

PROMPT = """You run a fast-growing YouTube channel.
Niche: {niche}
Audience: {audience}
Language: {language}
Style rules: {style_rules}

Titles already published (never repeat or closely rephrase these topics):
{past}

Pick ONE new topic with high click potential that big channels in this niche would make, then write it.
Return ONLY a JSON object with these keys:
  "topic": short topic name,
  "title": YouTube title under 70 chars, curiosity-driven, no clickbait lies, may include 1 emoji,
  "description": 2-3 sentence description followed by 3-5 relevant hashtags including #shorts if vertical,
  "tags": list of 10-15 search tags,
  "script": the voiceover, {paragraphs} short paragraphs, spoken style, facts must be accurate,
  "search_terms": list of 6-8 short English stock-footage search phrases that match the script visually
"""


def ask_llm(prompt):
    if os.environ.get("CLAUDE_CODE_OAUTH_TOKEN") and shutil.which("claude"):
        out = subprocess.run(
            ["claude", "-p", prompt, "--output-format", "text"],
            capture_output=True, text=True, check=True, timeout=300,
        ).stdout
    elif os.environ.get("GEMINI_API_KEY"):
        model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            params={"key": os.environ["GEMINI_API_KEY"]},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"},
            },
            timeout=120,
        )
        r.raise_for_status()
        out = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        sys.exit("Set CLAUDE_CODE_OAUTH_TOKEN (with claude CLI installed) or GEMINI_API_KEY")
    match = re.search(r"\{.*\}", out, re.S)
    return json.loads(match.group(0))


def write_engine_config():
    """MoneyPrinterTurbo only needs footage keys here: the script comes from us."""
    text = (ENGINE / "config.example.toml").read_text(encoding="utf-8")
    keys = json.dumps([k.strip() for k in os.environ["PEXELS_API_KEY"].split(",")])
    text = re.sub(r"(?m)^pexels_api_keys\s*=.*$", f"pexels_api_keys = {keys}", text, count=1)
    (ENGINE / "config.toml").write_text(text, encoding="utf-8")


def render(cfg, plan):
    cmd = [
        sys.executable, "cli.py",
        "--video-script", plan["script"],
        "--video-terms", ",".join(plan["search_terms"]),
        "--video-language", cfg["language"],
        "--video-aspect", cfg["aspect"],
        "--voice-name", cfg["voice"],
        "--video-source", "pexels",
        "--video-concat-mode", "random",
        "--video-transition-mode", "fade-in",
        "--subtitle-enabled",
        "--subtitle-position", "two_thirds_bottom",
        "--video-count", "1",
    ]
    proc = subprocess.run(cmd, cwd=ENGINE, capture_output=True, text=True)
    sys.stderr.write(proc.stderr[-4000:])
    if proc.returncode != 0:
        sys.exit(f"render failed (exit {proc.returncode})")
    result = json.loads(proc.stdout.strip().splitlines()[-1])["result"]
    video = Path(result["videos"][0])
    return video if video.is_absolute() else ENGINE / video


def main():
    cfg = yaml.safe_load((HERE / "channel.yaml").read_text(encoding="utf-8"))
    history = json.loads(HISTORY.read_text()) if HISTORY.exists() else []

    plan = ask_llm(PROMPT.format(
        past="\n".join(f"- {h['title']}" for h in history[-200:]) or "(none yet)",
        **{k: cfg[k] for k in ("niche", "audience", "language", "style_rules", "paragraphs")},
    ))
    print(f"Topic: {plan['topic']}\nTitle: {plan['title']}", flush=True)

    write_engine_config()
    video = render(cfg, plan)
    print(f"Rendered: {video}", flush=True)

    entry = {"date": date.today().isoformat(), "title": plan["title"], "topic": plan["topic"]}
    if os.environ.get("DRY_RUN") == "1":
        print("DRY_RUN=1: skipping upload")
    else:
        from youtube_upload import upload
        entry["video_id"] = upload(
            str(video), plan["title"], plan["description"], plan["tags"],
            privacy=cfg["privacy"], category_id=str(cfg["category_id"]),
            synthetic=cfg.get("made_with_ai_disclosure", True),
        )
        print(f"Uploaded ({cfg['privacy']}): https://youtu.be/{entry['video_id']}")
    history.append(entry)
    HISTORY.write_text(json.dumps(history, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    main()

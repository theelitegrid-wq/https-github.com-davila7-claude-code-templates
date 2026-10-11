"""Daily pipeline: pick a fresh topic -> write script -> make visuals -> render with MoneyPrinterTurbo -> upload.

Writer: Claude (CLAUDE_CODE_OAUTH_TOKEN, your Claude subscription) or Gemini free tier (GEMINI_API_KEY).
Visuals: "studio" = free 3D animation rendered by studio/ (Remotion + three.js, Kokoro voice),
         "veo" = AI-generated scenes from Google Veo (paid), "stock" = Pexels footage (free).
Upload: YouTube Data API (free).
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
STUDIO = ROOT / "studio"
HISTORY = HERE / "history.json"
STYLE = HERE / "style.md"

PROMPT = """You run a fast-growing YouTube channel.
Niche: {niche}
Audience: {audience}
Language: {language}
Style rules: {style_rules}

Titles already published (never repeat or closely rephrase these topics):
{past}

Channel style guide (follow it; owner feedback in it overrides anything below):
{style}

Pick ONE new topic with high click potential that big channels in this niche would make, then write it.
Return ONLY a JSON object with these keys:
  "topic": short topic name,
  "title": YouTube title under 70 chars, phrased as the same "What if..." question as the hook, may include 1 emoji,
  "description": 2-3 sentence description followed by 3-5 relevant hashtags including #shorts if vertical,
  "tags": list of 10-15 search tags,
  "scenes": list of {scenes} objects, each {{"narration": one short spoken sentence, "visual": one shot}}.
     Narration across scenes forms the whole voiceover. Facts must be accurate.
     HOOK: scene 1 narration is ONLY a short "What if you...?" question, max 10 words
     (e.g. "What if you don't sleep for 11 days?"). Scene 2 answers immediately; no intro, no filler.
     Keep every narration short: one sentence, max 16 words.
     Each "visual" is a self-contained shot description for an AI video model: subject, action,
     camera move, setting. Show, don't tell: cutaways, cross-sections, macro close-ups, dramatic
     "what happens if" moments. Never ask for on-screen text. Keep the same characters/objects consistent.
     Each scene also has:
       "type": the 3D scene that best fits, one of
          "person"  a realistic everyday person reacting (use for the hook, the human moments and
                    the ending; about half the scenes), optionally with a glowing organ (focus),
          "body"    x-ray human with one glowing organ (inside-the-body cutaways),
          "tunnel"  flying through a blood vessel / throat / gut / cave / pipe; with "mode": "water"
                    it becomes open deep water with drifting particles (ocean, sinking, darkness),
          "bathysphere" a steel deep-sea sphere sinking (submarines, deep dives, explorers),
          "blob"    a glossy pulsing organic object (organ, brain, cell, creature, food),
          "planet"  a planet in space (Earth, space, climate, global scale),
          "shatter" something exploding into pieces (shock, collapse, impact, a twist),
          "virus"   spiky germs floating (infection, bacteria, disease, immune system);
          vary the types, never the same type twice in a row,
       "focus": for "person" or "body", one of brain, head, eyes, heart, lungs, chest, stomach, liver,
          gut, kidneys, bones, legs, skin, blood (omit when nothing glows),
       "pose", "shot", "face": for "person" only. pose: idle, tired, sad, no, yes, sneak, walk, run.
          shot: full, medium, close. face: neutral, smile, shocked, scared. Vary shots between scenes.
       "color" and "accent": hex colors that fit the subject (accent is the glow/highlight),
       "callout": optional big on-screen number or time stamp (max 12 chars, e.g. "72 HOURS", "DAY 4");
          use it on 2-3 scenes only.
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
    """MoneyPrinterTurbo only needs footage keys here: the script and Veo clips come from us."""
    text = (ENGINE / "config.example.toml").read_text(encoding="utf-8")
    keys = json.dumps([k.strip() for k in os.environ.get("PEXELS_API_KEY", "").split(",") if k.strip()])
    text = re.sub(r"(?m)^pexels_api_keys\s*=.*$", f"pexels_api_keys = {keys}", text, count=1)
    (ENGINE / "config.toml").write_text(text, encoding="utf-8")


def render(cfg, plan, clips=None):
    script = " ".join(scene["narration"] for scene in plan["scenes"])
    if clips:
        visuals = [
            "--video-source", "local",
            "--video-materials", ",".join(str(c) for c in clips),
            "--video-concat-mode", "sequential",
            "--video-clip-duration", str(cfg.get("veo_seconds", 8)),
            "--video-transition-mode", "none",
        ]
    else:
        visuals = [
            "--video-source", "pexels",
            "--video-terms", ",".join(plan["search_terms"]),
            "--video-concat-mode", "random",
            "--video-transition-mode", "fade-in",
        ]
    cmd = [
        sys.executable, "cli.py",
        "--video-script", script,
        "--video-language", cfg["language"],
        "--video-aspect", cfg["aspect"],
        "--voice-name", cfg["voice"],
        *visuals,
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


def render_studio(cfg, plan):
    """Free 3D animation: Kokoro voice + Remotion/three.js scenes, all on CPU."""
    out = STUDIO / "out"
    out.mkdir(exist_ok=True)
    plan_in = out / "plan_in.json"
    plan_in.write_text(json.dumps({**plan, "audio": None}, ensure_ascii=False), encoding="utf-8")
    subprocess.run(
        [str(STUDIO / ".venv" / "bin" / "python"), "voice.py", str(plan_in),
         "--voice", cfg.get("studio_voice", "am_michael"), "--speed", str(cfg.get("studio_speed", 1.1))],
        cwd=STUDIO, check=True,
    )
    video = out / "final.mp4"
    cmd = ["npx", "remotion", "render", "src/index.ts", "Short", str(video),
           "--props=public/plan.json", "--concurrency=" + str(os.cpu_count() or 2), "--log=error"]
    if os.environ.get("REMOTION_BROWSER"):
        cmd.append("--browser-executable=" + os.environ["REMOTION_BROWSER"])
    subprocess.run(cmd, cwd=STUDIO, check=True)
    return video


def main():
    cfg = yaml.safe_load((HERE / "channel.yaml").read_text(encoding="utf-8"))
    history = json.loads(HISTORY.read_text()) if HISTORY.exists() else []

    plan = ask_llm(PROMPT.format(
        past="\n".join(f"- {h['title']}" for h in history[-200:]) or "(none yet)",
        style=STYLE.read_text(encoding="utf-8") if STYLE.exists() else "(none)",
        **{k: cfg[k] for k in ("niche", "audience", "language", "style_rules", "scenes")},
    ))
    print(f"Topic: {plan['topic']}\nTitle: {plan['title']}", flush=True)

    if cfg.get("visuals", "studio") == "studio":
        video = render_studio(cfg, plan)
        return publish(cfg, plan, video, history)

    clips = None
    if cfg.get("visuals") == "veo":
        from veo import scene_clips
        clips = scene_clips(
            plan["scenes"], cfg["veo_style"], ENGINE / "storage" / "veo" / date.today().isoformat(),
            aspect=cfg["aspect"], seconds=cfg.get("veo_seconds", 8),
            model=cfg.get("veo_model"), negative=cfg.get("veo_negative", ""),
        )
    write_engine_config()
    video = render(cfg, plan, clips)
    publish(cfg, plan, video, history)


def publish(cfg, plan, video, history):
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

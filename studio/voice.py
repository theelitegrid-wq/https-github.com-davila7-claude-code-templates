"""Voice a scene plan with Kokoro (free, offline) and time every scene and caption word to the audio.

usage: python voice.py plan_in.json [--voice am_michael] [--speed 1.1]
writes public/voice.wav and public/plan.json for the Remotion "Short" composition.
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = Path(__file__).resolve().parent
MODELS = HERE / "models"
GAP = 0.18  # breath between scenes, seconds


def word_times(text, start, length):
    """Spread words over the spoken span, weighted by length (Kokoro gives no timestamps)."""
    words = text.split()
    weights = [len(re.sub(r"\W", "", w)) + 2 for w in words]
    total = sum(weights) or 1
    out, t = [], start
    for word, weight in zip(words, weights):
        d = length * weight / total
        out.append({"w": word, "s": round(t, 3), "e": round(t + d, 3)})
        t += d
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--voice", default="am_michael")
    ap.add_argument("--speed", type=float, default=1.1)
    ap.add_argument("--lang", default="en-us")
    args = ap.parse_args()

    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    kokoro = Kokoro(str(MODELS / "kokoro-v1.0.int8.onnx"), str(MODELS / "voices-v1.0.bin"))

    chunks, t, rate = [], 0.0, 24000
    for scene in plan["scenes"]:
        samples, rate = kokoro.create(scene["narration"], voice=args.voice, speed=args.speed, lang=args.lang)
        speech = len(samples) / rate
        scene["start"] = round(t, 3)
        scene["duration"] = round(speech + GAP, 3)
        scene["words"] = word_times(scene["narration"], t + 0.05, speech - 0.12)
        chunks += [samples, np.zeros(int(GAP * rate), dtype=samples.dtype)]
        t += speech + GAP

    public = HERE / "public"
    sf.write(public / "voice.wav", np.concatenate(chunks), rate)
    plan["audio"] = "voice.wav"
    (public / "plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"voiced {len(plan['scenes'])} scenes, {t:.1f}s")


if __name__ == "__main__":
    main()

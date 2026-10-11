"""Voice a scene plan with Kokoro (free, offline), time every scene, cut and caption word to the
audio, and mix the final soundtrack: voice + whoosh on every cut + a quiet music bed,
loudness-normalized to -14 LUFS (the level YouTube Shorts play at).

usage: python voice.py plan_in.json [--voice am_michael] [--speed 1.0] [--no-music]
writes public/voice.wav and public/plan.json for the Remotion "Short" composition.
"""
import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = Path(__file__).resolve().parent
MODELS = HERE / "models"
GAP = 0.18  # breath between scenes, seconds
SUBCUT_OVER = 3.4  # scenes longer than this get a second camera angle halfway (shots ~2-3 s)


def ffmpeg_audio(filter_src, seconds, rate, af=""):
    """Render an ffmpeg lavfi audio source to a mono float array."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "a.wav"
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", filter_src, "-t", f"{seconds:.3f}",
               "-ac", "1", "-ar", str(rate)]
        if af:
            cmd += ["-af", af]
        subprocess.run(cmd + [str(out)], check=True)
        data, _ = sf.read(out, dtype="float32")
    return data


def soundtrack(voice, rate, cuts, music=True):
    total = len(voice) / rate
    mix = voice.astype(np.float32).copy()
    whoosh = ffmpeg_audio("anoisesrc=c=pink:a=0.6", 0.45, rate,
                          "highpass=f=400,lowpass=f=4000,afade=t=in:d=0.18,afade=t=out:st=0.18:d=0.27")
    for c in cuts:
        i = max(0, int((c - 0.2) * rate))
        seg = whoosh[: max(0, min(len(whoosh), len(mix) - i))]
        mix[i:i + len(seg)] += 0.22 * seg
    if music:
        # Soft minor pad with slow tremolo: A2 + C3 + E3 + A3; ducked under the voice.
        pad = ffmpeg_audio(
            "aevalsrc='0.25*sin(2*PI*110*t)+0.18*sin(2*PI*130.81*t)+0.16*sin(2*PI*164.81*t)"
            "+0.1*sin(2*PI*220*t)*(0.6+0.4*sin(2*PI*0.2*t))'", total, rate,
            f"lowpass=f=900,afade=t=in:d=1.5,afade=t=out:st={max(0, total - 1.5):.2f}:d=1.5")
        mix[: len(pad)] += 0.06 * pad[: len(mix)]
    peak = float(np.max(np.abs(mix))) or 1.0
    return mix / peak * 0.9


def loudnorm(path):
    tmp = path.with_suffix(".norm.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                    "-ar", "48000", str(tmp)], check=True)
    tmp.replace(path)


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
    ap.add_argument("--speed", type=float, default=0.95)
    ap.add_argument("--no-music", action="store_true")
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
        # Second camera angle halfway through long scenes (offset in seconds from scene start).
        scene["cuts"] = [round(scene["duration"] / 2, 3)] if scene["duration"] > SUBCUT_OVER else []
        chunks += [samples, np.zeros(int(GAP * rate), dtype=samples.dtype)]
        t += speech + GAP

    public = HERE / "public"
    voice = np.concatenate(chunks)
    cuts = [s["start"] + c for s in plan["scenes"] for c in [0, *s["cuts"]] if s["start"] + c > 0]
    sf.write(public / "voice.wav", soundtrack(voice, rate, cuts, music=not args.no_music), rate)
    loudnorm(public / "voice.wav")
    plan["audio"] = "voice.wav"
    (public / "plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"voiced {len(plan['scenes'])} scenes, {t:.1f}s")


if __name__ == "__main__":
    main()

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

import base64
import io
import os
import time
import urllib.error
import urllib.request

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = Path(__file__).resolve().parent
MODELS = HERE / "models"
GAP = 0.18  # breath between scenes, seconds
SUBCUT_OVER = 3.4  # scenes longer than this get a second camera angle halfway (shots ~2-3 s)


# Tried in order; each has its own small free daily quota (e.g. 10 requests/day).
GEMINI_TTS = ["gemini-3.8-flash-tts", "gemini-2.5-flash-preview-tts", "gemini-3.8-flash-lite-tts"]
NARRATOR = ("Read this line like an energetic, curious American YouTube Shorts narrator, "
            "fast but clear, with natural emphasis: ")


def gemini_key():
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"]
    cfg = Path.home() / ".config/watch/.env"
    if cfg.exists():
        for line in cfg.read_text().splitlines():
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip()
    return None


def gemini_tts(text, voice, rate, tries=6):
    """Natural narration from Gemini TTS (free tier). Returns float32 mono at `rate`."""
    body = {"contents": [{"parts": [{"text": NARRATOR + text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    for i in range(tries):
        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_TTS[i % len(GEMINI_TTS)]}:generateContent",
            data=json.dumps(body).encode(), headers={"x-goog-api-key": gemini_key(), "Content-Type": "application/json"})
        try:
            d = json.load(urllib.request.urlopen(req, timeout=120))
            raw = base64.b64decode(d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
            break
        except (urllib.error.HTTPError, urllib.error.URLError, KeyError) as e:
            if i == tries - 1:
                raise RuntimeError(f"Gemini TTS failed: {e}")
            time.sleep(3)
    if raw[:4] == b"RIFF":  # noqa: SIM108
        data, sr = sf.read(io.BytesIO(raw), dtype="float32")
    else:  # raw 16-bit PCM, 24 kHz mono
        data, sr = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768, 24000
    if sr != rate:
        data = np.interp(np.linspace(0, len(data), int(len(data) * rate / sr), endpoint=False),
                         np.arange(len(data)), data).astype(np.float32)
    return data


def split_lines(audio, rate, lines):
    """Split one narration take into per-line chunks at the pauses between lines.

    Chooses the N-1 pauses (dynamic programming) whose resulting chunk lengths best match each
    line's expected share of the take (by letters), preferring longer pauses."""
    win = int(0.02 * rate)
    env = np.array([np.sqrt(np.mean(audio[i:i + win] ** 2)) for i in range(0, len(audio) - win, win)])
    quiet = env < max(0.008, 0.06 * np.percentile(env, 95))
    gaps, start = [], None  # (center seconds, length seconds)
    for i, q in enumerate(np.append(quiet, False)):
        if q and start is None:
            start = i
        elif not q and start is not None:
            if (i - start) * 0.02 >= 0.15 and start > 0:
                gaps.append(((start + i) / 2 * 0.02, (i - start) * 0.02))
            start = None
    n = len(lines)
    if len(gaps) < n - 1:
        return None
    total = len(audio) / rate
    weight = [max(1, len(re.sub(r"[^A-Za-z0-9]", "", l))) for l in lines]
    expect = [total * w / sum(weight) for w in weight]
    G = len(gaps)
    INF = float("inf")
    # cost[k][j]: best cost placing boundary k (0-based) at gap j
    cost = [[INF] * G for _ in range(n - 1)]
    back = [[-1] * G for _ in range(n - 1)]
    seg = lambda a, b, k: ((b - a) - expect[k]) ** 2 / expect[k]
    for j in range(G):
        cost[0][j] = seg(0, gaps[j][0], 0) - 0.5 * gaps[j][1]
    for k in range(1, n - 1):
        for j in range(k, G):
            for i in range(k - 1, j):
                c = cost[k - 1][i] + seg(gaps[i][0], gaps[j][0], k) - 0.5 * gaps[j][1]
                if c < cost[k][j]:
                    cost[k][j], back[k][j] = c, i
    last = min(range(G), key=lambda j: cost[n - 2][j] + seg(gaps[j][0], total, n - 1))
    picks = [last]
    for k in range(n - 2, 0, -1):
        picks.append(back[k][picks[-1]])
    edges = [0.0, *[gaps[j][0] for j in reversed(picks)], total]
    return [audio[int(a * rate):int(b * rate)] for a, b in zip(edges, edges[1:])]


def trim(data, rate):
    loud = np.where(np.abs(data) > 0.02)[0]
    if len(loud):
        data = data[max(0, loud[0] - int(0.05 * rate)): loud[-1] + int(0.12 * rate)]
    return data


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
    ap.add_argument("--engine", choices=["gemini", "kokoro"], default="gemini",
                    help="gemini = natural Gemini TTS (needs GEMINI_API_KEY); kokoro = offline fallback")
    ap.add_argument("--gemini-voice", default="Charon", help="Gemini voice, e.g. Charon, Puck, Fenrir, Orus")
    ap.add_argument("--lang", default="en-us")
    args = ap.parse_args()

    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    engine = args.engine if (args.engine == "kokoro" or gemini_key()) else "kokoro"
    kokoro = None

    def speak(text):
        nonlocal kokoro
        if kokoro is None:
            kokoro = Kokoro(str(MODELS / "kokoro-v1.0.int8.onnx"), str(MODELS / "voices-v1.0.bin"))
        return kokoro.create(text, voice=args.voice, speed=args.speed, lang=args.lang)

    def gemini_takes():
        """One Gemini request for the whole script (the free tier allows very few requests)."""
        lines = [s["narration"] for s in plan["scenes"]]
        text = ("Pause for one full second between each of these lines.\n" + "\n".join(lines))
        # Cache the take: the free tier allows only a few requests per day.
        import hashlib
        cache = HERE / "out" / f"take-{hashlib.sha1((args.gemini_voice + text).encode()).hexdigest()[:12]}.wav"
        if cache.exists():
            audio, _ = sf.read(cache, dtype="float32")
        else:
            audio = gemini_tts(text, args.gemini_voice, 24000)
            cache.parent.mkdir(exist_ok=True)
            sf.write(cache, audio, 24000)
        parts = split_lines(audio, 24000, lines)
        if not parts:
            raise RuntimeError("could not split the narration into lines")
        return [trim(p, 24000) for p in parts]

    takes = None
    if engine == "gemini":
        try:
            takes = gemini_takes()
        except RuntimeError as e:
            print(f"{e}; using Kokoro")
            engine = "kokoro"

    def voice_all():
        chunks, t, rate = [], 0.0, 24000
        for n, scene in enumerate(plan["scenes"]):
            samples, rate = (trim(takes[n], 24000), 24000) if takes else speak(scene["narration"])
            samples = samples.astype(np.float32)
            speech = len(samples) / rate
            scene["start"] = round(t, 3)
            scene["duration"] = round(speech + GAP, 3)
            scene["words"] = word_times(scene["narration"], t + 0.05, speech - 0.12)
            # Second camera angle halfway through long scenes (offset in seconds from scene start).
            scene["cuts"] = [round(scene["duration"] / 2, 3)] if scene["duration"] > SUBCUT_OVER else []
            chunks += [samples, np.zeros(int(GAP * rate), dtype=np.float32)]
            t += speech + GAP
        return chunks, t, rate

    chunks, t, rate = voice_all()
    print(f"voice engine: {engine}")

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

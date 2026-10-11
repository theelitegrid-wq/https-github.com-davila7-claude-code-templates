"""Measure the editing style of reference videos: the numbers a renderer can copy.

usage: python metrics.py VIDEO [VIDEO ...] [--out DIR] [--threshold 0.3]

For each video prints duration, aspect, cut times, shot-length stats, cuts per minute,
brightness/saturation, loudness, and writes a contact sheet of every shot plus a 4 fps strip
of the first 3 seconds (the hook) to DIR. Needs ffmpeg/ffprobe only.
"""
import argparse
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, errors="replace")


def probe(path):
    out = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    data = json.loads(out.stdout or "{}")
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    num, _, den = (video.get("avg_frame_rate") or "0/1").partition("/")
    return {
        "duration": float(data.get("format", {}).get("duration", 0) or 0),
        "width": int(video.get("width", 0)),
        "height": int(video.get("height", 0)),
        "fps": round(float(num) / float(den or 1), 2) if float(den or 1) else 0,
        "has_audio": any(s.get("codec_type") == "audio" for s in data.get("streams", [])),
    }


def cuts(path, threshold):
    out = run(["ffmpeg", "-hide_banner", "-i", str(path), "-vf", f"select='gt(scene,{threshold})',showinfo",
               "-an", "-f", "null", "-"])
    return [round(float(t), 2) for t in re.findall(r"pts_time:([0-9.]+)", out.stderr)]


def picture(path):
    out = run(["ffmpeg", "-hide_banner", "-i", str(path), "-vf", "fps=2,signalstats,metadata=print",
               "-an", "-f", "null", "-"])
    def avg(key):
        vals = [float(v) for v in re.findall(rf"lavfi\.signalstats\.{key}=([0-9.]+)", out.stderr)]
        return round(statistics.mean(vals), 1) if vals else None
    return {"brightness_0_255": avg("YAVG"), "saturation_0_255": avg("SATAVG")}


def loudness(path):
    out = run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "ebur128", "-vn", "-f", "null", "-"])
    m = re.findall(r"I:\s+(-?[0-9.]+) LUFS", out.stderr)
    return float(m[-1]) if m else None


def sheets(path, cut_times, duration, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(path).stem
    # one frame from the middle of every shot
    bounds = [0.0, *cut_times, duration]
    mids = [round((a + b) / 2, 2) for a, b in zip(bounds, bounds[1:]) if b > a][:40]
    frames = []
    for i, t in enumerate(mids):
        f = out_dir / f"{stem}_shot{i:02d}.jpg"
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", str(path), "-frames:v", "1",
             "-vf", "scale=240:-2", str(f)])
        if f.exists():
            frames.append(f)
    sheet = out_dir / f"{stem}_shots.jpg"
    if frames:
        cols = min(8, len(frames))
        rows = (len(frames) + cols - 1) // cols
        run(["ffmpeg", "-v", "error", "-y", "-i", str(out_dir / f"{stem}_shot%02d.jpg"),
             "-vf", f"tile={cols}x{rows}", "-frames:v", "1", str(sheet)])
        for f in frames:
            f.unlink()
    hook = out_dir / f"{stem}_hook.jpg"
    run(["ffmpeg", "-v", "error", "-y", "-t", "3", "-i", str(path), "-vf",
         "fps=4,scale=180:-2,tile=12x1", "-frames:v", "1", str(hook)])
    return {"shots_sheet": str(sheet) if sheet.exists() else None,
            "hook_strip": str(hook) if hook.exists() else None, "shot_midpoints": mids}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("videos", nargs="+")
    ap.add_argument("--out", default="style-study-out")
    ap.add_argument("--threshold", type=float, default=0.3, help="scene-change sensitivity (lower = more cuts)")
    args = ap.parse_args()
    out_dir = Path(args.out)
    report = []
    for v in args.videos:
        info = probe(v)
        if not info["duration"]:
            print(f"skip {v}: not a readable video", file=sys.stderr)
            continue
        c = [t for t in cuts(v, args.threshold) if 0.2 < t < info["duration"] - 0.2]
        bounds = [0.0, *c, info["duration"]]
        shots = [round(b - a, 2) for a, b in zip(bounds, bounds[1:]) if b - a > 0.05]
        entry = {
            "video": v,
            **info,
            "aspect": f"{info['width']}x{info['height']}" + (" vertical" if info["height"] > info["width"] else " horizontal"),
            "cuts": len(c),
            "cut_times": c,
            "cuts_per_minute": round(len(c) / info["duration"] * 60, 1),
            "shot_seconds": {
                "mean": round(statistics.mean(shots), 2),
                "median": round(statistics.median(shots), 2),
                "min": min(shots),
                "max": max(shots),
            },
            "first_cut_at": c[0] if c else None,
            **picture(v),
            "loudness_lufs": loudness(v) if info["has_audio"] else None,
            **sheets(v, c, info["duration"], out_dir),
        }
        report.append(entry)
        print(json.dumps(entry, indent=2))
    if len(report) > 1:
        def med(k, sub=None):
            vals = [r[k][sub] if sub else r[k] for r in report if (r[k][sub] if sub else r[k]) is not None]
            return round(statistics.median(vals), 2) if vals else None
        print(json.dumps({"summary_across_videos": {
            "videos": len(report),
            "median_duration": med("duration"),
            "median_cuts_per_minute": med("cuts_per_minute"),
            "median_shot_seconds": med("shot_seconds", "median"),
            "median_first_cut_at": med("first_cut_at"),
            "median_brightness": med("brightness_0_255"),
            "median_saturation": med("saturation_0_255"),
            "median_loudness_lufs": med("loudness_lufs"),
        }}, indent=2))


if __name__ == "__main__":
    main()

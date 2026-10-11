"""Generate 3D-animated scene clips with Google Veo (the model behind Google Flow) via the Gemini API.

Needs GEMINI_API_KEY on a project with billing enabled: Veo has no free API tier.
"""
import os
import time
from pathlib import Path

from google import genai
from google.genai import errors, types

FALLBACK_MODEL = "veo-3.1-generate-preview"


def _generate(client, model, prompt, out, aspect, seconds, negative):
    operation = client.models.generate_videos(
        model=model,
        source=types.GenerateVideosSource(prompt=prompt),
        config=types.GenerateVideosConfig(
            aspect_ratio=aspect,
            duration_seconds=seconds,
            negative_prompt=negative,
            number_of_videos=1,
        ),
    )
    while not operation.done:
        time.sleep(10)
        operation = client.operations.get(operation)
    if operation.error:
        raise RuntimeError(f"Veo failed: {operation.error}")
    video = operation.result.generated_videos[0].video
    client.files.download(file=video)
    video.save(str(out))


def scene_clips(scenes, style, out_dir, aspect="9:16", seconds=8, model=None, negative=""):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    model = model or FALLBACK_MODEL
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    clips = []
    for i, scene in enumerate(scenes, 1):
        out = out_dir / f"scene-{i:02d}.mp4"
        prompt = f"{scene['visual']}. {style}"
        print(f"Veo scene {i}/{len(scenes)}: {scene['visual'][:80]}", flush=True)
        try:
            _generate(client, model, prompt, out, aspect, seconds, negative)
        except errors.ClientError as exc:
            if exc.code != 404 or model == FALLBACK_MODEL:
                raise
            print(f"{model} not found, falling back to {FALLBACK_MODEL}", flush=True)
            model = FALLBACK_MODEL
            _generate(client, model, prompt, out, aspect, seconds, negative)
        clips.append(out)
    return clips

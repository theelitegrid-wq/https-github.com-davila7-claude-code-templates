# AI YouTube Channel Autopilot

Picks a fresh topic in your niche every day, writes a scene-by-scene script, renders a
3D-animated short with voiceover and word-by-word captions, uploads it to YouTube, and
remembers what it posted so it never repeats. **Everything in the default setup is free.**

Default style: fast-cut, 3D-animated "what happens if..." shorts, rendered by `studio/`
(Remotion + three.js on CPU, no GPU or paid API) with the open-source Kokoro voice.
Example: `studio/examples/no-sleep-11-days.json`.

| `visuals:` in `automation/channel.yaml` | Look | Cost |
|---|---|---|
| `studio` (default) | 3D animated: a realistic person reacting, plus x-ray body, blood-vessel fly-through, organs, planets, explosions, viruses | free |
| `stock` | Pexels stock footage | free |
| `veo` | AI-generated cinematic scenes from Google Veo | paid per second |

| Part | Source | Cost |
|---|---|---|
| Free 3D animation | `studio/` (Remotion + three.js, this repo) | free |
| Voice for studio | [Kokoro](https://github.com/thewh1teagle/kokoro-onnx) (open source, runs offline) | free |
| Optional AI scenes | Google Veo 3.1 via Gemini API (`automation/veo.py`) | **paid per second**, no free API tier |
| Daily video engine | [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) (MIT) | free |
| Premium/custom videos in Claude Code | [digitalsamba/claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit) (MIT) | free core, AI clips ~cents |
| Claude skills: Remotion (12), ffmpeg, frontend-design | [remotion-dev/skills](https://github.com/remotion-dev/skills) (official) + toolkit | free |
| Script writer | Claude (your subscription) or Gemini free tier | free |
| Voice | Microsoft Edge TTS | free |
| Footage | Pexels API | free |
| Upload | YouTube Data API v3 | free (~6 uploads/day quota) |

## Setup (about 20 minutes, once)

1. **Pexels key** – only for `visuals: stock`; skip it otherwise. https://www.pexels.com/api/
2. **Script writer**, pick one:
   - Claude subscription: on your computer run `claude setup-token` and copy the token, or
   - Gemini (free): https://aistudio.google.com/app/apikey
   - For `visuals: veo` (3D animation) the Gemini key's Google Cloud project must have **billing
     enabled**. Check current Veo prices at https://ai.google.dev/gemini-api/docs/pricing and set a
     budget alert in Google Cloud. Use `veo_model: veo-3.1-fast-generate-preview` and fewer
     `scenes` to spend less.
3. **YouTube upload access**:
   1. https://console.cloud.google.com → new project → enable **YouTube Data API v3**.
   2. OAuth consent screen → External → add yourself as a test user, then **Publish app**
      (in "Testing" mode refresh tokens expire after 7 days).
   3. Credentials → Create OAuth client ID → **Desktop app** → download the JSON.
   4. On your computer: `pip install google-auth-oauthlib && python automation/get_youtube_token.py client_secret.json`
      and sign in with the channel's Google account.
4. **GitHub → Settings → Secrets and variables → Actions**, add:
   `PEXELS_API_KEY` (only for `visuals: stock`), `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`, and either
   `CLAUDE_CODE_OAUTH_TOKEN` or `GEMINI_API_KEY`.
5. Edit `automation/channel.yaml` (niche, voice, Shorts vs long-form, privacy).
6. **Actions → Daily video → Run workflow** with *dry run* ticked. Download the video artifact and watch it.
   Untick dry run when happy. After that it runs every day by itself.

## Run locally / in a Claude Code session

```bash
bash setup.sh                       # installs skills into .claude/skills and engines into vendor/
export PEXELS_API_KEY=... GEMINI_API_KEY=...   # plus YT_* to upload
DRY_RUN=1 vendor/MoneyPrinterTurbo/.venv/bin/python automation/daily.py

# render a hand-written plan (no API keys at all)
cd studio && .venv/bin/python voice.py examples/no-sleep-11-days.json \
  && npx remotion render src/index.ts Short out/test.mp4 --props=public/plan.json
```

### Change the person

The default character is Michelle (a Mixamo character from the three.js examples). To use any
other person, e.g. a regular guy in a hoodie:

1. Sign in free at https://www.mixamo.com → Characters → pick one → Download → FBX, "T-pose".
2. Convert to glb: `npx fbx2gltf -i character.fbx -o person.glb` (or Blender: import FBX, export glTF).
3. Save it as `studio/public/models/person.glb`. Animations are retargeted automatically
   (`studio/src/retarget.ts`), so any Mixamo character works.

Mixamo characters and animations are free for commercial videos; just don't share the raw model files.

Preview and tweak the 3D scenes live with `cd studio && npm run studio`. Scene types live in
`studio/src/scenes.tsx`; add your own and list them in the prompt in `automation/daily.py`.

For flagship long-form videos, open Claude Code in this repo and use `/remotion-create` (or open
`vendor/claude-code-video-toolkit` and use `/video`).

## Learn a style from reference videos

- `/watch <file or URL>`: the [watch skill](https://github.com/bradautomates/claude-video) (MIT)
  pulls scene frames and the transcript so Claude can see a video.
- `/style-study`: measures reference videos (cuts, shot length, hook timing, color, loudness,
  contact sheets) with `.claude/skills/style-study/scripts/metrics.py`, then writes the rules
  into `automation/style.md` and adjusts the renderer.
- `research/channels.md`: 30 big creator-led channels and 30 faceless channels, with how
  each makes its videos.

## Google Flow

Flow (labs.google/flow) has no API, so it cannot be automated; automating its website would break
its terms. Its free/plan credits are still useful by hand: make a hero scene in Flow, then render it
locally with `--video-source local --video-materials your_clip.mp4` in `vendor/MoneyPrinterTurbo`.

## Read this before going public

- YouTube demonetizes "mass-produced, repetitious" content (policy update July 2025). Keep
  `privacy: private` for the first week, watch every video, fix the prompt in `channel.yaml`,
  then switch to `public`. Add your own edits, opinions or voice where you can.
- AI disclosure is on by default (`containsSyntheticMedia`). Leave it on.
- Growth comes from the niche, titles/thumbnails and retention. Expect weeks, not days.

## AI shots on a free GPU (visuals: ai)

Every line gets its own AI-generated shot in the Zack D. Films style (the same character, Jake,
in everyday American places; x-ray cutaways for inside the body), made with open models on
Kaggle's free GPU (~30 h/week): Z-Image-Turbo stills (SDXL fallback) with camera moves, and
optional Wan 2.2 clips (`animate_shots` in `automation/channel.yaml`; slow on free GPUs).

1. Create a free account at kaggle.com and verify your phone number (needed for GPU + internet).
2. kaggle.com → Settings → API → **Create New Token** (downloads `kaggle.json` with username and key).
3. Add GitHub secrets `KAGGLE_USERNAME` and `KAGGLE_KEY` from that file.

If the GPU job fails, that day's video falls back to the procedural 3D studio. Narration uses
Gemini TTS (free tier, one request per video) with Kokoro as the offline fallback.

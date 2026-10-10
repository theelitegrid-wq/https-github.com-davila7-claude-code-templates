# AI YouTube Channel Autopilot

Picks a fresh topic in your niche every day, writes a scene-by-scene script, generates
3D-animated scenes with Google Veo (the model behind Google Flow), adds voiceover, captions and
music, uploads to YouTube, and remembers what it posted so it never repeats.

Default style: fast, 3D-animated "what happens if..." shorts. Set `visuals: stock` in
`automation/channel.yaml` for a fully free version with Pexels stock footage instead.

| Part | Source | Cost |
|---|---|---|
| 3D-animated scenes | Google Veo 3.1 via Gemini API (`automation/veo.py`) | **paid per second**, no free API tier |
| Daily video engine | [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) (MIT) | free |
| Premium/custom videos in Claude Code | [digitalsamba/claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit) (MIT) | free core, AI clips ~cents |
| Claude skills: Remotion (12), ffmpeg, frontend-design | [remotion-dev/skills](https://github.com/remotion-dev/skills) (official) + toolkit | free |
| Script writer | Claude (your subscription) or Gemini free tier | free |
| Voice | Microsoft Edge TTS | free |
| Footage | Pexels API | free |
| Upload | YouTube Data API v3 | free (~6 uploads/day quota) |

## Setup (about 20 minutes, once)

1. **Pexels key** (only needed for `visuals: stock`) – https://www.pexels.com/api/ → copy the key.
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
```

For flagship long-form videos, open Claude Code in this repo and use `/remotion-create` (or open
`vendor/claude-code-video-toolkit` and use `/video`).

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

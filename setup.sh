#!/usr/bin/env bash
# Installs the video skills and engines this repo automates.
# Every source is pinned to the commit that was reviewed; bump a SHA deliberately to upgrade.
set -euo pipefail
cd "$(dirname "$0")"

REMOTION_SKILLS_SHA=32b241b97f4e0e4ab61fe9a41b05e6e64503f8c5      # remotion-dev/skills (official)
VIDEO_TOOLKIT_SHA=4e7b296625e1ec3c4dc8bfac6bc0bdcbaef60962        # digitalsamba/claude-code-video-toolkit (MIT)
MONEYPRINTER_SHA=4204d0f39afa8ada6f3edc31604141f959fe254e         # harry0703/MoneyPrinterTurbo (MIT)
THREEJS_SHA=11738a9d55e502fb484cefffcea3a66dc44e9fe9               # mrdoob/three.js: Mixamo character + motions
WATCH_SKILL_SHA=03ceb42f7fa2c4439aca01752118044baabffb8f          # bradautomates/claude-video: /watch skill (MIT)

fetch() { # repo sha dest
  rm -rf "$3"; mkdir -p "$3"
  git -C "$3" init -q
  git -C "$3" fetch -q --depth 1 "https://github.com/$1" "$2"
  git -C "$3" checkout -q FETCH_HEAD
}

echo "==> Video engines"
fetch harry0703/MoneyPrinterTurbo "$MONEYPRINTER_SHA" vendor/MoneyPrinterTurbo
fetch digitalsamba/claude-code-video-toolkit "$VIDEO_TOOLKIT_SHA" vendor/claude-code-video-toolkit

echo "==> Claude skills -> .claude/skills"
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
fetch remotion-dev/skills "$REMOTION_SKILLS_SHA" "$TMP/remotion"
mkdir -p .claude/skills
cp -r "$TMP"/remotion/skills/* .claude/skills/
cp -r vendor/claude-code-video-toolkit/.claude/skills/{ffmpeg,frontend-design} .claude/skills/
fetch bradautomates/claude-video "$WATCH_SKILL_SHA" "$TMP/watch"
rm -rf .claude/skills/watch && cp -r "$TMP/watch/skills/watch" .claude/skills/watch
command -v yt-dlp >/dev/null || pip install --quiet --user "yt-dlp[default]" || true

if [[ "${SKIP_PYTHON:-0}" != 1 ]]; then
  echo "==> Python deps for MoneyPrinterTurbo (needs uv + ffmpeg)"
  command -v uv >/dev/null || pip install --quiet uv
  (cd vendor/MoneyPrinterTurbo && uv sync --quiet)
  uv pip install --quiet --python vendor/MoneyPrinterTurbo/.venv google-api-python-client google-auth google-genai pyyaml requests
fi
if [[ "${SKIP_STUDIO:-0}" != 1 ]]; then
  echo "==> Free 3D studio (Remotion + three.js) and Kokoro voice"
  (cd studio && npm ci --no-audit --no-fund)
  mkdir -p studio/models
  KOKORO=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
  for f in kokoro-v1.0.int8.onnx voices-v1.0.bin; do
    [[ -s studio/models/$f ]] || curl -sSLf -o studio/models/$f "$KOKORO/$f"
  done
  command -v uv >/dev/null || pip install --quiet uv
  if [[ ! -s studio/public/models/person.glb || ! -s studio/public/models/Xbot.glb ]]; then
    git init -q "$TMP/three"
    git -C "$TMP/three" sparse-checkout set --no-cone examples/models/gltf/Michelle.glb examples/models/gltf/Xbot.glb
    git -C "$TMP/three" fetch -q --depth 1 --filter=blob:none https://github.com/mrdoob/three.js "$THREEJS_SHA"
    git -C "$TMP/three" checkout -q FETCH_HEAD
    mkdir -p studio/public/models
    [[ -s studio/public/models/person.glb ]] || cp "$TMP/three/examples/models/gltf/Michelle.glb" studio/public/models/person.glb
    cp "$TMP/three/examples/models/gltf/Xbot.glb" studio/public/models/Xbot.glb
  fi
  [[ -d studio/.venv ]] || uv venv -q studio/.venv --python 3.11
  uv pip install --quiet --python studio/.venv kokoro-onnx==0.6.1 soundfile numpy
fi
echo "Done. Edit automation/channel.yaml, then: python automation/daily.py"

#!/usr/bin/env bash
# Installs the video skills and engines this repo automates.
# Every source is pinned to the commit that was reviewed; bump a SHA deliberately to upgrade.
set -euo pipefail
cd "$(dirname "$0")"

REMOTION_SKILLS_SHA=32b241b97f4e0e4ab61fe9a41b05e6e64503f8c5      # remotion-dev/skills (official)
VIDEO_TOOLKIT_SHA=4e7b296625e1ec3c4dc8bfac6bc0bdcbaef60962        # digitalsamba/claude-code-video-toolkit (MIT)
MONEYPRINTER_SHA=4204d0f39afa8ada6f3edc31604141f959fe254e         # harry0703/MoneyPrinterTurbo (MIT)

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

if [[ "${SKIP_PYTHON:-0}" != 1 ]]; then
  echo "==> Python deps for MoneyPrinterTurbo (needs uv + ffmpeg)"
  command -v uv >/dev/null || pip install --quiet uv
  (cd vendor/MoneyPrinterTurbo && uv sync --quiet)
  uv pip install --quiet --python vendor/MoneyPrinterTurbo/.venv google-api-python-client google-auth google-genai pyyaml requests
fi
echo "Done. Edit automation/channel.yaml, then: python automation/daily.py"

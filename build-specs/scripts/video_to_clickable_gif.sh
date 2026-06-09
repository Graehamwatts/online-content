#!/usr/bin/env bash
# video_to_clickable_gif.sh — turn any video into a standardized "clickable" GIF
# for SMS/email: vertical, short loop, centered play-button, "TAP TO WATCH" caption.
# Requires: ffmpeg.
#
# Usage:
#   ./video_to_clickable_gif.sh INPUT OUTPUT.gif ["CAPTION"] [START_SEC] [DURATION_SEC]
# Examples:
#   ./video_to_clickable_gif.sh buyer.mp4 buyer.gif
#   ./video_to_clickable_gif.sh seller.mp4 seller.gif "TAP TO WATCH" 2 3.5
#
# Env overrides: FONT=/path/to/bold.ttf  WIDTH=480  FPS=12
set -euo pipefail
IN="${1:?input video required}"
OUT="${2:?output .gif path required}"
CAPTION="${3:-TAP TO WATCH}"
START="${4:-0}"
DUR="${5:-3.5}"
# Bold font with a play glyph (▶). Linux default below; change for Mac/Win.
FONT="${FONT:-/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf}"
WIDTH="${WIDTH:-480}"
FPS="${FPS:-12}"
ffmpeg -y -ss "$START" -t "$DUR" -i "$IN" -vf "
fps=${FPS},scale=${WIDTH}:-2:flags=lanczos,
drawtext=fontfile=${FONT}:text='▶':fontsize=120:fontcolor=white@0.95:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.40:boxborderw=45,
drawtext=fontfile=${FONT}:text='${CAPTION}':fontsize=34:fontcolor=white:x=(w-text_w)/2:y=h-95:box=1:boxcolor=black@0.60:boxborderw=16,
split[s0][s1];[s0]palettegen=stats_mode=diff[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3" -loop 0 "$OUT"
echo "Created $OUT"

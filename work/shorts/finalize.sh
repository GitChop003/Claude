#!/usr/bin/env bash
# Rendu final d'un short : 9:16 (Reels/TikTok), 4:5 (LinkedIn, recadrage de la zone sûre), couverture.
# Usage : finalize.sh <dossier du short> <MOTCLE> [date]
set -euo pipefail
dir="$1"; kw="$2"; day="${3:-2026-11-08}"; ver="${4:-v1}"
cd "$dir"
mkdir -p renders
reel="renders/${day}_${kw}_reel_${ver}.mp4"
npx hyperframes render -q high -w 2 -o "${reel%.mp4}_raw.mp4" .
# Voix ramenée à -14 LUFS sur le rendu final (le mixage stéréo du rendu peut monter à -11)
ffmpeg -v error -y -i "${reel%.mp4}_raw.mp4" -c:v copy -af "loudnorm=I=-14:TP=-1.5:LRA=9,alimiter=limit=0.89" -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$reel"
rm -f "${reel%.mp4}_raw.mp4"
# 4:5 : tout le texte important est déjà dans la bande 1080×1350 centrée (y = 285 → 1635)
ffmpeg -v error -y -i "$reel" -vf "crop=1080:1350:0:285" -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p \
  -c:a copy -movflags +faststart "renders/${day}_${kw}_linkedin_${ver}.mp4"
# Couverture : l'accroche plein écran (même style que le texte écran), en 9:16 et en 4:5
ffmpeg -v error -y -ss 1.2 -i "$reel" -frames:v 1 "renders/${day}_${kw}_couverture_9x16.png"
ffmpeg -v error -y -ss 1.2 -i "$reel" -frames:v 1 -vf "crop=1080:1350:0:285" "renders/${day}_${kw}_couverture_4x5.png"
ls -la renders

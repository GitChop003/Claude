#!/usr/bin/env bash
# Production d'un lot de shorts : découpe (2 voies en parallèle), puis composition + rendu + exports.
# Usage : batch.sh <scratchpad> "s6:MOTCLE s7:MOTCLE ..."
set -uo pipefail
S="$1"; LIST="$2"; cd "$(dirname "$0")"
G="$(cat grade.txt)"; ids=(); for p in $LIST; do ids+=("${p%%:*}"); done
cut_one() { python3 cut.py specs/$1.json "$S/rt" "$S/rushes" ../../videos/shorts/$1/assets "$G" || echo "CUT_FAIL $1"; }
lane() { for k in "$@"; do cut_one "$k"; done; }
a=(); b=(); i=0; for k in "${ids[@]}"; do if (( i % 2 == 0 )); then a+=("$k"); else b+=("$k"); fi; i=$((i+1)); done
lane "${a[@]}" & lane "${b[@]}" & wait
for p in $LIST; do
  k=${p%%:*}; kw=${p##*:}
  python3 build.py specs/$k.json ../../videos/shorts/$k/assets/words.json ../../videos/shorts/$k || { echo "BUILD_FAIL $k"; continue; }
  if python3 -c "import json,sys;sys.exit(0 if json.load(open('specs/$k.json')).get('choc',{}).get('behind') else 1)"; then
    python3 matte_cut.py "$S/models/rvm.onnx" ../../videos/shorts/$k && python3 build.py specs/$k.json ../../videos/shorts/$k/assets/words.json ../../videos/shorts/$k
  fi
  ./finalize.sh "$(cd ../../videos/shorts/$k && pwd)" "$kw" || { echo "RENDER_FAIL $k"; continue; }
  f=../../videos/shorts/$k/renders/2026-11-08_${kw}_reel_v1.mp4
  ffmpeg -v error -y -i "$f" -c:v libx264 -crf 21 -preset slow -pix_fmt yuv420p -c:a copy -movflags +faststart "${f%.mp4}_livraison.mp4"
  echo "DONE $k"
done
echo BATCH_DONE

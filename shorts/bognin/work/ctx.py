"""Print words (source time + text) in a window, 8 per line.  ctx.py A B"""
import json, sys
a, b = float(sys.argv[1]), float(sys.argv[2])
W = [w for w in json.load(open("/home/claude/claude/shorts/bognin/work/full.words.json")) if a <= w["start"] <= b]
for i in range(0, len(W), 8):
    print("  ".join(f"{w['start']:.2f} {w['text']}" for w in W[i:i + 8]))

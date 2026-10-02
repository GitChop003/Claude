"""Build an edit decision list: editorial keep-ranges -> word-level jump cuts (silences/stutters removed)."""
import json, sys
raw = json.load(open("raw_words.json")); words = json.load(open("words.json"))
name = sys.argv[1]
KEEP = json.load(open(f"{name}.keep.json"))   # [[src_start, src_end, label], ...]
GAP, PRE, POST = 0.30, 0.10, 0.14
segs = []
for a, b, *_ in KEEP:
    ws = [w for w in raw if w["start"] >= a - 0.05 and w["end"] <= b + 0.2 and w["start"] < b]
    cur = None
    for w in ws:
        s, e = max(a, w["start"] - PRE), min(b, w["end"] + POST)
        if cur and w["start"] - cur[2] <= GAP: cur[1] = e; cur[2] = w["end"]
        else:
            if cur: segs.append(cur[:2])
            cur = [s, e, w["end"]]
    if cur: segs.append(cur[:2])
# avoid overlaps between neighbours
for i in range(1, len(segs)):
    if segs[i][0] < segs[i-1][1]: m = (segs[i][0] + segs[i-1][1]) / 2; segs[i-1][1] = m; segs[i][0] = m
segs = [[round(s, 3), round(e, 3)] for s, e in segs if e - s > 0.12]
# map source -> output time, carry caption words (whisper text) into output timeline
out_t, cap, cuts = 0.0, [], []
for s, e in segs:
    for w in words:
        mid = (w["start"] + w["end"]) / 2
        if s <= mid < e:
            cap.append({"text": w["text"], "start": round(out_t + max(w["start"], s) - s, 3), "end": round(out_t + min(w["end"], e) - s, 3)})
    out_t += e - s; cuts.append(round(out_t, 3))
json.dump({"segments": segs, "duration": round(out_t, 3), "cuts": cuts[:-1], "captions": cap}, open(f"{name}.edl.json", "w"), ensure_ascii=False, indent=1)
src = sum(b - a for a, b, *_ in KEEP)
print(f"{len(segs)} segments, {out_t:.2f}s output (editorial ranges {src:.2f}s)")
print(" ".join(c["text"] for c in cap))

"""Parakeet token timestamps -> word list (absolute source seconds).
Usage: words.py para.json OFFSET out.json"""
import json, sys
res, off, out = json.load(open(sys.argv[1])), float(sys.argv[2]), sys.argv[3]
W = []
for seg in res:
    toks = seg["tokens"]
    for k, t in enumerate(toks):
        txt, s = t["t"], t["s"]
        e = s + t.get("d", 0.08)
        if k + 1 < len(toks):
            e = min(max(e, s + 0.04), toks[k + 1]["s"])
        else:
            e = max(e, min(seg["end"], s + 0.35))
        if txt.startswith(" ") or not W or k == 0:
            W.append({"text": txt.strip(), "start": round(s + off, 3), "end": round(e + off, 3)})
        else:
            W[-1]["text"] += txt
            W[-1]["end"] = round(e + off, 3)
W = [w for w in W if w["text"]]
json.dump(W, open(out, "w"), ensure_ascii=False, indent=0)
for w in W:
    print(f'{w["start"]:8.2f} {w["end"]:8.2f}  {w["text"]}')

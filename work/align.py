import json, re, difflib, unicodedata
P = json.load(open("transcript.json")); W = json.load(open("whisper.json"))
def norm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9']", "", w)
out = []
for seg, wseg in zip(P, W):
    # parakeet words with times
    pw = []
    for t in seg["tokens"]:
        tok = t["t"]; end = t["s"] + t.get("d", 0.08)
        if tok.startswith(" ") or not pw:
            pw.append({"text": tok.strip(), "start": t["s"], "end": end})
        else:
            pw[-1]["text"] += tok; pw[-1]["end"] = end
    pw = [w for w in pw if norm(w["text"])]
    ww = [w for w in wseg["text"].split() if w]
    a = [norm(w["text"]) for w in pw]; b = [norm(w) for w in ww]
    times = [None] * len(ww)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1): times[j1 + k] = (pw[i1 + k]["start"], pw[i1 + k]["end"])
        elif tag == "replace" and i2 > i1:
            s0, e0 = pw[i1]["start"], pw[i2 - 1]["end"]; n = j2 - j1
            for k in range(n): times[j1 + k] = (s0 + (e0 - s0) * k / n, s0 + (e0 - s0) * (k + 1) / n)
    # interpolate missing
    for j in range(len(ww)):
        if times[j] is None:
            prev = next((times[k][1] for k in range(j - 1, -1, -1) if times[k]), seg["start"])
            nxt = next((times[k][0] for k in range(j + 1, len(ww)) if times[k]), seg["end"])
            run = [k for k in range(j, len(ww)) if times[k] is None]
            run = run[: next((i for i, k in enumerate(run) if k != j + i), len(run))]
            n = len(run)
            for i, k in enumerate(run): times[k] = (prev + (nxt - prev) * i / n, prev + (nxt - prev) * (i + 1) / n)
    for w, (s, e) in zip(ww, times):
        out.append({"text": w, "start": round(s, 3), "end": round(max(e, s + 0.05), 3)})
    out.append({"seg_end": True, "start": seg["start"], "end": seg["end"]})
json.dump([w for w in out if "text" in w], open("words.json", "w"), ensure_ascii=False, indent=0)
json.dump(P and [{"start": s["start"], "end": s["end"]} for s in P], open("vad.json", "w"))
# also parakeet raw words (true acoustic timing)
raw = []
for seg in P:
    for t in seg["tokens"]:
        if t["t"].startswith(" ") or not raw or raw[-1].get("_seg") != seg["start"]:
            raw.append({"text": t["t"].strip(), "start": t["s"], "end": t["s"] + t.get("d", .08), "_seg": seg["start"]})
        else:
            raw[-1]["text"] += t["t"]; raw[-1]["end"] = t["s"] + t.get("d", .08)
json.dump([{k: (round(v, 3) if isinstance(v, float) else v) for k, v in w.items() if k != "_seg"} for w in raw], open("raw_words.json", "w"), ensure_ascii=False, indent=0)
print(len(out), len(raw))

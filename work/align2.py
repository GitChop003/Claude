"""Whisper text (good French) on Parakeet anchors (exact where words match);
words in between are spread by character count over *speech-active* time (energy VAD), not wall time."""
import json, re, difflib, unicodedata, bisect
C = json.load(open("whisper_chunks.json")); SP = json.load(open("speech.json"))
def norm(w):
    w = unicodedata.normalize("NFD", w.lower()); w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", w)
def spread(lo, hi, weights):
    """split [lo,hi] by weights, measured in speech-active seconds"""
    iv = [(max(lo, s), min(hi, e)) for s, e in SP if e > lo and s < hi]
    tot_sp = sum(e - s for s, e in iv)
    if tot_sp < 0.05: iv, tot_sp = [(lo, hi)], max(hi - lo, 1e-3)
    def at(x):  # speech-seconds -> wall time
        for s, e in iv:
            if x <= e - s: return s + x
            x -= e - s
        return iv[-1][1]
    W = sum(weights); acc = 0; out = []
    for w in weights:
        out.append((at(tot_sp * acc / W), at(tot_sp * (acc + w) / W))); acc += w
    return out
res = []; stats = []
for c in C:
    pw = [w for w in c["pw"] if norm(w["text"])]; ww = c["text"].split()
    if not ww: continue
    a = [norm(w["text"]) for w in pw]; b = [norm(w) for w in ww]
    times = [None] * len(ww); matched = 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal" and (i2 - i1) >= 2 or (tag == "equal" and len(b[j1]) >= 4):
            for k in range(i2 - i1): times[j1 + k] = (pw[i1 + k]["start"], pw[i1 + k]["end"]); matched += 1
    stats.append((c["start"], round(matched / len(ww), 2)))
    j = 0
    while j < len(ww):
        if times[j] is None:
            k = j
            while k < len(ww) and times[k] is None: k += 1
            lo = times[j - 1][1] if j else c["start"]; hi = times[k][0] if k < len(ww) else c["end"]
            if hi <= lo: hi = lo + 0.1 * (k - j)
            for x, t in zip(range(j, k), spread(lo, hi, [max(2, len(b[y])) + 1 for y in range(j, k)])): times[x] = t
            j = k
        else: j += 1
    for w, (s, e) in zip(ww, times): res.append({"text": w, "start": round(s, 3), "end": round(max(e, s + 0.06), 3)})
json.dump(res, open("words2.json", "w"), ensure_ascii=False, indent=0)
print(len(res), "words; low-match segments:", [s for s in stats if s[1] < 0.6])

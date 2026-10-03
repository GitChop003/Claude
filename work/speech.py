"""Energy-based speech activity on the denoised voice track -> speech intervals (robust, ASR-independent)."""
import numpy as np, soundfile as sf, json
v, sr = sf.read("../media/voice_clean.wav", dtype="float32")
hop = int(0.01 * sr); n = len(v) // hop
rms = np.sqrt(np.mean(v[: n * hop].reshape(n, hop) ** 2, 1) + 1e-12); db = 20 * np.log10(rms)
floor = np.percentile(db, 10); peak = np.percentile(db, 97)
th = floor + 0.30 * (peak - floor)
act = db > th
# hangover / fill tiny holes (<120ms), drop blips (<60ms)
def runs(a):
    r, s = [], None
    for i, x in enumerate(a):
        if x and s is None: s = i
        if not x and s is not None: r.append([s, i]); s = None
    if s is not None: r.append([s, len(a)])
    return r
R = runs(act); M = []
for s, e in R:
    if M and s - M[-1][1] < 12: M[-1][1] = e
    else: M.append([s, e])
M = [[s / 100, e / 100] for s, e in M if e - s >= 6]
json.dump(M, open("speech.json", "w"))
print(f"floor {floor:.1f} dB, peak {peak:.1f} dB, threshold {th:.1f} dB, {len(M)} speech runs")
for a, b in [(324, 341), (463, 472), (486, 496)]:
    print(a, b, [(round(s, 2), round(e, 2)) for s, e in M if a <= s < b])

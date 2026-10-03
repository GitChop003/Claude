"""Original lo-fi background track, synthesized from scratch (deterministic, royalty-free)."""
import numpy as np, soundfile as sf, sys
SR = 48000; BPM = 84; BEAT = 60 / BPM; BAR = 4 * BEAT
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 300
rng = np.random.default_rng(7)
N = int(DUR * SR) + SR * 4
L = np.zeros(N); R = np.zeros(N)
def midi(n): return 440 * 2 ** ((n - 69) / 12)
def add(sig, t, pan=0.0, g=1.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N: return
    s = sig[: j - i] * g
    L[i:j] += s * np.cos((pan + 1) * np.pi / 4); R[i:j] += s * np.sin((pan + 1) * np.pi / 4)
def env(n, a, d):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / d)
def rhodes(note, dur, vel=1.0):
    n = int((dur + 1.5) * SR); t = np.arange(n) / SR; f = midi(note)
    s = (np.sin(2 * np.pi * f * t + 1.2 * np.exp(-t * 6) * np.sin(2 * np.pi * f * 2 * t))
         + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 3) + 0.12 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t * 5))
    e = env(n, 0.012, 1.4); rel = np.clip((dur + 0.4 - t) / 0.4, 0, 1)
    trem = 1 + 0.15 * np.sin(2 * np.pi * 4.2 * t)
    return s * e * rel * trem * vel * 0.16
def bass(note, dur):
    n = int((dur + 0.2) * SR); t = np.arange(n) / SR; f = midi(note)
    s = np.tanh(1.6 * np.sin(2 * np.pi * f * t)) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
    return s * env(n, 0.01, 0.9) * np.clip((dur - t) / 0.08, 0, 1) * 0.30
def kick():
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 45 + 75 * np.exp(-t * 28); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9) * 0.55
def snare():
    n = int(0.3 * SR); t = np.arange(n) / SR
    no = rng.standard_normal(n); no = np.convolve(no, np.ones(6) / 6, "same")
    return (0.5 * no * np.exp(-t * 22) + 0.3 * np.sin(2 * np.pi * 185 * t) * np.exp(-t * 30)) * 0.22
def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR); t = np.arange(n) / SR
    no = rng.standard_normal(n); no = no - np.convolve(no, np.ones(3) / 3, "same")
    return no * np.exp(-t * (14 if open_ else 70)) * 0.10
# Fmaj9 - Em7 - Dm9 - Cmaj7(add9)  (voiced around middle C)
CH = [([53, 57, 60, 64, 67], 41), ([52, 55, 59, 62, 66 - 0], 40), ([50, 53, 57, 60, 64], 38), ([48, 52, 55, 59, 62], 36)]
CH[1] = ([52, 55, 59, 62], 40)
nbars = int(DUR / BAR) + 1
for b in range(nbars):
    t0 = b * BAR; notes, root = CH[b % 4]; sect = (b // 8) % 4
    strum = 0.018
    for k, n in enumerate(notes):
        add(rhodes(n, BAR * 0.92, 0.9 + 0.1 * rng.random()), t0 + k * strum + 0.01 * rng.random(), pan=-0.35 + 0.7 * k / len(notes))
    if b % 2 == 1:   # little melodic answer on the off bars
        mel = [notes[-1] + 12, notes[-2] + 12, notes[-1] + 10]
        for k, n in enumerate(mel): add(rhodes(n, BEAT * 0.8, 0.45), t0 + BEAT * (2.5 + 0.5 * k), pan=0.4)
    if b < 2: continue    # intro: keys only
    drums = not (b % 16 in (14, 15))
    add(bass(root, BEAT * 1.4), t0); add(bass(root, BEAT * 0.9), t0 + BEAT * 2.5); add(bass(root + 7, BEAT * 0.8), t0 + BEAT * 3.5, g=0.7)
    if drums:
        for kb in (0, 2.5): add(kick(), t0 + kb * BEAT)
        for sb in (1, 3): add(snare(), t0 + sb * BEAT + 0.012, pan=0.05)
        for h in range(8):
            sw = 0.06 * BEAT if h % 2 else 0
            add(hat(open_=(h == 7 and b % 4 == 3)), t0 + h * BEAT / 2 + sw, pan=0.3, g=0.7 + 0.3 * (h % 2 == 0))
# vinyl crackle + hiss
cr = np.zeros(N); idx = rng.integers(0, N, int(DUR * 4)); cr[idx] = rng.standard_normal(len(idx)) * 0.07
cr += rng.standard_normal(N) * 0.0012; L += cr; R += np.roll(cr, 37)
# warm low-pass (one-pole, ~5 kHz) + gentle saturation
def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); acc = 0.0
    from scipy.signal import lfilter
    return lfilter([1 - a], [1, -a], x)
L = np.tanh(lp(L, 5200) * 1.1); R = np.tanh(lp(R, 5200) * 1.1)
out = np.stack([L, R], 1)[: int(DUR * SR)]
fade = int(2 * SR); out[:fade] *= np.linspace(0, 1, fade)[:, None]; out[-fade:] *= np.linspace(1, 0, fade)[:, None]
out /= np.max(np.abs(out)) / 0.8
sf.write(sys.argv[1], out.astype(np.float32), SR)
print("ok", out.shape[0] / SR)

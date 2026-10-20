"""Bognin shorts — edit engine (cut list, audio, plates).

Pipeline per short:
  editorial keep ranges  -> pauses shortened on the energy envelope, cut points snapped to the
  quietest neighbouring frame boundary (25 fps)  -> frame-exact cut of the 720p source
  -> voice: RNNoise denoise, 12 ms equal-power crossfades at every cut, loudnorm -14 LUFS
  -> plates: RVM person matte, light background blur, "4K" finish (denoise, lanczos, CAS, contrast)
     rendered twice: landscape 1920x1080 and portrait 1080x1920 (crop follows the speaker).
"""
import json, os, subprocess, sys
import numpy as np
import soundfile as sf

SCR = "/tmp/claude-0/-home-claude/3103370c-3a96-56b2-b40e-7458c05b9768/scratchpad"
SRC = f"{SCR}/src/source.mp4"
MODELS = f"{SCR}/models"
FPS = 25.0
FR = 1 / FPS


def load_env(a, b, sr=16000):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a}", "-to", f"{b}", "-i", SRC, "-ac", "1", "-ar", str(sr),
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    hop = int(0.01 * sr)
    n = len(x) // hop
    db = 20 * np.log10(np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1)) + 1e-6)
    return db - np.percentile(db, 95)          # dB relative to loud speech


def make_edl(keep, gap_db=-21, min_gap=0.18, pre=0.09, post=0.08, beats=None):
    """keep: [(a, b)] source seconds. beats: {source_time: pause_to_keep} for dramatic pauses."""
    beats = beats or {}
    a0, b0 = min(k[0] for k in keep) - 1, max(k[1] for k in keep) + 1
    db = load_env(a0, b0)
    t_of = lambda i: a0 + i * 0.01
    smooth = np.convolve(db, np.ones(5) / 5, "same")      # 50 ms: one stray frame doesn't break a pause
    sil = smooth < gap_db
    gaps, i = [], 0
    while i < len(sil):
        if sil[i]:
            j = i
            while j < len(sil) and sil[j]:
                j += 1
            if (j - i) * 0.01 >= min_gap:
                gaps.append((t_of(i), t_of(j)))
            i = j
        else:
            i += 1
    segs = []
    for a, b in keep:
        cur = a
        for g0, g1 in gaps:
            if g0 > a + 0.05 and g1 < b - 0.05:
                keep_pause = next((v for k, v in beats.items() if g0 - 0.3 <= k <= g1 + 0.3), None)
                if keep_pause:
                    cut0, cut1 = g0 + keep_pause / 2, g1 - keep_pause / 2
                else:
                    cut0, cut1 = g0 + pre, g1 - post
                if cut1 - cut0 > 0.08:
                    segs.append([cur, cut0])
                    cur = cut1
        segs.append([cur, b])

    def energy(t):
        k = int(round((t - a0) / 0.01))
        return db[max(0, k - 1):k + 2].mean()

    def snap(t):          # nearest frame boundary on the quieter side
        lo, hi = np.floor(t / FR) * FR, np.ceil(t / FR) * FR
        return round(lo if energy(lo) <= energy(hi) else hi, 4)

    segs = [(snap(s), snap(e)) for s, e in segs]
    segs = [(s, e) for s, e in segs if e - s >= 2 * FR]
    mp, o = [], 0.0
    for s, e in segs:
        mp.append((s, e, round(o, 4), round(e - s, 4)))
        o += e - s
    return mp, round(o, 4)


def src2out(mp, t):
    for s, e, o, d in mp:
        if t < s:
            return o
        if t < e:
            return o + t - s
    return mp[-1][2] + mp[-1][3]


def render_cut(mp, out_video, out_audio):
    """Frame-exact video cut (720p, near-lossless) + processed voice track."""
    expr = "+".join(f"between(t,{s - 0.5 * FR:.4f},{e - 0.5 * FR:.4f})" for s, e, o, d in mp)
    a, b = mp[0][0] - 0.5, mp[-1][1] + 0.5
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-to", f"{b}", "-copyts", "-i", SRC,
                    "-vf", f"select='{expr}',setpts=N/FRAME_RATE/TB", "-an", "-c:v", "libx264", "-preset", "medium",
                    "-crf", "10", "-pix_fmt", "yuv420p", "-r", "25", out_video], check=True)
    # voice: denoise the whole window once, then splice
    tmp = out_audio + ".src.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-to", f"{b}", "-i", SRC, "-ac", "1", "-ar", "48000",
                    "-af", f"highpass=f=75,arnndn=m={MODELS}/sh.rnnn:mix=0.85,"
                           "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2", tmp], check=True)
    v, sr = sf.read(tmp, dtype="float32")
    os.remove(tmp)
    X = int(0.012 * sr)
    total = mp[-1][2] + mp[-1][3]
    n = int(round(total * sr)) + 2 * X
    out = np.zeros(n, np.float32)
    ramp = np.sin(np.linspace(0, np.pi / 2, 2 * X)) ** 2
    for s, e, o, d in mp:
        i0, i1 = int(round((s - a) * sr)) - X, int(round((e - a) * sr)) + X
        seg = v[max(0, i0):i1].copy()
        w = np.ones(len(seg), np.float32)
        w[:2 * X] = ramp[:len(w[:2 * X])]
        w[-2 * X:] = ramp[::-1][-len(w[-2 * X:]):]
        p = int(round(o * sr))
        out[p:p + len(seg)] += (seg * w)[:len(out) - p]
    voice = out[X:X + int(round(total * sr))]
    fl = int(0.03 * sr)
    voice[:fl] *= np.linspace(0, 1, fl)
    voice[-int(0.25 * sr):] *= np.linspace(1, 0, int(0.25 * sr))
    raw = out_audio + ".raw.wav"
    sf.write(raw, voice, sr)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=7", "-ar", "48000",
                    out_audio], check=True)
    os.remove(raw)

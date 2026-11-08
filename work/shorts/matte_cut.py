"""Détourage (RobustVideoMatting) du sujet sur une fenêtre du montage, pour le mot choc derrière la tête."""
import sys, os, json, subprocess, numpy as np, onnxruntime as ort
from PIL import Image

M, d = sys.argv[1], sys.argv[2]
c = json.load(open(f"{d}/assets/choc.json")); t0, dur = c["t0"], c["d"]
tmp = f"{d}/assets/_mf"; os.makedirs(tmp, exist_ok=True); os.makedirs(f"{d}/assets/fg", exist_ok=True)
s0 = max(0, t0 - 1.0)  # 1 s de chauffe pour l'état récurrent du modèle
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s0:.3f}", "-t", f"{dur + (t0 - s0):.3f}", "-i",
                f"{d}/assets/cut.mp4", "-vf", "fps=30", f"{tmp}/%04d.png"], check=True)
s = ort.InferenceSession(M, providers=["CPUExecutionProvider"])
rec = [np.zeros([1, 1, 1, 1], np.float32)] * 4
fs = sorted(os.listdir(tmp)); skip = round((t0 - s0) * 30); k = 0
for i, f in enumerate(fs):
    im = Image.open(f"{tmp}/{f}").convert("RGB"); a = np.asarray(im, np.float32) / 255.
    fgr, pha, *rec = s.run(None, {"src": a.transpose(2, 0, 1)[None], "r1i": rec[0], "r2i": rec[1], "r3i": rec[2],
                                  "r4i": rec[3], "downsample_ratio": np.array([0.25], np.float32)})
    if i < skip: continue
    o = im.convert("RGBA"); o.putalpha(Image.fromarray((pha[0, 0] * 255).clip(0, 255).astype(np.uint8)))
    o.save(f"{d}/assets/fg/{k:04d}.webp", quality=85, method=4); k += 1
print("fg frames", k)

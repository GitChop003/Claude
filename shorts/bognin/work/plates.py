"""Person matte (RobustVideoMatting) -> light background blur -> "4K" finish, in two orientations.

Usage: plates.py CUT720.mp4 OUTDIR NAME [blur_sigma]
Writes OUTDIR/NAME_land.mp4 (1920x1080) and OUTDIR/NAME_port.mp4 (1080x1920), plus NAME_track.json.
"""
import json, subprocess, sys, time
import cv2, numpy as np, onnxruntime as ort

SCR = "/tmp/claude-0/-home-claude/3103370c-3a96-56b2-b40e-7458c05b9768/scratchpad"
src, outdir, name = sys.argv[1], sys.argv[2], sys.argv[3]
SIGMA = float(sys.argv[4]) if len(sys.argv) > 4 else 3.2      # 720p px — "pas trop dosé"
W, H, FPS = 1280, 720, 25
PW = 406                                                      # 9:16 window inside 720 px height

# "4K" finish: light temporal denoise, lanczos upscale, contrast-adaptive sharpening, a touch of contrast/colour
FINISH = "hqdn3d=1.2:1.0:3:3,scale={w}:{h}:flags=lanczos,cas=0.5,eq=contrast=1.05:saturation=1.08:gamma=0.98"

sess = ort.InferenceSession(f"{SCR}/models/rvm_mobilenetv3_fp32.onnx", providers=["CPUExecutionProvider"])
rec = [np.zeros((1, 1, 1, 1), np.float32)] * 4
dsr = np.array([0.4], np.float32)

dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
frames, alphas = [], []
t0 = time.time()
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    f = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    x = (f.astype(np.float32) / 255).transpose(2, 0, 1)[None]
    if not frames:                       # warm up the recurrent state on the first frame
        for _ in range(8):
            _, _, *rec = sess.run(None, {"src": x, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3], "downsample_ratio": dsr})
    fgr, pha, *rec = sess.run(None, {"src": x, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3], "downsample_ratio": dsr})
    frames.append(f)
    alphas.append((pha[0, 0] * 255).round().astype(np.uint8))   # uint8 to keep RAM low
    if len(frames) % 100 == 0:
        print(f"matte {len(frames)} frames, {time.time() - t0:.0f}s", flush=True)
N = len(frames)
print(f"matte done: {N} frames in {time.time() - t0:.0f}s", flush=True)

# speaker horizontal centre for the portrait crop: head/torso centroid, smoothed
cx = []
for a in alphas:
    top = a[: int(H * 0.7)].astype(np.float32) / 255
    col = top.sum(0)
    cx.append(float((col * np.arange(W)).sum() / (col.sum() + 1e-6)) if col.sum() > 50 else W / 2)
cx = np.array(cx)
k = 25
pad = np.pad(cx, (k, k), mode="edge")
med = np.array([np.median(pad[i:i + 2 * k + 1]) for i in range(N)])
sm = np.convolve(np.pad(med, (12, 12), mode="edge"), np.ones(25) / 25, "valid")
left = np.clip(sm - PW / 2, 0, W - PW).round().astype(int)
json.dump({"cx": sm.round(1).tolist(), "left": left.tolist()}, open(f"{outdir}/{name}_track.json", "w"))


def enc(path, w, h, iw, ih):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{iw}x{ih}", "-r", str(FPS),
                             "-i", "-", "-vf", FINISH.format(w=w, h=h) + ",format=yuv420p", "-c:v", "libx264", "-preset", "slow",
                             "-crf", "14", path], stdin=subprocess.PIPE)


land = enc(f"{outdir}/{name}_land.mp4", 1920, 1080, W, H)
port = enc(f"{outdir}/{name}_port.mp4", 1080, 1920, PW, H)
for i, (f, a) in enumerate(zip(frames, alphas)):
    a = cv2.GaussianBlur(a.astype(np.float32) / 255, (0, 0), 1.0)[..., None]                   # soften matte edge
    bg_w = 1 - a
    ff = f.astype(np.float32)
    # mask-normalised blur: background blurred without the speaker's colours bleeding into it
    num = cv2.GaussianBlur(ff * bg_w, (0, 0), SIGMA)
    den = cv2.GaussianBlur(bg_w, (0, 0), SIGMA)[..., None] + 1e-4
    bl = num / den
    bl = np.where(den > 0.05, bl, cv2.GaussianBlur(ff, (0, 0), SIGMA))
    out = np.clip(a * ff + (1 - a) * bl, 0, 255).astype(np.uint8)
    land.stdin.write(out.tobytes())
    port.stdin.write(np.ascontiguousarray(out[:, left[i]:left[i] + PW]).tobytes())
for p in (land, port):
    p.stdin.close()
    p.wait()
print("plates done", flush=True)

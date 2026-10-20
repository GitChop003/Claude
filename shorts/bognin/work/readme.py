"""Regenerate shorts/bognin/README.md from the specs and the renders present."""
import glob, importlib, os, subprocess, sys
WORK = "/home/claude/claude/shorts/bognin/work"
sys.path.insert(0, f"{WORK}/specs")
BASE = "/home/claude/claude/shorts/bognin"
rows = []
for f in sorted(glob.glob(f"{WORK}/specs/s*.py")):
    n = os.path.basename(f)[:-3]
    sp = importlib.import_module(n)
    p, l = f"{n}/port/renders/{n}_port.mp4", f"{n}/land/renders/{n}_land.mp4"
    if not (os.path.exists(f"{BASE}/{p}") and os.path.exists(f"{BASE}/{l}")):
        continue
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{BASE}/{p}"],
                             capture_output=True, text=True).stdout)
    a, b = sp.KEEP[0][0], sp.KEEP[-1][1]
    src = f"{int(a // 60)}:{int(a % 60):02d} → {int(b // 60)}:{int(b % 60):02d}"
    rows.append(f"| {n[1:]} | {sp.TITLE} | {src} | {d:.0f} s | [vertical]({p}) | [horizontal]({l}) |")
intro = open(f"{WORK}/README.head.md").read()
tail = open(f"{WORK}/README.tail.md").read()
table = "| N° | Sujet | Source | Durée | 9:16 (TikTok / Reels / Shorts) | 16:9 (YouTube / LinkedIn) |\n|---|---|---|---|---|---|\n" + "\n".join(rows)
open(f"{BASE}/README.md", "w").write(intro + "\n" + table + "\n\n" + tail)
print(len(rows), "shorts listed")

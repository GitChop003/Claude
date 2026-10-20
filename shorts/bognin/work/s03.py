"""Short 03 — « L'entrepreneuriat n'est pas fait pour tout le monde » (source 9:12 – 9:45)."""
import json, sys
sys.path.insert(0, "/home/claude/claude/shorts/bognin/work")
from edit import *

NAME = "s03"
OUT = f"{SCR}/s03"
KEEP = [
    (552.69, 552.92),   # « Je le »            (drops « Et c'est pourquoi »)
    (554.20, 580.49),   # « dis toujours, c'est que l'entrepreneuriat… des jours »  (drops the repeated « je dis toujours »)
    (580.99, 585.52),   # « où vous aurez l'impression… qui vous comprenne. »       (drops the hesitation after « jours »)
]
BEATS = {569.2: 0.30}   # short dramatic beat after « …un mental assez fort. » before « Ne faites pas… »

mp, D = make_edl(KEEP, beats=BEATS)

if __name__ == "__main__":
    print(f"{D:.2f} s, {len(mp)} segments")
    for s, e, o, d in mp:
        print(f"  src {s:8.2f}-{e:8.2f}  ->  out {o:6.2f} (+{d:.2f})")
    json.dump(mp, open(f"/home/claude/claude/shorts/bognin/work/{NAME}.edl.json", "w"), indent=1)
    if "cut" in sys.argv:
        os.makedirs(OUT, exist_ok=True)
        render_cut(mp, f"{OUT}/{NAME}_cut720.mp4", f"{OUT}/{NAME}_voice.wav")
        print("cut done")

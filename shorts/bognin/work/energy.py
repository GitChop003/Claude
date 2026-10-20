"""Energy (dB re loud speech over ±5 s) around boundary times.  energy.py T [T ...]   (10 ms steps, ±0.25 s, '|' = T)"""
import sys
sys.path.insert(0, "/home/claude/claude/shorts/bognin/work")
from edit import load_env
for t in map(float, sys.argv[1:]):
    db = load_env(t - 5, t + 5)
    k0 = int(round(4.75 / 0.01))
    print(f"{t:8.2f}: " + " ".join(("|" if k == 25 else "") + f"{v:.0f}" for k, v in enumerate(db[k0:k0 + 51])))

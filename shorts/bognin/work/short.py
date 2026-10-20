"""Generic runner for the Bognin shorts.  Each short is described by work/specs/<name>.py.

  python3 short.py s04 cut       # cut list, frame-exact 720p cut, cleaned voice
  python3 short.py s04 plates    # person matte, light background blur, "4K" finish (16:9 + 9:16)
  python3 short.py s04 media     # voice muxed into the plates + end-card hold, copied into both projects
  python3 short.py s04 comp      # (re)build both HyperFrames compositions
  python3 short.py s04 snap 1.2,5,9   # layout snapshots (scratch dir)
  python3 short.py s04 render    # final renders -> shorts/bognin/<name>/{port,land}/renders/
  python3 short.py s04 all       # everything above except snap

A spec defines: NAME, TITLE (topic), KEEP [(a, b)], optional BEATS {t: pause}, FIX {word: word},
KEY (caption keywords), and inserts(c, T, port, VOICE_D, DUR) which adds title, tags, inserts, end card.
"""
import importlib, json, os, subprocess, sys

WORK = "/home/claude/claude/shorts/bognin/work"
sys.path.insert(0, WORK)
sys.path.insert(0, f"{WORK}/specs")
from edit import SCR, make_edl, render_cut, src2out   # noqa: E402
from compose import Comp                               # noqa: E402

REPO = "/home/claude/claude"
HOLD = 1.8
BROWSER = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"


class Short:
    def __init__(self, name):
        self.spec = importlib.import_module(name)
        self.name = name
        self.out = f"{SCR}/{name}"
        self.proj = {o: f"{REPO}/shorts/bognin/{name}/{o}" for o in ("land", "port")}
        self.mp, self.voice_d = make_edl(self.spec.KEEP, beats=getattr(self.spec, "BEATS", None), trim=getattr(self.spec, "TRIM", False))
        self.dur = round(self.voice_d + HOLD, 3)
        wf = f"{WORK}/{name}.words.json"
        words = json.load(open(wf if os.path.exists(wf) else f"{WORK}/full.words.json"))
        pf = f"{WORK}/words_patch.json"            # passages re-decoded on short windows (better text/timings)
        if not os.path.exists(wf) and os.path.exists(pf):
            P = json.load(open(pf))
            words = sorted([w for w in words if not any(p["a"] <= w["start"] < p["b"] for p in P)] +
                           [w for p in P for w in p["words"]], key=lambda w: w["start"])
        fix = getattr(self.spec, "FIX", {})
        caps = []
        for w in words:
            if w["end"] < self.mp[0][0] - 1 or w["start"] > self.mp[-1][1] + 1:
                continue
            strict = getattr(self.spec, "STRICT_WORDS", True)
            for s, e, o, d in self.mp:
                ov = min(w["end"], e) - max(w["start"], s)
                # strict: the word must start inside the kept segment (or be mostly kept) — words whose start
                # falls in a removed stretch don't leak in as stray captions
                if (s - 0.05 <= w["start"] < e - 0.06 or ov >= 0.15) if strict else ov >= 0.03:
                    st = src2out(self.mp, max(w["start"], s))
                    en = src2out(self.mp, min(w["end"], e) - 1e-3)
                    t = fix.get((w["text"], round(w["start"])), fix.get(w["text"], w["text"]))
                    if t:
                        caps.append({"text": t, "src": w["start"], "start": round(st, 3), "end": round(max(en, st + 0.06), 3)})
                    break
            else:
                if getattr(self.spec, "STRICT_WORDS", True):
                    # word starting inside a pause the engine shortened (< 0.45 s): keep it, it is still spoken
                    in_keep = any(ka <= w["start"] < kb for ka, kb in self.spec.KEEP)   # inside a range = a shortened pause
                    for (s0, e0, o0, d0), (s1, e1, o1, d1) in zip(self.mp, self.mp[1:]):
                        if e0 - 0.06 <= w["start"] < s1 and (s1 - e0 < 0.45 or in_keep) and w["end"] > s1 - 0.3:
                            t = fix.get((w["text"], round(w["start"])), fix.get(w["text"], w["text"]))
                            if t:
                                en = src2out(self.mp, min(w["end"], e1) - 1e-3)
                                caps.append({"text": t, "src": w["start"], "start": round(o1, 3), "end": round(max(en, o1 + 0.06), 3)})
                            break
        if caps:
            caps[0]["text"] = caps[0]["text"][0].upper() + caps[0]["text"][1:]
        if getattr(self.spec, "STRICT_WORDS", True):        # sentence case after a cut
            for p_, c_ in zip(caps, caps[1:]):
                if p_["text"][-1:] in ".?!" and c_["text"][:1].islower():
                    c_["text"] = c_["text"][0].upper() + c_["text"][1:]
        self.caps = caps

    def T(self, word, near):
        lw = word.lower().strip(",.?!")
        c = [x for x in self.caps if x["text"].lower().strip(",.?!").startswith(lw) and abs(x["src"] - near) < 4]
        if not c:
            raise ValueError(f"{self.name}: {word!r} not found near {near}")
        return min(c, key=lambda x: abs(x["src"] - near))["start"]

    # ------------------------------------------------------------------ steps
    def cut(self):
        os.makedirs(self.out, exist_ok=True)
        json.dump(self.mp, open(f"{WORK}/{self.name}.edl.json", "w"), indent=1)
        render_cut(self.mp, f"{self.out}/{self.name}_cut720.mp4", f"{self.out}/{self.name}_voice.wav")

    def plates(self):
        subprocess.run(["python3", f"{WORK}/plates.py", f"{self.name}_cut720.mp4", ".", self.name], cwd=self.out, check=True)

    def media(self):
        for o in ("land", "port"):
            os.makedirs(f"{self.proj[o]}/assets", exist_ok=True)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{self.out}/{self.name}_{o}.mp4", "-i", f"{self.out}/{self.name}_voice.wav",
                            "-filter_complex", f"[0:v]tpad=stop_mode=clone:stop_duration={HOLD}[v];[1:a]apad=whole_dur={self.dur}[a]",
                            "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-pix_fmt", "yuv420p",
                            "-g", "25", "-c:a", "aac", "-b:a", "192k", "-t", f"{self.dur}", "-movflags", "+faststart",
                            f"{self.proj[o]}/assets/{self.name}_{o}.mp4"], check=True)

    def comp(self):
        for o in ("land", "port"):
            tf = f"{self.out}/{self.name}_track.json"
            cx = json.load(open(tf))["cx"] if os.path.exists(tf) else None
            face = (lambda t: cx[max(0, min(len(cx) - 1, int(t * 25)))] / 1280) if cx else None
            c = Comp(self.name, o, self.dur, f"{self.name}_{o}.mp4", self.caps, keywords=getattr(self.spec, "KEY", ()), face=face)
            c.zooms(self.mp)
            self.spec.inserts(c, self.T, o == "port", self.voice_d, self.dur)
            print(o, "caption chunks:", c.build(self.proj[o]))

    def _hf(self, *args):
        env = dict(os.environ, HYPERFRAMES_BROWSER_PATH=BROWSER)
        return subprocess.run(["npx", "hyperframes", *args], cwd=REPO, env=env, check=True)

    def snap(self, at):
        for o in ("port", "land"):
            self._hf("snapshot", f"shorts/bognin/{self.name}/{o}", "--at", at, "--no-end", "-o", f"{self.out}/snap_{o}",
                     "--describe", "false")

    def render(self):
        for o in ("port", "land"):
            self._hf("render", f"shorts/bognin/{self.name}/{o}", "-o", f"shorts/bognin/{self.name}/{o}/renders/{self.name}_{o}.mp4",
                     "--fps", "25", "--quiet")
            self.fit(o)

    def fit(self, o, limit_mb=90):
        """GitHub refuses files > 100 MB: cap the bitrate so the delivery file stays under `limit_mb`."""
        f = f"{REPO}/shorts/bognin/{self.name}/{o}/renders/{self.name}_{o}.mp4"
        if os.path.getsize(f) <= limit_mb * 1e6:
            return
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                   capture_output=True, text=True).stdout)
        vk = int((limit_mb * 8e3 * 0.97) / dur - 192)          # kbit/s for video, leaving room for 192k audio
        tmp = f + ".tmp.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                        "-maxrate", f"{vk}k", "-bufsize", f"{vk}k", "-pix_fmt", "yuv420p", "-c:a", "copy",
                        "-movflags", "+faststart", tmp], check=True)
        os.replace(tmp, f)
        print(f"fit {o}: {os.path.getsize(f) / 1e6:.0f} MB", flush=True)


if __name__ == "__main__":
    s = Short(sys.argv[1])
    step = sys.argv[2] if len(sys.argv) > 2 else "info"
    if step == "info":
        print(f"{s.name}: {s.voice_d:.2f}s voice, {len(s.mp)} segments, {s.dur}s total")
        for a, b, o, d in s.mp:
            print(f"  src {a:8.2f}-{b:8.2f} -> out {o:6.2f} (+{d:.2f})")
        print(" ".join(f"{x['text']}@{x['start']:.1f}" for x in s.caps))
    elif step == "fit":
        for o in ("port", "land"):
            s.fit(o)
    elif step == "snap":
        s.snap(sys.argv[3])
    elif step == "all":
        for st in ("cut", "plates", "media", "comp", "render"):
            print(f"== {s.name} {st}", flush=True)
            getattr(s, st)()
        print(f"== {s.name} DONE", flush=True)
    else:
        for st in step.split(","):
            print(f"== {s.name} {st}", flush=True)
            getattr(s, st)()
        print(f"== {s.name} {step} OK", flush=True)

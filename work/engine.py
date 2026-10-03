"""Shared editing engine for the interview recut.

Pipeline per question:
  keep ranges (editorial)  ->  word-level jump cuts (pauses shortened, fillers dropped)
  -> frame-exact video cut (single-pass select on the 1080p proxy)
  -> voice: denoised track, 25 ms equal-power crossfades at every cut
  -> music bed ducked under the voice
  -> HyperFrames composition: captions, zoom framing, animated inserts, SFX
"""
import html, json, os, shutil, subprocess
import numpy as np
import soundfile as sf

ROOT = "/home/user/Claude"
WORK = f"{ROOT}/work"
SHARED = f"{ROOT}/videos/_shared"
PROXY = f"{ROOT}/media/proxy1080.mp4"
VOICE = f"{ROOT}/media/voice_clean.wav"
MUSIC = f"{WORK}/music/lofi_600s.wav"
FR = 30000 / 1001

RAW = json.load(open(f"{WORK}/raw_words.json"))
WORDS = json.load(open(f"{WORK}/words2.json"))
# passages where Parakeet (exact timings) transcribed French better than Whisper
PARA = [(394.40, 419.60), (441.10, 466.40)]
WORDS = sorted([w for w in WORDS if not any(a <= w["start"] < b for a, b in PARA)] +
               [w for w in RAW if any(a <= w["start"] < b for a, b in PARA)], key=lambda w: w["start"])


def snap(t):
    return round(t * FR) / FR


# --------------------------------------------------------------------------- edit decision list
def make_edl(keep, gap=0.40, pre=0.10, post=0.16, min_seg=0.25, tail=0.0):
    """Keep ranges -> segments: shorten pauses longer than `gap` using energy-based speech runs."""
    SP = sorted([tuple(x) for x in json.load(open(f"{WORK}/speech.json"))] +
                [(v["start"], v["end"]) for v in json.load(open(f"{WORK}/vad.json"))])
    U = []
    for s_, e_ in SP:
        if U and s_ <= U[-1][1]:
            U[-1][1] = max(U[-1][1], e_)
        else:
            U.append([s_, e_])
    SP = U
    out = []
    for a, b, *_ in keep:
        runs = [(max(a, s_), min(b, e_)) for s_, e_ in SP if e_ > a and s_ < b]
        cur = None
        for s_, e_ in runs:
            if cur and s_ - cur[1] <= gap:
                cur[1] = e_
            else:
                if cur:
                    out.append([max(a, cur[0] - pre), min(b, cur[1] + post)])
                cur = [s_, e_]
        if cur:
            out.append([max(a, cur[0] - pre), min(b, cur[1] + post)])
    for i in range(1, len(out)):
        if out[i][0] < out[i - 1][1]:
            m = (out[i][0] + out[i - 1][1]) / 2
            out[i - 1][1] = out[i][0] = m
    if tail and out:
        out[-1][1] += tail
    segs = [(snap(s), snap(e)) for s, e in out if e - s >= min_seg]
    segs = [(s, e) for s, e in segs if e > s]
    mp, t = [], 0.0
    for s, e in segs:
        mp.append((s, e, t, e - s))
        t += e - s
    return mp, t


def src2out(mp, t):
    for s, e, o, d in mp:
        if t < s:
            return o
        if t < e:
            return o + t - s
    return mp[-1][2] + mp[-1][3]


def captions(mp, fixes=None, phrases=None, keep=None):
    fixes = fixes or {}
    cap = []
    if keep:   # every word inside a kept passage is shown; words in removed pauses snap to the segment edge
        for a, b, *_ in keep:
            for w in WORDS:
                if a - 0.05 <= w["start"] < b - 0.05:
                    st = src2out(mp, w["start"]); en = max(src2out(mp, w["end"]), st + 0.06)
                    cap.append({"text": w["text"], "src": w["start"], "start": round(st, 3), "end": round(en, 3)})
    else:
      for s, e, o, d in mp:
        for w in WORDS:
            if s - 0.08 <= w["start"] < e - 0.06:
                cap.append({"text": w["text"], "src": w["start"],
                            "start": round(o + max(w["start"], s) - s, 3), "end": round(o + min(w["end"], e) - s, 3)})
    # phrase-level corrections: [(old words, new words)]
    for old, new in (phrases or []):
        ow, nw = old.split(), new.split()
        i = 0
        while i <= len(cap) - len(ow):
            if [x["text"] for x in cap[i:i + len(ow)]] == ow:
                for k in range(len(ow)):
                    if k < len(nw):
                        cap[i + k]["text"] = nw[k] if k < len(ow) - 1 or len(nw) <= len(ow) else " ".join(nw[k:])
                    else:
                        cap[i + k]["text"] = None
                        cap[i + len(nw) - 1]["end"] = cap[i + k]["end"]
                i += len(ow)
            else:
                i += 1
    cap = [c for c in cap if c["text"]]
    out = []
    for c in cap:
        t = c["text"]
        hit = [k for k in fixes if isinstance(k, tuple) and k[0] == c["text"] and abs(c["src"] - k[1]) < 1.0]
        if hit:
            t = fixes[hit[0]]
        elif c["text"] in fixes:
            t = fixes[c["text"]]
        if t is None:
            continue
        if t in ("?", "!", ":", ";") and out:
            out[-1]["text"] += " " + t
            continue
        if out and out[-1]["text"][-1:] in ".?!" and t[:1].islower():
            t = t[0].upper() + t[1:]
        out.append(dict(c, text=t))
    return out


def word_at(word, near, window=6.0):
    """Source time of `word` (prefix match, case/accents-insensitive-ish) closest to `near`."""
    lw = word.lower().strip(",.?!«»\"'")
    cands = [w for w in WORDS if w["text"].lower().strip(",.?!«»\"'").startswith(lw) and abs(w["start"] - near) < window]
    if not cands:
        cands = [w for w in RAW if w["text"].lower().startswith(lw) and abs(w["start"] - near) < window]
    if not cands:
        raise ValueError(f"word {word!r} not found near {near}")
    return min(cands, key=lambda w: abs(w["start"] - near))["start"]


# --------------------------------------------------------------------------- media render
def render_media(name, mp, dur, outdir, music_offset=0.0):
    os.makedirs(outdir, exist_ok=True)
    # video: frame-exact single pass select
    expr = "+".join(f"between(t,{s - 0.5 / FR:.4f},{e - 0.5 / FR:.4f})" for s, e, o, d in mp)
    vtmp = f"{outdir}/_v.mp4"
    with open(f"{WORK}/{name}.select.txt", "w") as f:
        f.write(f"select='{expr}',setpts=N/FRAME_RATE/TB")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", PROXY, "-filter_script:v", f"{WORK}/{name}.select.txt", "-an",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-g", "30", "-r", "30000/1001", vtmp], check=True)
    # voice with equal-power crossfades (length preserving)
    v, sr = sf.read(VOICE, dtype="float32")
    X = int(0.025 * sr)
    n = int(round(dur * sr)) + 2 * X
    out = np.zeros(n, np.float32)
    for s, e, o, d in mp:
        a, b = int(s * sr) - X, int(e * sr) + X
        seg = v[max(0, a):b].copy()
        if a < 0:
            seg = np.concatenate([np.zeros(-a, np.float32), seg])
        w = np.ones(len(seg), np.float32)
        ramp = np.sin(np.linspace(0, np.pi / 2, 2 * X)) ** 2
        w[:2 * X] = ramp
        w[-2 * X:] = ramp[::-1]
        p = int(round(o * sr))
        out[p:p + len(seg)] += seg * w
    voice = out[X:X + int(round(dur * sr))]
    # loudness-ish normalisation of voice on speech RMS
    rms = np.sqrt(np.convolve(voice ** 2, np.ones(int(0.05 * sr)) / int(0.05 * sr), "same"))
    speech = rms > 0.02 * rms.max()
    voice *= 0.10 / (np.sqrt(np.mean(voice[speech] ** 2)) + 1e-9)
    # music bed, ducked under speech (smooth envelope)
    m, msr = sf.read(MUSIC, dtype="float32")
    m = m[int(music_offset * msr):][: len(voice)]
    if len(m) < len(voice):
        m = np.concatenate([m, np.zeros((len(voice) - len(m), 2), np.float32)])
    act = np.convolve(speech.astype(np.float32), np.ones(int(0.25 * sr)) / int(0.25 * sr), "same")
    act = np.clip(act * 2.5, 0, 1)
    k = int(0.35 * sr)  # slow release
    env = np.convolve(act, np.ones(k) / k, "same")
    mrms = np.sqrt(np.mean(m ** 2)) + 1e-9
    gain = (0.10 / mrms) * (10 ** (-17 / 20) * env + 10 ** (-10 / 20) * (1 - env))
    fade = np.ones(len(voice), np.float32)
    fl = int(1.2 * sr)
    fade[:fl] = np.linspace(0, 1, fl)
    fade[-int(2.0 * sr):] = np.linspace(1, 0, int(2.0 * sr))
    mix = m * (gain * fade)[:, None] + voice[:, None]
    mix = np.tanh(mix * 1.4) / 1.4
    atmp = f"{outdir}/_a.wav"
    sf.write(atmp, mix.astype(np.float32), sr)
    final = f"{outdir}/{name}_cut.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vtmp, "-i", atmp, "-map", "0:v", "-map", "1:a",
                    "-af", "loudnorm=I=-14:TP=-1.2:LRA=9", "-ar", "48000", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", final], check=True)
    os.remove(vtmp)
    os.remove(atmp)
    return final


# --------------------------------------------------------------------------- composition
CSS = """
@font-face{font-family:Inter;font-weight:400;src:url(assets/fonts/inter-latin-400-normal.woff2)}
@font-face{font-family:Inter;font-weight:400;font-style:italic;src:url(assets/fonts/inter-latin-400-italic.woff2)}
@font-face{font-family:Inter;font-weight:700;src:url(assets/fonts/inter-latin-700-normal.woff2)}
@font-face{font-family:Inter;font-weight:700;font-style:italic;src:url(assets/fonts/inter-latin-700-italic.woff2)}
@font-face{font-family:Inter;font-weight:800;src:url(assets/fonts/inter-latin-800-normal.woff2)}
@font-face{font-family:Inter;font-weight:900;src:url(assets/fonts/inter-latin-900-normal.woff2)}
@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/montserrat-latin-900-normal.woff2)}
@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/montserrat-latin-800-normal.woff2)}
:root{--neon:#3CFF9A;--pink:#FF4FA3;--sky:#5AC8FF;--sun:#FFD23F;--ink:#0b0d10}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1920px;height:1080px;overflow:hidden;background:#000;font-family:Inter,sans-serif}
#root{position:relative;width:1920px;height:1080px;overflow:hidden}
#vw{position:absolute;inset:0;transform-origin:56% 34%}
#vw video{width:100%;height:100%;object-fit:cover;display:block}
#grade{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at 55% 42%,rgba(0,0,0,0) 52%,rgba(0,0,0,.42) 100%)}
#dim{position:absolute;inset:0;background:#05070a;opacity:0}
#flash{position:absolute;inset:0;background:#fff;opacity:0}
#bar{position:absolute;left:0;top:0;height:7px;width:1920px;background:linear-gradient(90deg,var(--neon),var(--sky));transform-origin:0 50%;box-shadow:0 0 16px rgba(60,255,154,.7)}
.cap{position:absolute;left:0;right:0;bottom:84px;text-align:center;font-weight:800;font-size:64px;line-height:1.1;color:#fff;
  letter-spacing:-.01em;opacity:0;text-shadow:0 4px 0 rgba(0,0,0,.85),0 0 18px rgba(0,0,0,.85);-webkit-text-stroke:2px rgba(0,0,0,.9);paint-order:stroke fill}
.cap span{display:inline-block}
.cap.q{font-weight:700;font-style:italic;font-size:52px;color:#f4f4f4}
.glass{background:rgba(12,14,18,.70);border:2px solid rgba(255,255,255,.14);border-radius:30px;box-shadow:0 24px 70px rgba(0,0,0,.45)}
.qcard{position:absolute;left:80px;top:86px;width:860px;padding:38px 48px 42px;opacity:0}
.qcard .k{font-size:27px;font-weight:800;letter-spacing:.3em;color:var(--pink)}
.qcard .k b{color:#fff}
.qcard .t{margin-top:16px;font-size:56px;font-weight:800;line-height:1.08;color:#fff;letter-spacing:-.01em}
.qcard .u{margin-top:24px;height:8px;width:260px;background:var(--pink);border-radius:4px;transform-origin:0 50%}
.chip{position:absolute;display:flex;align-items:center;gap:18px;padding:16px 32px 16px 18px;border-radius:999px;font-weight:800;font-size:42px;
  color:var(--ink);background:var(--neon);opacity:0;box-shadow:0 14px 40px rgba(0,0,0,.45);white-space:nowrap}
.chip.noicon{padding:18px 34px}
.chip img{width:62px;height:62px}
.chip.white{background:#fff}.chip.pink{background:var(--pink);color:#fff}.chip.sun{background:var(--sun)}.chip.sky{background:var(--sky)}
.chip.dark{background:rgba(12,14,18,.85);color:#fff;border:2px solid rgba(255,255,255,.18)}
.emo{position:absolute;opacity:0;filter:drop-shadow(0 14px 26px rgba(0,0,0,.45))}
.stamp{position:absolute;padding:16px 40px;border:10px solid #ff3b3b;color:#ff3b3b;font-family:Mont;font-weight:900;font-size:88px;
  border-radius:18px;opacity:0;letter-spacing:.04em;background:rgba(255,255,255,.10);white-space:nowrap}
.lt{position:absolute;left:80px;bottom:250px;padding:24px 42px 26px 34px;opacity:0;border-left:10px solid var(--neon);border-radius:0 26px 26px 0;display:flex;gap:26px;align-items:center}
.lt img{width:96px;height:96px}
.lt .a{font-size:28px;font-weight:800;letter-spacing:.22em;color:var(--neon)}
.lt .b{font-size:50px;font-weight:800;color:#fff;margin-top:4px}
.lt .c{font-size:38px;font-style:italic;color:#ddd;margin-top:6px;opacity:0}
.panel{position:absolute;top:100px;width:max-content;min-width:600px;max-width:900px;padding:36px 44px 30px;opacity:0}
.panel h3{font-size:28px;letter-spacing:.24em;color:var(--pink);font-weight:800}
.panel ul{list-style:none;margin-top:16px}
.panel li{position:relative;white-space:nowrap;display:flex;align-items:center;gap:20px;font-size:42px;font-weight:800;color:#fff;padding:9px 0;opacity:0}
.panel li img{width:54px;height:54px}
.panel li .tm{font-size:30px;color:var(--neon);min-width:170px;font-weight:800;white-space:nowrap}
.panel li .s{position:absolute;left:0;right:-8px;top:50%;height:7px;margin-top:-3px;background:var(--pink);transform-origin:0 50%;border-radius:5px}
.logos{position:absolute;display:flex;gap:26px;opacity:1}
.logo{width:132px;height:132px;border-radius:34px;display:flex;align-items:center;justify-content:center;opacity:0;box-shadow:0 16px 40px rgba(0,0,0,.5)}
.logo svg{width:76px;height:76px;fill:#fff}
.logo .in{font-family:Inter;font-weight:900;font-size:82px;color:#fff;letter-spacing:-.04em;line-height:1}
.quote{position:absolute;top:150px;width:900px;opacity:0}
.quote .m{font-family:Mont;font-size:230px;line-height:.62;color:var(--neon);font-weight:900}
.quote p{font-size:66px;line-height:1.13;font-weight:800;color:#fff;margin-top:8px;text-shadow:0 6px 30px rgba(0,0,0,.8)}
.quote p span{opacity:.18}
.quote .who{margin-top:24px;font-size:30px;color:#cfcfcf;letter-spacing:.14em;opacity:0;font-weight:700}
.big{position:absolute;left:0;right:0;top:330px;text-align:center;font-family:Mont;font-weight:900;font-size:180px;letter-spacing:-.02em;color:#fff;opacity:0;
  text-shadow:0 10px 50px rgba(0,0,0,.7);line-height:1}
.big em{font-style:normal;color:var(--neon)}
.big small{display:block;font-family:Inter;font-size:52px;font-weight:800;letter-spacing:.25em;color:#fff;margin-bottom:18px}
.counter{position:absolute;display:flex;align-items:center;gap:30px;opacity:0}
.counter .n{font-family:Mont;font-weight:900;font-size:220px;color:var(--sun);line-height:1;text-shadow:0 10px 40px rgba(0,0,0,.6)}
.counter .l{font-size:54px;font-weight:800;color:#fff;line-height:1.1;text-shadow:0 4px 20px rgba(0,0,0,.8)}
.counter .icons{display:flex;gap:6px;margin-top:14px}
.counter .icons img{width:70px;height:70px;opacity:0}
.end{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;opacity:0}
.end .l1{font-size:58px;font-weight:800;color:#fff;letter-spacing:.3em}
.end .l2{font-family:Mont;font-size:170px;font-weight:900;color:var(--neon);letter-spacing:-.02em;line-height:1.02;text-align:center}
.end .l3{margin-top:30px;font-size:40px;font-weight:700;color:#ddd;letter-spacing:.06em}
"""

LOGO_BG = {"linkedin": "#0A66C2", "instagram": "linear-gradient(45deg,#f9ce34,#ee2a7b 50%,#6228d7)", "facebook": "#0866FF",
           "tiktok": "#111", "youtube": "#FF0000", "youtubeshorts": "#FF0000", "netflix": "#000", "gmail": "#EA4335",
           "whatsapp": "#25D366"}


def logo_html(key, id_):
    bg = LOGO_BG[key]
    if key == "linkedin":
        inner = '<span class="in">in</span>'
    else:
        svg = open(f"{SHARED}/logos/{key}.svg").read()
        inner = svg.replace("<svg ", '<svg fill="#fff" ', 1)
    return f'<div class="logo" id="{id_}" style="background:{bg}">{inner}</div>'


class Comp:
    def __init__(self, name, dur, mp, caps, qnum, qtitle, q_end, accent="var(--neon)"):
        self.name, self.dur, self.mp, self.caps = name, dur, mp, caps
        self.html, self.js, self.sfx, self.hide = [], [], [], []
        self.qnum, self.qtitle, self.q_end = qnum, qtitle, q_end
        self.n = 0
        self.dims = []

    def o(self, src):            # source time -> output time
        return src2out(self.mp, src)

    def id(self, p):
        self.n += 1
        return f"{p}{self.n}"

    def add_sfx(self, name, t, vol=0.35):
        self.sfx.append((name, t, vol))

    def dim(self, a, b, level=0.42):
        self.dims.append((a, b, level))

    # ---- components (times are OUTPUT seconds)
    def chip(self, text, a, b, x, y, icon=None, cls="", sfx="pop", anchor="right"):
        i = self.id("chip")
        pos = f"{anchor}:{x}px;top:{y}px"
        img = f'<img src="assets/img/{icon}.svg"/>' if icon else ""
        self.html.append(f'<div class="chip {cls} {"" if icon else "noicon"}" id="{i}" style="{pos}">{img}{html.escape(text)}</div>')
        self.js.append(f"pop('#{i}',{a:.3f},{b:.3f},{{y:26}});")
        if sfx:
            self.add_sfx(sfx, a, 0.28)

    def emoji(self, icon, a, b, x, y, size=170, rot=-8, sfx="pop", anchor="left"):
        i = self.id("emo")
        self.html.append(f'<img class="emo" id="{i}" src="assets/img/{icon}.svg" style="{anchor}:{x}px;top:{y}px;width:{size}px;height:{size}px"/>')
        self.js.append(f"tl.fromTo('#{i}',{{autoAlpha:0,scale:.3,rotation:{rot * 3}}},{{autoAlpha:1,scale:1,rotation:{rot},duration:.5,ease:'back.out(2.4)'}},{a:.3f});")
        bob = max(0, int((b - a - 0.8) / 0.9))
        if bob:
            self.js.append(f"tl.to('#{i}',{{y:-14,duration:.45,ease:'sine.inOut',yoyo:true,repeat:{bob * 2 - 1}}},{a + 0.5:.3f});")
        self.js.append(f"tl.to('#{i}',{{autoAlpha:0,scale:.6,duration:.3,ease:'power2.in'}},{b:.3f});")
        if sfx:
            self.add_sfx(sfx, a, 0.25)

    def stamp(self, text, a, b, x, y, rot=-10, color="#ff3b3b", anchor="right"):
        i = self.id("stamp")
        self.html.append(f'<div class="stamp" id="{i}" style="{anchor}:{x}px;top:{y}px;border-color:{color};color:{color};transform:rotate({rot}deg)">{html.escape(text)}</div>')
        self.js.append(f"tl.fromTo('#{i}',{{autoAlpha:0,scale:2.3,rotation:{rot + 6}}},{{autoAlpha:1,scale:1,rotation:{rot},duration:.24,ease:'power4.in'}},{a:.3f});")
        self.js.append(f"tl.to('#{i}',{{autoAlpha:0,duration:.3}},{b:.3f});")
        self.add_sfx("impact-bass-1", a + 0.2, 0.32)

    def lowerthird(self, kicker, title, a, b, sub=None, sub_t=None, icon=None):
        i = self.id("lt")
        img = f'<img src="assets/img/{icon}.svg"/>' if icon else ""
        subh = f'<div class="c">{html.escape(sub)}</div>' if sub else ""
        self.html.append(f'<div class="lt glass" id="{i}">{img}<div><div class="a">{html.escape(kicker)}</div><div class="b">{html.escape(title)}</div>{subh}</div></div>')
        self.js.append(f"tl.fromTo('#{i}',{{autoAlpha:0,x:-90}},{{autoAlpha:1,x:0,duration:.6,ease:'power3.out'}},{a:.3f});")
        if sub:
            self.js.append(f"tl.fromTo('#{i} .c',{{autoAlpha:0,y:12}},{{autoAlpha:1,y:0,duration:.4,ease:'power2.out'}},{sub_t:.3f});")
        self.js.append(f"tl.to('#{i}',{{autoAlpha:0,x:-90,duration:.45,ease:'power2.in'}},{b:.3f});")
        self.add_sfx("whoosh-short", a, 0.22)

    def panel(self, title, items, a, b, side="right", strike=None, kicker_color="var(--pink)"):
        """items: [(text, t_out, icon or None, time_label or None)]"""
        i = self.id("panel")
        lis = []
        for k, (txt, t, icon, tm) in enumerate(items):
            img = f'<img src="assets/img/{icon}.svg"/>' if icon else ""
            tmh = f'<span class="tm">{html.escape(tm)}</span>' if tm else ""
            sk = '<i class="s"></i>' if strike else ""
            lis.append(f'<li id="{i}l{k}">{tmh}{img}<span>{html.escape(txt)}</span>{sk}</li>')
        self.html.append(f'<div class="panel glass" id="{i}" style="{side}:80px"><h3 style="color:{kicker_color}">{html.escape(title)}</h3><ul>{"".join(lis)}</ul></div>')
        self.js.append(f"tl.fromTo('#{i}',{{autoAlpha:0,x:{90 if side == 'right' else -90}}},{{autoAlpha:1,x:0,duration:.6,ease:'power3.out'}},{a:.3f});")
        for k, (txt, t, icon, tm) in enumerate(items):
            self.js.append(f"tl.fromTo('#{i}l{k}',{{autoAlpha:0,x:36}},{{autoAlpha:1,x:0,duration:.45,ease:'back.out(1.8)'}},{t:.3f});")
            self.add_sfx("click-soft", t, 0.30)
        if strike:
            self.js.append(f"tl.fromTo('#{i} li .s',{{scaleX:0}},{{scaleX:1,duration:.3,stagger:.09,ease:'power2.out'}},{strike:.3f});")
            self.js.append(f"tl.to('#{i} li',{{opacity:.55,duration:.3,stagger:.09}},{strike:.3f});")
            self.add_sfx("whoosh-short", strike, 0.25)
        self.js.append(f"tl.to('#{i}',{{autoAlpha:0,x:{90 if side == 'right' else -90},duration:.45,ease:'power2.in'}},{b:.3f});")

    def logos(self, items, x, y, b, anchor="right"):
        """items: [(key, t)] — platform badges popping one by one."""
        i = self.id("logos")
        inner = "".join(logo_html(k, f"{i}g{n}") for n, (k, t) in enumerate(items))
        self.html.append(f'<div class="logos" id="{i}" style="{anchor}:{x}px;top:{y}px">{inner}</div>')
        for n, (k, t) in enumerate(items):
            self.js.append(f"tl.fromTo('#{i}g{n}',{{autoAlpha:0,y:40,scale:.5}},{{autoAlpha:1,y:0,scale:1,duration:.45,ease:'back.out(2.2)'}},{t:.3f});")
            self.add_sfx("pop", t, 0.26)
        self.js.append(f"tl.to('#{i} .logo',{{autoAlpha:0,y:-30,duration:.35,stagger:.05,ease:'power2.in'}},{b:.3f});")

    def quote(self, parts, who, a, b, side="left"):
        """parts: [(text, t)] revealed progressively."""
        i = self.id("quote")
        spans = " ".join(f'<span id="{i}p{k}">{html.escape(tx)}</span>' for k, (tx, t) in enumerate(parts))
        pos = "left:90px" if side == "left" else "right:90px"
        self.html.append(f'<div class="quote" id="{i}" style="{pos}"><div class="m">“</div><p>{spans}</p><div class="who">— {html.escape(who)}</div></div>')
        self.js.append(f"tl.fromTo('#{i}',{{autoAlpha:0,y:34}},{{autoAlpha:1,y:0,duration:.6,ease:'power3.out'}},{a:.3f});")
        for k, (tx, t) in enumerate(parts):
            self.js.append(f"tl.to('#{i}p{k}',{{opacity:1,duration:.45}},{max(a, t - 0.25):.3f});")
        self.js.append(f"tl.to('#{i} .who',{{opacity:1,duration:.45}},{parts[-1][1] + 0.4:.3f});")
        self.js.append(f"tl.to('#{i}',{{autoAlpha:0,y:-20,duration:.45,ease:'power2.in'}},{b:.3f});")
        self.dim(a, b + 0.2)
        self.hide.append((a, b + 0.3))
        self.add_sfx("whoosh", a - 0.15, 0.22)

    def big(self, inner_html, a, b, flash=True, small=None):
        i = self.id("big")
        sm = f"<small>{html.escape(small)}</small>" if small else ""
        self.html.append(f'<div class="big" id="{i}">{sm}{inner_html}</div>')
        self.js.append(f"tl.fromTo('#{i}',{{autoAlpha:0,scale:1.5}},{{autoAlpha:1,scale:1,duration:.38,ease:'power4.out'}},{a:.3f});")
        self.js.append(f"tl.to('#{i}',{{autoAlpha:0,scale:.92,duration:.3,ease:'power2.in'}},{b:.3f});")
        if flash:
            self.js.append(f"flash({a:.3f},.7);")
        self.dim(a, b + 0.1, 0.38)
        self.hide.append((a, b + 0.15))
        self.add_sfx("whoosh-cinematic" if flash else "whoosh", a - 0.1, 0.3)

    def counter(self, n, label, icon, a, b, x, y, ticks):
        i = self.id("cnt")
        icons = "".join(f'<img id="{i}i{k}" src="assets/img/{icon}.svg"/>' for k in range(n))
        self.html.append(f'<div class="counter" id="{i}" style="left:{x}px;top:{y}px"><div class="n" id="{i}n">1</div><div><div class="l">{label}</div><div class="icons">{icons}</div></div></div>')
        self.js.append(f"tl.fromTo('#{i}',{{autoAlpha:0,x:-60}},{{autoAlpha:1,x:0,duration:.5,ease:'power3.out'}},{a:.3f});")
        for k, t in enumerate(ticks):
            self.js.append(f"tl.set('#{i}n',{{textContent:'{k + 1}'}},{t:.3f});")
            self.js.append(f"tl.fromTo('#{i}i{k}',{{autoAlpha:0,scale:.3}},{{autoAlpha:1,scale:1,duration:.3,ease:'back.out(2.5)'}},{t:.3f});")
            self.js.append(f"tl.fromTo('#{i}n',{{scale:1.25}},{{scale:1,duration:.25,ease:'power2.out',immediateRender:false}},{t:.3f});")
            self.add_sfx("notification", t, 0.25)
        self.js.append(f"tl.to('#{i}',{{autoAlpha:0,x:-60,duration:.4,ease:'power2.in'}},{b:.3f});")
        self.dim(a, b, 0.3)

    def endcard(self, l1, l2, l3, a):
        i = self.id("end")
        self.html.append(f'<div class="end" id="{i}"><div class="l1">{html.escape(l1)}</div><div class="l2">{l2}</div><div class="l3">{html.escape(l3)}</div></div>')
        self.js.append(f"tl.fromTo('#{i}',{{autoAlpha:0,scale:1.25}},{{autoAlpha:1,scale:1,duration:.55,ease:'power4.out'}},{a:.3f});")
        self.js.append(f"tl.fromTo('#{i} .l3',{{autoAlpha:0,y:16}},{{autoAlpha:1,y:0,duration:.5,ease:'power2.out',immediateRender:false}},{a + 0.6:.3f});")
        self.js.append(f"flash({a:.3f},.85);")
        self.dim(a, self.dur + 1, 0.62)
        self.hide.append((a, self.dur + 1))
        self.add_sfx("impact-bass-1", a, 0.3)

    # ---- assembly
    def build(self, outdir):
        caps = self.caps
        # caption chunks
        chunks, cur = [], []
        for k, w in enumerate(caps):
            cur.append(w)
            nx = caps[k + 1] if k + 1 < len(caps) else None
            if (nx is None or len(cur) >= 4 or sum(len(x["text"]) + 1 for x in cur) > 24 or w["text"][-1] in ".?!,"
                    or nx["start"] - w["end"] > 0.35 or (w["start"] < self.q_end <= nx["start"])):
                chunks.append(cur)
                cur = []

        def hidden(t):
            return any(a <= t < b for a, b in self.hide)

        cap_html, cap_js = [], []
        chunks = [c for c in chunks if not hidden(c[0]["start"])]
        for k, ch in enumerate(chunks):
            s = ch[0]["start"]
            e = min(chunks[k + 1][0]["start"] if k + 1 < len(chunks) else ch[-1]["end"] + 0.5, ch[-1]["end"] + 0.7)
            for a, b in self.hide:
                if s < a < e:
                    e = a
            e = max(e, s + 0.2)
            q = " q" if s < self.q_end else ""
            spans = " ".join(f'<span id="w{k}_{j}">{html.escape(w["text"])}</span>' for j, w in enumerate(ch))
            cap_html.append(f'<div class="cap{q}" id="c{k}">{spans}</div>')
            cap_js.append(f"cap('#c{k}',{s:.3f},{e:.3f});")
            col = "#FF4FA3" if q else "#3CFF9A"
            for j, w in enumerate(ch):
                cap_js.append(f"hl('#w{k}_{j}',{w['start']:.3f},'{col}');")
        # framing: alternate zoom at cuts (only for segments long enough), slow drift inside segment
        Z = [1.0, 1.10, 1.04, 1.13]
        zi, zoom_js = 0, []
        for n, (s, e, o, d) in enumerate(self.mp):
            if n and d >= 1.0:
                zi += 1
            z = Z[zi % 4]
            zoom_js.append(f"tl.fromTo('#vw',{{scale:{z}}},{{scale:{z + 0.022:.3f},duration:{d - 0.01:.3f},ease:'none',immediateRender:false}},{o:.3f});")
        dim_js = []
        merged = []
        for a, b, lv in sorted(self.dims):
            if merged and a <= merged[-1][1] + 0.6:
                merged[-1][1] = max(merged[-1][1], b); merged[-1][2] = max(merged[-1][2], lv)
            else:
                merged.append([a, b, lv])
        for a, b, lv in merged:
            dim_js.append(f"tl.to('#dim',{{opacity:{lv},duration:.45,ease:'power2.out'}},{a:.3f});tl.to('#dim',{{opacity:0,duration:.45,ease:'power2.inOut'}},{min(b, self.dur - 0.05):.3f});")
        sfx_html = []
        ded = []
        for nm, t, vol in sorted(self.sfx, key=lambda x: x[1]):
            if any(abs(t - t2) < 0.2 for _, t2, _ in ded):
                continue
            ded.append((nm, t, vol))
        for k, (nm, t, vol) in enumerate(ded):
            t = max(0.0, t)
            if t > self.dur - 0.3:
                continue
            ln = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                       f"{SHARED}/sfx/{nm}.mp3"], capture_output=True, text=True).stdout)
            ln = min(ln, self.dur - t)
            sfx_html.append(f'<audio id="sfx{k}" data-start="{t:.3f}" data-duration="{ln:.3f}" data-volume="{vol}" src="assets/sfx/{nm}.mp3"></audio>')
        D = self.dur
        page = f"""<!doctype html>
<html lang="fr"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1920, height=1080"/>
<script src="assets/gsap.min.js"></script>
<style>{CSS}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D:.3f}" data-width="1920" data-height="1080">
  <div id="vw"><video id="v" class="clip" data-start="0" data-duration="{D:.3f}" data-has-audio="true" src="assets/{self.name}_cut.mp4" playsinline></video></div>
  <div id="grade"></div><div id="dim"></div>
  <div class="qcard glass" id="qcard"><div class="k">QUESTION <b>{self.qnum}</b> / 3</div><div class="t">{html.escape(self.qtitle)}</div><div class="u"></div></div>
  {''.join(self.html)}
  {''.join(cap_html)}
  <div id="flash"></div><div id="bar"></div>
  {''.join(sfx_html)}
</div>
<script>
const tl = gsap.timeline({{paused:true}});
function cap(id,a,b){{tl.fromTo(id,{{opacity:0,y:14,scale:.96}},{{opacity:1,y:0,scale:1,duration:.16,ease:'power2.out',immediateRender:false}},a);tl.to(id,{{opacity:0,duration:.12}},b);}}
function hl(id,a,c){{tl.to(id,{{color:c,duration:.08}},a);}}
function flash(a,v){{tl.fromTo('#flash',{{opacity:v}},{{opacity:0,duration:.45,ease:'power2.out',immediateRender:false}},a);}}
const pop=(id,a,b,from)=>{{tl.fromTo(id,Object.assign({{autoAlpha:0,scale:.55}},from||{{}}),{{autoAlpha:1,scale:1,x:0,y:0,duration:.45,ease:'back.out(2)'}},a);tl.to(id,{{autoAlpha:0,scale:.9,y:-10,duration:.3,ease:'power2.in'}},b);}};
tl.fromTo('#bar',{{scaleX:0}},{{scaleX:1,duration:{D:.3f},ease:'none'}},0);
{''.join(zoom_js)}
tl.fromTo('#qcard',{{autoAlpha:0,x:-70}},{{autoAlpha:1,x:0,duration:.7,ease:'power3.out'}},0.1);
tl.fromTo('#qcard .u',{{scaleX:0}},{{scaleX:1,duration:.7,ease:'power2.out'}},0.55);
tl.to('#qcard',{{autoAlpha:0,x:-70,duration:.5,ease:'power2.in'}},{self.q_end - 0.15:.3f});
{''.join(dim_js)}
{''.join(self.js)}
{''.join(cap_js)}
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>
"""
        os.makedirs(f"{outdir}/assets", exist_ok=True)
        for sub in ("fonts", "img", "sfx"):
            if os.path.exists(f"{outdir}/assets/{sub}"):
                shutil.rmtree(f"{outdir}/assets/{sub}")
            shutil.copytree(f"{SHARED}/{sub}", f"{outdir}/assets/{sub}")
        shutil.copy(f"{SHARED}/gsap.min.js", f"{outdir}/assets/gsap.min.js")
        open(f"{outdir}/index.html", "w").write(page)
        json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                   "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
                   "media": {"autoProxy": True}}, open(f"{outdir}/hyperframes.json", "w"), indent=2)
        json.dump({"id": self.name, "name": f"Question {self.qnum}"}, open(f"{outdir}/meta.json", "w"))
        return len(chunks)

"""HyperFrames composition builder for the Bognin shorts (landscape 1920x1080 + portrait 1080x1920).

Times are OUTPUT seconds. Components: word-by-word captions, title hook, name tag, chips, stamps,
emojis, checklist panel, full-screen statement, grayscale mood, end card, subtle SFX.
"""
import html, json, os, shutil, subprocess

REPO = "/home/claude/claude"
SHARED = f"{REPO}/videos/_shared"

LAYOUT = {
    "land": dict(W=1920, H=1080, cap_top=250, cap_size=66, cap_max_chars=24, cap_max_words=4,
                 chip_y=78, chip_x=80, emo_x=1470, emo_y=360, emo_alt_x=200, emo_alt_y=430, panel_top=440, panel_left=80,
                 title_css="left:80px;top:470px;width:max-content;max-width:820px", name_css="left:80px;bottom:110px",
                 big_size=124, origin="60% 75%", stamp_x=100, stamp_y=60),
    "port": dict(W=1080, H=1920, cap_top=585, cap_size=80, cap_max_chars=17, cap_max_words=3,
                 chip_y=400, chip_x=0, emo_x=820, emo_y=740, emo_alt_x=40, emo_alt_y=720, panel_top=150, panel_left=90,
                 title_css="left:60px;right:60px;top:140px", name_css="left:50%;top:405px",
                 big_size=118, origin="50% 72%", stamp_x=0, stamp_y=400),
}

CSS = """
@font-face{font-family:Inter;font-weight:700;src:url(assets/fonts/inter-latin-700-normal.woff2)}
@font-face{font-family:Inter;font-weight:800;src:url(assets/fonts/inter-latin-800-normal.woff2)}
@font-face{font-family:Inter;font-weight:900;src:url(assets/fonts/inter-latin-900-normal.woff2)}
@font-face{font-family:Mont;font-weight:900;src:url(assets/fonts/montserrat-latin-900-normal.woff2)}
@font-face{font-family:Mont;font-weight:800;src:url(assets/fonts/montserrat-latin-800-normal.woff2)}
:root{--neon:#3CFF9A;--pink:#FF4FA3;--sky:#5AC8FF;--sun:#FFD23F;--red:#FF3B3B;--ink:#0b0d10}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:__W__px;height:__H__px;overflow:hidden;background:#000;font-family:Inter,sans-serif}
#root{position:relative;width:__W__px;height:__H__px;overflow:hidden}
#vw{position:absolute;inset:0;transform-origin:__ORIGIN__}
#vw video{width:100%;height:100%;object-fit:cover;display:block}
#grade{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at 50% 60%,rgba(0,0,0,0) 50%,rgba(0,0,0,.40) 100%)}
#mood{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at 50% 62%,rgba(0,0,0,0) 30%,rgba(5,8,14,.62) 100%);opacity:0}
#dim{position:absolute;inset:0;background:#05070a;opacity:0}
#flash{position:absolute;inset:0;background:#fff;opacity:0}
#bar{position:absolute;left:0;top:0;height:8px;width:__W__px;background:linear-gradient(90deg,var(--neon),var(--sky));transform-origin:0 50%;box-shadow:0 0 16px rgba(60,255,154,.7)}
.cap{position:absolute;left:40px;right:40px;top:__CAPTOP__px;text-align:center;font-family:Mont;font-weight:900;font-size:__CAPSIZE__px;line-height:1.08;color:#fff;
  text-transform:uppercase;letter-spacing:.005em;opacity:0;text-shadow:0 5px 0 rgba(0,0,0,.9),0 0 22px rgba(0,0,0,.75);-webkit-text-stroke:3px #000;paint-order:stroke fill}
.cap span{display:inline-block;margin:0 .16em}
.cap span.k{color:var(--sun)}
.glass{background:rgba(12,14,18,.72);border:2px solid rgba(255,255,255,.14);border-radius:28px;box-shadow:0 24px 70px rgba(0,0,0,.45)}
.title{position:absolute;padding:24px 34px 26px;opacity:0;text-align:left}
.title .k{font-size:24px;font-weight:800;letter-spacing:.28em;color:var(--pink)}
.title .t{margin-top:8px;font-family:Mont;font-weight:900;font-size:50px;line-height:1.02;color:#fff;letter-spacing:-.01em;text-transform:uppercase}
.title .t em{font-style:normal;color:var(--sun)}
.name{position:absolute;display:flex;align-items:center;gap:16px;padding:14px 28px 14px 16px;border-radius:999px;opacity:0;white-space:nowrap}
.name .dot{width:18px;height:18px;border-radius:50%;background:var(--neon);box-shadow:0 0 14px var(--neon)}
.name b{font-size:34px;font-weight:900;color:#fff;letter-spacing:.04em}
.name i{font-style:normal;font-size:26px;font-weight:700;color:#cfd3d8;margin-left:6px}
.chip{position:absolute;display:flex;align-items:center;gap:16px;padding:14px 30px 14px 16px;border-radius:999px;font-weight:900;font-size:40px;
  color:var(--ink);background:var(--neon);opacity:0;box-shadow:0 14px 40px rgba(0,0,0,.45);white-space:nowrap}
.chip img{width:58px;height:58px}
.chip.white{background:#fff}.chip.sun{background:var(--sun)}.chip.red{background:var(--red);color:#fff}
.chip.dark{background:rgba(12,14,18,.88);color:#fff;border:2px solid rgba(255,255,255,.18)}
.emo{position:absolute;opacity:0;filter:drop-shadow(0 14px 26px rgba(0,0,0,.5))}
.stamp{position:absolute;padding:12px 34px;border:9px solid var(--red);color:var(--red);font-family:Mont;font-weight:900;font-size:76px;
  border-radius:16px;opacity:0;letter-spacing:.03em;background:rgba(255,255,255,.12);white-space:nowrap}
.panel{position:absolute;padding:28px 36px 22px;opacity:0;min-width:440px;max-width:__PANELMAX__}
.panel h3{font-size:26px;letter-spacing:.24em;color:var(--pink);font-weight:800}
.panel ul{list-style:none;margin-top:10px}
.panel li{display:flex;align-items:center;gap:18px;font-family:Mont;font-size:__PANELFS__px;font-weight:900;color:#fff;padding:8px 0;opacity:0;text-transform:uppercase}
.panel li span{line-height:1.05}
.panel li img{flex:none;width:__PANELIMG__px;height:__PANELIMG__px}
.big{position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);text-align:center;font-family:Mont;font-weight:900;font-size:__BIG__px;letter-spacing:-.02em;
  color:#fff;opacity:0;text-shadow:0 10px 50px rgba(0,0,0,.7);line-height:.98;text-transform:uppercase}
.big em{font-style:normal;color:var(--red)}
.big small{display:block;font-family:Inter;font-size:40px;font-weight:800;letter-spacing:.3em;color:#fff;margin-bottom:22px}
.logos{position:absolute;display:flex;gap:24px}
.logo{width:124px;height:124px;border-radius:32px;display:flex;align-items:center;justify-content:center;opacity:0;box-shadow:0 16px 40px rgba(0,0,0,.5)}
.logo svg{width:72px;height:72px;fill:#fff}
.logo .in{font-family:Inter;font-weight:900;font-size:78px;color:#fff;letter-spacing:-.04em;line-height:1}
.end{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;opacity:0;text-align:center;padding:0 60px}
.end .l1{font-size:46px;font-weight:800;color:#fff;letter-spacing:.32em}
.end .l2{font-family:Mont;font-size:__END__px;font-weight:900;color:var(--neon);letter-spacing:-.02em;line-height:1;margin-top:16px}
.end .l3{margin-top:34px;font-size:38px;font-weight:800;color:var(--ink);background:#fff;padding:16px 34px;border-radius:999px;letter-spacing:.02em}
"""


class Comp:
    def __init__(self, name, orient, dur, video, caps, keywords=(), face=None):
        self.name, self.o, self.L, self.dur, self.video = name, orient, LAYOUT[orient], dur, video
        self.caps, self.keywords = caps, {k.lower() for k in keywords}
        self.html, self.js, self.sfx, self.hide, self.dims, self.zoom = [], [], [], [], [], []
        self.n = 0
        self.title_hide = []
        self.face = face or (lambda t: 0.5)        # speaker's horizontal centre (0..1 of the 16:9 frame) at output time t

    def free_side(self, a, b):
        """Landscape: the side away from the speaker's face over [a, b]."""
        xs = [self.face(a + k * (b - a) / 8) for k in range(9)]
        return "right" if sum(xs) / len(xs) < 0.5 else "left"

    def id(self, p):
        self.n += 1
        return f"{p}{self.n}"

    def add_sfx(self, nm, t, vol):
        self.sfx.append((nm, t, vol))

    # ------------------------------------------------------------- components
    def title(self, kicker, text_html, a, b, hold=True):
        i = "title"
        css = self.L["title_css"]
        if self.o == "land" and self.free_side(a, min(b, a + 3)) == "right":
            css = css.replace("left:80px", "right:80px")
        self.html.append(f'<div class="title glass" id="{i}" style="{css}"><div class="k">{html.escape(kicker)}</div><div class="t">{text_html}</div></div>')
        self.js.append(f"tl.fromTo('#{i}',{{autoAlpha:0,y:-30}},{{autoAlpha:1,y:0,duration:.6,ease:'power3.out'}},{a:.3f});")
        self.title_window = (a, b)

    def name_tag(self, name, role, a, b):
        i = self.id("name")
        self.html.append(f'<div class="name glass" id="{i}" style="{self.L["name_css"]}"><span class="dot"></span><b>{html.escape(name)}</b><i>{html.escape(role)}</i></div>')
        if self.o == "port":
            self.js.append(f"(function(){{const e=document.querySelector('#{i}');e.style.marginLeft=(-e.offsetWidth/2)+'px';}})();")
        self.js.append(f"tl.fromTo('#{i}',{{autoAlpha:0,y:24}},{{autoAlpha:1,y:0,duration:.5,ease:'power3.out'}},{a:.3f});")
        self.js.append(f"tl.to('#{i}',{{autoAlpha:0,y:-12,duration:.35,ease:'power2.in'}},{b:.3f});")
        self.add_sfx("whoosh-short", a, 0.18)

    def chip(self, text, a, b, icon=None, cls="", y=None):
        i = self.id("chip")
        L = self.L
        y = L["chip_y"] if y is None else y
        pos = f"left:{L['chip_x']}px;top:{y}px" if self.o == "land" else f"left:50%;top:{y}px;margin-left:-9999px"
        img = f'<img src="assets/img/{icon}.svg"/>' if icon else ""
        self.html.append(f'<div class="chip {cls}" id="{i}" style="{pos}">{img}{html.escape(text)}</div>')
        if self.o == "port":     # centre horizontally once fonts are in
            self.js.append(f"(function(){{const e=document.querySelector('#{i}');e.style.marginLeft=(-e.offsetWidth/2)+'px';}})();")
        self.js.append(f"pop('#{i}',{a:.3f},{b:.3f},{{y:24}});")
        self.add_sfx("pop", a, 0.20)

    def emoji(self, icon, a, b, side="r", size=None, rot=-8, sfx=True):
        i = self.id("emo")
        L = self.L
        size = size or (170 if self.o == "land" else 190)
        if self.o == "land":
            fx = self.face(a + 0.3) * L["W"]
            ex = (L["emo_x"] if side == "r" else L["emo_alt_x"]) + size / 2
            if abs(fx - ex) < 330:
                side = "l" if side == "r" else "r"
        x, y = (L["emo_x"], L["emo_y"]) if side == "r" else (L["emo_alt_x"], L["emo_alt_y"])
        if self.o == "port" and side == "r":
            x = L["W"] - size - 50
        self.html.append(f'<img class="emo" id="{i}" src="assets/img/{icon}.svg" style="left:{x}px;top:{y}px;width:{size}px;height:{size}px"/>')
        self.js.append(f"tl.fromTo('#{i}',{{autoAlpha:0,scale:.3,rotation:{rot * 3}}},{{autoAlpha:1,scale:1,rotation:{rot},duration:.5,ease:'back.out(2.4)'}},{a:.3f});")
        bob = max(0, int((b - a - 0.8) / 0.9))
        if bob:
            self.js.append(f"tl.to('#{i}',{{y:-14,duration:.45,ease:'sine.inOut',yoyo:true,repeat:{bob * 2 - 1}}},{a + 0.5:.3f});")
        self.js.append(f"tl.to('#{i}',{{autoAlpha:0,scale:.6,duration:.3,ease:'power2.in'}},{b:.3f});")
        if sfx:
            self.add_sfx("pop", a, 0.18)

    def stamp(self, text, a, b, rot=-8):
        i = self.id("stamp")
        L = self.L
        pos = f"right:{L['stamp_x']}px;top:{L['stamp_y']}px" if self.o == "land" else f"left:50%;top:{L['stamp_y']}px"
        self.html.append(f'<div class="stamp" id="{i}" style="{pos}">{html.escape(text)}</div>')
        if self.o == "port":
            self.js.append(f"(function(){{const e=document.querySelector('#{i}');e.style.marginLeft=(-e.offsetWidth/2)+'px';}})();")
        self.js.append(f"tl.fromTo('#{i}',{{autoAlpha:0,scale:2.2,rotation:{rot + 6}}},{{autoAlpha:1,scale:1,rotation:{rot},duration:.24,ease:'power4.in'}},{a:.3f});")
        self.js.append(f"tl.to('#{i}',{{autoAlpha:0,duration:.3}},{b:.3f});")
        self.add_sfx("impact-bass-1", a + 0.2, 0.24)

    def panel(self, kicker, items, a, b):
        """items: [(text, t, icon)] revealed one by one."""
        i = self.id("panel")
        L = self.L
        side = self.free_side(a, b) if self.o == "land" else "left"
        pos = (f"{side}:{L['panel_left']}px;top:{L['panel_top']}px" if self.o == "land"
               else f"left:{L['panel_left']}px;right:{L['panel_left']}px;top:{L['panel_top']}px")
        dx = -80 if side == "left" else 80
        lis = "".join(f'<li id="{i}l{k}"><img src="assets/img/{ic}.svg"/><span>{html.escape(tx)}</span></li>' for k, (tx, t, ic) in enumerate(items))
        self.html.append(f'<div class="panel glass" id="{i}" style="{pos}"><h3>{html.escape(kicker)}</h3><ul>{lis}</ul></div>')
        self.js.append(f"tl.fromTo('#{i}',{{autoAlpha:0,x:{dx}}},{{autoAlpha:1,x:0,duration:.55,ease:'power3.out'}},{a:.3f});")
        for k, (tx, t, ic) in enumerate(items):
            self.js.append(f"tl.fromTo('#{i}l{k}',{{autoAlpha:0,x:34}},{{autoAlpha:1,x:0,duration:.45,ease:'back.out(1.8)'}},{t:.3f});")
            self.add_sfx("click-soft", t, 0.26)
        self.js.append(f"tl.to('#{i}',{{autoAlpha:0,x:{dx},duration:.4,ease:'power2.in'}},{b:.3f});")
        if self.o == "port":
            self.title_hide.append((a - 0.3, b + 0.45))

    LOGO_BG = {"linkedin": "#0A66C2", "instagram": "linear-gradient(45deg,#f9ce34,#ee2a7b 50%,#6228d7)", "facebook": "#0866FF",
               "tiktok": "#111", "youtube": "#FF0000", "whatsapp": "#25D366"}

    def logos(self, items, b, y=None):
        """items: [(platform, t)] — badges popping one by one (row centred in portrait, right side in landscape)."""
        i = self.id("logos")
        inner = []
        for n, (k, t) in enumerate(items):
            if k == "linkedin":
                body = '<span class="in">in</span>'
            else:
                body = open(f"{SHARED}/logos/{k}.svg").read().replace("<svg ", '<svg fill="#fff" ', 1)
            inner.append(f'<div class="logo" id="{i}g{n}" style="background:{self.LOGO_BG[k]}">{body}</div>')
        if self.o == "port":
            pos = f"left:0;right:0;justify-content:center;top:{y or 400}px"
        else:
            pos = f"right:110px;top:{y or 420}px"
        self.html.append(f'<div class="logos" id="{i}" style="{pos}">{"".join(inner)}</div>')
        for n, (k, t) in enumerate(items):
            self.js.append(f"tl.fromTo('#{i}g{n}',{{autoAlpha:0,y:40,scale:.5}},{{autoAlpha:1,y:0,scale:1,duration:.45,ease:'back.out(2.2)'}},{t:.3f});")
            self.add_sfx("pop", t, 0.18)
        self.js.append(f"tl.to('#{i} .logo',{{autoAlpha:0,y:-30,duration:.35,stagger:.05,ease:'power2.in'}},{b:.3f});")

    def big(self, inner, a, b, small=None):
        i = self.id("big")
        sm = f"<small>{html.escape(small)}</small>" if small else ""
        self.html.append(f'<div class="big" id="{i}">{sm}{inner}</div>')
        self.js.append(f"tl.fromTo('#{i}',{{autoAlpha:0,scale:1.45}},{{autoAlpha:1,scale:1,duration:.34,ease:'power4.out'}},{a:.3f});")
        self.js.append(f"tl.to('#{i}',{{autoAlpha:0,scale:.94,duration:.28,ease:'power2.in'}},{b:.3f});")
        self.js.append(f"flash({a:.3f},.55);")
        self.dims.append((a, b + 0.05, 0.55))
        self.hide.append((a, b + 0.1))
        self.title_hide.append((a - 0.1, b + 0.2))
        self.add_sfx("impact-bass-1", a, 0.26)

    def mood(self, a, b, gray=0.85):
        """Desaturate + darker vignette for an emotional line."""
        self.js.append(f"tl.to('#vw',{{filter:'grayscale({gray}) contrast(1.06) brightness(.92)',duration:.8,ease:'power2.inOut'}},{a:.3f});")
        self.js.append(f"tl.to('#mood',{{opacity:1,duration:.8,ease:'power2.inOut'}},{a:.3f});")
        if b < self.dur:
            self.js.append(f"tl.to('#vw',{{filter:'grayscale(0) contrast(1) brightness(1)',duration:.6}},{b:.3f});")
            self.js.append(f"tl.to('#mood',{{opacity:0,duration:.6}},{b:.3f});")

    def endcard(self, l1, l2, l3, a):
        i = self.id("end")
        l2 = l2.replace(" ?", "&nbsp;?").replace(" !", "&nbsp;!")
        self.html.append(f'<div class="end" id="{i}"><div class="l1">{html.escape(l1)}</div><div class="l2">{l2}</div><div class="l3">{html.escape(l3)}</div></div>')
        self.js.append(f"tl.fromTo('#{i}',{{autoAlpha:0,scale:1.2}},{{autoAlpha:1,scale:1,duration:.5,ease:'power4.out'}},{a:.3f});")
        self.js.append(f"tl.fromTo('#{i} .l3',{{autoAlpha:0,y:16}},{{autoAlpha:1,y:0,duration:.45,ease:'back.out(2)',immediateRender:false}},{a + 0.5:.3f});")
        self.js.append(f"flash({a:.3f},.7);")
        self.dims.append((a, self.dur + 1, 0.68))
        self.hide.append((a, self.dur + 1))
        self.title_hide.append((a - 0.1, self.dur + 1))
        self.add_sfx("whoosh-cinematic", a - 0.25, 0.22)

    def zooms(self, mp, Z=(1.0, 1.07, 1.03, 1.09)):
        zi = 0
        for n, (s, e, o, d) in enumerate(mp):
            if n and d >= 0.9:
                zi += 1
            z = Z[zi % len(Z)]
            self.zoom.append(f"tl.fromTo('#vw',{{scale:{z}}},{{scale:{z + 0.018:.3f},duration:{max(d - 0.01, 0.05):.3f},ease:'none',immediateRender:false}},{o:.3f});")

    # ------------------------------------------------------------- assembly
    def build(self, outdir):
        L = self.L
        caps = self.caps
        chunks, cur = [], []
        for k, w in enumerate(caps):
            cur.append(w)
            nx = caps[k + 1] if k + 1 < len(caps) else None
            if (nx is None or len(cur) >= L["cap_max_words"] or sum(len(x["text"]) + 1 for x in cur) + len(nx["text"]) > L["cap_max_chars"]
                    or w["text"][-1] in ".?!," or nx["start"] - w["end"] > 0.30):
                chunks.append(cur)
                cur = []
        hidden = lambda t: any(a <= t < b for a, b in self.hide)
        chunks = [c for c in chunks if not hidden(c[0]["start"])]
        cap_html, cap_js = [], []
        for k, ch in enumerate(chunks):
            s = ch[0]["start"]
            e = min(chunks[k + 1][0]["start"] if k + 1 < len(chunks) else ch[-1]["end"] + 0.4, ch[-1]["end"] + 0.6)
            for a, b in self.hide:
                if s < a < e:
                    e = a
            e = max(e, s + 0.2)
            spans = " ".join(f'<span id="w{k}_{j}" class="{"k" if w["text"].lower().strip(",.!?") in self.keywords else ""}">'
                             f'{html.escape(w["text"].rstrip(","))}</span>' for j, w in enumerate(ch))
            cap_html.append(f'<div class="cap" id="c{k}">{spans}</div>')
            cap_js.append(f"cap('#c{k}',{s:.3f},{e:.3f});")
            for j, w in enumerate(ch):
                kw = w["text"].lower().strip(",.!?") in self.keywords
                cap_js.append(f"hl('#w{k}_{j}',{w['start']:.3f},{'true' if kw else 'false'});")
        dims, merged = [], []
        for a, b, lv in sorted(self.dims):
            if merged and a <= merged[-1][1] + 0.5:
                merged[-1][1] = max(merged[-1][1], b); merged[-1][2] = max(merged[-1][2], lv)
            else:
                merged.append([a, b, lv])
        for a, b, lv in merged:
            dims.append(f"tl.to('#dim',{{opacity:{lv},duration:.35,ease:'power2.out'}},{a:.3f});")
            if b < self.dur:
                dims.append(f"tl.to('#dim',{{opacity:0,duration:.4,ease:'power2.inOut'}},{b:.3f});")
        th = []
        if hasattr(self, "title_window"):
            ta, tb = self.title_window
            merged_th = []                 # back-to-back hides (panels in a row) must not flash the title in between
            for a, b in sorted(self.title_hide):
                if merged_th and a <= merged_th[-1][1] + 1.0:
                    merged_th[-1][1] = max(merged_th[-1][1], b)
                else:
                    merged_th.append([a, b])
            for a, b in merged_th:
                if a >= tb:
                    continue
                th.append(f"tl.to('#title',{{autoAlpha:0,y:-20,duration:.3,ease:'power2.in'}},{max(a, 0.8):.3f});")
                if b < min(tb, self.dur):
                    th.append(f"tl.to('#title',{{autoAlpha:1,y:0,duration:.4,ease:'power2.out'}},{b:.3f});")
            if tb < self.dur:
                th.append(f"tl.to('#title',{{autoAlpha:0,y:-20,duration:.4,ease:'power2.in'}},{tb:.3f});")
        sfx_html, used = [], []
        for nm, t, vol in sorted(self.sfx, key=lambda x: x[1]):
            if any(abs(t - t2) < 0.2 for _, t2, _ in used) or t > self.dur - 0.3:
                continue
            used.append((nm, max(0.0, t), vol))
        for k, (nm, t, vol) in enumerate(used):
            ln = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                       f"{SHARED}/sfx/{nm}.mp3"], capture_output=True, text=True).stdout)
            sfx_html.append(f'<audio id="sfx{k}" data-start="{t:.3f}" data-duration="{min(ln, self.dur - t):.3f}" data-volume="{vol}" src="assets/sfx/{nm}.mp3"></audio>')
        css = (CSS.replace("__W__", str(L["W"])).replace("__H__", str(L["H"])).replace("__ORIGIN__", L["origin"])
               .replace("__CAPTOP__", str(L["cap_top"])).replace("__CAPSIZE__", str(L["cap_size"]))
               .replace("__BIG__", str(L["big_size"])).replace("__PANELFS__", "36" if self.o == "land" else "50").replace("__PANELIMG__", "46" if self.o == "land" else "62").replace("__PANELMAX__", "640px" if self.o == "land" else "none").replace("__END__", "150" if self.o == "land" else "130"))
        D = self.dur
        page = f"""<!doctype html>
<html lang="fr"><head><meta charset="UTF-8"/><meta name="viewport" content="width={L['W']}, height={L['H']}"/>
<script src="assets/gsap.min.js"></script>
<style>{css}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D:.3f}" data-width="{L['W']}" data-height="{L['H']}" data-fps="25">
  <div id="vw"><video id="v" class="clip" data-start="0" data-duration="{D:.3f}" data-has-audio="true" src="assets/{os.path.basename(self.video)}" playsinline></video></div>
  <div id="grade"></div><div id="mood"></div><div id="dim"></div>
  {''.join(self.html)}
  {''.join(cap_html)}
  <div id="flash"></div><div id="bar"></div>
  {''.join(sfx_html)}
</div>
<script>
const tl = gsap.timeline({{paused:true}});
function cap(id,a,b){{tl.fromTo(id,{{opacity:0,y:16,scale:.94}},{{opacity:1,y:0,scale:1,duration:.14,ease:'back.out(2)',immediateRender:false}},a);tl.to(id,{{opacity:0,duration:.06}},Math.max(a+.16,b-.07));}}
function hl(id,a,k){{tl.fromTo(id,{{scale:1}},{{scale:1.06,color:k?'#FFD23F':'#3CFF9A',duration:.08,immediateRender:false}},a);tl.to(id,{{scale:1,duration:.18}},a+.22);if(!k)tl.to(id,{{color:'#ffffff',duration:.12}},a+.38);}}
function flash(a,v){{tl.fromTo('#flash',{{opacity:v}},{{opacity:0,duration:.4,ease:'power2.out',immediateRender:false}},a);}}
const pop=(id,a,b,from)=>{{tl.fromTo(id,Object.assign({{autoAlpha:0,scale:.55}},from||{{}}),{{autoAlpha:1,scale:1,x:0,y:0,duration:.42,ease:'back.out(2)'}},a);tl.to(id,{{autoAlpha:0,scale:.9,y:-10,duration:.28,ease:'power2.in'}},b);}};
tl.fromTo('#bar',{{scaleX:0}},{{scaleX:1,duration:{D:.3f},ease:'none'}},0);
{''.join(self.zoom)}
{''.join(dims)}
{''.join(self.js)}
{''.join(th)}
{''.join(cap_js)}
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>
"""
        os.makedirs(f"{outdir}/assets", exist_ok=True)
        icons = sorted(set(re.findall(r'assets/img/([\w-]+)\.svg', page)))
        sfxs = sorted(set(re.findall(r'assets/sfx/([\w-]+)\.mp3', page)))
        for sub in ("img", "sfx", "fonts"):
            shutil.rmtree(f"{outdir}/assets/{sub}", ignore_errors=True)
            os.makedirs(f"{outdir}/assets/{sub}")
        for ic in icons:
            shutil.copy(f"{SHARED}/img/{ic}.svg", f"{outdir}/assets/img/")
        for s in sfxs:
            shutil.copy(f"{SHARED}/sfx/{s}.mp3", f"{outdir}/assets/sfx/")
        shutil.copy(f"{SHARED}/sfx/CREDITS.md", f"{outdir}/assets/sfx/")
        for f in os.listdir(f"{SHARED}/fonts"):
            shutil.copy(f"{SHARED}/fonts/{f}", f"{outdir}/assets/fonts/")
        shutil.copy(f"{SHARED}/gsap.min.js", f"{outdir}/assets/gsap.min.js")
        open(f"{outdir}/index.html", "w").write(page)
        json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                   "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
                   "media": {"autoProxy": True}}, open(f"{outdir}/hyperframes.json", "w"), indent=2)
        json.dump({"id": f"{self.name}_{self.o}", "name": f"Bognin {self.name} ({self.o})"}, open(f"{outdir}/meta.json", "w"))
        return len(chunks)


import re  # noqa: E402  (used in build)

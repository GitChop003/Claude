"""Génère la composition HyperFrames d'un short à partir de sa spec et de words.json.

Kit motion validé dans le configurateur : palette nuancée, verre subtil, texte allégé,
sous-titres 1 à 3 mots (doublure Montserrat italique en attendant Callum Slanted),
mot clé cyan à 120 %, punch-in sur les coupes (au plus toutes les ~4 s),
cartes plein écran, inserts HD, CTA en barre de recherche, carte de fin.
"""
import json, os, re, sys, html

KIT = os.path.join(os.path.dirname(__file__), "../../videos/shorts/_kit")


def esc(t): return html.escape(t, quote=True)


def chunks(words, kws):
    """Groupe les mots en sous-titres de 1 à 3 mots (≤ 20 caractères), coupure sur ponctuation ou pause."""
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        txt = " ".join(x["w"] for x in cur)
        nxt = words[i + 1] if i + 1 < len(words) else None
        brk = (len(cur) >= 3 or len(txt) >= 16 or re.search(r"[.,!?;:…]$", w["w"])
               or (nxt and nxt["s"] - w["e"] > 0.22) or nxt is None)
        if brk:
            out.append(cur); cur = []
    res = []
    for c in out:
        res.append({"s": c[0]["s"], "e": c[-1]["e"], "w": [(x["w"], norm(x["w"]) in kws) for x in c]})
    for i in range(len(res) - 1):  # le sous-titre reste jusqu'au suivant si l'écart est court
        if res[i + 1]["s"] - res[i]["e"] < 0.35: res[i]["e"] = res[i + 1]["s"]
    return res


def norm(w): return re.sub(r"[^\wÀ-ÿ'-]", "", w.lower())


def main(spec_path, words_path, out_dir):
    sp = json.load(open(spec_path)); W = json.load(open(words_path))
    dur = W["dur"] + 1.4  # 1,4 s de carte de fin après la dernière phrase
    kws = {norm(k) for k in sp.get("keywords", [])}
    rep = {k: v for k, v in sp.get("replace", {}).items()}
    for w in W["words"]:
        if w["w"] in rep: w["w"] = rep[w["w"]]
    for word, n, new in sp.get("replace_n", []):  # correction de la n-ième occurrence seulement
        for w in W["words"]:
            if w["w"] == word:
                n -= 1
                if n == 0: w["w"] = new; break
    W["words"] = [w for w in W["words"] if w["w"].strip()]
    for w in W["words"]: w["s"] = max(0.0, w["s"])
    def at(x):
        if isinstance(x, (int, float)): return float(x)
        n = x.get("n", 1); off = x.get("off", 0.0)
        exact = [w for w in W["words"] if w["w"] == x["word"]]  # d'abord l'orthographe exacte (casse, ponctuation)
        if len(exact) >= n: return exact[n - 1]["s"] + off
        for w in W["words"]:
            if norm(w["w"]) == norm(x["word"]):
                n -= 1
                if n == 0: return w["s"] + off
        raise SystemExit(f"ancre introuvable: {x}")
    caps = chunks(W["words"], kws)
    ins = {n: [at(v[0]), v[1]] for n, v in sp.get("inserts", {}).items()}  # {"1":[t|ancre,slot],...}
    insw = [(v[0], v[0] + min(2.0, v[1])) for v in ins.values()]
    flash = sp.get("flash", [])  # [{"t":..|ancre,"a":..,"b":..,"lab":..}]
    for f in flash: f["t"] = at(f["t"])
    # sous-titres masqués pendant les cartes plein écran
    fw = [(f["t"], f["t"] + f.get("d", 1.0)) for f in flash]
    cap_html, cap_js = [], []
    for i, c in enumerate(caps):
        if any(a <= c["s"] < b for a, b in fw): continue
        oi = " oi" if any(a <= c["s"] < b for a, b in insw) else ""
        spans = " ".join(f'<span class="kw">{esc(w)}</span>' if k else f"<span>{esc(w)}</span>" for w, k in c["w"])
        cap_html.append(f'<div class="cap{oi}" id="c{i}">{spans}</div>')
        nxt = caps[i + 1]["s"] if i + 1 < len(caps) else W["dur"]
        cap_js.append(f"cap('#c{i}',{c['s']:.3f},{min(c['e']+0.05, nxt, W['dur']):.3f});")
    # punch-in : à une coupe, au plus toutes les 4 s, alterne 1,00 / 1,08
    zoom_js, last, z = [], -9, 1.0
    for t in W["cuts"][:-1]:
        if t - last >= 4.0 and t > 3.2:
            z = 1.08 if z == 1.0 else 1.0; last = t
            zoom_js.append(f"tl.set('#vw',{{scale:{z}}},{t:.3f});")
    fl_html, fl_js = [], []
    for j, f in enumerate(flash):
        fl_html.append(f'<div class="flashc" id="f{j}"><div class="in"><div class="lab">{esc(f.get("lab",""))}</div>'
                       f'<div class="a"><span>{esc(f["a"])}</span></div><div class="b"><span>{esc(f["b"])}</span></div><div class="thread"></div></div></div>')
        d = f.get("d", 1.0)
        fl_js.append(f"flash('#f{j}',{f['t']:.3f},{d});")
    # Mot choc : devant (à côté du visage) ou derrière la tête (détourage image par image)
    choc = sp.get("choc"); choc_html = choc_vw = choc_js = ""
    if choc:
        ct = at(choc["at"]); cd = choc.get("d", 1.6)
        letters = "".join(f"<span>{esc(c)}</span>" for c in choc["text"])
        os.makedirs(f"{out_dir}/assets", exist_ok=True)
        json.dump({"t0": ct, "d": cd}, open(f"{out_dir}/assets/choc.json", "w"))
        if choc.get("behind"):
            fgd = f"{out_dir}/assets/fg"; nf = len(os.listdir(fgd)) if os.path.isdir(fgd) else 0
            choc_vw = (f'<div id="choc" class="behind">{letters}</div>'
                       f'<img id="fgimg" src="assets/fg/0000.webp" style="position:absolute;left:0;top:0;width:1080px;height:1920px;opacity:0"/>')
            choc_js = (f"tl.set('#fgimg',{{opacity:1}},{ct:.3f});tl.set('#fgimg',{{opacity:0}},{ct+cd:.3f});"
                       f"for(let i=0;i<{nf};i++)tl.set('#fgimg',{{attr:{{src:'assets/fg/'+String(i).padStart(4,'0')+'.webp'}}}},{ct:.3f}+i/30);")
        else:
            choc_html = f'<div id="choc">{letters}</div>'
        choc_js += (f"(function(){{const sp=$$('#choc span'),mid=(sp.length-1)/2;tl.set('#choc',{{opacity:1}},{ct:.3f});"
                    f"tl.fromTo(sp,{{opacity:0,x:i=>(mid-i)*18,filter:'blur(10px)'}},{{opacity:1,x:0,filter:'blur(0px)',duration:.8,ease:IN,immediateRender:false}},{ct:.3f});"
                    f"tl.to('#choc',{{opacity:0,duration:.25}},{ct+cd-0.25:.3f});}})();")
    # ---- Composants du configurateur posés sur le plan (pas plein écran) ----
    ICON = {
        "cal": '<svg viewBox="0 0 48 48" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round"><rect x="7" y="10" width="34" height="31" rx="6"/><path d="M7 19h34M16 6v8M32 6v8"/><path d="M17 30l5 5 9-10" stroke="#00D9FF"/></svg>',
        "dm": '<svg viewBox="0 0 48 48" fill="none" stroke="#fff" stroke-width="3.4" stroke-linejoin="round"><path d="M8 11h32v21H22l-9 8v-8H8z"/><path d="M16 20h16M16 26h10" stroke="#00D9FF" stroke-linecap="round"/></svg>',
        "draft": '<svg viewBox="0 0 48 48" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 6h18l8 8v28H12z"/><path d="M30 6v8h8" /><path d="M18 26h14M18 33h9" stroke="#00D9FF"/></svg>',
        "rec": '<svg viewBox="0 0 48 48" fill="none" stroke="#fff" stroke-width="3.4" stroke-linejoin="round"><rect x="6" y="13" width="26" height="22" rx="5"/><path d="M32 21l10-6v18l-10-6z"/><circle cx="16" cy="24" r="4" fill="#00D9FF" stroke="none"/></svg>',
    }
    MK = {"check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>', "x": '<path d="M7 7l10 10M17 7L7 17"/>'}
    ov_html, ov_js, reveal = [], [], []
    for j, u in enumerate(sp.get("ui", [])):
        ut = at(u["t"]); ud = u.get("d", 2.4)
        lab = f'<div class="ex">{esc(u.get("label","Exemple"))}</div>' if u.get("label", "Exemple") else ""
        ov_html.append(f'<div class="glass white ui" id="u{j}" style="top:{u.get("top",600)}px"><div class="ic">{ICON[u.get("icon","dm")]}</div>'
                       f'<div><div class="t1">{esc(u["t1"])}</div><div class="t2">{esc(u["t2"])}</div><div class="t3">{esc(u.get("t3",""))}</div></div>{lab}</div>')
        ov_js.append(f"tl.fromTo('#u{j}',{{opacity:0,y:120}},{{opacity:1,y:0,duration:.6,ease:IN,immediateRender:false}},{ut:.3f});"
                     f"tl.to('#u{j}',{{opacity:0,y:-24,duration:D_OUT,ease:OUT}},{ut+ud:.3f});")
    for j, L in enumerate(sp.get("lists", [])):
        lt = at(L["t"]); rows = []; tick = []
        for r, it in enumerate(L["items"]):
            mk = it.get("mark", "check")
            rows.append(f'<div class="li" id="l{j}r{r}"><i class="mk {mk}"><svg viewBox="0 0 24 24">{MK[mk]}</svg></i><span>{esc(it["text"])}</span></div>')
            tick.append(at(it["at"]))
        le = at(L["until"]) if "until" in L else tick[-1] + L.get("hold", 1.4)
        ov_html.append(f'<div class="glass white lst" id="l{j}" style="top:{L.get("top",520)}px"><div class="lt">{esc(L["title"])}</div>{"".join(rows)}</div>')
        js = (f"tl.fromTo('#l{j}',{{opacity:0,y:90}},{{opacity:1,y:0,duration:.55,ease:IN,immediateRender:false}},{lt:.3f});"
              f"tl.set('#l{j} .li',{{opacity:.35}},{lt:.3f});")
        for r, tt in enumerate(tick):
            js += (f"tl.to('#l{j}r{r}',{{opacity:1,duration:.2}},{tt:.3f});tl.set('#l{j}r{r} .mk',{{className:'mk {L['items'][r].get('mark','check')} on'}},{tt:.3f});"
                   f"tl.fromTo('#l{j}r{r} .mk',{{scale:.7}},{{scale:1,duration:.3,ease:IN,immediateRender:false}},{tt:.3f});")
        js += f"tl.to('#l{j}',{{opacity:0,y:-24,duration:D_OUT,ease:OUT}},{le:.3f});"
        ov_js.append(js)
    if sp.get("method"):
        m = sp["method"]; mt = at(m["t"]); md = m.get("d", 3.2); on = m.get("on", 2)
        names = ["Mindset", "Offre", "Acquisition", "Closing"]
        rows = "".join(f'<div class="row" id="m{i+1}"><div class="dot"></div><div class="n">0{i+1}</div><div class="w">{n}</div>'
                       + (f'<div class="here">{esc(m.get("here","tu es ici"))}</div>' if i + 1 == on else "") + "</div>" for i, n in enumerate(names))
        ov_html.append(f'<div class="glass" id="method"><div class="h">La méthode The Process</div><div class="rail"></div><div class="railc"></div>{rows}</div>')
        js = (f"gsap.set('#method .railc',{{scaleY:0}});tl.to('#dim',{{opacity:.35,duration:D_IN,ease:IN}},{mt:.3f});"
              f"tl.fromTo('#method',{{opacity:0,y:32,scale:.98}},{{opacity:1,y:0,scale:1,duration:.6,ease:IN,immediateRender:false}},{mt:.3f});"
              f"tl.fromTo('#method .row',{{opacity:0,x:-18}},{{opacity:1,x:0,duration:.45,ease:IN,stagger:.1,immediateRender:false}},{mt+0.2:.3f});"
              f"tl.to('#method .railc',{{scaleY:{(on-1)/3:.3f},duration:.7,ease:MOVE}},{mt+0.9:.3f});")
        for i in range(on):
            js += f"tl.set('#m{i+1}',{{className:'row on'}},{mt+0.9+i*0.25:.3f});"
        js += (f"tl.fromTo('#m{on} .here',{{opacity:0,x:-12}},{{opacity:1,x:0,duration:D_IN,ease:IN,immediateRender:false}},{mt+1.2:.3f});"
               f"tl.to('#method',{{opacity:0,y:-20,duration:D_OUT,ease:OUT}},{mt+md:.3f});tl.to('#dim',{{opacity:0,duration:D_OUT}},{mt+md:.3f});")
        ov_js.append(js)
    for j, g in enumerate(sp.get("tags", [])):
        gt = at(g["t"]); gd = g.get("d", 2.6)
        ov_html.append(f'<div class="glass tag tg" id="g{j}"><i></i>{esc(g["text"])}</div>')
        ov_js.append(f"tl.fromTo('#g{j}',{{opacity:0,y:32}},{{opacity:1,y:0,duration:D_IN,ease:IN,immediateRender:false}},{gt:.3f});"
                     f"tl.to('#g{j}',{{opacity:0,y:-10,duration:D_OUT,ease:OUT}},{gt+gd:.3f});")
    # Un seul son discret, sur la révélation principale (charte §7)
    if sp.get("reveal") is not None: reveal.append(at(sp["reveal"]))
    elif choc: reveal.append(at(choc["at"]))
    elif sp.get("flash"): reveal.append(flash[0]["t"])
    reveal_html = "".join(f'<audio id="sfx" data-start="{r:.3f}" data-duration="0.37" data-volume="0.32" src="assets/kit/reveal.mp3"></audio>' for r in reveal[:1])
    inserts_html = open(f"{KIT}/inserts.html").read()
    for n, t in sp.get("insert_titles", {}).items():
        inserts_html = re.sub(rf'(<div class="ins" id="ins{n}"><div class="it">).*?(</div>)', rf"\g<1>{t}\g<2>", inserts_html, count=1)
    inserts_js = open(f"{KIT}/inserts.js").read()
    hook = sp["hook"]  # [ligne1, ligne2]
    # 2 lignes max (charte) : taille calculée pour que la plus longue ligne tienne dans 888 px (Montserrat Black ≈ 0,64 em/caractère)
    hook_fs = int(max(64, min(84, 888 / (0.64 * max(len(l) for l in hook)))))
    if hook_fs * 0.64 * max(len(l) for l in hook) > 900:
        raise SystemExit(f"accroche trop longue pour 2 lignes : {hook}")
    cta = sp["cta"]; T_END = W["dur"]
    obj = sp.get("objection")
    topic_html = (f'<div id="objection" style="opacity:1"><b>OBJECTION :</b> « {esc(obj)} »</div>' if obj else
                  f'<div class="glass" id="topic"><span>{esc(sp.get("topic",hook)[0])}</span><b>{esc(sp.get("topic",hook)[1])}</b></div>')
    KITCSS = open(f"{KIT}/kit.css").read().replace("url(fonts/", "url(assets/kit/fonts/")
    doc = f"""<!doctype html>
<html lang="fr"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1080, height=1920"/>
<title>{esc(sp['title'])}</title>
<script src="assets/kit/gsap.min.js"></script>
<style>
{KITCSS}
#root.pal-n .cap.oi{{color:var(--encre);-webkit-text-stroke:12px var(--papier)}}
#root.pal-n .cap.oi .kw{{color:var(--cyan-p)}}
.flashc{{position:absolute;inset:0;background:var(--papier);color:var(--encre);opacity:0}}
.flashc .in{{position:absolute;left:96px;right:236px;top:700px}}
.flashc .lab{{display:inline-block;background:var(--sable-d);color:var(--sable-t);padding:6px 18px;border-radius:999px;font:800 italic 32px Montserrat;margin-bottom:28px}}
.flashc .lab:empty{{display:none}}
.flashc .a{{font:900 92px/1.04 Montserrat;letter-spacing:-.02em;overflow:hidden}}
.flashc .b{{font:800 italic 80px/1.15 Montserrat;color:var(--cyan-p);margin-left:110px;overflow:hidden}}
.flashc .a span,.flashc .b span{{display:block}}
.flashc .thread{{height:4px;width:400px;background:var(--cyan-p);margin:34px 0 0 110px;transform-origin:0 50%;border-radius:2px}}
#end{{background:rgba(10,18,32,.0)}}
#hook{{right:96px}}
#hook .l{{white-space:nowrap;font-size:{hook_fs}px}}
#choc span{{display:inline-block;margin:0 .02em}}
#choc.behind{{left:0;width:1080px;top:520px;font-size:156px;letter-spacing:-.03em;text-shadow:none}}
#ctaw .lab{{color:#fff;text-shadow:0 2px 14px rgba(10,18,32,.6)}}
#prog{{position:absolute;left:64px;top:298px;width:876px;height:5px;border-radius:3px;background:rgba(255,255,255,.3);overflow:hidden;opacity:0}}
#prog i{{display:block;height:100%;width:100%;background:var(--cyan);transform-origin:0 50%;transform:scaleX(0)}}
.ui .t3:empty{{display:none}}
.ui > div:nth-child(2){{padding-right:150px;min-width:0}}
.ui .ex{{top:auto;bottom:18px;right:22px;font-size:19px}}
.tg{{position:absolute;left:64px;top:1080px;opacity:0}}
.lst{{left:96px;width:844px;border-radius:32px;padding:28px 36px 14px;opacity:0;color:var(--encre)}}
.lst .lt{{font:700 23px Montserrat;letter-spacing:.08em;text-transform:uppercase;color:#5b6575;margin-bottom:6px}}
.lst .li{{display:flex;gap:22px;align-items:center;padding:14px 0;border-top:1px solid #E6E9EE;font:800 38px Montserrat}}
.lst .mk{{width:52px;height:52px;flex:0 0 52px;border-radius:50%;border:2.5px solid #C9CED6;display:flex;align-items:center;justify-content:center}}
.lst .mk svg{{width:30px;height:30px;fill:none;stroke:#fff;stroke-width:3.4;stroke-linecap:round;stroke-linejoin:round;opacity:0}}
.lst .mk.on{{background:var(--cyan-p);border-color:var(--cyan-p)}}
.lst .mk.x.on{{background:var(--rouge);border-color:var(--rouge)}}
.lst .mk.on svg{{opacity:1}}
</style></head>
<body>
<div id="root" class="pal-n lite" data-composition-id="main" data-start="0" data-duration="{dur:.3f}" data-width="1080" data-height="1920">
  <div id="vw"><video id="v" data-start="0" data-duration="{dur:.3f}" data-has-audio="true" src="assets/cut.mp4" playsinline></video>{choc_vw}</div>
  <div id="dimfix"></div><div id="dim"></div>
{inserts_html}
  {topic_html}
  <div id="prog"><i></i></div>
  <div id="hookbg"></div>
  <div id="hook"><div class="l"><span>{esc(hook[0])}</span></div><div class="l c"><span>{esc(hook[1])}</span></div></div>
  <div id="sig"><svg viewBox="0 0 32 32" fill="none"><rect id="sigr" x="2.5" y="2.5" width="27" height="27" rx="8" stroke="#fff" stroke-width="2.6"/><circle id="sigc" cx="16" cy="16" r="6.2" stroke="#fff" stroke-width="2.6"/><circle id="sigd" cx="23.6" cy="8.4" r="1.8" fill="#fff"/></svg><span>@the_process.io</span></div>
  {choc_html}
  {''.join(ov_html)}
  {''.join(fl_html)}
  {''.join(cap_html)}
  <div id="ctaw"><div class="lab">Commente</div>
    <div class="glass white" id="cta"><svg class="s" viewBox="0 0 40 40" fill="none" stroke="#001F3F" stroke-width="4" stroke-linecap="round"><circle cx="17" cy="17" r="11"/><path d="M25 25l9 9"/></svg>
      <div class="q"><span id="ctat"></span><span class="cur"></span></div>
      <div class="go"><svg viewBox="0 0 42 42" fill="none" stroke="#001F3F" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21h22M22 11l10 10-10 10"/></svg></div></div></div>
  <div id="end"><svg viewBox="0 0 32 32" fill="none"><rect x="2.5" y="2.5" width="27" height="27" rx="8" stroke="#fff" stroke-width="2"/><circle cx="16" cy="16" r="6.2" stroke="#fff" stroke-width="2"/><circle cx="23.6" cy="8.4" r="1.6" fill="#00D9FF"/></svg><div class="h">@the_process.io</div></div>
  {reveal_html}
</div>
<script>
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const IN='expo.out',OUT='power2.in',MOVE='power3.inOut',k=1,D_IN=.5,D_OUT=.28;
const cfg={{ins:true,insDur:200}};const INS={json.dumps({int(n): v for n, v in ins.items()})};let INSWIN=[];
$$('.ins .d').forEach(p=>{{const L=Math.ceil(p.getTotalLength());p._L=L;p.setAttribute('stroke-dasharray',L);}});
const tl=gsap.timeline({{paused:true}});
function cap(id,a,b){{const sp=$$(id+' > span');tl.set(id,{{opacity:1}},a);
  tl.fromTo(sp,{{opacity:0,y:14,filter:'blur(6px)'}},{{opacity:1,y:0,filter:'blur(0px)',duration:.3,ease:IN,stagger:.07,immediateRender:false}},a);
  tl.set(id,{{opacity:0}},b);}}
function flash(id,a,d){{tl.set(id,{{opacity:1}},a);
  tl.fromTo(id+' .a span,'+id+' .b span',{{yPercent:110}},{{yPercent:0,duration:.6,ease:IN,stagger:.08,immediateRender:false}},a);
  tl.fromTo(id+' .thread',{{scaleX:0}},{{scaleX:1,duration:.5,ease:MOVE,immediateRender:false}},a+.3);
  tl.set(id,{{opacity:0}},a+d);}}
gsap.set(['#sig','#ctaw','#end'],{{opacity:0}});
/* Accroche : plein écran 0 → 2,4 s puis se rétracte en bandeau */
tl.fromTo('#hook .l span',{{yPercent:110}},{{yPercent:0,duration:.7,ease:IN,stagger:.08,immediateRender:false}},0);
tl.fromTo('#vw',{{scale:1.0}},{{scale:1.04,duration:2.6,ease:'none',immediateRender:false}},0);
tl.to('#hook',{{opacity:0,y:-40,duration:D_OUT,ease:OUT}},2.25);
(function(){{const tp=$('#topic')||$('#objection');const L=tp.offsetLeft,T=tp.offsetTop,W=tp.offsetWidth,H=tp.offsetHeight;
  gsap.set(tp,{{opacity:0}});
  tl.fromTo('#hookbg',{{clipPath:'inset(0px 0px 0px 0px round 0px)'}},{{clipPath:`inset(${{T}}px ${{1080-L-W}}px ${{1920-T-H}}px ${{L}}px round 16px)`,duration:.6,ease:MOVE,immediateRender:false}},2.3);
  tl.set(tp,{{opacity:1}},2.9);tl.set('#hookbg',{{opacity:0}},2.9);}})();
tl.set('#vw',{{scale:1.0}},2.6);
tl.to('#sig',{{opacity:1,duration:D_IN,ease:IN}},.2);
tl.set(['#sigr','#sigc'],{{attr:{{stroke:'#00D9FF'}}}},.2);tl.set('#sigd',{{attr:{{fill:'#00D9FF'}}}},.2);
tl.set(['#sigr','#sigc'],{{attr:{{stroke:'#fff'}}}},.7);tl.set('#sigd',{{attr:{{fill:'#fff'}}}},.7);
{''.join(zoom_js)}
{''.join(fl_js)}
{choc_js}
{''.join(ov_js)}
/* Barre de progression : où on en est dans la vidéo */
tl.to('#prog',{{opacity:1,duration:.4}},2.9);
tl.fromTo('#prog i',{{scaleX:0}},{{scaleX:1,duration:{T_END:.3f},ease:'none',immediateRender:false}},0);
tl.to('#prog',{{opacity:0,duration:.3}},{T_END:.3f});
{''.join(cap_js)}
{inserts_js}
/* CTA : barre de recherche dans les 2,6 dernières secondes de parole, puis carte de fin */
tl.set('#vw',{{scale:1.0}},{T_END-2.7:.3f});
tl.to('#dim',{{opacity:.3,duration:D_IN}},{T_END-2.7:.3f});
tl.fromTo('#ctaw',{{opacity:0,y:60}},{{opacity:1,y:0,duration:.6,ease:IN,immediateRender:false}},{T_END-2.65:.3f});
(function(){{const el=$('#ctat'),w={json.dumps(cta)},o={{n:0}};tl.to(o,{{n:w.length,duration:1.1,ease:'none',onUpdate:()=>{{el.textContent=w.slice(0,Math.round(o.n));}}}},{T_END-2.1:.3f});}})();
tl.to('#cta .go',{{scale:.88,duration:.12}},{T_END-0.6:.3f});tl.to('#cta .go',{{scale:1,duration:.3,ease:IN}},{T_END-0.48:.3f});
tl.to('#ctaw',{{opacity:0,duration:D_OUT,ease:OUT}},{T_END+0.05:.3f});
tl.to('#dim',{{opacity:.74,duration:.4,ease:IN}},{T_END:.3f});
tl.to(['#topic','#objection','#sig'].filter(s=>$(s)),{{opacity:0,duration:.3}},{T_END:.3f});
tl.fromTo('#end',{{opacity:0,y:16}},{{opacity:1,y:0,duration:D_IN,ease:IN,immediateRender:false}},{T_END+0.1:.3f});
window.__timelines=window.__timelines||{{}};window.__timelines["main"]=tl;tl.seek(0);
</script></body></html>"""
    os.makedirs(f"{out_dir}/assets", exist_ok=True)
    import shutil
    shutil.copytree(KIT, f"{out_dir}/assets/kit", dirs_exist_ok=True)
    open(f"{out_dir}/index.html", "w").write(doc)
    json.dump({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json", "paths": {"assets": "assets"}, "media": {"autoProxy": True}},
              open(f"{out_dir}/hyperframes.json", "w"))
    json.dump({"id": sp["id"], "name": sp["title"]}, open(f"{out_dir}/meta.json", "w"), ensure_ascii=False)
    print(sp["id"], "composition", round(dur, 2), "s,", len(cap_html), "sous-titres,", len(zoom_js), "punch-in")


if __name__ == "__main__":
    main(*sys.argv[1:4])

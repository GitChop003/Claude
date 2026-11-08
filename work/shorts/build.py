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
    TAIL = W.get("tail", 1.4)
    dur = W["dur"] + TAIL  # CTA lisible après la dernière phrase, puis carte de fin
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
    # Visage mesuré (faces.py) : les éléments vont dans la bande SOUS le visage, sinon en plein écran
    FACES = json.load(open(f"{out_dir}/assets/faces.json")) if os.path.exists(f"{out_dir}/assets/faces.json") else []
    BAND, FS_TOP = 1170, 760
    def face_low(a, b):
        z = [o[2] for o in FACES if a - 0.3 <= o[0] <= b + 0.3]
        return 730 + (max(z) - 730) * 1.08 if z else 0   # punch-in 108 % centré à y≈730
    fsw = []   # fenêtres plein écran (fond papier) : sous-titres passent en encre
    def place(a, b, h_needed=225):
        """Renvoie (top, plein_écran) pour un élément visible de a à b."""
        if face_low(a, b) > BAND - 15 or h_needed > 1395 - BAND:
            fsw.append((a, b)); return FS_TOP, True
        return BAND, False
    ins = {n: [at(v[0]), v[1]] for n, v in sp.get("inserts", {}).items()}  # {"1":[t|ancre,slot],...}
    insw = [(v[0], v[0] + min(2.0, v[1])) for v in ins.values()]
    flash = sp.get("flash", [])  # [{"t":..|ancre,"a":..,"b":..,"lab":..}]
    for f in flash: f["t"] = at(f["t"])
    # sous-titres masqués pendant les cartes plein écran
    fw = [(f["t"], f["t"] + f.get("d", 1.0)) for f in flash]
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
            ctop, cfs = place(ct, ct + cd, 180)
            choc_html = f'<div id="choc" style="top:{ctop}px">{letters}</div>'
            if cfs: choc_js += f"tl.set('#fsbg',{{opacity:1}},{ct:.3f});tl.set('#fsbg',{{opacity:0}},{ct+cd:.3f});"
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
        utop, ufs = place(ut, ut + ud, 170)
        if ufs: ov_js.append(f"tl.set('#fsbg',{{opacity:1}},{ut:.3f});tl.set('#fsbg',{{opacity:0}},{ut+ud+0.3:.3f});")
        ov_html.append(f'<div class="glass white ui" id="u{j}" style="top:{utop}px"><div class="ic">{ICON[u.get("icon","dm")]}</div>'
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
        fsw.append((lt, le)); ov_js.append(f"tl.set('#fsbg',{{opacity:1}},{lt:.3f});tl.set('#fsbg',{{opacity:0}},{le+0.3:.3f});")
        ov_html.append(f'<div class="glass white lst" id="l{j}" style="top:{FS_TOP - 120}px"><div class="lt">{esc(L["title"])}</div>{"".join(rows)}</div>')
        js = (f"tl.fromTo('#l{j}',{{opacity:0,y:90}},{{opacity:1,y:0,duration:.55,ease:IN,immediateRender:false}},{lt:.3f});"
              f"tl.set('#l{j} .li',{{opacity:.35}},{lt:.3f});")
        for r, tt in enumerate(tick):
            js += (f"tl.to('#l{j}r{r}',{{opacity:1,duration:.2}},{tt:.3f});tl.set('#l{j}r{r} .mk',{{className:'mk {L['items'][r].get('mark','check')} on'}},{tt:.3f});"
                   f"tl.fromTo('#l{j}r{r} .mk',{{scale:.7}},{{scale:1,duration:.3,ease:IN,immediateRender:false}},{tt:.3f});")
        js += f"tl.to('#l{j}',{{opacity:0,y:-24,duration:D_OUT,ease:OUT}},{le:.3f});"
        ov_js.append(js)
    # Énumérations : formules variées (directive « ne pas répéter la liste à cases »)
    TILE = {
        "call": '<path d="M10 28v-4a14 14 0 0 1 28 0v4"/><rect x="7" y="27" width="7" height="12" rx="3"/><rect x="34" y="27" width="7" height="12" rx="3"/><path d="M38 39c0 4-5 5-9 5"/>',
        "sale": '<path d="M24 6h16v16L22 40 8 26z"/><circle cx="32" cy="14" r="3"/>',
        "doc": '<path d="M12 5h17l9 9v29H12z"/><path d="M29 5v9h9"/><path d="M18 24h14M18 30h14M18 36h8"/>',
        "video": '<rect x="5" y="12" width="28" height="24" rx="5"/><path d="M33 20l10-6v20l-10-6z"/>',
        "msg": '<path d="M7 10h34v22H22l-9 8v-8H7z"/>',
        "story": '<circle cx="24" cy="24" r="17" stroke-dasharray="9 4"/><circle cx="24" cy="24" r="10"/>',
        "focus": '<circle cx="24" cy="24" r="16"/><circle cx="24" cy="24" r="8"/><circle cx="24" cy="24" r="1.5"/>',
        "learn": '<path d="M4 18l20-9 20 9-20 9z"/><path d="M12 22v10c0 3 6 6 12 6s12-3 12-6V22"/>',
        "seance": '<circle cx="16" cy="17" r="6"/><circle cx="33" cy="17" r="6"/><path d="M5 38c1-7 6-10 11-10s10 3 11 10M22 38c1-7 6-10 11-10s10 3 11 10"/>',
    }
    for j, E in enumerate(sp.get("enum", [])):
        et = at(E["t"]); ticks = [at(it["at"]) for it in E["items"]]
        ee = at(E["until"]) if "until" in E else ticks[-1] + E.get("hold", 1.4)
        st = E["style"]
        etop, efs = place(et, ee, {"giant": 200, "stack": 64 * len(E["items"]) + 10, "tiles": 210, "strike": 64 * len(E["items"]) + 10, "numbers": 190}.get(st, 210))
        if efs: ov_js.append(f"tl.set('#fsbg',{{opacity:1}},{et:.3f});tl.set('#fsbg',{{opacity:0}},{ee+0.3:.3f});")
        if st == "giant":  # un mot géant par élément, chacun remplace le précédent
            words = "".join(f'<div class="gw" id="e{j}w{r}"><small>{r+1}/{len(E["items"])}</small><span>{esc(it["text"])}</span></div>' for r, it in enumerate(E["items"]))
            ov_html.append(f'<div class="enum-g{" fs" if efs else ""}" id="e{j}" style="top:{etop}px">{words}</div>')
            js = ""
            for r, tt in enumerate(ticks):
                nx = ticks[r + 1] if r + 1 < len(ticks) else ee
                js += (f"tl.fromTo('#e{j}w{r}',{{opacity:0,y:50,filter:'blur(8px)'}},{{opacity:1,y:0,filter:'blur(0px)',duration:.45,ease:IN,immediateRender:false}},{tt:.3f});"
                       f"tl.to('#e{j}w{r}',{{opacity:0,y:-40,duration:.25,ease:OUT}},{nx-0.05:.3f});")
            ov_js.append(js)
        elif st == "stack":  # les mots s'empilent dans la marge, reliés par un fil cyan
            words = "".join(f'<div class="sw" id="e{j}w{r}">{esc(it["text"])}</div>' for r, it in enumerate(E["items"]))
            ov_html.append(f'<div class="enum-s{" fs" if efs else ""}" id="e{j}" style="top:{etop}px"><i class="rail"></i>{words}</div>')
            js = f"gsap.set('#e{j} .rail',{{scaleY:0}});tl.set('#e{j}',{{opacity:1}},{et:.3f});"
            for r, tt in enumerate(ticks):
                js += (f"tl.fromTo('#e{j}w{r}',{{opacity:0,x:-60}},{{opacity:1,x:0,duration:.5,ease:IN,immediateRender:false}},{tt:.3f});"
                       f"tl.to('#e{j} .rail',{{scaleY:{(r+1)/len(ticks):.3f},duration:.45,ease:MOVE}},{tt:.3f});")
                if r: js += f"tl.to('#e{j}w{r-1}',{{opacity:.55,duration:.3}},{tt:.3f});"
            js += f"tl.to('#e{j}',{{opacity:0,x:-30,duration:D_OUT,ease:OUT}},{ee:.3f});"
            ov_js.append(js)
        elif st == "tiles":  # tuiles avec icônes qui s'allument une à une
            tiles = "".join(f'<div class="tl-t" id="e{j}w{r}"><div class="ic"><svg viewBox="0 0 48 48">{TILE[it.get("icon","doc")]}</svg></div><b>{esc(it["text"])}</b></div>' for r, it in enumerate(E["items"]))
            ov_html.append(f'<div class="enum-t{" fs" if efs else ""}" id="e{j}" style="top:{etop}px"><div class="row">{tiles}</div></div>')
            js = (f"tl.fromTo('#e{j}',{{opacity:0,y:60}},{{opacity:1,y:0,duration:.55,ease:IN,immediateRender:false}},{et:.3f});"
                  f"tl.set('#e{j} .tl-t',{{opacity:.35,scale:.94}},{et:.3f});")
            for r, tt in enumerate(ticks):
                js += (f"tl.to('#e{j}w{r}',{{opacity:1,scale:1,duration:.35,ease:IN}},{tt:.3f});"
                       f"tl.set('#e{j}w{r}',{{className:'tl-t on'}},{tt:.3f});")
            js += f"tl.to('#e{j}',{{opacity:0,y:-24,duration:D_OUT,ease:OUT}},{ee:.3f});"
            ov_js.append(js)
        elif st == "strike":  # les mots apparaissent ; ceux « à éviter » sont barrés
            words = "".join(f'<div class="kw2{" x" if it.get("mark") == "x" else ""}" id="e{j}w{r}"><span>{esc(it["text"])}</span><i></i></div>' for r, it in enumerate(E["items"]))
            ov_html.append(f'<div class="enum-x{" fs" if efs else ""}" id="e{j}" style="top:{etop}px">{words}</div>')
            js = f"tl.set('#e{j}',{{opacity:1}},{et:.3f});gsap.set('#e{j} i',{{scaleX:0}});"
            for r, (tt, it) in enumerate(zip(ticks, E["items"])):
                js += f"tl.fromTo('#e{j}w{r}',{{opacity:0,y:24}},{{opacity:1,y:0,duration:.4,ease:IN,immediateRender:false}},{tt:.3f});"
                if it.get("mark") == "x": js += f"tl.to('#e{j}w{r} i',{{scaleX:1,duration:.35,ease:MOVE}},{tt+0.35:.3f});tl.to('#e{j}w{r} span',{{opacity:.55,duration:.3}},{tt+0.4:.3f});"
            js += f"tl.to('#e{j}',{{opacity:0,y:-20,duration:D_OUT,ease:OUT}},{ee:.3f});"
            ov_js.append(js)
        elif st == "numbers":  # grand numéro + mot, chacun remplace le précédent
            words = "".join(f'<div class="nb" id="e{j}w{r}"><b>{r+1}</b><span>{esc(it["text"])}</span></div>' for r, it in enumerate(E["items"]))
            ov_html.append(f'<div class="enum-n{" fs" if efs else ""}" id="e{j}" style="top:{etop}px">{words}</div>')
            js = ""
            for r, tt in enumerate(ticks):
                nx = ticks[r + 1] if r + 1 < len(ticks) else ee
                js += (f"tl.fromTo('#e{j}w{r} b',{{opacity:0,scale:.6}},{{opacity:1,scale:1,duration:.45,ease:IN,immediateRender:false}},{tt:.3f});"
                       f"tl.fromTo('#e{j}w{r} span',{{opacity:0,x:-30}},{{opacity:1,x:0,duration:.45,ease:IN,immediateRender:false}},{tt+0.08:.3f});"
                       f"tl.set('#e{j}w{r}',{{opacity:1}},{tt:.3f});tl.to('#e{j}w{r}',{{opacity:0,duration:.2}},{nx-0.05:.3f});")
            ov_js.append(js)
    if sp.get("method"):
        m = sp["method"]; mt = at(m["t"]); md = m.get("d", 3.2); on = m.get("on", 2)
        names = ["Mindset", "Offre", "Acquisition", "Closing"]
        rows = "".join(f'<div class="row" id="m{i+1}"><div class="dot"></div><div class="n">0{i+1}</div><div class="w">{n}</div>'
                       + (f'<div class="here">{esc(m.get("here","tu es ici"))}</div>' if i + 1 == on else "") + "</div>" for i, n in enumerate(names))
        ov_html.append(f'<div class="glass" id="method"><div class="h">La méthode The Process</div><div class="rail"></div><div class="railc"></div>{rows}</div>')
        fsw.append((mt, mt + md))
        js = (f"gsap.set('#method .railc',{{scaleY:0}});tl.set('#fsbg',{{opacity:1}},{mt:.3f});tl.set('#fsbg',{{opacity:0}},{mt+md+0.3:.3f});"
              f"tl.fromTo('#method',{{opacity:0,y:32,scale:.98}},{{opacity:1,y:0,scale:1,duration:.6,ease:IN,immediateRender:false}},{mt:.3f});"
              f"tl.fromTo('#method .row',{{opacity:0,x:-18}},{{opacity:1,x:0,duration:.45,ease:IN,stagger:.1,immediateRender:false}},{mt+0.2:.3f});"
              f"tl.to('#method .railc',{{scaleY:{(on-1)/3:.3f},duration:.7,ease:MOVE}},{mt+0.9:.3f});")
        for i in range(on):
            js += f"tl.set('#m{i+1}',{{className:'row on'}},{mt+0.9+i*0.25:.3f});"
        js += (f"tl.fromTo('#m{on} .here',{{opacity:0,x:-12}},{{opacity:1,x:0,duration:D_IN,ease:IN,immediateRender:false}},{mt+1.2:.3f});"
               f"tl.to('#method',{{opacity:0,y:-20,duration:D_OUT,ease:OUT}},{mt+md:.3f});")
        ov_js.append(js)
    for j, g in enumerate([]):  # étiquettes retirées (v4)
        gt = at(g["t"]); gd = g.get("d", 2.6)
        ov_html.append(f'<div class="glass tag tg" id="g{j}"><i></i>{esc(g["text"])}</div>')
        ov_js.append(f"tl.fromTo('#g{j}',{{opacity:0,y:32}},{{opacity:1,y:0,duration:D_IN,ease:IN,immediateRender:false}},{gt:.3f});"
                     f"tl.to('#g{j}',{{opacity:0,y:-10,duration:D_OUT,ease:OUT}},{gt+gd:.3f});")
    cap_html, cap_js = [], []
    for i, c in enumerate(caps):
        if any(a <= c["s"] < b for a, b in fw): continue
        oi = " oi" if any(a <= c["s"] < b for a, b in insw + fsw) else ""
        spans = " ".join(f'<span class="kw">{esc(w)}</span>' if k else f"<span>{esc(w)}</span>" for w, k in c["w"])
        cap_html.append(f'<div class="cap{oi}" id="c{i}">{spans}</div>')
        nxt = caps[i + 1]["s"] if i + 1 < len(caps) else W["dur"]
        cap_js.append(f"cap('#c{i}',{c['s']:.3f},{min(c['e']+0.05, nxt, W['dur']):.3f});")
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
    ftop = [o[1] for o in FACES if o[0] <= 2.6]
    face_top = min(ftop) if ftop else 560
    h1 = int(min(54, 936 / (0.6 * len(hook[0])))); h2 = int(min(116, 936 / (0.52 * len(hook[1]))))
    hook_top = int(max(300, min(sp.get("hook_top", 9999), face_top - 70 - (h1 * 1.08 + h2 * 1.08 + 33))))
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
#root{{--cap-y:1408px}}
#hookbg,#sig{{display:none}}
/* Ouvertures typographiques sur le plan (v4) */
#hook{{left:72px;right:72px;top:{hook_top}px;color:#fff;text-shadow:0 2px 18px rgba(10,18,32,.45)}}
#root.pal-n #hook{{color:#fff}}
#hook .l{{white-space:nowrap}}
#hook .l:first-child{{font-weight:600;font-size:{h1}px;letter-spacing:0;margin-bottom:6px}}
#hook .l.c{{font-size:{h2}px;letter-spacing:-.03em}}
#root.pal-n #hook .l.c span{{color:#fff}}
#hook .rule{{width:120px;height:5px;border-radius:3px;background:var(--cyan);margin-top:22px;transform-origin:0 50%}}
#topic{{left:72px;top:322px;height:auto;padding:0;background:none!important;border:0;box-shadow:none;-webkit-backdrop-filter:none;backdrop-filter:none;
  font-size:30px;font-weight:500;color:#fff;gap:12px;text-shadow:0 1px 10px rgba(10,18,32,.5)}}
#topic::after{{display:none}}
#root.pal-n #topic{{color:#fff}}
#root.pal-n #topic b{{color:#fff;font-weight:800}}
#fsbg{{position:absolute;inset:0;background:var(--papier);opacity:0}}
.fs .gw span,.fs .sw,.fs .kw2 span,.fs .nb span{{color:var(--encre)!important;text-shadow:none!important}}
.fs .nb b{{color:var(--cyan-p)!important}}
#choc span{{display:inline-block;margin:0 .02em}}
#choc.behind{{left:0;width:1080px;top:520px;font-size:156px;letter-spacing:-.03em;text-shadow:none}}
#ctaw .lab{{color:#fff;text-shadow:0 2px 14px rgba(10,18,32,.6)}}
#ctaw{{top:1150px}}
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
.enum-g{{position:absolute;left:64px;width:952px;top:470px;height:260px}}
.enum-g .gw{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;opacity:0}}
.enum-g .gw small{{font:800 30px Montserrat;letter-spacing:.12em;color:var(--cyan);text-shadow:0 2px 12px rgba(10,18,32,.5)}}
.enum-g .gw span{{font:900 132px/1 Montserrat;letter-spacing:-.02em;color:#fff;text-transform:uppercase;text-shadow:0 6px 30px rgba(10,18,32,.45)}}
.enum-s{{position:absolute;left:64px;top:560px;padding-left:34px;opacity:0}}
.enum-s .rail{{position:absolute;left:0;top:6px;width:6px;height:calc(100% - 12px);border-radius:3px;background:var(--cyan);transform-origin:50% 0}}
.enum-s .sw{{font:900 76px/1.12 Montserrat;letter-spacing:-.02em;color:#fff;text-shadow:0 4px 22px rgba(10,18,32,.55);opacity:0}}
.enum-t{{position:absolute;left:64px;width:952px;top:520px;opacity:0}}
.enum-t .tt{{font:800 30px Montserrat;color:#fff;text-shadow:0 2px 12px rgba(10,18,32,.55);margin:0 0 18px 6px}}
.enum-t .row{{display:flex;gap:22px}}
.enum-t .tl-t{{flex:1;border-radius:28px;padding:28px 18px 24px;display:flex;flex-direction:column;align-items:center;gap:16px;
  background:rgba(255,255,255,.86);-webkit-backdrop-filter:blur(24px);backdrop-filter:blur(24px);border:1px solid rgba(255,255,255,.7);box-shadow:0 24px 60px rgba(10,18,32,.25)}}
.enum-t .ic{{width:110px;height:110px;border-radius:30px;background:#EEF0F3;display:flex;align-items:center;justify-content:center}}
.enum-t .ic svg{{width:64px;height:64px;fill:none;stroke:#8a93a3;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}}
.enum-t .tl-t b{{font:800 30px/1.15 Montserrat;color:var(--encre);text-align:center}}
.enum-t .tl-t.on .ic{{background:var(--cyan-p)}}
.enum-t .tl-t.on .ic svg{{stroke:#fff}}
.enum-t .row{{gap:16px}}
.enum-t .tl-t{{padding:22px 10px 18px;gap:12px;border-radius:24px}}
.enum-t .ic{{width:88px;height:88px;border-radius:24px}}
.enum-t .ic svg{{width:52px;height:52px}}
.enum-t .tl-t b{{font-size:27px;line-height:1.1}}
.enum-x{{position:absolute;left:72px;opacity:1}}
.kw2{{position:relative;font:900 64px/1.08 Montserrat;letter-spacing:-.02em;color:#fff;text-shadow:0 3px 18px rgba(10,18,32,.5);opacity:0;width:max-content}}
.kw2 i{{position:absolute;left:-6px;right:-6px;top:52%;height:7px;border-radius:4px;background:var(--rouge);transform-origin:0 50%}}
.enum-n{{position:absolute;left:72px;width:936px;height:190px}}
.nb{{position:absolute;inset:0;display:flex;align-items:center;gap:30px;opacity:0}}
.nb b{{font:900 170px/1 Montserrat;color:var(--cyan);text-shadow:0 4px 24px rgba(10,18,32,.4)}}
.nb span{{font:800 68px/1.05 Montserrat;color:#fff;text-shadow:0 3px 18px rgba(10,18,32,.5)}}
</style></head>
<body>
<div id="root" class="pal-n lite" data-composition-id="main" data-start="0" data-duration="{dur:.3f}" data-width="1080" data-height="1920">
  <div id="vw"><video id="v" data-start="0" data-duration="{dur:.3f}" data-has-audio="true" src="assets/cut.mp4" playsinline></video>{choc_vw}</div>
  <div id="dimfix"></div><div id="dim"></div>
{inserts_html}
  {topic_html}
  <div id="prog"><i></i></div>
  <div id="hookbg"></div>
  <div id="hook"><div class="l"><span>{esc(hook[0])}</span></div><div class="l c"><span>{esc(hook[1])}</span></div><div class="rule"></div></div>
  <div id="sig"><svg viewBox="0 0 32 32" fill="none"><rect id="sigr" x="2.5" y="2.5" width="27" height="27" rx="8" stroke="#fff" stroke-width="2.6"/><circle id="sigc" cx="16" cy="16" r="6.2" stroke="#fff" stroke-width="2.6"/><circle id="sigd" cx="23.6" cy="8.4" r="1.8" fill="#fff"/></svg><span>@the_process.io</span></div>
  <div id="fsbg"></div>
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
const cfg={{ins:true,insDur:450}};const INS={json.dumps({int(n): v for n, v in ins.items()})};let INSWIN=[];
$$('.ins .d').forEach(p=>{{const L=Math.ceil(p.getTotalLength());p._L=L;p.setAttribute('stroke-dasharray',L);}});
const tl=gsap.timeline({{paused:true}});
function cap(id,a,b){{const sp=$$(id+' > span');tl.set(id,{{opacity:1}},a);
  tl.fromTo(sp,{{opacity:0,y:14,filter:'blur(6px)'}},{{opacity:1,y:0,filter:'blur(0px)',duration:.3,ease:IN,stagger:.07,immediateRender:false}},a);
  tl.set(id,{{opacity:0}},b);}}
function flash(id,a,d){{tl.set(id,{{opacity:1}},a);
  tl.fromTo(id+' .a span,'+id+' .b span',{{yPercent:110}},{{yPercent:0,duration:.6,ease:IN,stagger:.08,immediateRender:false}},a);
  tl.fromTo(id+' .thread',{{scaleX:0}},{{scaleX:1,duration:.5,ease:MOVE,immediateRender:false}},a+.3);
  tl.set(id,{{opacity:0}},a+d);}}
gsap.set(['#ctaw','#end'],{{opacity:0}});
/* Ouverture typographique au-dessus de la tête (v4) : pas de carte, pas de @ */
gsap.set('#topic',{{opacity:0}});
tl.fromTo('#hook .l span',{{yPercent:110}},{{yPercent:0,duration:.7,ease:IN,stagger:.12,immediateRender:false}},0.05);
tl.fromTo('#hook .rule',{{scaleX:0}},{{scaleX:1,duration:.6,ease:MOVE,immediateRender:false}},0.45);
tl.fromTo('#vw',{{scale:1.0}},{{scale:1.04,duration:2.6,ease:'none',immediateRender:false}},0);
tl.to('#hook .l span',{{yPercent:-110,duration:.4,ease:OUT,stagger:.05}},2.3);
tl.to('#hook .rule',{{scaleX:0,transformOrigin:'100% 50%',duration:.35,ease:OUT}},2.3);
tl.fromTo('#topic',{{opacity:0,y:10}},{{opacity:1,y:0,duration:.5,ease:IN,immediateRender:false}},2.75);
tl.set('#vw',{{scale:1.0}},2.6);
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
tl.to('#dim',{{opacity:.12,duration:D_IN}},{T_END-2.7:.3f});
tl.fromTo('#ctaw',{{opacity:0,y:60}},{{opacity:1,y:0,duration:.6,ease:IN,immediateRender:false}},{T_END-2.65:.3f});
(function(){{const el=$('#ctat'),w={json.dumps(cta)},o={{n:0}};tl.to(o,{{n:w.length,duration:1.1,ease:'none',onUpdate:()=>{{el.textContent=w.slice(0,Math.round(o.n));}}}},{T_END-2.1:.3f});}})();
tl.to('#cta .go',{{scale:.88,duration:.12}},{T_END+0.4:.3f});tl.to('#cta .go',{{scale:1,duration:.3,ease:IN}},{T_END+0.52:.3f});
tl.to('#ctaw',{{opacity:0,duration:D_OUT,ease:OUT}},{T_END+TAIL-1.35:.3f});
tl.to('#dim',{{opacity:.74,duration:.4,ease:IN}},{T_END+TAIL-1.35:.3f});
tl.to(['#topic','#objection'].filter(s=>$(s)),{{opacity:0,duration:.3}},{T_END+TAIL-1.35:.3f});
tl.fromTo('#end',{{opacity:0,y:16}},{{opacity:1,y:0,duration:D_IN,ease:IN,immediateRender:false}},{T_END+TAIL-1.25:.3f});
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

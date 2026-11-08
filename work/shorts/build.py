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
    def at(x):
        if isinstance(x, (int, float)): return float(x)
        n = x.get("n", 1); off = x.get("off", 0.0)
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
        cap_js.append(f"cap('#c{i}',{c['s']:.3f},{min(c['e']+0.05, W['dur']):.3f});")
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
    inserts_html = open(f"{KIT}/inserts.html").read()
    for n, t in sp.get("insert_titles", {}).items():
        inserts_html = re.sub(rf'(<div class="ins" id="ins{n}"><div class="it">).*?(</div>)', rf"\g<1>{t}\g<2>", inserts_html, count=1)
    inserts_js = open(f"{KIT}/inserts.js").read()
    hook = sp["hook"]  # [ligne1, ligne2]
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
#hook .l{{white-space:nowrap}}
#choc span{{display:inline-block;margin:0 .02em}}
#choc.behind{{left:0;width:1080px;top:452px;font-size:156px;letter-spacing:-.03em;text-shadow:none}}
#ctaw .lab{{color:#fff;text-shadow:0 2px 14px rgba(10,18,32,.6)}}
</style></head>
<body>
<div id="root" class="pal-n lite" data-composition-id="main" data-start="0" data-duration="{dur:.3f}" data-width="1080" data-height="1920">
  <div id="vw"><video id="v" data-start="0" data-duration="{dur:.3f}" data-has-audio="true" src="assets/cut.mp4" playsinline></video>{choc_vw}</div>
  <div id="dimfix"></div><div id="dim"></div>
{inserts_html}
  {topic_html}
  <div id="hookbg"></div>
  <div id="hook"><div class="l"><span>{esc(hook[0])}</span></div><div class="l c"><span>{esc(hook[1])}</span></div></div>
  <div id="sig"><svg viewBox="0 0 32 32" fill="none"><rect id="sigr" x="2.5" y="2.5" width="27" height="27" rx="8" stroke="#fff" stroke-width="2.6"/><circle id="sigc" cx="16" cy="16" r="6.2" stroke="#fff" stroke-width="2.6"/><circle id="sigd" cx="23.6" cy="8.4" r="1.8" fill="#fff"/></svg><span>@the_process.io</span></div>
  {choc_html}
  {''.join(fl_html)}
  {''.join(cap_html)}
  <div id="ctaw"><div class="lab">Commente</div>
    <div class="glass white" id="cta"><svg class="s" viewBox="0 0 40 40" fill="none" stroke="#001F3F" stroke-width="4" stroke-linecap="round"><circle cx="17" cy="17" r="11"/><path d="M25 25l9 9"/></svg>
      <div class="q"><span id="ctat"></span><span class="cur"></span></div>
      <div class="go"><svg viewBox="0 0 42 42" fill="none" stroke="#001F3F" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21h22M22 11l10 10-10 10"/></svg></div></div></div>
  <div id="end"><svg viewBox="0 0 32 32" fill="none"><rect x="2.5" y="2.5" width="27" height="27" rx="8" stroke="#fff" stroke-width="2"/><circle cx="16" cy="16" r="6.2" stroke="#fff" stroke-width="2"/><circle cx="23.6" cy="8.4" r="1.6" fill="#00D9FF"/></svg><div class="h">@the_process.io</div></div>
</div>
<script>
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const IN='expo.out',OUT='power2.in',MOVE='power3.inOut',k=1,D_IN=.5,D_OUT=.28;
const cfg={{ins:true,insDur:200}};const INS={json.dumps({int(n): v for n, v in ins.items()})};let INSWIN=[];
$$('.ins .d').forEach(p=>{{const L=Math.ceil(p.getTotalLength());p._L=L;p.setAttribute('stroke-dasharray',L);}});
/* Accroche : 2 lignes max (charte) → on réduit la taille (84 → 64 px) jusqu'à ce que chaque ligne tienne */
(function(){{const h=$('#hook');let fs=84;$$('#hook .l').forEach(l=>l.style.fontSize=fs+'px');
  while(fs>64&&$$('#hook .l').some(l=>l.scrollWidth>h.clientWidth)){{fs-=2;$$('#hook .l').forEach(l=>l.style.fontSize=fs+'px');}}}})();
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

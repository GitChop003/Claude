"""Accroches visuelles (1re seconde) : un élément graphique lié au sujet, différent pour chaque vidéo.
Chaque fonction renvoie (html, css, js). Les éléments vivent dans la zone libre au-dessus du visage
(z = (haut, bas) en px) ou passent brièvement sur le cadre ; aucun ne reste devant le visage.
Style maison : traits blancs fins, accent cyan, Montserrat, pas de dégradé ni d'émoji."""
import json

SH = "text-shadow:0 2px 14px rgba(10,18,32,.45)"


def _out(sel, t=2.6):
    return f"tl.to('{sel}',{{opacity:0,y:-16,duration:.35,ease:OUT}},{t});"


def viewfinder(p, z):  # s1 : viseur de caméra, « REC » et code temporel
    return ('<div id="vf"><i class="c tl"></i><i class="c tr"></i><i class="c bl"></i><i class="c br"></i>'
            '<div class="rec"><b></b>REC <span id="tc">00:00:00</span></div></div>', "",
            "tl.set('#vf',{opacity:1},0);"
            "tl.fromTo('#vf .tl',{x:-46,y:-46,opacity:0},{x:0,y:0,opacity:1,duration:.5,ease:'expo.out',immediateRender:false},0);"
            "tl.fromTo('#vf .tr',{x:46,y:-46,opacity:0},{x:0,y:0,opacity:1,duration:.5,ease:'expo.out',immediateRender:false},0);"
            "tl.fromTo('#vf .bl',{x:-46,y:46,opacity:0},{x:0,y:0,opacity:1,duration:.5,ease:'expo.out',immediateRender:false},0);"
            "tl.fromTo('#vf .br',{x:46,y:46,opacity:0},{x:0,y:0,opacity:1,duration:.5,ease:'expo.out',immediateRender:false},0);"
            "tl.fromTo('#vf .rec',{opacity:0},{opacity:1,duration:.3,immediateRender:false},.25);"
            + "".join(f"tl.set('#vf .rec b',{{opacity:{0 if k % 2 else 1}}},{0.25 + k * 0.45:.2f});" for k in range(6))
            + "(function(){const el=$('#tc'),o={t:0};tl.to(o,{t:2.8,duration:2.8,ease:'none',onUpdate:()=>{const f=Math.floor(o.t*30)%30,s=Math.floor(o.t);el.textContent='00:0'+s+':'+String(f).padStart(2,'0');}},0);})();"
            "tl.to('#vf .c,#vf .rec',{opacity:0,duration:.35,ease:OUT},2.6);")


def notif(p, z):  # s2 : notification de messagerie qui tombe du haut… vide
    top = max(262, z[0])
    html = (f'<div id="vh" class="vh-notif" style="top:{top}px"><div class="ic"><svg viewBox="0 0 48 48"><path d="M7 10h34v22H22l-9 8v-8H7z"/></svg></div>'
            f'<div class="tx"><b>{p.get("t1", "Messages")}</b><span>{p.get("t2", "Aucun nouveau message")}</span></div><em>maintenant</em></div>')
    css = (".vh-notif{position:absolute;left:100px;width:800px;height:100px;border-radius:30px;background:rgba(255,255,255,.93);display:flex;align-items:center;gap:22px;padding:0 30px;"
           "box-shadow:0 18px 44px rgba(10,18,32,.22);color:var(--encre);opacity:0}"
           ".vh-notif .ic{width:56px;height:56px;border-radius:16px;background:var(--cyan-d);display:flex;align-items:center;justify-content:center;flex:0 0 56px}"
           ".vh-notif svg{width:32px;height:32px;fill:none;stroke:var(--cyan-t);stroke-width:3.4;stroke-linejoin:round}"
           ".vh-notif b{display:block;font:800 27px Montserrat}.vh-notif span{display:block;font:500 25px Montserrat;opacity:.7;margin-top:2px}"
           ".vh-notif em{margin-left:auto;font:500 20px Montserrat;font-style:normal;opacity:.45}")
    js = ("tl.fromTo('#vh',{opacity:0,y:-120},{opacity:1,y:0,duration:.65,ease:'expo.out',immediateRender:false},.1);"
          "tl.to('#vh',{y:-140,opacity:0,duration:.45,ease:OUT},2.6);")
    return html, css, js


def typing(p, z):  # s3 : une phrase s'écrit… puis s'efface (on écrit, on efface)
    top = (z[0] + z[1]) // 2 - 60
    txt = p.get("text", "Je suis coach et je peux t'aider à")
    html = (f'<div id="vh" class="vh-type" style="top:{top}px"><small>{p.get("label", "Brouillon")}</small>'
            f'<div class="ln"><span id="vht"></span><i></i></div><div class="ul"></div></div>')
    css = (f".vh-type{{position:absolute;left:72px;width:868px;opacity:0;color:#fff;{SH}}}"
           ".vh-type small{display:block;font:700 22px Montserrat;letter-spacing:.14em;text-transform:uppercase;opacity:.75;margin-bottom:10px}"
           ".vh-type .ln{font:600 40px Montserrat;min-height:52px;white-space:nowrap}"
           ".vh-type .ln i{display:inline-block;width:4px;height:42px;background:var(--cyan);margin-left:4px;vertical-align:-7px}"
           ".vh-type .ul{height:2px;background:rgba(255,255,255,.55);margin-top:12px;transform-origin:0 50%}")
    js = (f"tl.set('#vh',{{opacity:1}},0);tl.fromTo('#vh .ul',{{scaleX:0}},{{scaleX:1,duration:.5,ease:MOVE,immediateRender:false}},0);"
          f"(function(){{const el=$('#vht'),w={json.dumps(txt)},o={{n:0}};"
          f"tl.to(o,{{n:w.length,duration:1.15,ease:'none',onUpdate:()=>{{el.textContent=w.slice(0,Math.round(o.n));}}}},.2);"
          f"tl.to(o,{{n:0,duration:.55,ease:'none',onUpdate:()=>{{el.textContent=w.slice(0,Math.round(o.n));}}}},1.75);}})();"
          + "".join(f"tl.set('#vh .ln i',{{opacity:{0 if k % 2 else 1}}},{0.2 + k * 0.4:.2f});" for k in range(7))
          + "tl.to('#vh',{opacity:0,duration:.35,ease:OUT},2.6);")
    return html, css, js


def iris(p, z):  # s4 : projecteur qui se referme sur le visage (le regard des autres)
    cx, cy, r = p["cx"], p["cy"], p.get("r", 330)
    html = f'<div id="vh" class="vh-iris" style="left:{cx - r}px;top:{cy - r}px;width:{2 * r}px;height:{2 * r}px"></div>'
    css = (".vh-iris{position:absolute;border-radius:50%;box-shadow:0 0 0 2600px rgba(10,18,32,.74);opacity:0;"
           "outline:3px solid rgba(255,255,255,.7);outline-offset:-3px}")
    js = ("tl.set('#vh',{opacity:1},0);"
          "tl.fromTo('#vh',{scale:5.5},{scale:1,duration:.9,ease:'expo.out',immediateRender:false},.05);"
          "tl.to('#vh',{scale:5.5,duration:.7,ease:'power2.in'},2.0);tl.set('#vh',{opacity:0},2.7);")
    return html, css, js


def wave(p, z):  # s5 : forme d'onde de la voix, d'abord timide… puis pleine
    n, top = 26, (z[0] + z[1]) // 2 - 60
    lo = [8, 12, 6, 14, 9, 18, 7, 12, 10, 16, 8, 11, 6, 14, 9, 12, 7, 15, 10, 8, 13, 6, 11, 9, 14, 7]
    hi = [40, 72, 58, 96, 120, 84, 60, 110, 70, 46, 92, 120, 76, 54, 100, 118, 64, 88, 112, 70, 50, 96, 80, 60, 42, 30]
    bars = "".join(f'<i style="left:{k * 30}px"></i>' for k in range(n))
    html = f'<div id="vh" class="vh-wave" style="top:{top}px">{bars}</div>'
    css = (".vh-wave{position:absolute;left:150px;width:780px;height:120px;opacity:0}"
           ".vh-wave i{position:absolute;bottom:0;width:14px;height:100px;border-radius:7px;background:#fff;transform-origin:50% 100%;box-shadow:0 2px 10px rgba(10,18,32,.25)}")
    js = "tl.set('#vh',{opacity:1},0);"
    for k in range(n):
        js += (f"tl.fromTo('#vh i:nth-child({k + 1})',{{scaleY:.02}},{{scaleY:{lo[k] / 100:.2f},duration:.3,ease:IN,immediateRender:false}},{0.05 + k * 0.015:.3f});"
               f"tl.to('#vh i:nth-child({k + 1})',{{scaleY:{hi[k] / 100:.2f},backgroundColor:'{'#00D9FF' if k % 4 == 1 else '#fff'}',duration:.45,ease:IN}},{1.05 + k * 0.012:.3f});")
    js += "tl.to('#vh',{opacity:0,duration:.35,ease:OUT},2.6);"
    return html, css, js


def countdown(p, z):  # s6 : compte à rebours jusqu'à la nouvelle année
    top = max(262, (z[0] + z[1]) // 2 - 110)
    a, b = p.get("from", 365), p.get("to", 60)
    html = (f'<div id="vh" class="vh-cd" style="top:{top}px"><b id="vhn">{a}</b><span>{p.get("label", "jours avant 2027")}</span></div>')
    css = (f".vh-cd{{position:absolute;left:72px;width:868px;text-align:center;color:#fff;opacity:0;{SH}}}"
           ".vh-cd b{display:block;font:900 150px/1 Montserrat;letter-spacing:-.03em;font-variant-numeric:tabular-nums}"
           ".vh-cd span{display:block;font:600 30px Montserrat;letter-spacing:.04em;margin-top:6px;opacity:.9}")
    js = ("tl.fromTo('#vh',{opacity:0,scale:.92},{opacity:1,scale:1,duration:.4,ease:IN,immediateRender:false},0);"
          f"(function(){{const el=$('#vhn'),o={{n:{a}}};tl.to(o,{{n:{b},duration:1.5,ease:'expo.out',onUpdate:()=>{{el.textContent=Math.round(o.n);}}}},.1);}})();"
          "tl.to('#vhn',{color:'#00D9FF',duration:.2},1.5);tl.to('#vh',{opacity:0,y:-16,duration:.35,ease:OUT},2.6);")
    return html, css, js


def timer(p, z):  # s7 : chronomètre qui tourne : « 2 h plus tard »
    top = (z[0] + z[1]) // 2 - 75
    html = (f'<div id="vh" class="vh-tm" style="top:{top}px"><svg viewBox="0 0 150 150"><circle class="bg" cx="75" cy="75" r="64"/>'
            f'<circle class="fg" cx="75" cy="75" r="64"/><path class="hd" d="M75 75V26"/></svg>'
            f'<div><small>{p.get("t1", "ton idée")}</small><b>{p.get("t2", "2 h plus tard…")}</b></div></div>')
    css = (f".vh-tm{{position:absolute;left:110px;display:flex;align-items:center;gap:34px;color:#fff;opacity:0;{SH}}}"
           ".vh-tm svg{width:150px;height:150px;transform:rotate(-90deg);filter:drop-shadow(0 2px 10px rgba(10,18,32,.35))}"
           ".vh-tm circle{fill:none;stroke-width:9}.vh-tm .bg{stroke:rgba(255,255,255,.35)}.vh-tm .fg{stroke:#00D9FF;stroke-linecap:round;stroke-dasharray:402;stroke-dashoffset:402}"
           ".vh-tm .hd{stroke:#fff;stroke-width:7;stroke-linecap:round;transform-origin:75px 75px}"
           ".vh-tm small{display:block;font:700 24px Montserrat;letter-spacing:.12em;text-transform:uppercase;opacity:.8}"
           ".vh-tm b{display:block;font:900 64px/1.05 Montserrat;letter-spacing:-.02em;opacity:0}")
    js = ("tl.fromTo('#vh',{opacity:0,x:-30},{opacity:1,x:0,duration:.45,ease:IN,immediateRender:false},0);"
          "tl.fromTo('#vh .fg',{strokeDashoffset:402},{strokeDashoffset:0,duration:1.4,ease:'power2.inOut',immediateRender:false},.15);"
          "tl.fromTo('#vh .hd',{rotation:90},{rotation:450*3+90,duration:1.4,ease:'power2.inOut',immediateRender:false},.15);"
          "tl.fromTo('#vh b',{opacity:0,y:20},{opacity:1,y:0,duration:.4,ease:IN,immediateRender:false},1.1);"
          "tl.to('#vh',{opacity:0,y:-16,duration:.35,ease:OUT},2.7);")
    return html, css, js


def pathline(p, z):  # s8 : une ligne de progression se trace, les étapes s'allument une à une
    n = p.get("n", 5)
    dots = "".join(f'<b style="left:{k * 860 // (n - 1) - 9}px"></b>' for k in range(n))
    html = f'<div id="vh" class="vh-path" style="top:{max(262, z[0])}px"><i class="l0"></i><i class="l1"></i>{dots}</div>'
    css = (".vh-path{position:absolute;left:76px;width:860px;height:24px;opacity:0;filter:drop-shadow(0 1px 6px rgba(10,18,32,.35))}"
           ".vh-path i{position:absolute;left:0;right:0;top:10px;height:4px;border-radius:2px;transform-origin:0 50%}"
           ".vh-path .l0{background:rgba(255,255,255,.45)}.vh-path .l1{background:#00D9FF}"
           ".vh-path b{position:absolute;top:3px;width:18px;height:18px;border-radius:50%;background:#fff;border:3px solid #fff}")
    js = ("tl.set('#vh',{opacity:1},0);tl.fromTo('#vh .l0',{scaleX:0},{scaleX:1,duration:.6,ease:MOVE,immediateRender:false},0);"
          "tl.fromTo('#vh b',{scale:0},{scale:1,duration:.3,ease:IN,stagger:.08,immediateRender:false},.15);"
          "tl.fromTo('#vh .l1',{scaleX:0},{scaleX:1,duration:1.5,ease:'power1.inOut',immediateRender:false},.7);")
    for k in range(n):
        js += f"tl.to('#vh b:nth-of-type({k + 1})',{{backgroundColor:'#00D9FF',borderColor:'#00D9FF',scale:1.25,duration:.2}},{0.7 + 1.5 * k / (n - 1):.2f});"
    js += "tl.to('#vh',{opacity:0,duration:.35,ease:OUT},2.6);"
    return html, css, js


def arrows(p, z):  # s9 : des flèches dans tous les sens… qui finissent par pointer la même direction
    rots = [150, -70, 215, 35, -130, 95]
    top = (z[0] + z[1]) // 2 - 45
    ar = "".join(f'<svg viewBox="0 0 90 90" style="left:{k * 150}px"><path d="M14 45h58M50 23l22 22-22 22"/></svg>' for k in range(len(rots)))
    html = f'<div id="vh" class="vh-ar" style="top:{top}px">{ar}</div>'
    css = (".vh-ar{position:absolute;left:96px;width:840px;height:90px;opacity:0}"
           ".vh-ar svg{position:absolute;top:0;width:90px;height:90px;fill:none;stroke:#fff;stroke-width:7;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 2px 8px rgba(10,18,32,.35))}")
    js = "tl.set('#vh',{opacity:1},0);"
    for k, r in enumerate(rots):
        js += (f"tl.fromTo('#vh svg:nth-child({k + 1})',{{rotation:{r - 40},opacity:0}},{{rotation:{r},opacity:1,duration:.4,ease:IN,immediateRender:false}},{0.05 + k * 0.05:.2f});"
               f"tl.to('#vh svg:nth-child({k + 1})',{{rotation:0,duration:.6,ease:'back.out(1.2)'}},{1.0 + k * 0.07:.2f});")
    js += "tl.to('#vh svg',{stroke:'#00D9FF',duration:.25},1.6);tl.to('#vh',{opacity:0,x:40,duration:.35,ease:OUT},2.6);"
    return html, css, js


def qmark(p, z):  # s10 : un point d'interrogation géant se dessine puis se remplit
    top = max(240, (z[0] + z[1]) // 2 - 190)
    html = f'<div id="vh" class="vh-q" style="top:{top}px">?</div>'
    css = ".vh-q{position:absolute;left:0;width:1080px;text-align:center;font:900 330px/1 Montserrat;color:rgba(0,217,255,0);-webkit-text-stroke:5px #fff;opacity:0;filter:drop-shadow(0 4px 18px rgba(10,18,32,.35))}"
    js = ("tl.fromTo('#vh',{opacity:0,scale:.6,rotation:-14},{opacity:1,scale:1,rotation:0,duration:.7,ease:'expo.out',immediateRender:false},0);"
          "tl.to('#vh',{color:'rgba(0,217,255,1)',webkitTextStrokeColor:'#00D9FF',duration:.35},1.0);"
          "tl.to('#vh',{opacity:0,scale:.9,duration:.35,ease:OUT},2.4);")
    return html, css, js


def scan(p, z):  # s11 : une ligne d'analyse balaie l'image, « Analyse… »
    html = ('<div id="vh" class="vh-scan"><i></i><small>Analyse<span id="vhd"></span></small></div>')
    css = (".vh-scan{position:absolute;inset:0;opacity:0;pointer-events:none}"
           ".vh-scan i{position:absolute;left:0;right:0;top:0;height:3px;background:#00D9FF;box-shadow:0 0 18px 4px rgba(0,217,255,.55)}"
           f".vh-scan small{{position:absolute;right:164px;top:{max(262, z[0])}px;font:700 24px Montserrat;letter-spacing:.16em;text-transform:uppercase;color:#fff;{SH}}}")
    js = ("tl.set('#vh',{opacity:1},0);"
          "tl.fromTo('#vh i',{y:250,opacity:1},{y:1520,duration:1.2,ease:'power1.inOut',immediateRender:false},.05);"
          "tl.to('#vh i',{opacity:0,duration:.2},1.25);"
          "(function(){const el=$('#vhd'),o={n:0};tl.to(o,{n:9,duration:2.4,ease:'none',onUpdate:()=>{el.textContent='.'.repeat(Math.floor(o.n)%4);}},0);})();"
          "tl.to('#vh small',{opacity:0,duration:.3,ease:OUT},2.5);")
    return html, css, js


STYLES = {"viewfinder": viewfinder, "notif": notif, "typing": typing, "iris": iris, "wave": wave, "countdown": countdown,
          "timer": timer, "pathline": pathline, "arrows": arrows, "qmark": qmark, "scan": scan}


def make(spec, zone):
    v = spec.get("vhook")
    if not v: return "", "", ""
    if isinstance(v, str): v = {"style": v}
    return STYLES[v["style"]](v, zone)

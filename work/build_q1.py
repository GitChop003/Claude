import json, html
e = json.load(open("q1.edl.json")); D = e["duration"]; caps = e["captions"]
FIX = {"alors, ?": "alors,", "Développer": "développer", "Une": "une", "aussi.": "aussi", "Veut": "veut", "deux": "deux,"}
for c in caps: c["text"] = FIX.get(c["text"], c["text"])
Q_END = 12.45  # interviewer speaks until here
QUOTE = (52.35, 56.0); FINAL = 57.65
# ---- caption chunks
chunks, cur = [], []
for i, w in enumerate(caps):
    cur.append(w)
    nxt = caps[i + 1] if i + 1 < len(caps) else None
    brk = (nxt is None or len(cur) >= 4 or sum(len(x["text"]) + 1 for x in cur) > 24 or w["text"][-1] in ".?!,"
           or nxt["start"] - w["end"] > 0.35 or (w["start"] < Q_END <= nxt["start"]))
    if brk: chunks.append(cur); cur = []
chunks = [c for c in chunks if not (QUOTE[0] <= c[0]["start"] < QUOTE[1]) and c[0]["start"] < FINAL]
cap_html, cap_js = [], []
for k, ch in enumerate(chunks):
    s = ch[0]["start"]; e_ = chunks[k + 1][0]["start"] if k + 1 < len(chunks) else ch[-1]["end"] + 0.3
    e_ = min(e_, ch[-1]["end"] + 0.6)
    if s < QUOTE[0] < e_: e_ = QUOTE[0]
    if s < FINAL < e_: e_ = FINAL
    q = " q" if s < Q_END else ""
    spans = "".join(f'<span id="w{k}_{j}">{html.escape(w["text"])}</span> ' for j, w in enumerate(ch))
    cap_html.append(f'<div class="cap{q}" id="c{k}">{spans.strip()}</div>')
    cap_js.append(f"show('#c{k}',{s:.3f},{e_:.3f});")
    for j, w in enumerate(ch): cap_js.append(f"hl('#w{k}_{j}',{w['start']:.3f});")
# ---- zoom per jump cut (alternate framing hides the cut)
Z = [1.0, 1.12, 1.04, 1.15]; zoom_js = []
t = 0
for i, (s, x, o, d) in enumerate(e["map"]):
    zoom_js.append(f"tl.set('#vw',{{scale:{Z[i % 4]}}},{o:.3f});")
def at(word, n=1):
    hits = [c for c in caps if c["text"].lower().startswith(word.lower())]; return hits[n - 1]["start"]
T = dict(biz=at("business"), phys=at("physique"), virt=at("virtuelle"), declic=at("déclic"), bac=at("bac"),
         eleve=at("premier"), cher=at("cher", 2), netflix=at("Netflix"), mycanal=at("MyCanal"), pages=at("pages"),
         sites=at("sites"), boost=at("boostage"), consorts=at("consorts"), acheter=at("acheter"), formes=at("formes"),
         final=at("C'était"))
items = [("Comptes Netflix", T["netflix"]), ("Comptes MyCanal", T["mycanal"]), ("Pages de vente", T["pages"]),
         ("Petits sites web", T["sites"]), ("Boostage de comptes", T["boost"])]
list_html = "".join(f'<li id="li{i}"><span class="dot"></span>{html.escape(n)}<i class="s"></i></li>' for i, (n, _) in enumerate(items))
list_js = "".join(f"tl.fromTo('#li{i}',{{autoAlpha:0,x:40}},{{autoAlpha:1,x:0,duration:.35,ease:'back.out(2)'}},{t_:.3f});" for i, (_, t_) in enumerate(items))
page = f"""<!doctype html>
<html lang="fr"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1920, height=1080"/>
<script src="assets/gsap.min.js"></script>
<style>
@font-face{{font-family:Inter;font-weight:400;src:url(assets/fonts/Inter-400-latin.woff2) format('woff2')}}
@font-face{{font-family:Inter;font-weight:700;src:url(assets/fonts/Inter-700-latin.woff2) format('woff2')}}
:root{{--neon:#3CFF9A;--pink:#FF4FA3;--ink:#0b0d10;--white:#fff}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1920px;height:1080px;overflow:hidden;background:#000;font-family:Inter,sans-serif}}
#root{{position:relative;width:1920px;height:1080px;overflow:hidden}}
#vw{{position:absolute;inset:0;transform-origin:56% 32%}}
#vw video{{width:100%;height:100%;object-fit:cover;display:block}}
#vignette{{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at 55% 40%,transparent 55%,rgba(0,0,0,.45) 100%)}}
#dim{{position:absolute;inset:0;background:#05070a;opacity:0}}
#flash{{position:absolute;inset:0;background:#fff;opacity:0}}
#bar{{position:absolute;left:0;top:0;height:8px;width:1920px;background:var(--neon);transform-origin:0 50%;box-shadow:0 0 18px var(--neon)}}
.cap{{position:absolute;left:0;right:0;bottom:92px;text-align:center;font-weight:700;font-size:66px;line-height:1.1;color:#fff;
  letter-spacing:-.01em;opacity:0;text-shadow:0 4px 0 #000,0 0 14px rgba(0,0,0,.9);-webkit-text-stroke:2px #000;paint-order:stroke fill}}
.cap span.on{{color:var(--neon)}}
.cap.q{{font-weight:400;font-style:italic;font-size:54px;color:#f2f2f2}}
.cap.q span.on{{color:var(--pink)}}
.glass{{background:rgba(10,12,16,.72);border:2px solid rgba(255,255,255,.12);border-radius:28px;backdrop-filter:blur(8px)}}
#qcard{{position:absolute;left:80px;top:90px;width:820px;padding:40px 48px;opacity:0}}
#qcard .k{{font-size:28px;font-weight:700;letter-spacing:.28em;color:var(--pink)}}
#qcard .k b{{color:#fff}}
#qcard .t{{margin-top:18px;font-size:58px;font-weight:700;line-height:1.08;color:#fff}}
#qcard .u{{margin-top:26px;height:8px;width:0;background:var(--pink);border-radius:4px}}
.chip{{position:absolute;padding:20px 34px;border-radius:999px;font-weight:700;font-size:44px;color:var(--ink);background:var(--neon);
  opacity:0;box-shadow:0 12px 40px rgba(0,0,0,.45);letter-spacing:.02em}}
.chip.alt{{background:#fff}}
#big{{position:absolute;left:0;right:0;top:330px;text-align:center;font-weight:700;font-size:190px;letter-spacing:-.03em;color:#fff;opacity:0;
  text-shadow:0 10px 50px rgba(0,0,0,.7)}}
#big em{{font-style:normal;color:var(--neon)}}
#stamp{{position:absolute;right:60px;top:420px;padding:18px 40px;border:10px solid #ff3b3b;color:#ff3b3b;font-weight:700;font-size:96px;
  border-radius:18px;transform:rotate(-12deg);opacity:0;letter-spacing:.06em;background:rgba(255,255,255,.08)}}
#lt{{position:absolute;left:80px;bottom:260px;padding:26px 40px 28px 34px;opacity:0;border-left:10px solid var(--neon);border-radius:0 24px 24px 0}}
#lt .a{{font-size:30px;font-weight:700;letter-spacing:.2em;color:var(--neon)}}
#lt .b{{font-size:52px;font-weight:700;color:#fff;margin-top:6px}}
#lt .c{{font-size:40px;font-style:italic;color:#ddd;margin-top:8px;opacity:0}}
#panel{{position:absolute;right:80px;top:110px;width:640px;padding:40px 46px;opacity:0}}
#panel h3{{font-size:30px;letter-spacing:.24em;color:var(--pink);font-weight:700}}
#panel ul{{list-style:none;margin-top:22px}}
#panel li{{position:relative;font-size:46px;font-weight:700;color:#fff;padding:12px 0 12px 44px;opacity:0}}
#panel li .dot{{position:absolute;left:0;top:30px;width:20px;height:20px;border-radius:50%;background:var(--neon)}}
#panel li .s{{position:absolute;left:36px;right:-10px;top:50%;height:7px;margin-top:-3px;background:var(--pink);transform-origin:0 50%;border-radius:5px}}
#quote{{position:absolute;left:90px;top:170px;width:860px;opacity:0}}
#quote .m{{font-size:220px;line-height:.6;color:var(--neon);font-weight:700}}
#quote p{{font-size:68px;line-height:1.12;font-weight:700;color:#fff;margin-top:10px;text-shadow:0 6px 30px rgba(0,0,0,.8)}}
#quote p span{{opacity:.15}}
#quote .who{{margin-top:24px;font-size:32px;color:#cfcfcf;letter-spacing:.12em;opacity:0}}
#end{{position:absolute;left:0;right:0;top:380px;text-align:center;opacity:0}}
#end .l1{{font-size:64px;font-weight:700;color:#fff;letter-spacing:.3em}}
#end .l2{{font-size:200px;font-weight:700;color:var(--neon);letter-spacing:-.03em;line-height:1}}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{D:.3f}" data-width="1920" data-height="1080">
  <div id="vw"><video id="v" class="clip" data-start="0" data-duration="{D:.3f}" data-has-audio="true" src="assets/q1_cut.mp4" playsinline></video></div>
  <div id="vignette"></div><div id="dim"></div>
  <div id="qcard" class="glass"><div class="k">QUESTION <b>1</b> / 3</div><div class="t">Quel genre d'accompagnement proposes-tu&nbsp;?</div><div class="u"></div></div>
  <div class="chip" id="chip-biz" style="right:150px;top:250px">BUSINESS EN LIGNE</div>
  <div class="chip" id="chip-phys" style="right:330px;top:230px">PHYSIQUE</div>
  <div class="chip alt" id="chip-virt" style="right:150px;top:360px">OU VIRTUELLE</div>
  <div id="stamp">BAC RATÉ</div>
  <div id="lt" class="glass"><div class="a">LE DÉBUT</div><div class="b">Mon 1er élève français</div><div class="c">« il m'a payé cher »</div></div>
  <div id="panel" class="glass"><h3>AVANT, JE VENDAIS</h3><ul>{list_html}</ul></div>
  <div id="quote"><div class="m">“</div><p id="qp"><span id="q1">Je ne veux pas acheter un service.</span> <span id="q2">Je veux que tu me formes.</span></p><div class="who">— SON PREMIER ÉLÈVE</div></div>
  {''.join(cap_html)}
  <div id="big">LE <em>DÉCLIC</em></div>
  <div id="end"><div class="l1">C'ÉTAIT ÇA</div><div class="l2">LE DÉCLIC.</div></div>
  <div id="flash"></div><div id="bar"></div>
</div>
<script>
const tl = gsap.timeline({{paused:true}});
function show(id,a,b){{tl.set(id,{{opacity:1}},a);tl.set(id,{{opacity:0}},b);}}
function hl(id,a){{tl.set(id,{{className:'on'}},a);}}
const pop=(id,a,b,from)=>{{tl.fromTo(id,Object.assign({{autoAlpha:0,scale:.6}},from||{{}}),{{autoAlpha:1,scale:1,x:0,y:0,duration:.35,ease:'back.out(2.2)'}},a);tl.to(id,{{autoAlpha:0,scale:.9,duration:.25,ease:'power2.in'}},b);}};
tl.fromTo('#bar',{{scaleX:0}},{{scaleX:1,duration:{D:.3f},ease:'none'}},0);
{''.join(zoom_js)}
// Question card
tl.fromTo('#qcard',{{autoAlpha:0,x:-60}},{{autoAlpha:1,x:0,duration:.6,ease:'power3.out'}},0.05);
tl.to('#qcard .u',{{width:260,duration:.6,ease:'power2.out'}},0.5);
tl.to('#qcard',{{autoAlpha:0,x:-60,duration:.4,ease:'power2.in'}},{Q_END - 0.2:.3f});
// keyword inserts
pop('#chip-biz',{T['biz']:.3f},{T['biz'] + 2.6:.3f},{{y:30}});
pop('#chip-phys',{T['phys']:.3f},{T['virt'] + 1.0:.3f},{{x:60}});
pop('#chip-virt',{T['virt']:.3f},{T['virt'] + 1.0:.3f},{{x:60}});
// "le déclic" : flash + kinetic word + punch-in
tl.set('#flash',{{opacity:.85}},{T['declic']:.3f});tl.to('#flash',{{opacity:0,duration:.35,ease:'power2.out'}},{T['declic']:.3f});
tl.fromTo('#big',{{autoAlpha:0,scale:1.6}},{{autoAlpha:1,scale:1,duration:.3,ease:'power4.out'}},{T['declic']:.3f});
tl.to('#big',{{autoAlpha:0,duration:.25}},{T['declic'] + 1.1:.3f});
tl.to('#dim',{{opacity:.35,duration:.2}},{T['declic']:.3f});tl.to('#dim',{{opacity:0,duration:.3}},{T['declic'] + 1.1:.3f});
// bac raté stamp
tl.fromTo('#stamp',{{autoAlpha:0,scale:2.4,rotation:-4}},{{autoAlpha:1,scale:1,rotation:-12,duration:.22,ease:'power4.in'}},{T['bac']:.3f});
tl.to('#stamp',{{autoAlpha:0,duration:.25}},{T['bac'] + 1.5:.3f});
// lower third
tl.fromTo('#lt',{{autoAlpha:0,x:-80}},{{autoAlpha:1,x:0,duration:.45,ease:'power3.out'}},{T['eleve'] - 0.3:.3f});
tl.fromTo('#lt .c',{{autoAlpha:0,y:12}},{{autoAlpha:1,y:0,duration:.3}},{T['cher']:.3f});
tl.to('#lt',{{autoAlpha:0,x:-80,duration:.35,ease:'power2.in'}},{T['cher'] + 1.6:.3f});
// list panel
tl.fromTo('#panel',{{autoAlpha:0,x:80}},{{autoAlpha:1,x:0,duration:.45,ease:'power3.out'}},{T['netflix'] - 0.5:.3f});
{list_js}
tl.to('#panel li',{{opacity:.55,duration:.3,stagger:.08}},{T['consorts'] + 0.4:.3f});
tl.fromTo('#panel li .s',{{scaleX:0}},{{scaleX:1,duration:.25,stagger:.08,ease:'power2.out'}},{T['consorts'] + 0.4:.3f});
tl.to('#panel',{{autoAlpha:0,x:80,duration:.35,ease:'power2.in'}},{QUOTE[0] - 0.3:.3f});
// quote
tl.fromTo('#quote',{{autoAlpha:0,y:30}},{{autoAlpha:1,y:0,duration:.45,ease:'power3.out'}},{QUOTE[0]:.3f});
tl.to('#q1',{{opacity:1,duration:.4}},{T['acheter'] - 0.4:.3f});
tl.to('#q2',{{opacity:1,duration:.4}},{T['formes'] - 0.4:.3f});
tl.to('#quote .who',{{opacity:1,duration:.4}},{T['formes'] + 0.3:.3f});
tl.to('#dim',{{opacity:.45,duration:.5}},{QUOTE[0]:.3f});
tl.to('#dim',{{opacity:0,duration:.4}},{QUOTE[1]:.3f});
tl.to('#quote',{{autoAlpha:0,duration:.35}},{QUOTE[1]:.3f});
// final title
tl.set('#flash',{{opacity:.9}},{FINAL:.3f});tl.to('#flash',{{opacity:0,duration:.4}},{FINAL:.3f});
tl.to('#dim',{{opacity:.6,duration:.3}},{FINAL:.3f});
tl.fromTo('#end',{{autoAlpha:0,scale:1.3}},{{autoAlpha:1,scale:1,duration:.4,ease:'power4.out'}},{FINAL:.3f});
tl.fromTo('#vw',{{scale:1.04}},{{scale:1.14,duration:{D - FINAL:.3f},ease:'none'}},{FINAL:.3f});
{''.join(cap_js)}
window.__timelines = window.__timelines || {{}};
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body></html>
"""
open("/home/user/Claude/videos/q1/index.html", "w").write(page)
json.dump(T, open("q1.times.json", "w"), indent=1); print(T, len(chunks), "caption chunks")

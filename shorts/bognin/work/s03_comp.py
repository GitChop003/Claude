"""Short 03 — compositions (landscape + portrait).  Run after s03.py cut and plates.py.

  python3 s03_comp.py media   # mux voice into plates, add end-card hold, copy into the projects
  python3 s03_comp.py         # (re)build both HyperFrames projects
"""
import json, os, subprocess, sys
sys.path.insert(0, "/home/claude/claude/shorts/bognin/work")
from s03 import mp, D as VOICE_D, NAME, OUT
from edit import src2out
from compose import Comp

REPO = "/home/claude/claude"
HOLD = 1.8                      # end card over a held last frame
DUR = round(VOICE_D + HOLD, 3)
PROJ = {o: f"{REPO}/shorts/bognin/{NAME}/{o}" for o in ("land", "port")}

# --------------------------------------------------------------------------- captions
FIX = {"lui": "le", "faite": "fait", "revient": "réveiller"}
WORDS = json.load(open(f"{REPO}/shorts/bognin/work/{NAME}.words.json"))
caps = []
for w in WORDS:
    for s, e, o, d in mp:
        ov = min(w["end"], e) - max(w["start"], s)
        if ov >= 0.03:
            st = src2out(mp, max(w["start"], s))
            en = src2out(mp, min(w["end"], e) - 1e-3)
            caps.append({"text": FIX.get(w["text"], w["text"]), "src": w["start"], "start": round(st, 3), "end": round(max(en, st + 0.06), 3)})
            break
caps[0]["text"] = "Je"            # sentence start after the cut


def T(word, near):
    """Output time of the kept word `word` whose source time is closest to `near`."""
    lw = word.lower()
    c = [x for x in caps if x["text"].lower().strip(",.") .startswith(lw) and abs(x["src"] - near) < 4]
    if not c:
        raise ValueError(f"{word!r} not found near {near}")
    return min(c, key=lambda x: abs(x["src"] - near))["start"]


KEY = ("entrepreneuriat", "l'entrepreneuriat", "monde", "mental", "fort", "n'entreprenez", "persévérance", "personne", "seul")


def build(o):
    c = Comp(NAME, o, DUR, f"{NAME}_{o}.mp4", caps, keywords=KEY)
    port = o == "port"
    c.zooms(mp)
    # hook + who
    c.title("CE QUE PERSONNE N'OSE TE DIRE", "L'entrepreneuriat<br>n'est <em>pas</em> pour<br>tout le monde" if port
            else "L'entrepreneuriat n'est <em>pas</em><br>pour tout le monde", 0.15, DUR if port else T("Si", 557.75) - 0.2)
    c.name_tag("PARFAIT BOGNIN", "· entrepreneur", 0.5, 2.9) if not port else c.name_tag("PARFAIT BOGNIN", "", 0.5, 2.9)
    c.add_sfx("whoosh", 0.05, 0.2)
    # « Si vous n'avez pas un mental assez fort… n'entreprenez pas »
    t = T("mental", 558.71); c.emoji("brain", t - 0.1, t + 2.3, side="r", rot=-8)
    t = T("fort", 559.51); c.stamp("MENTAL REQUIS", t - 0.05, t + 1.9)
    t = T("n'entreprenez", 561.67); c.chip("N'ENTREPRENEZ PAS", t - 0.1, T("Je", 563.19) - 0.05, icon="cross", cls="red")
    # « Je suis vraiment désolé… je le redis encore »
    t = T("désolé", 563.83); c.emoji("pray", t - 0.15, t + 1.9, side="l", rot=6)
    t = T("redis", 565.83); c.chip("JE LE REDIS", t - 0.15, t + 1.5, icon="warning", cls="white")
    t = T("mental", 567.43); c.emoji("muscle", t - 0.1, T("Ne", 569.43) - 0.2, side="r", rot=-6)
    # « Ne faites pas de l'entrepreneuriat. »  -> full-screen statement
    a = T("Ne", 569.43); b = T("L'entrepreneuriat", 571.70) - 0.15
    c.big("NE FAITES PAS<br>DE <em>L'ENTREPRENEURIAT</em>" if not port else "NE FAITES<br>PAS DE<br><em style=\"font-size:.7em\">L'ENTREPRENEURIAT</em>",
          a - 0.05, b, small="SI VOUS N'AVEZ PAS LE MENTAL")
    # « …demandent le plus de mental possible, le plus de persévérance possible. »  -> checklist
    pa = T("demandent", 573.46)
    c.panel("CE QUE ÇA DEMANDE", [("Du mental", T("mental", 574.58) - 0.1, "brain"),
                                  ("De la persévérance", T("persévérance", 576.98) - 0.1, "fire")],
            pa - 0.2, T("Vous", 578.82) + 0.6)
    # « …des jours où… personne autour de vous qui vous comprenne. »  -> mood + insert
    t = T("réveiller", 579.54); c.mood(t - 0.2, DUR + 1)
    c.emoji("moon", t - 0.1, t + 2.2, side="l", rot=-6)
    t = T("personne", 582.98); c.chip("SEUL CONTRE TOUS", t - 0.1, VOICE_D - 0.05, icon="sob", cls="dark")
    c.endcard("ET TOI ?", "TU AS LE<br>MENTAL ?", "Abonne-toi pour la suite", VOICE_D + 0.05)
    return c


def media():
    for o in ("land", "port"):
        os.makedirs(f"{PROJ[o]}/assets", exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{OUT}/{NAME}_{o}.mp4", "-i", f"{OUT}/{NAME}_voice.wav",
                        "-filter_complex", f"[0:v]tpad=stop_mode=clone:stop_duration={HOLD}[v];[1:a]apad=whole_dur={DUR}[a]",
                        "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p",
                        "-g", "25", "-c:a", "aac", "-b:a", "192k", "-t", f"{DUR}", "-movflags", "+faststart",
                        f"{PROJ[o]}/assets/{NAME}_{o}.mp4"], check=True)
        print("media", o)


if __name__ == "__main__":
    if "media" in sys.argv:
        media()
    for o in ("land", "port"):
        print(o, "chunks:", build(o).build(PROJ[o]))
    print(f"duration {DUR}s")
    print(" ".join(f"{x['text']}@{x['start']:.2f}" for x in caps))

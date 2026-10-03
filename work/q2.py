import sys; sys.path.insert(0, "/home/user/Claude/work")
from engine import *
NAME, OUT = "q2", "/home/user/Claude/videos/q2"
KEEP = [[103.55, 113.60], [115.10, 118.35], [122.45, 124.70], [125.30, 127.50], [128.10, 133.80], [138.30, 143.45],
        [146.85, 155.10], [156.60, 164.45], [166.60, 176.20], [181.85, 189.30], [192.25, 202.45], [204.25, 211.00],
        [212.50, 232.40]]
FIX = {"1er": "Première", "show": "chose,", "l'indy": "LinkedIn", ("j'ai", 167): "j'interagis", ("interagé", 167): None,
       "chanxion": "j'enchaîne", "deux.": "de", ("je", 229): "ça", ("ne", 229): None, "Short.": "Shorts.", "postes": "posts",
       ("chaque", 192): "Chaque", ("Maintenant", 204): "Maintenant", ("ces", 156): "Ces", ("plus", 172.8): "Le plus", ("élèves.", 146.6): None, ("que", 192.1): None, ("j'ai", 172.9): "j'ai", ("de", 181.9): "De", ("heures", 175.8): "heures."}
mp, D = make_edl(KEEP)
caps = captions(mp, FIX)
if __name__ == "__main__" and sys.argv[1:] == ["caps"]:
    print(round(D, 2), "s,", len(mp), "segments")
    print(" ".join(f"{c['text']}@{c['start']:.1f}" for c in caps)); sys.exit()

c = Comp(NAME, D, mp, caps, 2, "À quoi ressemble ta journée type ?", q_end=src2out(mp, 113.7))
T = lambda w, near: c.o(word_at(w, near))
L = dict(anchor="left")
# routine
t = T("même", 117.8); c.chip("LA MÊME ROUTINE, CHAQUE JOUR", t - 0.3, t + 2.2, 90, 170, icon="calendar", cls="white", **L)
t = T("lève", 123.9); c.emoji("sun", t - 0.3, t + 1.8, 1430, 200, size=190, rot=0)
t = T("LinkedIn", 126.7); c.logos([("linkedin", t - 0.2)], 120, 190, T("LinkedIn", 133.5) + 0.3)
# time blocks (lower thirds)
t = T("6h", 129.1); c.lowerthird("6H – 7H", "Post LinkedIn", t - 0.2, T("LinkedIn", 133.5) + 0.5, icon="phone")
t = T("lundi", 138.9); c.chip("LE LUNDI", t - 0.1, t + 4.0, 90, 170, icon="calendar", cls="sky", **L)
t = T("8h", 142.3); c.lowerthird("8H – 10H", "Coaching avec mes élèves", t - 0.2, t + 3.4, icon="grad")
t = T("jeudi", 152.0); c.chip("JEUDI · VENDREDI · SAMEDI", t - 0.2, T("samedi", 154.8) + 1.0, 90, 170, icon="calendar", cls="white", **L)
t = T("commentaires", 159.4); c.emoji("speech", t - 0.1, t + 3.0, 1430, 200, size=180, rot=-6)
t = T("énormément", 161.8); c.chip("ÇA PREND ÉNORMÉMENT DE TEMPS", t - 0.1, t + 2.4, 90, 170, icon="clock", cls="sun", **L)
t = T("prospecter", 170.4); c.chip("PROSPECTION", t - 0.1, t + 2.0, 90, 170, icon="target", **L)
t = T("11", 175.4); c.lowerthird("JUSQU'À 11H", "Commentaires & prospection", t - 0.4, t + 1.6, icon="speech")
t = T("11h", 182.9); c.lowerthird("11H – 15H", "Appels de vente", t - 0.2, T("vente", 188.7) + 0.8, icon="call")
c.emoji("call", t + 0.6, T("vente", 188.7) + 0.8, 1430, 200, size=180, rot=8, sfx=None)
t = T("15h", 192.9); c.lowerthird("15H – 18H", "Posts sur les réseaux", t - 0.2, T("Short", 201.8) + 1.0, icon="phone")
c.logos([("instagram", T("Instagram", 196.0)), ("linkedin", T("LinkedIn", 197.9)), ("facebook", T("Facebook", 199.4)),
         ("tiktok", T("TikTok", 200.5)), ("youtubeshorts", T("YouTube", 201.4))], 90, 120, T("Short", 201.8) + 1.0, anchor="left")
t = T("18h", 206.6); c.lowerthird("18H – 20H", "Appels & séances de coaching", t - 0.2, t + 4.3, icon="call")
t = T("20h", 213.0); c.lowerthird("20H – 22H", "Programmation & deep work", t - 0.2, T("veille", 216.9) + 1.2, icon="moon")
t = T("programme", 215.1); c.emoji("calendar", t, t + 2.4, 1430, 200, size=170, rot=-8)
t = T("deep", 219.3); c.chip("DEEP WORK", t - 0.1, t + 2.6, 90, 170, icon="brain", cls="pink", **L)
t = T("former", 224.2); c.emoji("books", t - 0.4, t + 2.2, 1430, 200, size=180, rot=6)
t = T("mentors", 225.9); c.chip("MENTORS & RECHERCHES", t - 0.2, t + 2.0, 90, 170, icon="star", cls="white", **L)
# recap
ra = T("suite", 228.6) - 0.4
items = [("Post LinkedIn", "6H – 7H", "phone"), ("Coaching (lundi)", "8H – 10H", "grad"), ("Commentaires", "→ 11H", "speech"),
         ("Appels de vente", "11H – 15H", "call"), ("Posts réseaux", "15H – 18H", "phone"), ("Appels & coaching", "18H – 20H", "call"),
         ("Deep work", "20H – 22H", "moon")]
c.panel("MA JOURNÉE TYPE", [(txt, ra + 0.35 + 0.22 * k, ic, tm) for k, (txt, tm, ic) in enumerate(items)], ra, D - 0.05, side="left")
t = T("change", 231.3); c.chip("ÇA NE CHANGE PAS.", t - 0.3, D - 0.05, 120, 250, cls="sun")
c.add_sfx("whoosh", 0.05, 0.25)
if __name__ == "__main__":
    if "media" in sys.argv: print(render_media(NAME, mp, D, OUT + "/assets", music_offset=95))
    print("chunks", c.build(OUT))

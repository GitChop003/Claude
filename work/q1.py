import sys; sys.path.insert(0, "/home/user/Claude/work")
from engine import *
NAME, OUT = "q1", "/home/user/Claude/videos/q1"
KEEP = [[3.30, 5.50], [5.50, 17.85], [21.90, 22.90], [23.75, 35.70], [40.00, 46.60], [48.80, 56.30], [58.40, 70.40],
        [70.50, 78.05], [80.40, 86.32], [87.05, 101.95]]
FIX = {"huit": "oui.", ("deux", 22.2): "deux,", ("Tu", 11.6): "tu", "virtuel.": "virtuelle.", "alors": "alors,", "Une": "une", "aussi": "aussi", "accompagn": "accompagnements pour…", ("?", 11): None, "aussi.": "aussi", "alors,": "alors…",
       "proposait": "proposais", "banque": "vente,", "boustage": "boostage", "boom": None, "dont": "donc", "jour.": "aujourd'hui.", ("aujourd'hui", 86): None, ("aujourd'hui", 85): None}
mp, D = make_edl(KEEP)
caps = captions(mp, FIX, keep=KEEP)
if __name__ == "__main__" and sys.argv[1:] == ["caps"]:
    print(round(D, 2), "s,", len(mp), "segments")
    print(" ".join(f"{c['text']}@{c['start']:.1f}" for c in caps)); sys.exit()

c = Comp(NAME, D, mp, caps, 1, "Quel genre d'accompagnement proposes-tu ?", q_end=src2out(mp, 17.9))
T = lambda w, near: c.o(word_at(w, near))
# --- inserts (output seconds)
t = T("business", 27.8); c.chip("BUSINESS EN LIGNE", t, t + 2.6, 90, 170, icon="laptop", anchor="left")
t = T("physique", 34.1); c.chip("PHYSIQUE", t, T("virtuel", 34.8) + 1.1, 90, 170, icon="store", cls="white", anchor="left")
t2 = T("virtuel", 34.8); c.chip("OU VIRTUELLE", t2, t2 + 1.1, 90, 285, icon="globe", anchor="left")
t = T("déclic", 41.1); c.big("LE <em>DÉCLIC</em>", t, t + 1.1)
c.emoji("bulb", t + 0.05, t + 1.1, 1350, 250, size=200, rot=10, sfx=None)
t = T("bac", 45.9); c.stamp("BAC RATÉ", t, t + 1.6, 60, 420)
c.emoji("grad", t + 0.1, t + 1.6, 1530, 250, size=150, rot=-14, sfx=None)
t = T("premier", 50.6); c.lowerthird("LE DÉBUT", "Mon 1er élève français", t - 0.3, T("cher", 55.1) + 1.6, sub="« il m'a payé cher »", sub_t=T("cher", 52.6), icon="fr")
t = T("cher", 55.1); c.emoji("money", t, t + 1.8, 1450, 230, size=190, rot=8)
c.panel("AVANT, JE VENDAIS", [("Comptes Netflix", T("Netflix", 61.9), "tv", None), ("Comptes MyCanal", T("MyCanal", 63.2), "tv", None),
        ("Pages de vente", T("pages", 65.1), "cart", None), ("Petits sites web", T("sites", 66.7), "laptop", None),
        ("Boostage de comptes", T("boostage", 67.3), "rocket", None)],
        T("Netflix", 61.9) - 0.6, T("acheter", 73.1) - 1.2, strike=T("consorts", 69.7) + 0.4, side="left")
qa = T("acheter", 73.1); c.quote([("Je ne veux pas acheter un service.", qa), ("Je veux que tu me formes.", T("formes", 74.6))],
        "SON PREMIER ÉLÈVE", qa - 0.9, T("toi", 77.3) + 0.4)
t = T("déclic", 81.2); c.big("C'ÉTAIT ÇA LE <em>DÉCLIC.</em>", t - 0.4, t + 1.0, small=None)
t = T("t'accompagner", 88.5); c.chip("ON PEUT T'ACCOMPAGNER", t, t + 2.4, 90, 170, icon="handshake", cls="white", anchor="left")
t = T("donner", 92.1); c.chip("PAS DE BUSINESS CLÉ EN MAIN", t - 0.2, t + 1.9, 90, 170, icon="cross", cls="dark", anchor="left")
t = T("idée", 97.8); c.emoji("bulb", t - 0.1, t + 1.6, 1420, 210, size=200, rot=-8)
c.chip("TON IDÉE", t - 0.1, t + 1.6, 90, 170, cls="sun", anchor="left")
t = T("développer", 100.5); c.emoji("rocket", t - 0.5, D - 0.2, 1440, 210, size=200, rot=12)
c.chip("ON T'AIDE À LA DÉVELOPPER", t - 0.5, D - 0.3, 90, 285, anchor="left")
c.add_sfx("whoosh", 0.05, 0.25)
if __name__ == "__main__":
    if "media" in sys.argv: print(render_media(NAME, mp, D, OUT + "/assets", music_offset=0))
    print("chunks", c.build(OUT))

import sys; sys.path.insert(0, "/home/user/Claude/work")
from engine import *
NAME, OUT = "q3", "/home/user/Claude/videos/q3"
KEEP = [[233.20, 258.35], [258.60, 269.45], [271.90, 290.42], [291.78, 295.95], [298.50, 329.98],
        [334.60, 339.45], [339.90, 370.60], [370.90, 466.05], [469.80, 494.80],
        [495.00, 509.20]]
FIX = {"reclamation": "réclamation", "video": "vidéo", "consort.": "consorts.", "m'envoie": "lui envoie", "CapCode.": "CapCut.",
       "plainteux,": "plainte,", "entreté": "sûre", ("jour,", 507): "aujourd'hui,", "jusqu'au": "jusqu'à"}
PHRASES = [("C'est un atteinte", "C'est une atteinte"), ("C'était un client que", "C'était une cliente que"), ("il n'avait pas", "il n'y avait pas"),
           ("est ce que je cache mais maintenant", "est-ce que je cache maintenant"),
           ("et j'oublie de cacher après ça me créer des problèmes", "et oublier de cacher, après ça me crée des problèmes."),
           ("pas le point", "pas de problème"), ("cinq semaines,", "cinq emails,"), ("je lui ai aussi compris.", "je l'ai aussi comprise."),
           ("et qu'on sort.", "et consorts."), ("je m'avais porté", "elle m'a porté"), ("porter plein de temps en retour.", "porter plainte en retour."),
           ("porter plein de temps en retour,", "porter plainte en retour,")]
mp, D = make_edl(KEEP, tail=2.4)
caps = captions(mp, FIX, PHRASES, keep=KEEP)
if __name__ == "__main__" and sys.argv[1:] == ["caps"]:
    print(round(D, 2), "s,", len(mp), "segments")
    print(" ".join(f"{c['text']}@{c['start']:.1f}" for c in caps)); sys.exit()

c = Comp(NAME, D, mp, caps, 3, "C'est difficile ? Tu as déjà voulu lâcher un client ?", q_end=src2out(mp, 258.4))
T = lambda w, near: c.o(word_at(w, near))
L = dict(anchor="left")
t = T("remboursement", 263.2); c.chip("AUCUNE DEMANDE DE REMBOURSEMENT", t - 0.2, t + 2.8, 90, 170, icon="check", cls="white", **L)
t = T("cliente.", 268.3); c.lowerthird("L'HISTOIRE", "La cliente qui ne voulait pas être filmée", t - 0.2, t + 5.5, icon="camera")
t = T("filmer", 279.4); c.emoji("camera", t - 0.2, t + 2.6, 1430, 200, size=180, rot=-8)
t = T("transcript", 284.0); c.chip("LE TRANSCRIPT → SES PROBLÉMATIQUES", t - 0.2, t + 3.0, 90, 170, icon="memo", cls="white", **L)
t = T("stratégie", 288.7); c.chip("MA STRATÉGIE DE CONTENU", t - 0.2, t + 2.0, 90, 285, icon="chart", **L)
qa = T("meilleurs", 292.1); c.quote([("Mes meilleurs contenus", qa), ("ressortent de mes appels avec mes élèves.", T("ressortent", 293.0))],
                                    "SA MÉTHODE", qa - 0.4, T("élèves.", 295.3) + 0.6)
t = T("caché", 305.6); c.emoji("seeno", t - 0.2, t + 2.6, 1430, 200, size=190, rot=6)
c.chip("VISAGE CACHÉ", t - 0.2, t + 2.6, 90, 170, icon="lock", cls="dark", **L)
t = T("plainte.", 313.4); c.stamp("PLAINTE ?!", t - 0.3, t + 1.6, 60, 400, rot=-9)
c.emoji("angry", t - 0.2, t + 1.6, 1500, 170, size=160, rot=-10, sfx=None)
t = T("atteinte", 316.5); c.chip("« ATTEINTE À MA VIE PRIVÉE »", t - 0.2, t + 3.0, 90, 170, icon="law", cls="pink", **L)
t = T("folle.", 322.8); c.emoji("thinking", t - 0.6, t + 1.6, 1440, 200, size=170, rot=8)
t = T("habitude", 350.5); c.chip("JE CACHE LE VISAGE DE TOUS MES ÉLÈVES", t - 0.3, t + 3.2, 90, 170, icon="seeno", cls="white", **L)
e0 = T("cinq", 364.4); c.counter(5, "EMAILS EN MOINS<br>DE 5 MINUTES", "mail", e0 - 0.3, e0 + 3.6, 90, 140,
                                [e0 + 0.12 * 0 + k * 0.28 for k in range(5)])
pa = T("réclamation", 367.8)
c.panel("SES EMAILS", [("Réclamation de confidentialité", pa, "lock", None), ("« Je vais porter plainte »", T("porter", 371.9), "law", None),
        ("« Supprime toutes mes vidéos »", T("supprimer", 374.5), "cross", None)], pa - 0.4, T("Directement", 376.5) + 1.2, side="left")
t = T("CapCut", 379.5) if False else T("application", 379.2); c.chip("CAPCUT : LA PREUVE", t + 0.4, t + 3.4, 90, 170, icon="film", cls="sky", **L)
t = T("filtre", 383.5); c.emoji("eyes", t - 0.2, t + 2.2, 1430, 200, size=170, rot=0)
t = T("folle", 393.7); c.emoji("sweat", t - 0.8, t + 1.4, 1440, 200, size=170, rot=6)
t = T("voice", 406.9); c.chip("UN VOCAL POUR PROUVER", t - 0.2, t + 2.8, 90, 170, icon="mic", **L)
c.emoji("mic", t - 0.1, t + 2.8, 1440, 200, size=170, rot=-6, sfx=None)
t = T("s'excuser,", 413.0); c.emoji("pray", t - 0.2, t + 2.4, 1440, 200, size=180, rot=0)
t = T("trois", 441.9); c.chip("3–4 JOURS PLUS TARD", t - 0.3, t + 2.6, 90, 170, icon="calendar", cls="white", **L)
qa = T("mécontentement,", 455.0)
c.quote([("On a eu un malentendu,", T("malentendu,", 456.4)), ("mais ça ne veut pas dire qu'on va arrêter l'accompagnement.", T("veut", 457.6))],
        "SA RÉPONSE", qa - 0.3, T("l'accompagnement.", 459.0) + 0.9, side="left")
t = T("jamais", 472.4); c.chip("ZÉRO RÉCLAMATION", t - 0.3, t + 2.4, 90, 170, icon="check", cls="white", **L)
t = T("Cameroun,", 483.6); c.emoji("cm", t - 0.2, t + 3.2, 1330, 200, size=150, rot=-6)
t2 = T("France.", 485.7); c.emoji("fr", t2 - 0.2, t + 3.2, 1530, 200, size=150, rot=6)
t = T("police", 490.7); c.emoji("police", t - 0.3, t + 2.0, 1440, 200, size=180, rot=0)
t = T("pourtant,", 493.1); c.big("ET CE N'ÉTAIT <em>PAS ELLE.</em>", t + 0.3, t + 2.0)
t = T("retour", 498.8) if False else T("laissé,", 500.6); c.chip("J'AI LAISSÉ PASSER", t - 0.2, t + 2.4, 90, 170, icon="relieved", cls="white", **L)
t = T("collaborer", 505.6); c.emoji("handshake", t - 0.2, D - 1.0, 1440, 200, size=190, rot=0)
c.endcard("AUJOURD'HUI", "ON COLLABORE<br>TOUJOURS.", "Un malentendu n'arrête pas l'accompagnement", D - 2.2)
c.add_sfx("whoosh", 0.05, 0.25)
if __name__ == "__main__":
    if "media" in sys.argv: print(render_media(NAME, mp, D, OUT + "/assets", music_offset=200))
    print("chunks", c.build(OUT))

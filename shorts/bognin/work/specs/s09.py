"""Short 09 — « De 10 € à 2 000 € » (source 5:00 – 5:41)."""
NAME = "s09"
TITLE = "De 10 € à 2 000 €"
TRIM = True
LOCAL_REF = True
KEEP = [
    (300.25, 303.85),   # « Mais lorsque j'ai vu comment il me payait, je me suis dit : mais pourquoi pas ? »
    (304.70, 307.15),   # « Pourquoi pas essayer ? Pourquoi pas le faire, en fait ? »
    (308.85, 309.80),   # « Du coup, let's go. »
    (313.10, 315.75),   # « Je l'ai fait, j'ai pris l'accompagnement en question. »   (drops the stutter « Je je l'ai fait »)
    (316.20, 323.20),   # « J'avais encore peur… mais lorsque j'ai vu la somme qu'il m'a payée, parce que j'étais habitué à vendre les trucs à 200 euros »
    (324.05, 324.85),   # « Maximum. »
    (325.25, 334.30),   # « En fait, vu que je proposais juste les services… 5 euros, 50 euros. »
    (334.70, 341.00),   # « Bref, j'étais habitué à recevoir l'argent petit à petit… une grosse somme d'un coup de cette façon. »
]
FIX = {("pas", 304): "pas ?", ("?", 304): None, "essayer": "essayer ?", ("?", 306): None, ("fait", 307): "fait ?", ("?", 307): None,
       ("qui", 320): "qu'il", "payé": "payée,", "compte": "comptes", ("des", 332): "de", ("petit", 336): "petit à", "euros.": "euros.",
       "Maximum.": "Maximum.", "payer.": "payer", "Une": "une", ("vu.", 301): "vu", ("Comment", 302): "comment"}
KEY = ("payait,", "peur,", "somme", "200", "maximum.", "10", "5", "netflix,", "mycanal,", "50", "petit,", "grosse")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("LE DÉCLIC PRIX", "De 10 € à<br><em>2 000 €</em>", 0.15, DUR if port else 2.2)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.4, 1.7)
    c.add_sfx("whoosh", 0.05, 0.2)
    t = T("payait", 302.30); c.chip("2 000 € D'UN COUP", t - 0.2, t + 1.8, icon="money", cls="sun")
    t = T("pourquoi", 303.34); c.emoji("thinking", t - 0.1, t + 2.4, side="r", rot=6)
    t = T("let's", 309.29); c.chip("LET'S GO", t - 0.15, t + 1.2, icon="rocket", cls="")
    t = T("l'accompagnement", 314.58); c.chip("ACCOMPAGNEMENT VENDU", t - 0.2, t + 1.6, icon="check", cls="white")
    t = T("énormément", 317.84); c.emoji("sweat", T("peur", 317.04) - 0.1, t + 1.4, side="l", rot=-6)
    t = T("200", 322.48); c.chip("MAX 200 €", t - 0.1, T("Maximum", 324.16) + 0.6, icon="cart", cls="white")
    pa = T("vendais", 327.99)
    c.panel("CE QUE JE VENDAIS", [("Services à 5–10 €", T("10", 329.11) - 0.1, "cart"),
                                  ("Comptes Netflix, MyCanal", T("Netflix", 331.03) - 0.1, "tv"),
                                  ("Pages à 5–50 €", T("création", 332.15) - 0.1, "laptop")],
            pa - 0.3, T("Bref", 334.79) - 0.05)
    t = T("petit", 336.39); c.emoji("money", t - 0.2, t + 1.4, side="r", rot=-6)
    a = T("grosse", 339.16)
    c.big("2 000 €<br><em style=\"color:var(--neon)\">D'UN COUP</em>", a - 0.2, VOICE_D - 0.05, small="JE NE SAVAIS PAS")
    c.endcard("ET TOI ?", "TU VENDS<br>À QUEL PRIX ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

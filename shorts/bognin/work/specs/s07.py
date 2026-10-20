"""Short 07 — « J'avais peur de la caméra » (source 7:56 – 8:29)."""
NAME = "s07"
TITLE = "J'étais timide, j'avais peur de la caméra"
TRIM = True
LOCAL_REF = True
KEEP = [
    (476.20, 504.90),   # « J'ai lancé mon activité. Les trois premiers mois… honte de parler devant les gens. »
    (506.90, 508.75),   # « J'ai commencé à faire mes premières vidéos. »   (drops the « Mm » before it)
]
FIX = {"l'ancien": "lancé", ("trois.", 480): "trois", ("catastrophique.", 485): "catastrophiques.", "at": "à", "barne,": "banc,",
       "existait": "se disait"}
KEY = ("catastrophiques.", "peur", "regard", "caméra,", "timide,", "voisin", "filmait", "honte", "visage,", "photogénique,", "vidéos.")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("AVANT LES VUES", "J'avais peur<br>de la <em>caméra</em>", 0.15, DUR if port else 2.4)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.4, 1.7)
    c.add_sfx("whoosh", 0.05, 0.2)
    t = T("activité", 477.59); c.chip("LE LANCEMENT", t - 0.3, t + 1.2, icon="rocket", cls="white")
    t = T("catastrophiques", 482.33); c.stamp("CATASTROPHE", t - 0.05, t + 1.6)
    t = T("catastrophique", 484.94); c.emoji("sweat", t - 0.2, t + 1.3, side="r", rot=6)
    a = T("Déjà", 486.28); c.mood(a, T("J'ai", 507.08) - 0.1, gray=0.75)
    c.panel("J'AVAIS PEUR", [("Du regard des autres", T("regard", 487.56) - 0.1, "eyes"),
                             ("De la caméra", T("caméra", 489.48) - 0.1, "camera"),
                             ("Toujours timide", T("timide", 490.52) - 0.1, "seeno")],
            a - 0.1, T("j'étais", 491.16) + 0.2)
    t = T("l'école", 491.96); c.emoji("grad", t - 0.2, t + 1.8, side="r", rot=-6)
    t = T("voisin", 493.40); c.chip("MUET À L'ÉCOLE", t - 0.2, t + 1.4, icon="books", cls="dark")
    t = T("communiquait", 495.40); c.emoji("mask", t - 0.1, t + 1.3, side="l", rot=6)
    t = T("filmait", 497.40); c.chip("JAMAIS FILMÉ", t - 0.2, t + 1.3, icon="camera", cls="dark")
    t = T("visage", 499.32); c.emoji("seeno", T("honte", 498.68) - 0.1, t + 1.2, side="r", rot=-4)
    t = T("photogénique", 501.16); c.chip("« PAS PHOTOGÉNIQUE »", t - 0.3, t + 1.3, icon="cross", cls="red")
    t = T("parler", 503.64); c.emoji("mic", t - 0.2, min(t + 1.4, T("J'ai", 507.08) - 0.2), side="l", rot=6)
    a = T("J'ai", 507.08); c.big("MES PREMIÈRES<br><em>VIDÉOS</em>" if not port else "MES<br>PREMIÈRES<br><em>VIDÉOS</em>",
                                 a - 0.05, VOICE_D - 0.05, small="ET POURTANT…")
    c.endcard("ET TOI ?", "QU'EST-CE QUI<br>TE BLOQUE ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

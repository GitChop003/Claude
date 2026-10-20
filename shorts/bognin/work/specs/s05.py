"""Short 05 — « 800 000 vues = 0 client, 500 vues = mes meilleurs clients » (source 20:41 – 21:37)."""
NAME = "s05"
TITLE = "800 000 vues, presque 0 client"
TRIM = True
KEEP = [
    (1241.30, 1247.40),   # « Mon post qui a fait le plus de vues sur Instagram a pratiquement 800 000 vues. Mais après combien de temps ? »
    (1248.90, 1251.90),   # « Et est-ce que ce post-là m'a même rapporté vraiment des clients ? »
    (1252.45, 1256.95),   # « Le post qui m'a le plus rapporté de clients sur LinkedIn, c'est un post qui a fait 500 vues. »
    (1262.70, 1265.46),   # « Pourtant, le post qui avait fait pratiquement 800 000 vues »
    (1266.18, 1269.70),   # « ne m'a même pas rapporté trois conversations en DM. »   (spliced « ne|ne »: drops the false start « ne m'a rapporté »)
    (1271.90, 1281.60),   # « Une façon de vous dire… arrêtez de traquer les mauvaises métriques… ça ne compte pas. »
    (1282.70, 1283.78),   # « Ce qui vous importe »
    (1287.10, 1293.10),   # « le nombre de conversations démarrées, le nombre de calls bookés, le ratio… le cash collecté. »
    (1294.60, 1297.30),   # « C'est sur ça que vous devez vous concentrer. »
]
FIX = {"poste": "post", "posté": "post", "Linzing": "LinkedIn,", ("à", 1269): "en", "Dem.": "DM.", "call": "calls", "bouclés,": "bookés,",
       "800": "800 000", "000": None, "temps": "temps ?", "?": None, ("clients", 1251): "clients ?", "importe": "importe :",
       "rapporté.": "rapporté"}
KEY = ("800", "500", "clients", "clients ?", "dm.", "mauvaises", "métriques.", "compte", "conversations", "bookés,", "cash", "concentrer.")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("LA VÉRITÉ SUR LES VUES", "800 000 vues,<br>presque <em>0 client</em>", 0.15, DUR if port else T("Mais", 1245.99) - 0.2)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.5, 2.9)
    c.add_sfx("whoosh", 0.05, 0.2)
    t = T("Instagram", 1243.19); c.logos([("instagram", t - 0.1)], t + 2.2, y=520 if port else None)
    t = T("800", 1244.47); c.chip("800 000 VUES", t - 0.15, t + 1.6, icon="eyes", cls="white")
    t = T("combien", 1246.39); c.emoji("clock", t - 0.2, t + 1.8, side="l", rot=-6)
    t = T("clients", 1251.16); c.emoji("thinking", T("rapporté", 1250.36) - 0.1, t + 1.0, side="r", rot=6)
    t = T("LinkedIn", 1254.76); c.logos([("linkedin", t - 0.1)], T("500", 1255.96) + 1.4, y=520 if port else None)
    t = T("500", 1255.96); c.chip("500 VUES = MES MEILLEURS CLIENTS", t - 0.1, t + 1.8, icon="trophy", cls="sun")
    pa = T("Pourtant", 1262.88)
    c.panel("LE BILAN", [("800 000 vues → pas 3 DM", T("trois", 1267.58) - 0.15, "cross"),
                         ("500 vues → mes meilleurs clients", T("conversations", 1268.06) + 0.5, "check")],
            pa - 0.15, T("Une", 1272.11) - 0.1)
    t = T("mauvaises", 1276.11); c.stamp("MAUVAISES MÉTRIQUES", t - 0.15, t + 1.3)
    pa = T("Le", 1276.83)
    c.panel("ÇA NE COMPTE PAS", [("Les vues", T("vues", 1277.31) - 0.1, "eyes"), ("Les likes", T("likes", 1278.19) - 0.1, "heart"),
                                ("Les commentaires", T("commentaires", 1279.47) - 0.1, "speech")],
            pa - 0.15, T("Ce", 1282.83) - 0.1)
    pa = T("Ce", 1282.83)
    c.panel("CE QUI COMPTE", [("Conversations démarrées", T("conversations", 1287.60) - 0.1, "speech"),
                             ("Calls bookés", T("call", 1289.36) - 0.1, "call"),
                             ("Ratio vues → cash", T("ratio", 1290.32) - 0.1, "money")],
            pa - 0.1, T("C'est", 1294.73) - 0.1)
    t = T("concentrer", 1295.85); c.chip("CONCENTRE-TOI LÀ-DESSUS", T("C'est", 1294.73) - 0.05, VOICE_D - 0.05, icon="target", cls="sun")
    c.endcard("ET TOI ?", "QUELLE EST TA<br>VRAIE MÉTRIQUE ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

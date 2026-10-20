"""Bonus 13-14 — « Coach niveau 5 ou niveau 100 ? » (les gros coachs vendent leur image) (source 36:42 – 37:57)."""
NAME = "s13"
TITLE = "Coach niveau 5 ou niveau 100 ?"
TRIM = True
LOCAL_REF = True
KEEP = [
    (2202.25, 2205.00),   # « Mais aussi, lorsque vous vous lancez sur les réseaux sociaux, »
    (2206.05, 2218.60),   # « je préfère que vous preniez une personne… au niveau 5… L'avantage… il apprend la base avec vous. »
    (2221.70, 2233.95),   # « Parce que les coachs qui font des gros chiffres d'affaires… bref, leurs environnements. »
    (2238.60, 2242.30),   # « Vous achetez chez eux parce que vous voulez vous vanter d'avoir leur numéro. Vous achetez chez eux »
    (2243.33, 2246.40),   # « parce que vous êtes blasés par leur montre, par leur Rolex, par le lifestyle. »  (spliced « parce|parce »: drops « vous êtes là »)
    (2249.80, 2251.78),   # « Or lorsque vous achetez un coach qui vous dépasse »
    (2253.15, 2261.55),   # « du niveau cinq ou du niveau dix, vous l'achetez parce que vous aimez son process… pour son expertise, en gros. »
    (2262.00, 2265.75),   # « Et ce type de coach-là prend énormément le temps à vous comprendre. »
    (2274.55, 2277.00),   # « il prend le temps de vraiment s'ancrer dans votre activité. »
]
FIX = {"lorsqu'on": "lorsque vous", ("vous", 2203): "vous", "lance": "lancez", ("sociaux.", 2205): "sociaux,", ("Je", 2206): "je",
       ("5.", 2209): "5. Peut-être que vous pouvez", "cette": "ce type de", "depuis": "plus", ("leur", 2229): "leur Rolex, leur",
       "loup": "luxe,", ("achetez", 2239): "Vous achetez", ("leurs", 2228): "leur", ("voiture", 2231): "voiture,", "Bref,": "bref,", "que": "que", ("que", 2240.48): "d'avoir", ("vous", 2240.56): None,
       ("avez", 2240.64): None, ("numéro", 2241): "numéro.", ("vous", 2241.44): "vous", ("Du", 2253): "du", "suitez": "suivez", ("la", 2259): "le",
       "couche": "coach-là", ("là.", 2263): "prend", "ancrer": "entrer", ("comprendre", 2265): "comprendre.", ("il", 2275): "Il",
       "images": "image,", "blasé": "blasés", ("le", 2246): "leur", ("Parce", 2222): "Parce", ("personne,", 2216): "personne,"}
KEY = ("niveau", "5.", "cinq", "dix.", "base", "image,", "rolex,", "luxe,", "lifestyle.", "process.", "méthode,", "expertise,", "comprendre.", "activité.")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("BIEN CHOISIR SON COACH", "Niveau 5<br>ou niveau <em>100</em> ?", 0.15, DUR if port else 2.6)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.4, 1.7)
    c.add_sfx("whoosh", 0.05, 0.2)
    pa = T("préfère", 2206.28)
    c.panel("LE BON ÉCART", [("Toi : niveau 1", T("actuellement", 2212.38) - 0.6, "grad"),
                             ("Ton coach : niveau 5 à 10", T("cinq", 2213.90) - 0.2, "rocket")],
            T("niveau", 2208.92) - 0.2, T("L'avantage", 2215.59) - 0.1)
    t = T("base", 2217.75); c.chip("IL APPREND LA BASE AVEC TOI", T("L'avantage", 2215.59) - 0.05, t + 1.2, icon="books", cls="white")
    t = T("gros", 2222.99); c.chip("LES GROS CHIFFRES D'AFFAIRES…", t - 0.3, T("ils", 2227.29) - 0.1, icon="money", cls="sun")
    pa = T("ils", 2227.29)
    c.panel("…TE VENDENT", [("Leur image", T("image", 2228.09) - 0.1, "camera"), ("Leur Rolex", pa + 1.6, "clock"),
                            ("Voiture, maison de luxe", T("maison", 2231.29) - 0.1, "sparkles"),
                            ("Leur lifestyle", T("lifestyle", 2245.83) - 0.2, "star")],
            pa - 0.1, T("Or", 2249.88) - 0.15)
    t = T("numéro", 2241.04); c.emoji("phone", t - 0.2, t + 1.4, side="r", rot=-6)
    t = T("Rolex", 2245.11); c.emoji("eyes", T("blasés", 2243.83) - 0.1, t + 0.9, side="l", rot=6)
    pa = T("process", 2256.16)
    c.panel("NIVEAU 5–10 : TU ACHÈTES", [("Son process", pa - 0.15, "chart"), ("Sa méthode", T("méthode", 2258.42) - 0.1, "bulb"),
                                         ("Son expertise", T("expertise", 2260.34) - 0.1, "target")],
            T("l'achetez", 2254.96) - 0.1, T("Et", 2262.10) - 0.1)
    t = T("comprendre", 2265.09); c.chip("IL PREND LE TEMPS DE TE COMPRENDRE", T("énormément", 2263.65) - 0.2, t + 0.8, icon="clock", cls="white")
    t = T("activité", 2276.79); c.emoji("handshake", T("Il", 2274.63) - 0.1, VOICE_D - 0.05, side="r", rot=0)
    c.endcard("ET TOI ?", "TU SUIS QUEL<br>NIVEAU DE COACH ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

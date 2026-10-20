"""Short 04 — « 3 mois catastrophiques, puis le déclic » (source 11:07 – 13:19)."""
NAME = "s04"
TITLE = "3 mois catastrophiques, puis le déclic"
TRIM = True
KEEP = [
    (667.53, 687.30),   # « Mes trois premiers mois… ne performaient pas vraiment. Le soutien… ça n'allait pas. Du coup, j'ai dû me battre contre moi-même. »
    (689.60, 707.00),   # « Après trois mois, j'ai commencé à évoluer… plus sur mon avatar client. »   (drops the false start « Après j'ai vu que »)
    (709.85, 718.65),   # « J'ai refait ma promesse… c'était plutôt la façon de faire, la façon de travailler »
    (726.90, 735.60),   # « Ça m'épuisait déjà… sur TikTok et Instagram. »
    (736.90, 748.60),   # « LinkedIn… on me bannit. »
    (756.20, 767.50),   # « Et pour une personne qui vient de connaître les codes… à te bannir. »
    (770.52, 773.00),   # « Je comprenais pas, je voulais abandonner. »
    (773.90, 777.50),   # « Il m'a fallu un an pour avoir 1000 abonnés sur LinkedIn. Aujourd'hui, je suis à 2000 abonnés. »
    (785.65, 789.05),   # « Mais il m'a fallu encore un mois pour avoir 1000 abonnés. »
    (789.93, 791.40),   # « Lorsque j'ai compris vraiment le code »   (drops a long « euh » before it)
    (793.57, 799.20),   # « Je reviens sur ça pour vous montrer… ce qui ne marche pas. »
]
FIX = {"démarques": "demandes", "d'un": "en", "démarrés.": "demandes.", "reussis": "réussis", ("like", 746): "likes",
       "emotionnel,": "émotionnel,", "my": "ma", "family": "famille", "or": "ou", "auto,": "autre,", "types": None, "code": "codes",
       ("cours", 791): "code.", "poste": "post", "1000": "1 000", "2000": "2 000", "10": "10 000", "000": None,
       "Client,": None, "Be": None, "young.": None, ("coup,", 668): None, "morale.": "moral,", "siècle": "cercle",
       ("n'est", 671): "ne", ("pas...", 671): "performaient", ("Mais", 672): None, ("faut", 672): None, ("mais", 672): None,
       ("travailler", 718): "travailler.", "L'indicine": "LinkedIn,", ("j'ai", 738): "j'ai fait", ("soit.", 676): "soit", ("systèmes.", 703): "systèmes,", ("Même", 680): "même",
       ("autre", 719): None, ("chose.", 719): None}
KEY = ("catastrophiques.", "soutien", "moi-même.", "demandes", "systèmes", "promesse", "positionnement", "problème", "façon",
       "trois", "bannit.", "bannir", "démoralisant.", "abandonner.", "an", "mois", "code.", "marche", "linkedin")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("LES COULISSES", "3 mois de galère<br>avant le <em>déclic</em>", 0.15, DUR if port else T("Le", 674.07) - 0.2)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.4, 1.75)
    c.add_sfx("whoosh", 0.05, 0.2)
    # struggle
    t = T("catastrophiques", 669.37); c.stamp("CATASTROPHE", t - 0.05, t + 1.6)
    t = T("performaient", 671.21); c.emoji("sweat", t - 0.1, t + 1.6, side="r", rot=6)
    pa = T("soutien", 675.19)
    c.panel("ZÉRO SOUTIEN", [("Financier", T("financier", 676.75) - 0.1, "money"), ("Émotionnel", T("émotionnel", 677.71) - 0.1, "heart"),
                             ("Moral", T("moral", 678.83) - 0.1, "brain"), ("Mes proches", T("famille", 681.58) - 0.1, "handshake")],
            pa - 0.2, T("Du", 683.4) - 0.05)
    t = T("battre", 684.02); c.chip("SEUL CONTRE MOI-MÊME", t - 0.2, t + 1.8, icon="muscle", cls="dark")
    # first signs
    t = T("Après", 689.77); c.chip("APRÈS 3 MOIS…", t - 0.1, t + 2.0, icon="calendar", cls="white")
    t = T("demandes", 693.13); c.emoji("mail", t - 0.1, t + 2.6, side="r", rot=-6)
    t = T("pourquoi", 696.30); c.emoji("thinking", t - 0.1, t + 1.8, side="l", rot=6)
    pa = T("analyser", 699.83)
    c.panel("J'AI ANALYSÉ", [("Analyser", pa - 0.1, "chart"), ("Traquer", T("traquer", 700.39) - 0.1, "eyes"),
                             ("Mettre des systèmes", T("systèmes", 702.79) - 0.25, "laptop"), ("Mon avatar client", T("avatar", 704.67) - 0.2, "target")],
            pa - 0.3, T("refait", 710.16) - 0.3)
    pa = T("refait", 710.16)
    c.panel("J'AI REFAIT", [("Ma promesse", T("promesse", 710.64) - 0.1, "handshake"), ("Mon positionnement", T("positionnement", 711.84) - 0.1, "target")],
            pa - 0.15, T("Après", 714.11) - 0.1)
    a = T("Après", 714.11); b = T("c'était", 716.27) + 0.1
    c.big("LE PROBLÈME,<br>CE N'ÉTAIT PAS <em>MOI</em>" if not port else "LE PROBLÈME,<br>CE N'ÉTAIT<br>PAS <em>MOI</em>", a - 0.05, b, small="J'AI COMPRIS QUE")
    t = T("façon", 716.83); c.chip("C'ÉTAIT LA FAÇON DE FAIRE", t - 0.1, T("travailler", 718.11) + 0.6, icon="bulb", cls="sun")
    # grind + bans
    t = T("trois", 730.39); c.chip("3 POSTS PAR JOUR", t - 0.1, t + 2.2, icon="calendar", cls="white")
    c.logos([("tiktok", T("TikTok", 733.23) - 0.1), ("instagram", T("Instagram", 733.87) - 0.1), ("linkedin", T("LinkedIn", 737.1) - 0.1)],
            T("mois", 739.78) - 0.15)
    t = T("mois", 739.78); c.chip("1 MOIS = 1 LIKE", t - 0.1, t + 1.9, icon="heart", cls="white")
    t = T("Deux", 741.88); c.chip("2 MOIS = 1 LIKE", t - 0.1, T("explose", 744.92) - 0.1, icon="heart", cls="white")
    t = T("explose", 744.92); c.emoji("fire", t - 0.1, t + 2.0, side="r", rot=-6)
    t = T("impressions", 747.08); c.chip("10 000 IMPRESSIONS", T("10", 746.60) - 0.15, T("bannit", 747.72) - 0.05, icon="rocket", cls="")
    t = T("bannit", 747.72); c.stamp("BANNI", t - 0.05, t + 1.6)
    t = T("bannir", 759.95); c.chip("BANNI 4 FOIS", t - 0.2, t + 2.6, icon="lock", cls="red")
    a = T("démoralisant", 760.99); c.mood(a - 0.2, T("Il", 773.98) - 0.1)
    c.emoji("sob", a - 0.1, a + 2.4, side="l", rot=6)
    t = T("abandonner", 771.64); c.chip("J'AI VOULU ABANDONNER", t - 0.3, t + 1.6, icon="cross", cls="dark")
    # turning point
    t = T("an", 774.54); c.chip("1 AN → 1 000 ABONNÉS", t - 0.2, T("Aujourd'hui", 776.30) - 0.05, icon="calendar", cls="white")
    t = T("Aujourd'hui", 776.30); c.chip("AUJOURD'HUI : 2 000", t - 0.1, t + 1.9, icon="trophy", cls="sun")
    c.logos([("linkedin", t)], t + 1.9, y=520 if port else None)
    a = T("encore", 786.51); b = T("compris", 790.71) - 0.05
    c.big("+1 000 EN<br><em>1 MOIS</em>", a - 0.1, b, small="QUAND J'AI COMPRIS")
    t = T("code", 791.27); c.chip("LE CODE", t - 0.15, t + 1.5, icon="bulb", cls="sun")
    # closing
    t = T("marche,", 796.41); c.chip("CE QU'ON VOUS MONTRE", t - 0.15, VOICE_D - 0.05, icon="check", cls="white")
    t = T("ne", 797.93); c.chip("CE QU'ON VOUS CACHE", t - 0.1, VOICE_D - 0.05, icon="cross", cls="red", y=(490 if port else 170))
    c.endcard("ET TOI ?", "TU EN ES<br>À QUEL MOIS ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

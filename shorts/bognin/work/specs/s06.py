"""Short 06 — « Ma pire erreur : recruter mes amis » (source 13:54 – 16:46)."""
NAME = "s06"
TITLE = "Ma pire erreur : recruter mes amis"
TRIM = True
KEEP = [
    (834.40, 840.85),    # « Du coup je me suis dit : ah ok, pourquoi pas recruter. Très grosse, très mauvaise erreur. »
    (843.73, 850.75),    # « C'est l'erreur qui m'a coûté le plus cher sur Instagram. Pas seulement… sur tous mes réseaux sociaux. »
    (851.25, 864.70),    # « Pourquoi ? Parce que j'étais débutant… J'ai recruté uniquement mes amis. Le monteur vidéo… le montage. »
    (865.30, 868.30),    # « J'ai délégué le setting à deux autres de mes amis. »
    (869.92, 871.70),    # « ils ne connaissaient pas le setting. »   (drops « Ils ne connaissaient non plus »)
    (897.50, 901.70),    # « Mais à partir d'un mois, ils ont commencé à avoir des problèmes. »
    (906.85, 915.40),    # « Parfois, ils écrivaient aux prospects… du coup ils se démoralisaient. »
    (929.90, 937.60),    # « On dit souvent… pour ses compétences. Moi, j'ai recruté des amis parce que je voulais aider des amis. »
    (976.10, 978.10),    # « Du coup, je les ai retirés de la team. »
    (980.70, 981.95),    # « Ça m'a tellement démoralisé. »
    (982.75, 987.45),    # « J'ai fait pratiquement encore peut-être trois mois, ou deux mois sans poster. »
    (997.25, 1000.85),   # « Lorsque vous lancez une activité en ligne, ne comptez pas sur vos amis. »
    (1002.25, 1006.47),  # « Je préfère encore que vous payiez cher une personne qui maîtrise cette compétence »
]
FIX = {"Setsine": "setting", "bloquer": "booker", "col,": "call,", "l'apprendre": "lui apprendre", "payez": "payiez",
       ("Pourquoi", 851): "Pourquoi ?", ("?", 852): None, "ok.": "OK,", ("recruter", 837): "recruter ?", "Avoir": "avoir",
       ("compétence", 1006): "compétence.", ("très", 838): "Très", ("Pourquoi", 837): "pourquoi", ("temps.", 862): "temps",
       ("Pour", 863): "pour", ("ils", 870): "Ils", ("mois.", 985): "mois,", ("Ou", 986): "ou", "donc": None}
KEY = ("erreur.", "cher", "amis.", "ami.", "compétences", "setting.", "problèmes.", "démoralisaient.", "team.", "démoralisé.",
       "poster.", "amis", "maîtrise")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("MA PIRE ERREUR", "J'ai recruté<br>mes <em>amis</em>", 0.15, DUR if port else 2.4)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.4, 1.9)
    c.add_sfx("whoosh", 0.05, 0.2)
    t = T("recruter", 837.43); c.emoji("bulb", t - 0.15, t + 1.3, side="r", rot=-6)
    t = T("grosse", 838.71); c.stamp("GROSSE ERREUR", t - 0.1, T("c'est", 843.80) - 0.1)
    t = T("cher", 845.32); c.chip("L'ERREUR LA PLUS CHÈRE", t - 0.2, t + 2.0, icon="money", cls="red")
    t = T("tous", 849.61); c.logos([("tiktok", t - 0.1), ("instagram", t + 0.05), ("linkedin", t + 0.2)], t + 1.6)
    t = T("débutant", 852.14); c.emoji("grad", t - 0.1, t + 1.6, side="l", rot=-8)
    t = T("uniquement", 854.22); c.chip("UNIQUEMENT MES AMIS", t - 0.15, t + 1.8, icon="handshake", cls="sun")
    pa = T("monteur", 855.58)
    c.panel("MON ÉQUIPE", [("Monteur : mon ami", pa - 0.1, "film"),
                           ("Setters : 2 amis", T("délégué", 865.63) - 0.1, "phone")],
            pa - 0.25, T("setting", 871.19) + 0.7)
    t = T("compétences", 858.95); c.stamp("ZÉRO COMPÉTENCE", t - 0.1, t + 1.7)
    t = T("partir", 897.90); c.chip("APRÈS 1 MOIS…", t - 0.2, t + 2.2, icon="calendar", cls="white")
    pa = T("prospects", 908.06)
    c.panel("LES PROBLÈMES", [("Prospects sans réponse", T("répondaient", 908.94) - 0.1, "seeno"),
                              ("Aucun call booké", T("bloquer", 911.66) - 0.1, "call"),
                              ("Aucun nouveau client", T("signer", 913.02) - 0.1, "cross"),
                              ("Équipe démoralisée", T("démoralisaient", 914.86) - 0.1, "sob")],
            pa - 0.3, T("On", 929.96) - 0.15)
    a = T("On", 929.96); b = T("Moi", 934.76) - 0.15
    c.big("ON RECRUTE POUR<br>LES <em>COMPÉTENCES</em>" if not port else "ON RECRUTE<br>POUR LES<br><em style=\"font-size:.8em\">COMPÉTENCES</em>", a - 0.05, b,
          small="LA RÈGLE")
    t = T("aider", 936.68); c.chip("MOI : POUR AIDER MES AMIS", T("Moi", 934.76) - 0.05, t + 1.0, icon="heart", cls="white")
    t = T("retirés", 977.29); c.chip("RETIRÉS DE LA TEAM", t - 0.2, t + 1.6, icon="cross", cls="dark")
    a = T("tellement", 981.27); c.mood(a - 0.4, T("Lorsque", 997.32) - 0.1)
    c.emoji("sob", a - 0.2, a + 1.8, side="l", rot=6)
    t = T("trois", 984.43); c.chip("2 À 3 MOIS SANS POSTER", t - 0.2, T("poster", 987.16) + 0.6, icon="calendar", cls="dark")
    a = T("ne", 999.40); b = T("Je", 1002.35) - 0.1
    c.big("NE COMPTEZ PAS<br>SUR VOS <em>AMIS</em>" if not port else "NE COMPTEZ<br>PAS SUR<br>VOS <em>AMIS</em>", a - 0.1, b, small="LANCER EN LIGNE ?")
    t = T("payez", 1003.55); c.chip("PAYEZ CHER UN EXPERT", t - 0.15, VOICE_D - 0.05, icon="money", cls="sun")
    c.endcard("ET TOI ?", "TU AS RECRUTÉ<br>TES AMIS ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

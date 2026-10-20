"""Bonus 24 — « Mon premier client : un élève français sur Telegram » (source 3:26 – 4:54)."""
NAME = "s24"
TITLE = "Mon premier client en accompagnement"
TRIM = True
LOCAL_REF = True
KEEP = [   # range ends sit on the next speech segment's start; TRIM tightens them onto the voice
    (207.05, 209.55),   # « J'ai eu beaucoup de problèmes, »   (drops « Euh »)
    (209.55, 214.78),   # « que ce soit à l'école, que ce soit dans mes business et autres, j'ai lancé énormément de projets. »
    (214.78, 218.42),   # « J'ai lancé la vente de connexion Internet dans toute ma ville. »
    (218.42, 223.30),   # « J'ai lancé la création des sites web… avec les formations à vendre. »
    (226.30, 228.15),   # « J'ai fait du e-commerce. »   (drops « J'ai fait des »)
    (230.95, 233.05),   # « En ligne, j'ai formé des gens. »
    (234.15, 235.85),   # « J'ai fait du trading. »
    (236.05, 237.85),   # « J'ai fait de la crypto. »
    (237.90, 241.92),   # « En fait, j'ai énormément fait de choses, et les choses que j'ai faites ont échoué »
    (245.70, 251.75),   # « Mais au fur et à mesure… pourquoi tu ne te professionnalises pas ? »
    (251.90, 260.60),   # « Et je n'avais pas vraiment pensé à ça. Du coup, j'ai continué… c'était sur Telegram. »
    (262.90, 268.60),   # « Il m'a contacté, il m'a dit : je ne veux pas acheter l'un de tes services. Je veux un accompagnement chez toi. »
    (270.40, 272.95),   # « La première fois même que je pense aux accompagnements, en fait. »
    (288.15, 294.05),   # « Et à la fin de l'accompagnement, il m'a dit : professionnalise-toi, tu as un très gros potentiel. »
]
FIX = {"Euh": None, "banque": "vente", "faux,": "fort,", "professionises": "professionnalises", ("pas", 250.57): "pas ?", ("?", 250.65): None,
       ("tombé", 257.14): "Je suis tombé", ("la", 288.36): "à la", ("la", 288.68): None, "compagnie": "l'accompagnement,",
       "profise-toi,": "professionnalise-toi,", ("la", 270.52): "La", ("échoué", 241.43): "échoué.", ("fait", 272.44): "fait.", ("du", 272.68): None, ("coup", 272.76): None, ("m'a", 289.48): "il m'a",
       ("problèmes.", 208.09): "problèmes,", ("soit", 209.96): "que ce soit"}
KEY = ("problèmes,", "projets.", "internet", "web", "e-commerce.", "trading.", "crypto.", "échoué.", "fort,", "professionnalises",
       "telegram.", "accompagnement", "potentiel.")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("MON PREMIER CLIENT", "« Je veux un<br><em>accompagnement</em> »", 0.15, DUR if port else 2.0)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.3, 1.6)
    c.add_sfx("whoosh", 0.05, 0.2)
    pa = T("projets", 214.0)
    c.panel("J'AI TOUT ESSAYÉ", [("Connexion Internet", T("connexion", 216.0) - 0.2, "globe"), ("Sites web", T("sites", 220.0) - 0.2, "laptop"),
                                 ("E-commerce", T("e-commerce", 226.95) - 0.3, "cart"), ("Former en ligne", T("formé", 232.0) - 0.3, "grad"),
                                 ("Trading", T("trading", 234.88) - 0.3, "chart"), ("Crypto", T("crypto", 236.8) - 0.3, "money")],
            pa - 0.3, T("En", 237.99) + 0.5)
    t = T("échoué", 241.43); c.stamp("ÉCHEC", t - 0.1, t + 1.2)
    t = T("professionnalises", 249.85); c.chip("« PROFESSIONNALISE-TOI »", t - 0.3, t + 1.6, icon="speech", cls="white")
    t = T("pensé", 253.0); c.emoji("thinking", t - 0.3, t + 1.4, side="r", rot=6)
    t = T("français", 258.02); c.emoji("fr", t - 0.3, t + 2.6, side="l", rot=-6)
    t = T("Telegram", 260.0); c.chip("UN ÉLÈVE FRANÇAIS, SUR TELEGRAM", T("Il", 258.8) - 0.1, t + 1.0, icon="phone", cls="sky")
    t = T("services", 265.8); c.chip("PAS UN SERVICE…", t - 0.3, t + 1.0, icon="cross", cls="dark")
    a = T("accompagnement", 267.5)
    c.big("« JE VEUX UN<br><em style=\"color:var(--neon)\">ACCOMPAGNEMENT</em> »" if not port else "« JE VEUX UN<br><em style=\"color:var(--neon);font-size:.7em\">ACCOMPAGNEMENT</em> »",
          T("Je", 266.7) - 0.1, T("La", 270.52) - 0.1)
    t = T("pense", 271.24); c.emoji("bulb", t - 0.2, t + 1.5, side="r", rot=-6)
    t = T("potentiel", 292.84); c.chip("TU AS UN TRÈS GROS POTENTIEL", T("tu", 291.72) - 0.1, VOICE_D - 0.05, icon="rocket", cls="sun")
    c.emoji("sparkles", T("professionnalise-toi", 289.88) - 0.1, VOICE_D - 0.05, side="r", rot=6)
    c.endcard("ET TOI ?", "TU TE<br>PROFESSIONNALISES ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

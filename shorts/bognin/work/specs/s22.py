"""Bonus 22 — « J'ai raté mon voyage, puis mon bac » (le moment où tout bascule) (source 6:25 – 7:10)."""
NAME = "s22"
TITLE = "J'ai tout perdu, puis j'ai décidé de me lancer"
TRIM = True
LOCAL_REF = True
KEEP = [
    (385.95, 388.40),   # « Mais j'avais encore peur de me lancer, c'est le mot. »
    (393.45, 397.40),   # « J'avais un voyage d'affaires que je devais faire et j'ai raté mon voyage. »
    (399.85, 402.15),   # « La personne qui s'occupait de mes dossiers avait fait une erreur. »   (drops the false start)
    (403.90, 405.30),   # « Une semaine après, »
    (406.85, 408.75),   # « je rate encore mon examen, c'est-à-dire le bac. »
    (408.85, 418.30),   # « Du coup, je suis entré dans une… dépression pas possible… qu'est-ce que je veux faire de ma vie, »
    (419.45, 424.60),   # « qu'actuellement je viens pratiquement de tout perdre. OK, maintenant, qu'est-ce que je dois faire ? »
    (425.95, 430.30),   # « Cet élève français encore, qui était dans mes oreilles, me dit : vas-y, professionnalise-toi. »
]
FIX = {("lancer,", 387.02): "lancer,", ("c'est", 387.66): "officiellement.", ("le", 387.74): None, ("mot.", 387.90): None, "heureuse.": "erreur.", ("personne", 399.82): "La personne", ("après.", 404.48): "après,", ("Et", 406.99): None,
       ("suis", 407.23): "échoué", ("je", 407.07): "j'ai", "bas.": "bac.", "ancré": "entré", "une...": "une…", "informé": "enfermé", ("entre", 427.93): None,
       "professionnalise": "professionnalise-toi.", "toi.": None, ("que", 419.78): "vu", "actuellement": "qu'actuellement",
       "Ok,": "OK,", "vie.": "vie,", ("dépression", 413.07): "dépression,", ("semaines", 414.91): "semaines,", "faire": "faire",
       ("faire", 424.03): "faire ?", ("?", 424.11): None, ("qu'est", 416.82): "qu'est-ce", ("ce", 417.06): None, ("possible", 411.87): "possible,"}
KEY = ("peur", "voyage.", "erreur.", "bac.", "dépression", "chambre", "vie.", "perdre.", "professionnalise-toi.")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("LE TOURNANT", "J'ai tout perdu,<br>puis je me suis <em>lancé</em>", 0.15, DUR if port else 2.3)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.4, 1.7)
    c.add_sfx("whoosh", 0.05, 0.2)
    t = T("peur", 386.6); c.emoji("sweat", t - 0.2, t + 1.5, side="r", rot=6)
    t = T("voyage", 397.0); c.chip("VOYAGE D'AFFAIRES RATÉ", T("raté", 396.6) - 0.2, t + 1.4, icon="cross", cls="red")
    t = T("dossiers", 400.78); c.emoji("memo", t - 0.2, t + 1.3, side="l", rot=-6)
    t = T("après", 404.48); c.chip("UNE SEMAINE APRÈS…", T("Une", 404.00) - 0.1, t + 1.1, icon="calendar", cls="white")
    t = T("bac", 408.51); c.stamp("BAC RATÉ", t - 0.2, t + 1.4)
    a = T("Du", 408.96); c.mood(a - 0.2, T("Cet", 426.09) - 0.1, gray=0.85)
    t = T("chambre", 414.0); c.chip("2 SEMAINES ENFERMÉ", t - 0.3, t + 1.6, icon="moon", cls="dark")
    t = T("vie", 417.6); c.emoji("thinking", T("question", 416.4) - 0.2, t + 1.0, side="r", rot=6)
    a = T("perdre", 421.5)
    c.big("J'AVAIS<br>PRESQUE <em>TOUT PERDU</em>" if not port else "J'AVAIS<br>PRESQUE<br><em>TOUT PERDU</em>", T("pratiquement", 420.9) - 0.2, T("OK", 422.59) - 0.1)
    t = T("français", 426.73); c.emoji("fr", t - 0.2, t + 2.2, side="l", rot=-6)
    t = T("professionnalise-toi", 428.97); c.chip("« VAS-Y, PROFESSIONNALISE-TOI »", T("vas-y", 428.65) - 0.15, VOICE_D - 0.05, icon="rocket", cls="sun")
    c.endcard("ET TOI ?", "QUEL A ÉTÉ<br>TON DÉCLIC ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

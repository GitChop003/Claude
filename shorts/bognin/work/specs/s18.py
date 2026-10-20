"""Bonus 18-19 — « Bossez, soyez obsédés… et ne déléguez pas trop vite » (source 41:32 – 42:05)."""
NAME = "s18"
TITLE = "Bossez, puis maîtrisez avant de déléguer"
TRIM = True
LOCAL_REF = True
KEEP = [
    (2491.90, 2493.60),   # « Donc bossez, les amis. »
    (2494.15, 2496.30),   # « Soyez obsédés par ce que vous faites. »
    (2496.45, 2502.85),   # « Et ne bossez pas juste pour bosser. Remettez-vous en question… pourquoi ça a marché, »
    (2503.25, 2506.90),   # « pourquoi ça n'a pas marché, essayez d'ajuster, essayez d'améliorer. »
    (2507.40, 2508.90),   # « Et ne déléguez pas trop vite. »   (drops the repetition)
    (2511.20, 2521.70),   # « Apprenez une compétence avant de la déléguer… avant de la déléguer. »
    (2522.80, 2525.10),   # « Et vous allez voir, ça va faire toute la différence. »
]
FIX = {("Vous", 2494): "Bossez, soyez", "obsédé": "obsédés", "cherchant": "cherchez", ("ça", 2503.82): "pourquoi ça n'a", "essayer": "essayez",
       "Apprenons": "Apprenez", ("ça", 2515.03): "à", "100%.": "100 %.", ("quatre", 2516.82): "80 %", ("vingt", 2516.98): None,
       ("pour", 2517.22): None, ("cent", 2517.38): None, ("les", 2520.82): "la", ("les", 2512.79): "la", ("marché.", 2502.20): "marché,", ("marché", 2504.14): "marché,",
       ("d'ajuster", 2504.78): "d'ajuster,", "d'améliorer": "d'améliorer.", ("essayer", 2504.46): "essayez", ("essayer", 2505.58): "essayez"}
KEY = ("bossez", "obsédés", "question,", "marché,", "ajuster,", "améliorer.", "déléguez", "vite.", "compétence", "maîtrisez", "différence.")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("MES CONSEILS", "Bossez. Maîtrisez.<br>Puis <em>déléguez</em>.", 0.15, DUR if port else 1.9)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.3, 1.6)
    c.add_sfx("whoosh", 0.05, 0.2)
    t = T("bossez", 2492.44); c.emoji("fire", t - 0.1, t + 1.5, side="r", rot=-6)
    t = T("obsédés", 2494.95); c.stamp("OBSÉDÉS", t - 0.1, t + 1.3)
    t = T("bosser", 2497.6); c.chip("PAS JUSTE POUR BOSSER", T("juste", 2497.2) - 0.2, t + 0.9, icon="cross", cls="dark")
    pa = T("Remettez-vous", 2499.0)
    c.panel("REMETTEZ-VOUS EN QUESTION", [("Pourquoi ça a marché ?", T("pourquoi", 2501.72) - 0.2, "check"),
                                          ("Pourquoi ça n'a pas marché ?", T("pourquoi", 2503.82) - 0.1, "cross"),
                                          ("Ajuster, améliorer", T("d'ajuster", 2504.6) - 0.2, "target")],
            pa - 0.2, T("Et", 2507.58) - 0.1)
    t = T("vite", 2508.46); c.stamp("NE DÉLÉGUEZ PAS TROP VITE", T("déléguez", 2507.82) - 0.1, t + 1.6)
    t = T("Maîtrisez", 2513.51); c.chip("MAÎTRISEZ D'ABORD", t - 0.15, t + 1.6, icon="target", cls="sun")
    t = T("100", 2515.27); c.chip("PAS À 100 %, PAS MÊME À 80 %", t - 0.3, T("mais", 2518.5) - 0.1, icon="chart", cls="white")
    a = T("différence", 2524.3)
    c.big("TOUTE LA<br><em style=\"color:var(--neon)\">DIFFÉRENCE</em>", T("toute", 2524.0) - 0.15, VOICE_D - 0.05, small="VOUS ALLEZ VOIR")
    c.endcard("ET TOI ?", "TU DÉLÈGUES<br>TROP TÔT ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

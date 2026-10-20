"""Short 08 — « Le vrai facteur : j'aime ce que je fais » (source 40:06 – 40:44)."""
NAME = "s08"
TITLE = "Le vrai facteur : j'aime ce que je fais"
TRIM = True
KEEP = [
    (2406.75, 2413.95),   # « Mais le véritable facteur… c'est parce que j'aime ce que je fais. »
    (2414.95, 2422.72),   # « J'adore ce que je fais. C'est-à-dire quoi ? Même quand… même quand je me disais »
    (2428.76, 2433.95),   # « que j'étais maudit parce que mes vidéos TikTok… YouTube, LinkedIn et autres. »  (drops « je suis maudit parce que je le disais. Je le disais. Je les disais »)
    (2434.45, 2437.66),   # « Je commandais mes appareils, ça n'arrivait pas, j'avais énormément de problèmes, »
    (2441.60, 2445.30),   # « Mais ça m'empêchait pas de continuer, parce que j'aimais ce que je faisais. »
]
FIX = {("c'est", 2442): "ça", "m'empêcher": "m'empêchait", ("pour", 2442): "pas de", ("j'ai", 2443): "j'aimais", ("mis", 2443): None,
       "quoi?": "quoi ?", ("problèmes,", 2437): "problèmes.", ("Je", 2411): "je", ("je", 2438): None, ("disais", 2438): None, ("ah.", 2438): None, ("disais", 2422): "disais", "sentais...": "sentais…"}
KEY = ("facteur", "j'aime", "j'adore", "problèmes,", "mal,", "dépression,", "maudit", "vues,", "continuer", "j'aimais")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("LE VRAI SECRET", "J'<em>aime</em><br>ce que je fais", 0.15, DUR if port else 2.4)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.4, 1.7)
    c.add_sfx("whoosh", 0.05, 0.2)
    t = T("facteur", 2408.18); c.chip("LE VRAI FACTEUR", t - 0.15, t + 2.0, icon="target", cls="sun")
    t = T("j'aime", 2412.84); c.emoji("heart", t - 0.1, t + 2.2, side="r", rot=-6)
    t = T("J'adore", 2415.05); c.chip("J'ADORE ÇA", t - 0.1, t + 1.4, icon="heart", cls="white")
    a = T("même", 2416.67); c.mood(a - 0.2, T("Mais", 2441.69) - 0.1, gray=0.85)
    c.panel("MÊME QUAND…", [("J'avais des problèmes", T("problèmes", 2417.31) - 0.1, "warning"),
                            ("Je me sentais mal", T("mal", 2418.51) - 0.1, "sob"),
                            ("J'étais en dépression", T("dépression", 2421.24) - 0.1, "moon"),
                            ("Je me croyais maudit", T("maudit", 2429.05) - 0.1, "angry")],
            a - 0.2, T("TikTok", 2429.77) - 0.15)
    t = T("TikTok", 2429.77)
    c.logos([("tiktok", t - 0.1), ("instagram", T("Instagram", 2431.05) - 0.1), ("youtube", T("YouTube", 2432.33) - 0.1),
             ("linkedin", T("LinkedIn", 2432.81) - 0.1)], T("Je", 2434.59) - 0.1)
    t = T("vues", 2430.57); c.chip("PAS DE VUES", t - 0.1, T("Je", 2434.59) - 0.1, icon="eyes", cls="red", y=(1500 if port else 170))
    t = T("appareils", 2435.23); c.emoji("package", t - 0.15, t + 1.8, side="l", rot=-6)
    t = T("n'arrivait", 2435.71); c.chip("COLIS JAMAIS ARRIVÉS", t - 0.15, T("Mais", 2441.69) - 0.2, icon="cross", cls="dark")
    a = T("Mais", 2441.69)
    c.big("J'AIMAIS CE<br>QUE JE <em style=\"color:var(--neon)\">FAISAIS</em>" if not port else "J'AIMAIS<br>CE QUE JE<br><em style=\"color:var(--neon)\">FAISAIS</em>",
          T("parce", 2442.89) - 0.1, VOICE_D - 0.05, small="ÇA NE M'A PAS ARRÊTÉ")
    c.endcard("ET TOI ?", "TU AIMES CE<br>QUE TU FAIS ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

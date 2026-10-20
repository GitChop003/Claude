"""Bonus 26-31 — « 5 mois sur Instagram, même pas 200 abonnés » (source 39:25 – 40:01)."""
NAME = "s26"
TITLE = "5 mois sur Instagram, même pas 200 abonnés"
TRIM = True
LOCAL_REF = True
KEEP = [
    (2365.90, 2372.50),   # « Je postais sur Instagram pendant au moins cinq mois. Pour moi, je n'ai dépassé même pas les 200 abonnés. »  (drops « Je » stutter)
    (2373.60, 2373.93),   # « En fait »
    (2374.57, 2377.20),   # « je ne dépassais même pas les 200 vues sur certains de mes posts. »   (spliced « je|je »: drops « je ne descendais »)
    (2380.20, 2386.80),   # « Mais je continuais. Et beaucoup de personnes se demandent comment j'ai réussi à continuer malgré ça, en fait. »
    (2387.00, 2391.60),   # « C'est vrai, de temps en temps, j'avais quand même d'autres services… vu que je suis quand même informaticien. »
    (2395.75, 2401.00),   # « vu que la vente, quand même, je maîtrise. J'ai vendu avant de venir sur le marché, en fait. »
]
FIX = {("Je", 2365): None, ("je", 2366): "Je", ("sur", 2368): None, ("But", 2380): "Mais", ("you", 2381): "je", "continue.": "continuais.",
       "postes.": "posts.", ("deux", 2375): "200", ("cents", 2376): None, ("informaticien.", 2391): "informaticien,", ("vu", 2396): "et",
       ("maîtrise", 2397): "maîtrise."}
KEY = ("instagram", "cinq", "200", "abonnés.", "vues", "continuais.", "continuer", "services", "informaticien,", "vente", "vendu")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("LES COULISSES", "5 mois sur Instagram,<br>même pas <em>200 abonnés</em>", 0.15, DUR if port else 2.6)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.4, 1.7)
    c.add_sfx("whoosh", 0.05, 0.2)
    t = T("Instagram", 2366.97)
    if not port:
        c.logos([("instagram", t - 0.1)], t + 2.2)
    t = T("cinq", 2368.81); c.chip("5 MOIS", t - 0.15, t + 1.3, icon="calendar", cls="white")
    t = T("200", 2371.13); c.chip("MOINS DE 200 ABONNÉS", t - 0.15, t + 1.5, icon="sob", cls="dark")
    a = T("200", 2375.47); c.mood(T("dépassais", 2374.91) - 0.3, T("Mais", 2380.35) - 0.1, gray=0.8)
    c.stamp("200 VUES MAX", a - 0.1, a + 1.5)
    a = T("Mais", 2380.35)
    c.big("MAIS JE<br><em style=\"color:var(--neon)\">CONTINUAIS</em>", a - 0.05, T("Et", 2382.65) - 0.1)
    t = T("comment", 2383.93); c.emoji("thinking", t - 0.2, t + 1.8, side="r", rot=6)
    pa = T("services", 2388.72)
    c.panel("CE QUI M'A FAIT TENIR", [("D'autres services à côté", pa - 0.2, "laptop"),
                                      ("Je suis informaticien", T("informaticien", 2390.80) - 0.2, "phone"),
                                      ("Je maîtrise la vente", T("vente", 2396.25) - 0.2, "money")],
            pa - 0.4, T("J'ai", 2398.19) - 0.1)
    t = T("vendu", 2398.51); c.chip("J'AI VENDU AVANT", t - 0.2, VOICE_D - 0.05, icon="cart", cls="sun")
    c.endcard("ET TOI ?", "QU'EST-CE QUI<br>TE FAIT TENIR ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

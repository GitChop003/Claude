"""Bonus 11-20-25 — « Banni 4 fois sur LinkedIn » (source 12:06 – 12:53)."""
NAME = "s11"
TITLE = "Banni 4 fois sur LinkedIn"
TRIM = True
LOCAL_REF = True
KEEP = [
    (726.90, 735.60),   # « Ça m'épuisait déjà, vu que je postais quand même pratiquement trois fois par jour. Et j'avais commencé directement sur TikTok et Instagram. »
    (736.90, 748.60),   # « LinkedIn, que j'ai fait pratiquement un mois avec pratiquement un like… on me bannit. »
    (756.20, 767.50),   # « Et pour une personne qui vient de connaître les codes d'une plateforme… à te bannir. »
    (770.52, 773.00),   # « Je ne comprenais pas, je voulais abandonner. »
]
FIX = {"reussis": "réussis", ("like", 746): "likes", "types": None, "code": "codes", "poste": "post", "10": "10 000", "000": None,
       "L'indicine": "LinkedIn,", ("j'ai", 738): "j'ai fait", ("Ça", 727): "Ça"}
KEY = ("trois", "linkedin,", "like.", "explose", "impressions,", "bannit.", "bannir", "démoralisant.", "abandonner.")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("LES COULISSES", "Banni <em>4 fois</em><br>sur LinkedIn", 0.15, DUR if port else 2.4)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.4, 1.7)
    c.add_sfx("whoosh", 0.05, 0.2)
    t = T("trois", 730.39); c.chip("3 POSTS PAR JOUR", t - 0.1, t + 2.0, icon="calendar", cls="white")
    if not port:
        c.logos([("tiktok", T("TikTok", 733.23) - 0.1), ("instagram", T("Instagram", 733.87) - 0.1), ("linkedin", T("LinkedIn", 737.1) - 0.1)],
                T("mois", 739.78) - 0.15)
    t = T("mois", 739.78); c.chip("1 MOIS = 1 LIKE", t - 0.1, t + 1.9, icon="heart", cls="white")
    t = T("Deux", 741.88); c.chip("2 MOIS = 1 LIKE", t - 0.1, T("explose", 744.92) - 0.1, icon="heart", cls="white")
    t = T("explose", 744.92); c.emoji("fire", t - 0.1, t + 2.0, side="r", rot=-6)
    c.chip("10 000 IMPRESSIONS", T("10", 746.60) - 0.15, T("bannit", 747.72) - 0.05, icon="rocket", cls="")
    t = T("bannit", 747.72); c.stamp("BANNI", t - 0.05, t + 1.6)
    t = T("bannir", 759.95); c.chip("BANNI 4 FOIS", t - 0.2, t + 2.6, icon="lock", cls="red")
    a = T("démoralisant", 760.99); c.mood(a - 0.2, DUR + 1)
    c.emoji("sob", a - 0.1, a + 2.4, side="l", rot=6)
    t = T("abandonner", 771.64)
    c.big("J'AI VOULU<br><em>ABANDONNER</em>", T("voulais", 771.32) - 0.2, VOICE_D - 0.05)
    c.endcard("ET TOI ?", "TU AURAIS<br>CONTINUÉ ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

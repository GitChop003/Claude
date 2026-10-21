"""Bonus 15-16 — « Ayez une intention précise : audience ou fans ? » (source 38:31 – 38:58)."""
NAME = "s15"
TITLE = "Audience ou fans ? Ayez une intention précise"
TRIM = True
LOCAL_REF = True
KEEP = [
    (2311.13, 2318.06),   # « Ayez une intention précise. Si vous voulez… être influenceur… faire des vues, faire des likes, ou des clients »
    (2318.85, 2320.55),   # « Vous voulez des abonnés ? »   (drops the « Mm » before it and the first « c'est pas la même chose »)
    (2322.60, 2326.60),   # « Ce n'est pas la même chose. Vous voulez créer une audience ou vous voulez juste des fans ? »
    (2327.50, 2329.80),   # « Créer une communauté ou créer des fans, c'est pas la même chose. »
    (2331.70, 2338.10),   # « Une audience, une communauté achète. Les fans vous admirent juste. Maintenant, il faut… les convertir. »
]
FIX = {("encore.", 2311.03): None, ("Vous", 2318.91): "vous", "prise.": "précise.", ("Si", 2312.79): None, ("vous", 2312.87): None, ("voulez.", 2312.95): None, ("vous", 2313.78): "Vous", ("fait", 2316.58): "faire", ("les", 2317.46): "des",
       ("clients", 2317.62): "clients,", ("vous", 2319.15): None, "abonnés,": "abonnés ?", ("fans.", 2326.22): "fans ?",
       "community": "Créer une communauté", "créiste": "ou créer", "achète": "achète.", ("les", 2333.52): "Les", "accueilli": "admirent",
       "juste": "juste", ("juste", 2334.48): "juste.", "eux.": None, "d'errée": "derrière", ("le", 2337.64): "les"}
KEY = ("intention", "précise.", "influenceur", "entrepreneur", "clients,", "abonnés", "chose.", "audience", "fans", "communauté", "achète.", "admirent", "convertir.")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("AYEZ UNE INTENTION PRÉCISE", "Audience<br>ou <em>fans</em> ?", 0.15, DUR if port else 2.4)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.4, 1.7)
    c.add_sfx("whoosh", 0.05, 0.2)
    t = T("intention", 2311.99); c.emoji("target", t - 0.2, t + 1.6, side="r", rot=-6)
    pa = T("influenceur", 2314.18)
    c.panel("VOUS VOULEZ QUOI ?", [("Être influenceur", pa - 0.1, "star"), ("Être entrepreneur", T("entrepreneur", 2315.22) - 0.1, "rocket"),
                                   ("Des vues, des likes", T("vues", 2316.26) - 0.1, "heart"), ("Clients ou abonnés ?", T("clients", 2317.62) - 0.1, "money")],
            pa - 0.4, T("Ce", 2322.78) - 0.27)
    a = T("Ce", 2322.78)
    c.big("CE N'EST PAS<br>LA <em style=\"color:var(--neon)\">MÊME CHOSE</em>" if not port else "CE N'EST<br>PAS LA<br><em style=\"color:var(--neon)\">MÊME CHOSE</em>",
          a + 0.15, T("Vous", 2323.82) - 0.1)
    t = T("audience", 2324.70); c.chip("AUDIENCE", t - 0.15, T("fans", 2326.22) - 0.1, icon="handshake", cls="sun")
    t = T("fans", 2326.22); c.chip("OU JUSTE DES FANS ?", t - 0.15, t + 1.4, icon="heart", cls="white", y=(490 if port else 170))
    pa = T("Une", 2331.92)
    c.panel("LA DIFFÉRENCE", [("Une communauté achète", T("achète", 2333.12) - 0.2, "money"),
                              ("Les fans admirent, c'est tout", T("admirent", 2334.08) - 0.1, "heart")],
            pa - 0.2, T("Maintenant", 2335.24) + 0.2)
    t = T("système", 2336.60); c.chip("UN SYSTÈME POUR CONVERTIR", t - 0.2, VOICE_D - 0.05, icon="bulb", cls="sun")
    c.endcard("ET TOI ?", "AUDIENCE<br>OU FANS ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

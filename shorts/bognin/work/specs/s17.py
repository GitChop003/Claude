"""Bonus 17 — « Grâce à toi, j'ai closé » (le plaisir des résultats clients) (source 40:47 – 41:28)."""
NAME = "s17"
TITLE = "« Grâce à toi, j'ai closé »"
TRIM = True
LOCAL_REF = True
KEEP = [
    (2447.60, 2452.10),   # « Il y a une chose aussi qui booste énormément… vos premiers clients et qu'ils ont des résultats. »
    (2452.85, 2458.70),   # « Il y a une chose dont on ne vous parle pas assez… grâce à toi, j'ai closé. »
    (2458.95, 2461.80),   # « Grâce à toi, j'ai eu un client, grâce à toi j'ai voyagé. »
    (2462.15, 2466.90),   # « Grâce à toi, j'ai doublé mon chiffre d'affaires. Grâce à toi j'ai fait ceci… cela. »
    (2468.30, 2475.70),   # « C'est un plaisir immense… ça dépasse 10 000 euros. »
    (2476.30, 2483.30),   # « Lorsqu'une personne vous dit grâce à toi, j'ai lancé mon business en ligne… gagner de l'argent en ligne. »
    (2484.40, 2488.10),   # « C'est une chose que beaucoup de personnes ne connaissent pas, mais c'est un plaisir immense. »
]
FIX = {"premients": "premiers clients", "qu'on": "dont on ne", ("vous", 2453): "vous", "quand": "quand", "derrière": "dans", "10": "10 000",
       "000": None, ("en", 2455): "en", ("fait", 2455): "fait,"}
KEY = ("booste", "résultats.", "closé.", "client,", "voyagé.", "doublé", "immense.", "motivation.", "euros.", "business", "argent")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("LE VRAI MOTEUR", "« Grâce à toi,<br>j'ai <em>closé</em> »", 0.15, DUR if port else 2.5)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.4, 1.7)
    c.add_sfx("whoosh", 0.05, 0.2)
    t = T("booste", 2449.0); c.emoji("rocket", t - 0.2, t + 1.6, side="r", rot=-8)
    t = T("résultats", 2451.2); c.chip("TES CLIENTS ONT DES RÉSULTATS", T("premiers", 2450.4) - 0.2, t + 1.0, icon="trophy", cls="sun")
    pa = T("closé", 2458.0)
    c.panel("« GRÂCE À TOI… »", [("J'ai closé", pa - 0.1, "check"), ("J'ai eu un client", T("client", 2460.0) - 0.15, "handshake"),
                                 ("J'ai voyagé", T("voyagé", 2461.0) - 0.15, "globe"),
                                 ("J'ai doublé mon CA", T("doublé", 2463.0) - 0.15, "chart")],
            pa - 0.4, T("C'est", 2468.48) - 0.1)
    t = T("immense", 2468.88); c.emoji("heart", t - 0.2, t + 1.4, side="l", rot=6)
    t = T("motivation", 2471.36); c.chip("UNE ÉNORME MOTIVATION", T("énormément", 2470.88) - 0.2, t + 0.9, icon="fire", cls="white")
    a = T("dépasse", 2474.40)
    c.big("ÇA VAUT PLUS<br>QUE <em style=\"color:var(--neon)\">10 000 €</em>" if not port else "ÇA VAUT<br>PLUS QUE<br><em style=\"color:var(--neon)\">10 000 €</em>",
          a - 0.3, T("Lorsqu'une", 2476.4) - 0.1)
    pa = T("lancé", 2478.0)
    c.panel("« GRÂCE À TOI… »", [("J'ai lancé mon business", pa - 0.2, "rocket"), ("Je vis du business en ligne", T("vis", 2479.6) - 0.2, "laptop"),
                                 ("Je gagne de l'argent en ligne", T("gagner", 2481.5) - 0.4, "money")],
            pa - 0.5, T("C'est", 2484.5) - 0.1)
    t = T("immense", 2487.4); c.chip("UN PLAISIR IMMENSE", T("plaisir", 2487.0) - 0.2, VOICE_D - 0.05, icon="heart", cls="sun")
    c.endcard("ET TOI ?", "QUI AS-TU<br>DÉJÀ AIDÉ ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

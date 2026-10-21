"""Bonus 29-30 — « 90 % de mes prospects viennent en DM » (trafic organique + setting) (source 42:56 – 43:30)."""
NAME = "s29"
TITLE = "90 % de mes prospects viennent en DM"
TRIM = True
LOCAL_REF = True
KEEP = [
    (2576.20, 2579.90),   # « Aujourd'hui, on boucle minimum 30 appels par mois. »
    (2580.45, 2580.85),   # « Et »
    (2583.33, 2585.60),   # « quatre-vingt-dix pour cent de nos prospects viennent en DM. »   (drops the false start « 90 % de nous »)
    (2586.20, 2592.55),   # « 90 %, oui, c'est total. En fait, ça fait pas deux semaines… le setting dans mon activité »
    (2593.10, 2595.92),   # « C'est-à-dire la prospection, je l'ai implémentée le plus souvent dans le compte »
    (2597.05, 2598.40),   # « de mes clients, mais pas pour moi. »   (drops the stutter « de mes… »)
    (2599.25, 2606.05),   # « Vu que je le dis encore, ma stratégie est basée sur du trafic organique et du setting… formé comme ça. »
    (2607.68, 2610.40),   # « Lorsque j'ai commencé à vendre, j'étais habitué à faire uniquement ça. »
]
FIX = {("Quatre", 2583.32): "90", ("vingt", 2583.56): None, ("dix", 2583.72): None, ("pour", 2583.88): "%", ("cent", 2583.96): None,
       ("Quatre", 2586.33): "90", ("vingt", 2586.49): None, ("pour", 2586.81): "%,", ("cent", 2586.89): None, ("total", 2587.53): "total.",
       ("en", 2588.01): "En", ("me", 2588.41): None, ("pas.", 2588.65): "pas deux", "j'ai": "j'ai", ("j'ai", 2594.07): "je l'ai",
       ("ça", 2594.87): None, ("implémenté", 2594.31): "implémentée", "30": "30", "boucle": "boucle", ("Et", 2580.55): "Et", ("que", 2592.70): None, ("vu", 2592.54): None,
       ("activité", 2592.14): "activité.", ("j'ai", 2607.75): "Lorsque j'ai"}
KEY = ("30", "appels", "90", "dm.", "total.", "setting", "prospection,", "clients,", "organique", "setting,", "vendre,", "uniquement")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("MON ACQUISITION", "<em>90 %</em> de mes<br>prospects en DM", 0.15, DUR if port else 2.4)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.4, 1.7)
    c.add_sfx("whoosh", 0.05, 0.2)
    t = T("30", 2578.32); c.chip("30 APPELS / MOIS MINIMUM", t - 0.2, t + 1.8, icon="call", cls="sun")
    a = T("90", 2583.32)
    c.big("<em style=\"color:var(--neon)\">90 %</em><br><span style=\"display:block;font-size:.42em;line-height:1.1;margin-top:14px;letter-spacing:.02em\">DE NOS PROSPECTS<br>VIENNENT EN DM</span>",
          a - 0.1, T("90", 2586.33) + 0.9)
    t = T("setting", 2591.34); c.chip("LE SETTING : DEPUIS 2 SEMAINES", T("semaines", 2589.82) - 0.4, t + 1.0, icon="calendar", cls="white")
    t = T("clients", 2597.40); c.emoji("handshake", T("compte", 2595.75) - 0.2, t + 1.2, side="r", rot=-6)
    pa = T("stratégie", 2600.63)
    c.panel("MA STRATÉGIE", [("Trafic organique", T("organique", 2602.15) - 0.3, "chart"),
                             ("Setting en DM", T("setting", 2603.03) - 0.2, "speech")],
            pa - 0.2, T("Lorsque", 2607.75) - 0.1)
    t = T("vendre", 2608.23); c.chip("J'AI APPRIS EN VENDANT", t - 0.2, VOICE_D - 0.05, icon="cart", cls="sun")
    c.endcard("ET TOI ?", "TES PROSPECTS<br>VIENNENT D'OÙ ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

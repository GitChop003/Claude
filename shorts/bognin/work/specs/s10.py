"""Short 10 — « Il y a un degré de chance, mais elle se provoque » (source 27:16 – 28:41)."""
NAME = "s10"
TITLE = "Un degré de chance existe"
TRIM = True
LOCAL_REF = True
KEEP = [
    (1636.30, 1642.30),   # « Et j'ai aussi compris un truc dans l'accompagnement… c'est un degré de chance. »
    (1644.65, 1654.40),   # « Il y a des personnes que j'accompagnais… des mamans même. »
    (1663.65, 1669.40),   # « Ils ont eu pratiquement trois mille abonnés en moins d'un mois. Ils ont closé en moins de deux semaines. »
    (1673.40, 1673.96),   # « Je pense »
    (1675.40, 1678.60),   # « que ce soit les réseaux sociaux, que ce soit le business en ligne, il y a aussi un degré de chance. »  (drops « que si les réseaux sociaux »)
    (1681.55, 1684.10),   # « Mais cette chance-là, vous devez la provoquer. »
    (1684.90, 1689.85),   # « Et aussi une chose… mais ça ne prend pas. »
    (1691.85, 1695.95),   # « Faire les choses de la bonne façon, mais ça ne réussit pas comme vous voulez. »
    (1711.10, 1720.95),   # « Mais comme je l'ai dit, les bonnes choses prennent du temps… d'arriver où vous voulez être. »
]
FIX = {"chanceux.": "chance.", ("ils", 1677): "il y a", ("ont", 1678): None, ("des", 1678): "un", "grilles": "degré de", "chances.": "chance.",
       ("en", 1647): "à", ("moment", 1647): "moment,", ("m'a", 1648): "m'ont", ("vues.", 1649): "vues,", ("un", 1650): "le",
       "parlaient": "partaient", ("les", 1654): "des", ("de", 1666): "d'un", ("un", 1666): None, ("?", 1718): None, "D'arriver": "d'arriver",
       ("les", 1692): "Faire les", ("est-ce", 1716): None, ("que", 1716): "que", ("même", 1650): "même", ("degré", 1642): "degré de", ("ce", 1675): "que ce", ("ce", 1676): "que ce"}
KEY = ("chance.", "compétence,", "dépassé", "rien,", "mille", "closé", "provoquer.", "normaliser", "temps.", "processus,")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("PERSONNE N'EN PARLE", "Il y a un degré<br>de <em>chance</em>", 0.15, DUR if port else 2.3)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.4, 1.7)
    c.add_sfx("whoosh", 0.05, 0.2)
    t = T("accompagné", 1638.58); c.chip("MES ÉLÈVES", t - 0.15, t + 1.6, icon="grad", cls="white")
    t = T("degré", 1641.54); c.emoji("sparkles", t - 0.2, t + 1.6, side="r", rot=-6)
    pa = T("dépassé", 1647.74)
    c.panel("ILS M'ONT DÉPASSÉ", [("En abonnés", T("d'abonnés", 1648.46) - 0.1, "chart"),
                                  ("En vues", T("vues", 1649.26) - 0.1, "eyes"),
                                  ("En ventes / semaine", T("ventes", 1650.70) - 0.1, "money")],
            pa - 0.3, T("Il", 1651.66) + 0.3)
    t = T("aucune", 1646.22); c.chip("AUCUNE COMPÉTENCE", t - 0.15, T("mais", 1646.78) + 0.6, icon="cross", cls="dark")
    t = T("rien", 1653.34); c.chip("PARTIS DE RIEN", t - 0.3, t + 1.4, icon="sparkles", cls="white")
    t = T("trois", 1664.63); c.chip("3 000 ABONNÉS EN < 1 MOIS", t - 0.2, T("Ils", 1667.48) - 0.05, icon="trophy", cls="sun")
    t = T("closé", 1667.80); c.chip("1ER CLOSING EN < 2 SEMAINES", t - 0.2, t + 1.7, icon="handshake", cls="sun")
    t = T("degré", 1677.97); c.emoji("star", t - 0.2, t + 1.5, side="l", rot=6)
    a = T("Mais", 1681.70)
    c.big("LA CHANCE,<br>ÇA SE <em style=\"color:var(--neon)\">PROVOQUE</em>" if not port else "LA CHANCE,<br>ÇA SE<br><em style=\"color:var(--neon)\">PROVOQUE</em>",
          a - 0.05, T("Et", 1684.99) - 0.1)
    t = T("normaliser", 1686.59); c.chip("NORMALISE-LE", t - 0.15, t + 1.8, icon="warning", cls="white")
    t = T("prend", 1689.31); c.stamp("ÇA NE PREND PAS", t - 0.1, t + 1.3)
    t = T("réussit", 1694.56); c.emoji("sweat", t - 0.2, t + 1.4, side="r", rot=-6)
    t = T("temps", 1712.70); c.chip("LES BONNES CHOSES PRENNENT DU TEMPS", T("bonnes", 1711.90) - 0.15, t + 1.6, icon="clock", cls="sun")
    t = T("processus", 1715.57); c.emoji("clock", t - 0.2, t + 2.0, side="l", rot=-6)
    t = T("voulez", 1720.29); c.emoji("target", T("D'arriver", 1719.65) - 0.1, VOICE_D - 0.05, side="r", rot=0)
    c.endcard("ET TOI ?", "TU PROVOQUES<br>TA CHANCE ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

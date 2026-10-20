"""Bonus 32 — « J'ai failli abandonner plusieurs fois » (clients qui ne paient pas, l'impression d'être maudit) (source 18:44 – 19:39)."""
NAME = "s32"
TITLE = "J'ai failli abandonner plusieurs fois"
TRIM = True
LOCAL_REF = True
KEEP = [
    (1124.85, 1127.40),   # « Je vous dis, il y a plusieurs moments où j'ai failli abandonner. »
    (1128.45, 1135.55),   # « J'ai eu plusieurs déceptions. J'ai eu des clientes qui ne voulaient pas payer… mais ils ne veulent pas payer. »
    (1143.15, 1145.75),   # « J'ai eu des clients qui te dérangent, en fait. »   (drops the repeated « clientes que tu formes bien… »)
    (1149.35, 1156.70),   # « Je suis resté jusqu'au moment où je me demandais si on m'avait maudit… personne ne m'écoutait. »
    (1157.95, 1163.30),   # « J'avais l'impression que je parlais dans le vide… tu cales à 300 likes. »
    (1164.20, 1169.45),   # « Et j'étais encore matrixé par ça… le nombre de likes et par le nombre de vues. »
    (1170.30, 1177.52),   # « Lorsqu'une vidéo ne faisait pas de like, je me disais forcément c'est moi le problème. C'est pas toi le problème. Toute vidéo ne doit pas performer. »
]
FIX = {"formes": "formes,", "m'écouttait.": "m'écoutait.", "cal": "cales", "matrixée": "matrixé", "attirée": "attiré", ("je", 1166): None,
       ("t'ai", 1166): None, ("dit", 1166): None, ("leur", 1133): "les", ("le", 1172): "de", ("j'étais", 1167): "j'étais", "postes,": "posts,", "resté": "resté"}
KEY = ("abandonner.", "déceptions.", "payer.", "dérangent", "maudit.", "vide,", "likes", "matrixé", "problème.", "performer.")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("LES COULISSES", "J'ai failli<br><em>abandonner</em>", 0.15, DUR if port else 2.3)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.4, 1.7)
    c.add_sfx("whoosh", 0.05, 0.2)
    t = T("abandonner", 1126.79); c.stamp("FAILLI ABANDONNER", t - 0.1, t + 1.3)
    pa = T("déceptions", 1129.22)
    c.panel("MES DÉCEPTIONS", [("Clients qui ne paient pas", T("clientes", 1131.02) - 0.1, "money"),
                               ("Malgré leurs résultats", T("résultats", 1134.26) - 0.1, "check"),
                               ("Clients qui dérangent", T("dérangent", 1144.60) - 0.15, "angry")],
            pa - 0.3, T("Je", 1149.45) - 0.1)
    a = T("maudit", 1151.37); c.mood(a - 0.4, T("Lorsqu'une", 1170.4) - 0.1, gray=0.8)
    c.emoji("sob", a - 0.2, a + 1.6, side="r", rot=6)
    t = T("personne", 1154.16); c.chip("PERSONNE NE ME VOYAIT", t - 0.15, T("J'avais", 1158.03) - 0.1, icon="seeno", cls="dark")
    t = T("vide", 1159.23); c.emoji("speech", t - 0.2, t + 1.4, side="l", rot=-6)
    t = T("200", 1161.47); c.chip("BLOQUÉ À 200–300 LIKES", t - 0.15, T("Et", 1164.24) - 0.05, icon="heart", cls="white")
    t = T("matrixé", 1165.12); c.stamp("MATRIXÉ PAR LES LIKES", t - 0.1, t + 1.6)
    t = T("problème", 1173.33); c.chip("« C'EST MOI LE PROBLÈME »", T("forcément", 1172.37) - 0.1, t + 0.9, icon="thinking", cls="dark")
    a = T("C'est", 1174.69)
    c.big("C'EST PAS <em style=\"color:var(--neon)\">TOI</em><br>LE PROBLÈME" if not port else "C'EST PAS<br><em style=\"color:var(--neon)\">TOI</em> LE<br>PROBLÈME",
          a - 0.05, T("Toute", 1175.89) - 0.1)
    t = T("performer", 1176.93); c.chip("TOUTE VIDÉO NE DOIT PAS PERFORMER", T("Toute", 1175.89) - 0.05, VOICE_D - 0.05, icon="film", cls="sun")
    c.endcard("ET TOI ?", "TU AS DÉJÀ<br>VOULU LÂCHER ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

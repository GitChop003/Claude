"""Bonus 27-28 — « Toute vidéo n'est pas faite pour performer » (attirer / éduquer / convertir) (source 19:39 – 20:34)."""
NAME = "s27"
TITLE = "Toute vidéo n'est pas faite pour performer"
TRIM = True
LOCAL_REF = True
KEEP = [
    (1179.55, 1183.70),   # « Lorsque vous lancez les réseaux sociaux, comprenez déjà que toute vidéo n'est pas faite pour performer. »
    (1186.25, 1203.00),   # « Il y a des vidéos qui sont faites pour attirer… parce qu'on parle à un public très large. »
    (1204.00, 1208.93),   # « Lorsqu'on parle déjà d'éduquer une personne… à une personne précise »
    (1210.21, 1217.95),   # « qui a un problème précis… c'est normal qu'ils ne suivent pas la vidéo »  (drops the stutter « qui a un… »)
    (1219.45, 1224.22),   # « Et encore, le plus pire encore, il y a des vidéos qui sont faites pour convertir. Et ce type de vidéos, c'est la catastrophe. »
    (1225.66, 1229.70),   # « Le plus souvent, ce type de vidéo ne fait pas beaucoup de vues, parce que vous vendez directement. »  (drops « Je dis bien que c'est la catastrophe »)
    (1229.85, 1234.50),   # « Oui, vu que vous avez déjà attiré, vous avez déjà qualifié, éduqué, mais il faut convertir. »
]
FIX = {("un", 1210.56): "a un", "Tofu,": "TOFU,", "mon": "moins", "vue": "vues,", ("précis", 1213): "précise", ("le", 1213): "lui", ("un", 1211): "un", "font": "fait",
       ("un", 1201): "à un", ("vidéo", 1218): "vidéo.", "Oui,": "Oui,", ("un", 1209): None, ("catégorie.", 1216): "catégorie,", ("C'est", 1217): "c'est"}
KEY = ("performer.", "attirer.", "qualifier,", "éduquer,", "convertir.", "viralité.", "vues.", "large.", "précise", "précis", "catastrophe.",
       "directement.", "convertir.")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("STRATÉGIE CONTENU", "Toute vidéo n'est pas<br>faite pour <em>performer</em>", 0.15, DUR if port else 3.0)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.4, 1.7)
    c.add_sfx("whoosh", 0.05, 0.2)
    pa = T("attirer", 1187.82)
    c.panel("3 TYPES DE VIDÉOS", [("Attirer", pa - 0.1, "rocket"), ("Qualifier, éduquer", T("qualifier", 1190.06) - 0.1, "books"),
                                  ("Convertir", T("convertir", 1192.22) - 0.1, "money")],
            T("vidéos", 1186.78) - 0.2, T("Le", 1193.02) + 0.3)
    t = T("TOFU", 1195.90); c.chip("TOFU = VIRALITÉ", t - 0.15, T("viralité", 1197.82) + 0.8, icon="fire", cls="sun")
    t = T("beaucoup", 1199.58); c.emoji("eyes", t - 0.2, t + 1.5, side="r", rot=-6)
    t = T("large", 1202.30); c.chip("PUBLIC TRÈS LARGE", T("public", 1201.74) - 0.15, t + 1.0, icon="globe", cls="white")
    t = T("moins", 1206.76); c.chip("ÉDUQUER = MOINS DE VUES", t - 0.15, T("parce", 1207.4) + 0.6, icon="books", cls="white")
    pa = T("personne", 1208.28)
    c.panel("ÉDUQUER, C'EST PARLER À", [("Une personne précise", pa - 0.1, "target"), ("Un problème précis", T("problème", 1210.72) - 0.1, "warning"),
                                        ("Une solution précise", T("solution", 1212.16) - 0.1, "bulb")],
            pa - 0.3, T("C'est-à-dire", 1213.76) + 0.4)
    t = T("catégorie", 1216.0); c.emoji("seeno", t - 0.2, t + 1.6, side="l", rot=6)
    t = T("convertir", 1222.16); c.chip("VIDÉOS DE CONVERSION", t - 0.2, t + 1.4, icon="money", cls="sun")
    t = T("catastrophe", 1223.76); c.stamp("PEU DE VUES", t - 0.1, t + 1.6)
    t = T("directement", 1228.56); c.chip("VENTE DIRECTE", t - 0.15, t + 1.2, icon="cart", cls="white")
    a = T("Oui", 1230.00)
    c.big("ATTIRER → ÉDUQUER<br>→ <em style=\"color:var(--neon)\">CONVERTIR</em>" if not port else "ATTIRER<br>ÉDUQUER<br><em style=\"color:var(--neon)\">CONVERTIR</em>",
          T("attiré", 1231.20) - 0.2, VOICE_D - 0.05, small="LE PARCOURS")
    c.endcard("ET TOI ?", "TU FAIS QUEL<br>TYPE DE VIDÉO ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

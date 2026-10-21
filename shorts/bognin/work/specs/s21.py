"""Bonus 21 — « Je n'aimais pas l'école… mais l'école m'a énormément appris » (source 2:34 – 3:23)."""
NAME = "s21"
TITLE = "Je n'aimais pas l'école (mais elle m'a appris)"
TRIM = True
LOCAL_REF = True
KEEP = [
    (154.70, 158.30),   # « Mais honnêtement, je n'aimais même pas l'école. Je vous l'assure, j'aimais pas. »
    (158.55, 160.20),   # « Ça me plaît pas de le dire, en fait. »   (drops the repetition)
    (163.30, 167.55),   # « Je dis souvent : je n'aime pas l'école. Ce n'est pas pour dire que je conseille aux gens de ne pas faire l'école. »
    (168.20, 171.20),   # « Impossible. Moi, c'est juste que ce n'était pas ma chose. Je forçais. »
    (171.45, 178.10),   # « Mais je voulais avoir cet examen aussi… vu que je le faisais plus pour mes parents, pas pour moi. »
    (179.50, 185.05),   # « J'ai décidé d'abandonner, mais c'était une grosse déception pour moi, parce que je voulais leur faire plaisir avec ça. »
    (197.50, 203.30),   # « Je n'aimais pas l'école, mais ça ne veut pas dire que je conseille aux gens de ne pas faire l'école. Et l'école m'a énormément appris. »
]
FIX = {("n'ai", 155.38): "n'aimais", ("la", 157.00): "l'assure,", ("vous", 156.84): "vous", ("suis,", 157.16): None, "j'aiimais": "j'aimais",
       ("me", 165.67): None, ("pour", 166.23): "aux", ("de", 166.71): "de ne pas", ("sinon", 180.82): None, ("Le", 183.73): "leur",
       ("fait", 183.97): "faire", ("n'ai", 197.81): "n'aimais", ("juste", 198.21): None, ("fait.", 160.05): "fait.", ("Je", 163.43): "Je"}
KEY = ("l'école.", "l'école,", "j'aimais", "forçais.", "parents,", "moi.", "d'abandonner,", "déception", "plaisir", "appris.")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("SANS FILTRE", "Je n'aimais pas<br><em>l'école</em>", 0.15, DUR if port else 2.4)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.4, 1.7)
    c.add_sfx("whoosh", 0.05, 0.2)
    t = T("l'école", 155.70); c.emoji("grad", t - 0.2, t + 1.8, side=("r" if port else "l"), rot=-6)
    t = T("plaît", 159.09); c.emoji("sweat", t - 0.2, t + 1.3, side="l", rot=6)
    t = T("conseille", 165.83); c.chip("CE N'EST PAS UN CONSEIL", T("Ce", 164.87) - 0.1, T("Impossible", 168.38) + 0.6, icon="warning", cls="white")
    t = T("forçais", 170.70); c.stamp("JE FORÇAIS", t - 0.1, t + 1.2)
    t = T("parents", 177.00); c.chip("POUR MES PARENTS, PAS POUR MOI", T("faisais", 176.28) - 0.2, t + 1.4, icon="heart", cls="white")
    t = T("d'abandonner", 180.10); c.chip("J'AI ABANDONNÉ", t - 0.2, t + 1.2, icon="cross", cls="red")
    a = T("déception", 181.62); c.mood(a - 0.3, T("Je", 197.65) - 0.1, gray=0.75)
    c.emoji("sob", a - 0.2, a + 1.8, side="r", rot=6)
    t = T("plaisir", 184.13); c.chip("JE VOULAIS LEUR FAIRE PLAISIR", T("voulais", 182.90) - 0.15, t + 1.0, icon="heart", cls="dark")
    a = T("appris", 202.85)
    c.big("L'ÉCOLE M'A<br>ÉNORMÉMENT <em style=\"color:var(--neon)\">APPRIS</em>" if not port else "L'ÉCOLE<br>M'A ÉNORMÉMENT<br><em style=\"color:var(--neon)\">APPRIS</em>",
          T("Et", 201.65) - 0.05, VOICE_D - 0.05)
    c.endcard("ET TOI ?", "L'ÉCOLE<br>T'A AIDÉ ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

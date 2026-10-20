"""Short 03 — « L'entrepreneuriat n'est pas fait pour tout le monde » (source 9:12 – 9:45)."""
NAME = "s03"
TITLE = "L'entrepreneuriat n'est pas fait pour tout le monde"
KEEP = [
    (552.69, 552.92),   # « Je le »            (drops « Et c'est pourquoi »)
    (554.20, 580.49),   # « dis toujours, c'est que l'entrepreneuriat… des jours »  (drops the repeated « je dis toujours »)
    (580.99, 585.52),   # « où vous aurez l'impression… qui vous comprenne. »       (drops the hesitation after « jours »)
]
STRICT_WORDS = False   # cut before the stricter caption rule existed; keeps the published render identical
BEATS = {569.2: 0.30}   # short dramatic beat before « Ne faites pas… »
FIX = {"lui": "le", "faite": "fait", "revient": "réveiller"}
KEY = ("entrepreneuriat", "l'entrepreneuriat", "monde", "mental", "fort", "n'entreprenez", "persévérance", "personne", "seul")


def inserts(c, T, port, VOICE_D, DUR):
    c.title("CE QUE PERSONNE N'OSE TE DIRE", "L'entrepreneuriat<br>n'est <em>pas</em> pour<br>tout le monde" if port
            else "L'entrepreneuriat n'est <em>pas</em><br>pour tout le monde", 0.15, DUR if port else T("Si", 557.75) - 0.2)
    c.name_tag("PARFAIT BOGNIN", "" if port else "· entrepreneur", 0.5, 2.9)
    c.add_sfx("whoosh", 0.05, 0.2)
    t = T("mental", 558.71); c.emoji("brain", t - 0.1, t + 2.3, side="r", rot=-8)
    t = T("fort", 559.51); c.stamp("MENTAL REQUIS", t - 0.05, t + 1.9)
    t = T("n'entreprenez", 561.67); c.chip("N'ENTREPRENEZ PAS", t - 0.1, T("Je", 563.19) - 0.05, icon="cross", cls="red")
    t = T("désolé", 563.83); c.emoji("pray", t - 0.15, t + 1.9, side="l", rot=6)
    t = T("redis", 565.83); c.chip("JE LE REDIS", t - 0.15, t + 1.5, icon="warning", cls="white")
    t = T("mental", 567.43); c.emoji("muscle", t - 0.1, T("Ne", 569.43) - 0.2, side="r", rot=-6)
    a = T("Ne", 569.43); b = T("L'entrepreneuriat", 571.70) - 0.15
    c.big("NE FAITES PAS<br>DE <em>L'ENTREPRENEURIAT</em>" if not port else "NE FAITES<br>PAS DE<br><em style=\"font-size:.7em\">L'ENTREPRENEURIAT</em>",
          a - 0.05, b, small="SI VOUS N'AVEZ PAS LE MENTAL")
    pa = T("demandent", 573.46)
    c.panel("CE QUE ÇA DEMANDE", [("Du mental", T("mental", 574.58) - 0.1, "brain"),
                                  ("De la persévérance", T("persévérance", 576.98) - 0.1, "fire")],
            pa - 0.2, T("Vous", 578.82) + 0.6)
    t = T("réveiller", 579.54); c.mood(t - 0.2, DUR + 1)
    c.emoji("moon", t - 0.1, t + 2.2, side="l", rot=-6)
    t = T("personne", 582.98); c.chip("SEUL CONTRE TOUS", t - 0.1, VOICE_D - 0.05, icon="sob", cls="dark")
    c.endcard("ET TOI ?", "TU AS LE<br>MENTAL ?", "Abonne-toi pour la suite", VOICE_D + 0.05)

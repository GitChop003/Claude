# Shorts — Parfait Bognin

Découpe de la vidéo « Si tu te sens perdu… regarde cette vidéo » (44 min) en shorts, d'après le PDF
*Analyse exhaustive — transcript Bognin Parfait* (TOP 5 + TOP 6-10 + bonus). Les shorts 01 et 02 ont été montés à part.

Chaque short existe en **deux orientations**, avec le même traitement : coupe des vides, bégaiements et répétitions,
flou d'arrière-plan léger, effet « 4K » dosé, sous-titres mot par mot, inserts animés, carte de fin.

| N° | Sujet | Source | Durée | 9:16 (TikTok / Reels / Shorts) | 16:9 (YouTube / LinkedIn) |
|---|---|---|---|---|---|
| 03 | L'entrepreneuriat n'est pas fait pour tout le monde | 9:12 → 9:45 | 30 s | [vertical](s03/port/renders/s03_port.mp4) | [horizontal](s03/land/renders/s03_land.mp4) |
| 04 | 3 mois catastrophiques, puis le déclic | 11:07 → 13:19 | 82 s | [vertical](s04/port/renders/s04_port.mp4) | [horizontal](s04/land/renders/s04_land.mp4) |

## Méthode

- **Découpe** : les points de coupe du PDF sont des repères ; chaque short est recalé sur les phrases complètes
  (début et fin là où l'idée commence et se conclut), et chaque coupe tombe dans un silence ou entre deux sons identiques.
  Les répétitions, faux départs et hésitations sont retirés, les pauses raccourcies. Les choix sont commentés dans
  [`work/specs/`](work/specs) (un fichier par short).
- **Image** : détourage RobustVideoMatting, flou gaussien léger du décor ; « 4K » = débruitage léger, upscale Lanczos,
  netteté adaptative (CAS 0,5), contraste +5 %, saturation +8 % ; punch-ins alternés à chaque coupe ; en 16:9 les panneaux
  se placent du côté libre du visage ; en 9:16 le cadrage suit le visage.
- **Son** : voix seule, débruitage RNNoise, fondus de 12 ms à chaque coupe, normalisation à -14 LUFS ; bruitages discrets.
- **Transcription** : Parakeet TDT 0.6B v3 (horodatage par mot) recoupé avec Whisper small (sherpa-onnx), passages
  difficiles re-décodés (`work/words_patch.json`).
- Fichiers livrés plafonnés sous 90 Mo (limite GitHub).

## Refaire / modifier un short

Les sources lourdes (vidéo d'origine, plaques intermédiaires) ne sont pas versionnées.

```bash
cd shorts/bognin/work
python3 short.py s04 info                    # liste de coupes + sous-titres
python3 short.py s04 cut,plates,media,comp   # découpe, détourage/flou/4K, voix, compositions HyperFrames
python3 short.py s04 snap 2,10,30            # captures de contrôle
python3 short.py s04 render                  # rendus 9:16 et 16:9 (+ plafonnement de taille)
python3 readme.py                            # met à jour ce tableau
```

Crédits des polices, emojis et effets sonores : voir [`../../videos/CREDITS.md`](../../videos/CREDITS.md).

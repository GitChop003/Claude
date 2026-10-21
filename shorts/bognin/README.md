# Shorts — Parfait Bognin

Découpe de la vidéo « Si tu te sens perdu… regarde cette vidéo » (44 min) en shorts, d'après le PDF
*Analyse exhaustive — transcript Bognin Parfait* (TOP 5 + TOP 6-10 + bonus). Les shorts 01 et 02 ont été montés à part.

Chaque short existe en **deux orientations**, avec le même traitement : coupe des vides, bégaiements et répétitions,
flou d'arrière-plan léger, effet « 4K » dosé, sous-titres mot par mot, inserts animés, carte de fin.

| N° | Sujet | Source | Durée | 9:16 (TikTok / Reels / Shorts) | 16:9 (YouTube / LinkedIn) |
|---|---|---|---|---|---|
| 03 | L'entrepreneuriat n'est pas fait pour tout le monde | 9:12 → 9:45 | 30 s | [vertical](s03/port/renders/s03_port.mp4) | [horizontal](s03/land/renders/s03_land.mp4) |
| 04 | 3 mois catastrophiques, puis le déclic | 11:07 → 13:19 | 82 s | [vertical](s04/port/renders/s04_port.mp4) | [horizontal](s04/land/renders/s04_land.mp4) |
| 05 | 800 000 vues, presque 0 client | 20:41 → 21:37 | 35 s | [vertical](s05/port/renders/s05_port.mp4) | [horizontal](s05/land/renders/s05_land.mp4) |
| 06 | Ma pire erreur : recruter mes amis | 13:54 → 16:46 | 65 s | [vertical](s06/port/renders/s06_port.mp4) | [horizontal](s06/land/renders/s06_land.mp4) |
| 07 | J'étais timide, j'avais peur de la caméra | 7:56 → 8:28 | 28 s | [vertical](s07/port/renders/s07_port.mp4) | [horizontal](s07/land/renders/s07_land.mp4) |
| 08 | Le vrai facteur : j'aime ce que je fais | 40:06 → 40:45 | 25 s | [vertical](s08/port/renders/s08_port.mp4) | [horizontal](s08/land/renders/s08_land.mp4) |
| 09 | De 10 € à 2 000 € | 5:00 → 5:41 | 32 s | [vertical](s09/port/renders/s09_port.mp4) | [horizontal](s09/land/renders/s09_land.mp4) |
| 10 | Un degré de chance existe | 27:16 → 28:40 | 46 s | [vertical](s10/port/renders/s10_port.mp4) | [horizontal](s10/land/renders/s10_land.mp4) |
| 11 | Banni 4 fois sur LinkedIn | 12:06 → 12:53 | 30 s | [vertical](s11/port/renders/s11_port.mp4) | [horizontal](s11/land/renders/s11_land.mp4) |
| 13 | Coach niveau 5 ou niveau 100 ? | 36:42 → 37:57 | 49 s | [vertical](s13/port/renders/s13_port.mp4) | [horizontal](s13/land/renders/s13_land.mp4) |
| 15 | Audience ou fans ? Ayez une intention précise | 38:31 → 38:58 | 22 s | [vertical](s15/port/renders/s15_port.mp4) | [horizontal](s15/land/renders/s15_land.mp4) |
| 17 | « Grâce à toi, j'ai closé » | 40:47 → 41:28 | 35 s | [vertical](s17/port/renders/s17_port.mp4) | [horizontal](s17/land/renders/s17_land.mp4) |
| 18 | Bossez, puis maîtrisez avant de déléguer | 41:31 → 42:05 | 27 s | [vertical](s18/port/renders/s18_port.mp4) | [horizontal](s18/land/renders/s18_land.mp4) |
| 21 | Je n'aimais pas l'école (mais elle m'a appris) | 2:34 → 3:23 | 30 s | [vertical](s21/port/renders/s21_port.mp4) | [horizontal](s21/land/renders/s21_land.mp4) |
| 22 | J'ai tout perdu, puis j'ai décidé de me lancer | 6:25 → 7:10 | 28 s | [vertical](s22/port/renders/s22_port.mp4) | [horizontal](s22/land/renders/s22_land.mp4) |

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

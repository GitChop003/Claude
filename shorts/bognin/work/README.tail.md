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

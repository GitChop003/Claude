# Shorts — Parfait Bognin

Découpe de la vidéo « Si tu te sens perdu… regarde cette vidéo » (44 min) en shorts, d'après le PDF
*Analyse exhaustive — transcript Bognin Parfait* (TOP 5 + TOP 6-10 + bonus).

Chaque short existe en **deux orientations** :

| Short | Sujet | Vertical 9:16 (TikTok / Reels / Shorts) | Horizontal 16:9 (YouTube / LinkedIn) |
|---|---|---|---|
| 03 | L'entrepreneuriat n'est pas fait pour tout le monde | [`s03/port/renders/s03_port.mp4`](s03/port/renders/s03_port.mp4) | [`s03/land/renders/s03_land.mp4`](s03/land/renders/s03_land.mp4) |

## Short 03 — choix de montage

- **Source** : 9:12 → 9:45 (le PDF indiquait 9:09 → 9:31). Début décalé pour ne pas reprendre la fin de la
  phrase sur l'entourage (short 02) ; fin prolongée jusqu'à « …personne autour de vous qui vous comprenne »,
  qui fait une meilleure chute.
- **Nettoyage** : « Et c'est pourquoi » et la répétition « et c'est une chose que je dis toujours » retirés,
  hésitation entre « des jours » et « où » coupée, pauses raccourcies (une courte pause dramatique gardée
  avant « Ne faites pas de l'entrepreneuriat »). 33,6 s → 27,9 s de parole.
- **Image** : flou d'arrière-plan léger (détourage RobustVideoMatting, flou gaussien σ ≈ 3 px en 720p),
  effet « 4K » dosé (débruitage léger, upscale Lanczos, netteté adaptative CAS 0,5, contraste +5 %,
  saturation +8 %), punch-ins alternés à chaque coupe, passage en noir et blanc sur la dernière phrase.
- **Son** : voix seule (pas de musique, comme recommandé), débruitage RNNoise, fondus de 12 ms à chaque coupe,
  -14 LUFS ; quelques effets sonores discrets sur les inserts.
- **Habillage** : sous-titres mot par mot (mots-clés en jaune), titre d'accroche, nom, emojis, tampon
  « MENTAL REQUIS », carte « Ce que ça demande », plein écran « Ne faites pas de l'entrepreneuriat »,
  carte de fin « Et toi ? Tu as le mental ? ».

## Refaire / modifier un short

Les sources lourdes (vidéo d'origine, plaques intermédiaires) ne sont pas versionnées.

```bash
cd shorts/bognin/work
python3 s03.py cut                 # liste de coupes + coupe vidéo 720p + voix nettoyée
python3 plates.py <cut720.mp4> <dir> s03   # détourage, flou, « 4K », 16:9 et 9:16
python3 s03_comp.py media          # mixe la voix, ajoute la tenue de fin, (re)génère les deux compositions
npx hyperframes render shorts/bognin/s03/port -o shorts/bognin/s03/port/renders/s03_port.mp4 --fps 25
npx hyperframes render shorts/bognin/s03/land -o shorts/bognin/s03/land/renders/s03_land.mp4 --fps 25
```

Transcription : Parakeet TDT 0.6B v3 (horodatage par mot) + Whisper small, via sherpa-onnx.
Crédits des polices, emojis et effets sonores : voir [`../../videos/CREDITS.md`](../../videos/CREDITS.md).

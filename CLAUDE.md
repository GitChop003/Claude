# Mémoire du projet : shorts The Process (Bognin « Parfait »)

Lire aussi : `videos/shorts/DIRECTIVES.md` (toutes les règles de montage, à respecter) et `videos/shorts/TITRES.md`.

## Contexte
- Utilisateur : Patrick, monteur. Client : Bognin Parfait, @the_process.io (coach de coachs). ADN : moderne, sobre, classe, épuré.
- Branche de travail : `claude/wizardly-newton-u6b79q`. Commit + push à chaque étape. Pas de PR sans demande.
- Patrick a peu de quota : réponses courtes, peu d'exploration.

## État (27 novembre 2026)
- 11 shorts v5 rendus : `videos/shorts/sN/renders/*_reel_v5_livraison.mp4`.
- **Référence validée par Bognin : s1 SÉANCE v4** (commit `f77f1ea`, `videos/shorts/s1/index.html` de ce commit) : titre en haut au-dessus de la tête, sobre, sans viseur REC.
- **Demande en cours** : appliquer le préréglage de s1 v4 à DEUX autres shorts, puis livrer les 3 vidéos dans un artefact de validation où Parfait commente (lecteur, « commenter à cet instant », statut par vidéo, historique des versions ; commentaires en base partagée ; vidéos de relecture 720p ≈ 5 Mo).
- À corriger aussi : reflet vert des LED sur la peau (menton/cou) ; s6 compte à rebours « 60 jours avant 2027 » devenu faux ; relecture complète des sous-titres ; couvertures sans animation ; fichiers 4:5 > 50 Mo ; police Callum Slanted manquante (Montserrat italique en attendant).

## Pipeline (`work/shorts/`)
- `cut.py spec rt rushes out grade` : découpe + son (gain mesuré, pas de loudnorm dynamique). `reaudio.py` : refait seulement le son.
- `build.py spec words.json dir` : composition HyperFrames (index.html). `vhooks.py` : accroches visuelles.
- `finalize.sh dir MOTCLE date version` : rendu 9:16, 4:5, couvertures, -14 LUFS. Puis encodage livraison crf 21.
- `faces.py` : position du visage (faces.json). Specs : `work/shorts/specs/sN.json`.
- Transcriptions sauvegardées : `work/shorts/rt/*.json` ; liste des rushes : `work/shorts/rt/RUSHES.txt`.
- Les rushes (≈10 Go, Dropbox de Bognin) et les modèles (sherpa-onnx Parakeet, rvm.onnx) ne sont PAS dans git : les retélécharger (demander les liens Dropbox à Patrick). Dépendances : `opencv-python-headless<5`, `onnxruntime`, `sherpa-onnx`, Node (npx hyperframes).
- Le `cut.mp4` de chaque short est ignoré par git : sans rushes, impossible de rerendre. Priorité au démarrage : récupérer les rushes.

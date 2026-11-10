# Directives de montage des shorts : The Process (Bognin Parfait)

Réglages hérités des échanges avec la production (novembre 2026). Ils complètent la charte V3 de Bognin et passent avant les réglages par défaut. Chaque nouveau lot part de ce fichier.

## Découpe
- Un rush contient souvent plusieurs idées ou plusieurs prises de la même phrase : on découpe **par plage précise**, jamais un fichier entier, et on garde **la meilleure prise** de chaque phrase.
- Rythme « juste milieu », ni brut ni mou : pauses de plus de 0,45 s raccourcies, « euh » isolés retirés.
- **Fins de mots jamais coupées** : bornes calées sur l'énergie réelle de la voix (+0,12 s), sans mordre sur le mot suivant.
- Passages mal captés (transcription incohérente) écartés plutôt que sous-titrés au hasard.
- Faute de français à l'oral : on cherche d'abord le bon mot ailleurs dans les rushes, sinon **on coupe la phrase**. La voix clonée a été testée (accord de Bognin) puis **retirée à la demande de la production** : pas de voix générée sans nouvelle demande explicite.
- Aucun chiffre de résultat non prouvé à l'écran. Pas de visage ni de voix d'élève sans accord écrit.

## Image et son
- Étalonnage **clair et sobre** : balance automatique (grayworld) + neutralisation des LED vert/rose/bleu, **sans assombrir** l'image.
- Voix à **-14 LUFS en stéréo** (une voix mono dupliquée au rendu monte à -11 LUFS : toujours vérifier).
- Nappe musicale originale très basse (environ 25 dB sous la voix), un seul son discret sur la révélation principale.

## Habillage
- Palette « nuancée » (fond papier, cyan profond, touches sable) + verre dépoli subtil sur les cartes. Pas de marqueurs « IA par défaut » (bordures orange, barre colorée à gauche, émojis, dégradés, rebonds).
- Accroche sur 2 lignes maximum (ouvertures variées, voir v4), titre tenu 5 à 9 s puis disparu, sans barre de progression (v5).
- Sous-titres 1 à 3 mots, mot clé en cyan, doublure Montserrat italique en attendant Callum Slanted.
- **Fin** : le CTA (« Commente MOT », barre de recherche) arrive **pendant la dernière phrase**, au-dessus des sous-titres (qui restent lisibles), reste environ 1,7 s après la voix, puis carte de fin de 1,3 s.

## Inserts et animations : varier
3 à 4 moments graphiques par short (v4), synchronisés sur les mots, jamais devant le visage. **Ne pas répéter la même formule** :
- **Liste à cases** : au plus une fois par lot, jamais sur deux vidéos qui se suivent.
- Pour une énumération, alterner entre : mot géant élément par élément · tuiles d'icônes ou logos stylisés qui s'allument · pile de notifications · chemin relié par un fil cyan · mots qui s'accumulent en marge · numérotation géante · mots barrés (ce qu'il faut éviter) · bulles de conversation (citations).
- Même logique pour les cartes d'interface (DM, Calendly, notes), le schéma de la méthode, les cartes plein écran et les inserts HD : on les fait tourner d'une vidéo à l'autre.
- Mot derrière la tête (détourage) : avec parcimonie, une fois par lot environ.

## Retours de Bognin et de la production (8 novembre, v4)
- **Ouvertures** : plus jamais la carte plein écran à fond blanc en ouverture. Ouvertures **typographiques sur le plan**, variées d'une vidéo à l'autre (texte géant, mot unique, citation, empilement, machine à écrire…), jamais deux fois la même d'affilée.
- **Ne jamais cacher le visage** : tout élément graphique se place **sous le visage** (bande basse), les sous-titres juste en dessous, au-dessus de la zone masquée par Instagram. Position du visage **mesurée** sur chaque vidéo. Si un élément ne tient pas sous le visage, il passe en **superposition plein écran**.
- **Pas de @the_process.io permanent** (v5 : retiré aussi de la carte de fin, remplacé par un passage à l'acte).
- **Le moins chargé possible** : pas d'étiquettes ni de bandeaux en verre. On joue sur la **typographie** (tailles, graisses, contraste fin/gras) plutôt que sur des cadres. 3 à 4 moments graphiques par vidéo maximum.
- **Mise en page mesurée** : haut (y ≈ 300–560) pour l'ouverture au-dessus de la tête puis le sujet en petit texte ; bande sous le visage (y ≈ 1170–1395) pour les cartes, tuiles, mot choc et CTA ; sous-titres sur une ligne à y ≈ 1408 (dans la zone 4:5 et au-dessus du masque Instagram).
- **Énumérations** : une formule différente pour chaque vidéo d'un même lot (tuiles d'icônes, mot géant, empilement en marge, mots barrés, numérotation, liste à cases…).

## Retours de Bognin (10 novembre, v5) : modèle de référence = s1 SÉANCE v4
- **Accroche visuelle obligatoire** dans la première seconde, en plus du texte : coup de zoom arrière + un élément graphique lié au sujet (s1 : viseur de caméra « REC »). Une accroche visuelle **différente pour chaque vidéo**.
- **Plus de barre de progression** en haut.
- **Le titre (headline) disparaît** : tenu jusqu'à la première fin de phrase après 5 s (entre 5 et 9 s), puis plus rien en haut de l'écran. Pas de rappel permanent du sujet.
- **Assombrissement de l'écran** : remplace la carte blanche plein écran pour le moment clé (méthode, question, phrase choc). Le visage reste visible derrière, le texte se place sous le visage.
- **Varier les types de montage** d'une vidéo à l'autre (accroche visuelle, ouverture, formule d'énumération, moment assombri), à partir du modèle s1.
- **Son** : la dernière phrase doit s'entendre. Pas de `loudnorm` dynamique en bout de chaîne (son tampon de 3 s coupait la fin) : gain fixe mesuré + limiteur, et contrôle automatique de la fin à chaque découpe.
- **Fin** : plus de @the_process.io, même sur la carte de fin. Quand l'écran s'assombrit, une phrase de **passage à l'acte** propre à la vidéo (s1 : « À toi de jouer. / Filme ta prochaine séance. »), sous le visage.
- Toujours proscrit : début tout blanc, @the_process.io (y compris à la fin), barre de progression, éléments devant le visage.

## Livraison
- Par short : 9:16 (version légère de livraison), 4:5 LinkedIn, couvertures 9:16 et 4:5, titres, 2 accroches alternatives, légende, mot-clé de CTA proposé (à valider par Bognin).

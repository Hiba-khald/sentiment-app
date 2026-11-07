## Besoin en une phrase (obligatoire)

Détecter automatiquement les ordonnances incomplètes (champ obligatoire manquant) avant la délivrance, pour que le pharmacien les fasse corriger.

## Utilisateur final (obligatoire)

Le pharmacien ou le préparateur qui réceptionne et valide les ordonnances au comptoir.

## Approche retenue (obligatoire)

Cocher une seule case :

- [x] Règles métier
- [ ] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, ...)

Règles métier car (b) chaque alerte renvoie à un champ précis que le pharmacien vérifie en quelques secondes, et (d) une ordonnance validée à tort peut mettre le patient en danger, donc la logique doit être déterministe et auditable. De plus (c) le coût par requête est quasi nul, et (a) nous n'avons pas d'ordonnances étiquetées alors que la liste des champs obligatoires est connue.

## Données nécessaires et leur origine (obligatoire)

Les ordonnances saisies ou numérisées issues du logiciel de la pharmacie, et la liste des mentions obligatoires d'une ordonnance.

## Métrique de succès et seuil d'acceptation (obligatoire)

Rappel d'au moins 99 % sur les ordonnances réellement incomplètes, avec moins de 10 % de fausses alertes, mesuré sur un jeu vérifié par un pharmacien.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Une ordonnance incomplète validée à tort peut causer une erreur de délivrance dangereuse ; une fausse alerte ne coûte que quelques minutes. Le pharmacien garde la validation finale, l'outil ne fait que signaler.

## Risques éthiques ou de confidentialité (obligatoire)

Ce sont des données de santé : accès restreint, pas de stockage inutile, données anonymisées pour les tests, respect de la loi marocaine 09-08.

## Approche écartée et pourquoi (facultatif)

Le machine learning est écarté : pas de données étiquetées, et un modèle serait moins explicable qu'une règle précise.
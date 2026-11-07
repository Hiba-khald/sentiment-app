## Besoin en une phrase (obligatoire)

Identifier automatiquement les avis clients négatifs parmi des milliers d'avis, afin que l'équipe les traite en priorité.

## Utilisateur final (obligatoire)

L'équipe du service client du site e-commerce, qui doit répondre aux clients mécontents le plus vite possible.

## Approche retenue (obligatoire)

Cocher une seule case :

- [ ] Règles métier
- [x] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, ...)

Machine learning car (a) les avis arrivent avec des notes en étoiles et peuvent être étiquetés positif/négatif, ce qui permet d'entraîner un classifieur supervisé, et (c) le coût par avis est très faible une fois le modèle entraîné, ce qui compte pour des milliers d'avis. De plus (b) chaque prédiction reste vérifiable en relisant l'avis, et (d) une erreur de classement a une conséquence limitée.

## Données nécessaires et leur origine (obligatoire)

Un historique d'avis clients du site, avec le texte et la note en étoiles, complété par un échantillon étiqueté à la main pour contrôler la qualité des étiquettes.

## Métrique de succès et seuil d'acceptation (obligatoire)

Un rappel d'au moins 85 % sur la classe « négatif » et une F1 d'au moins 0,80, mesurés sur un jeu de test séparé de l'entraînement.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Un avis négatif classé comme positif est traité en retard ; un avis positif classé négatif fait perdre quelques minutes à l'équipe. Le modèle ne fait que prioriser : un humain lit chaque avis avant de répondre au client.

## Risques éthiques ou de confidentialité (obligatoire)

Les avis peuvent contenir des noms ou des données personnelles : il faut les anonymiser avant l'entraînement. Il faut aussi vérifier que le modèle ne traite pas moins bien certaines langues ou certains styles d'écriture.

## Approche écartée et pourquoi (facultatif)

Les règles métier sont écartées : une liste de mots négatifs rate l'ironie, les fautes d'orthographe et les mélanges de langues.
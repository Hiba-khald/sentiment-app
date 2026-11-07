## Besoin en une phrase (obligatoire)

Permettre aux élèves et aux parents d'obtenir une réponse rapide et fiable aux questions sur le règlement intérieur de l'école.

## Utilisateur final (obligatoire)

Les élèves, les parents et le secrétariat de l'école, qui posent des questions sur les absences, les retards, la tenue ou les sanctions.

## Approche retenue (obligatoire)

Cocher une seule case :

- [ ] Règles métier
- [ ] Machine learning
- [x] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, ...)

RAG car (b) chaque réponse peut être vérifiée en citant l'article du règlement dont elle provient, et (d) une information fausse sur une sanction ou une absence peut léser un élève, donc la réponse doit s'appuyer sur le texte officiel. De plus (a) nous n'avons pas de questions étiquetées pour entraîner un modèle, alors que les documents existent déjà.

## Données nécessaires et leur origine (obligatoire)

Le règlement intérieur de l'école en version officielle (PDF ou texte), fourni par l'administration, ainsi qu'une vingtaine de questions types pour tester.

## Métrique de succès et seuil d'acceptation (obligatoire)

Au moins 90 % de réponses correctes et accompagnées de l'article cité, mesuré sur une vingtaine de questions types vérifiées par le secrétariat.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Une réponse erronée peut induire un élève ou un parent en erreur sur une sanction ou une obligation. Chaque réponse affiche l'article source, et le secrétariat reste le recours pour les cas litigieux.

## Risques éthiques ou de confidentialité (obligatoire)

Le règlement est un document public interne, donc peu sensible, mais il ne faut pas enregistrer les questions des élèves avec leur nom. Il faut aussi éviter qu'une réponse inventée soit prise pour une décision officielle.

## Approche écartée et pourquoi (facultatif)

Le modèle génératif seul est écarté : sans le texte du règlement, il risquerait d'inventer des règles, et on ne pourrait pas vérifier ses réponses.
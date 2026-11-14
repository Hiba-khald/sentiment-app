# Changelog

## [1.0.0] - 2026-11-14

### Added

- Paquet `sentiment_app` installable avec `pip`, incluant le modèle sérialisé.
- Fonction publique `predict(texte)` renvoyant `label` et `score`.
- Commande console `sentiment` avec sortie texte ou `--json`.
- Vérification du livrable par `scripts/verifier_livrable.py`.

### Limitations

- Modèle entraîné sur le jeu de démonstration `data/demo_reviews.csv` (290 avis).
- Deux classes seulement : `positive` et `negative` ; l'abstention `INDETERMINE` reste côté API.
- Les versions de `scikit-learn` et `joblib` sont liées à la sérialisation du modèle.

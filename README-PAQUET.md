# sentiment-app

Paquet Python de prédiction de sentiment pour des avis clients rédigés en français.

## Installation

```bash
pip install sentiment_app-1.0.0-py3-none-any.whl
```

Le modèle est embarqué dans la roue : aucun accès au dépôt n'est nécessaire.

## Utilisation

```python
from sentiment_app import predict

predict("Livraison rapide, produit conforme, très satisfait")
# {'label': 'positive', 'score': 0.8}
```

Ou en ligne de commande :

```bash
sentiment "Colis abîmé, je suis déçu"
sentiment --json "Livraison rapide, produit conforme, très satisfait"
sentiment --version
```

## Limites

- Le modèle est un TF-IDF + régression logistique entraîné sur 290 avis de démonstration.
- Il connaît deux étiquettes (`positive`, `negative`) et un score de confiance ; le seuil d'abstention est géré par l'API, pas par le paquet.
- Les textes hors du vocabulaire d'entraînement peuvent être mal classés malgré un score élevé.
- Prévu pour des avis clients en français ; d'autres domaines ou langues demandent un réentraînement.

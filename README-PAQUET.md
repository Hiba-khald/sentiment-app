# sentiment-app

Classe le sentiment d'un avis client en français (positive / negative).

## Installation
    pip install sentiment_app-1.0.0-py3-none-any.whl

## Utilisation
    from sentiment_app import predict
    predict("Livraison rapide, très satisfait")

    sentiment "Livraison rapide, très satisfait" --json

## Limites
Modèle entraîné sur 290 avis de démonstration générés : ne pas l'utiliser tel quel en production.
La confiance n'est pas une garantie de justesse.
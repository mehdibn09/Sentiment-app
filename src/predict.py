#!/usr/bin/env python
"""Prédiction unitaire : la fonction que l'API de la semaine 3 appellera.

Usage :
  python src/predict.py "Livraison rapide, très satisfait"
  >>> from predict import predict ; predict("texte")
"""
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal, TypedDict

import joblib

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"


class Prediction(TypedDict):
    """Contrat de sortie de predict() : exactement ces deux clés."""

    label: Literal["positive", "negative"]
    score: float


@lru_cache(maxsize=1)
def charger_modele() -> Any:
    """Chargé une seule fois par processus, pas à chaque appel."""
    if not MODELE.exists():
        raise FileNotFoundError("models/sentiment.joblib absent : lancez python src/train.py")
    return joblib.load(MODELE)


def predict(texte: str) -> Prediction:
    """Renvoie {'label': 'positive'|'negative', 'score': float}."""
    if not isinstance(texte, str) or not texte.strip():
        raise ValueError("texte vide")
    pipeline = charger_modele()
    probabilites = pipeline.predict_proba([texte])[0]
    rang = int(probabilites.argmax())
    return {
        "label": pipeline.classes_[rang],
        "score": round(float(probabilites[rang]), 4),
    }


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    resultat = predict(" ".join(sys.argv[1:]))
    print(f"{resultat['label']} (confiance {resultat['score']:.0%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

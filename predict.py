#!/usr/bin/env python
"""Prédiction unitaire : la fonction que l'API de la semaine 3 appellera.

Usage :
  python src/predict.py "Livraison rapide, très satisfait"
  >>> from predict import predict ; predict("texte")
"""
import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal, TypedDict

import joblib

RACINE = Path(__file__).resolve().parents[1]


def chemin_modele() -> Path:
    """Chemin externe, ou modèle de développement à la racine du dépôt."""
    return Path(os.environ.get("SENTIMENT_MODELE") or RACINE / "models" / "sentiment.joblib")


MODELE = chemin_modele()


class Prediction(TypedDict):
    """Contrat de sortie de predict() : exactement ces deux clés."""

    label: Literal["positive", "negative"]
    score: float


@lru_cache(maxsize=1)
def charger_modele(chemin: Path | None = None) -> Any:
    """Chargé une seule fois par processus, pas à chaque appel."""
    cible = chemin if chemin is not None else MODELE
    if not cible.exists():
        raise FileNotFoundError(
            f"Modèle introuvable : {cible}. Lancez python src/train.py "
            "ou définissez SENTIMENT_MODELE."
        )
    return joblib.load(cible)


def predict(texte: str, chemin: Path | None = None) -> Prediction:
    """Renvoie {'label': 'positive'|'negative', 'score': float}."""
    if not isinstance(texte, str) or not texte.strip():
        raise ValueError("texte vide")
    pipeline = charger_modele() if chemin is None else charger_modele(chemin)
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

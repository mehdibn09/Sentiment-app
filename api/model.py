"""Raccord entre l'API et le modèle entraîné au TP2.

L'API n'entraîne rien et ne connaît pas scikit-learn : elle appelle la fonction
predict() de sentiment_app/predict.py, qui charge models/sentiment.joblib une seule fois.
Sous le seuil d'abstention, l'étiquette devient INDETERMINE (le score reste renvoyé).
"""
from pathlib import Path
from typing import TypedDict

from api.schemas import Etiquette
from sentiment_app import predict as tp2

MODELE = tp2.MODELE
charger_modele = tp2.charger_modele

SEUIL_ABSTENTION = 0.60
# Étiquettes du modèle (TP2) -> étiquettes du contrat de l'API
CORRESPONDANCE: dict[str, Etiquette] = {"positive": "POSITIVE", "negative": "NEGATIVE"}

__all__ = ["MODELE", "SEUIL_ABSTENTION", "SentimentClassifier", "charger_modele", "load_model"]


class Resultat(TypedDict):
    """Retour de SentimentClassifier.predict, conforme à PredictResponse."""

    label: Etiquette
    score: float
    text: str


class SentimentClassifier:
    """Enveloppe du modèle TP2 avec l'interface attendue par l'API."""

    model_name = "tfidf-logreg (TP2, models/sentiment.joblib)"

    def __init__(self, chemin: Path | None = None) -> None:
        self.chemin = chemin
        pipeline = charger_modele() if chemin is None else charger_modele(chemin)
        inconnues = set(map(str, pipeline.classes_)) - set(CORRESPONDANCE)
        if inconnues:
            raise ValueError(f"classes du modèle absentes du contrat de l'API : {sorted(inconnues)}")

    def predict(self, text: str) -> Resultat:
        """Renvoie {'label': POSITIVE|NEGATIVE|INDETERMINE, 'score': float, 'text': aperçu}."""
        r = tp2.predict(text) if self.chemin is None else tp2.predict(text, self.chemin)
        label: Etiquette = "INDETERMINE" if r["score"] < SEUIL_ABSTENTION else CORRESPONDANCE[r["label"]]
        return {"label": label, "score": r["score"], "text": text[:100]}


def load_model(chemin: Path = MODELE) -> SentimentClassifier:
    """Construit le classifier ; FileNotFoundError si le fichier du modèle n'existe pas."""
    if not chemin.exists():
        raise FileNotFoundError(f"{chemin.name} absent : lancez python src/train.py")
    return SentimentClassifier(chemin)

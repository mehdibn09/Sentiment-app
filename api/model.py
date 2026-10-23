"""Raccord entre l'API et le modèle entraîné au TP2.

L'API n'entraîne rien et ne connaît pas scikit-learn : elle appelle la fonction
predict() de src/predict.py, qui charge models/sentiment.joblib une seule fois.
Sous le seuil d'abstention, l'étiquette devient INDETERMINE (le score reste renvoyé).
"""
import sys
from pathlib import Path
from typing import TypedDict

from api.schemas import Etiquette

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
import predict as tp2  # noqa: E402  (module du TP2)

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

    def __init__(self) -> None:
        pipeline = charger_modele()  # échoue immédiatement si le joblib manque
        inconnues = set(map(str, pipeline.classes_)) - set(CORRESPONDANCE)
        if inconnues:
            raise ValueError(f"classes du modèle absentes du contrat de l'API : {sorted(inconnues)}")

    def predict(self, text: str) -> Resultat:
        """Renvoie {'label': POSITIVE|NEGATIVE|INDETERMINE, 'score': float, 'text': aperçu}."""
        r = tp2.predict(text)
        label: Etiquette = "INDETERMINE" if r["score"] < SEUIL_ABSTENTION else CORRESPONDANCE[r["label"]]
        return {"label": label, "score": r["score"], "text": text[:100]}


def load_model(chemin: Path = MODELE) -> SentimentClassifier:
    """Construit le classifier ; FileNotFoundError si le fichier du modèle n'existe pas."""
    if not chemin.exists():
        raise FileNotFoundError(f"{chemin.name} absent : lancez python src/train.py")
    return SentimentClassifier()

"""Génère la matrice de confusion du modèle sur le jeu de démonstration."""
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")   # pas de fenêtre : écriture directe dans un fichier
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix

RACINE = Path(__file__).resolve().parents[1]
MODELE = RACINE / "models" / "sentiment.joblib"
DONNEES = RACINE / "data" / "demo_reviews.csv"
SORTIE = RACINE / "docs" / "captures" / "confusion.png"

# 1. Vérifications
if not MODELE.exists():
    raise SystemExit("models/sentiment.joblib absent : lancez d'abord python src/train.py")
if not DONNEES.exists():
    raise SystemExit("data/demo_reviews.csv absent : lancez d'abord python src/make_demo.py")

# 2. Chargement
pipeline = joblib.load(MODELE)
df = pd.read_csv(DONNEES)

# 3. Prédictions
y_vrai = df["label"]
y_predit = pipeline.predict(df["review"])

# 4. Matrice
cm = confusion_matrix(y_vrai, y_predit, labels=["negative", "positive"])
disp = ConfusionMatrixDisplay(cm, display_labels=["negative", "positive"])
disp.plot(cmap="Blues", values_format="d")

plt.title(f"Matrice de confusion — {len(df)} avis de démonstration")
SORTIE.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(SORTIE, dpi=150, bbox_inches="tight")
print(f"Écrit : {SORTIE}")
print()
print("Matrice (lignes = vérité, colonnes = prédiction) :")
print(f"  negative  {cm[0][0]:>6}  {cm[0][1]:>6}")
print(f"  positive  {cm[1][0]:>6}  {cm[1][1]:>6}")

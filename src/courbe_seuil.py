#!/usr/bin/env python
"""Courbe du seuil d'abstention : que gagne-t-on, que perd-on à relever le seuil ? (TP4, étape C)

Usage, depuis la racine du dépôt, modèle entraîné :
  python src/courbe_seuil.py             # jeu de test du TP2 (jeu de démonstration)
  python src/courbe_seuil.py --allocine  # jeu de test Allociné

Pour chaque seuil, on simule : « le modèle répond seulement si son score >= seuil,
sinon l'avis part à un humain ». Les chiffres vont dans docs/semaine4.md, partie 3.
"""
import argparse
import json
import sys
from pathlib import Path

import joblib
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parent))  # pour lancer depuis la racine
from train import GRAINE, METRIQUES, MODELE, charger  # mêmes constantes que l'entraînement

SEUILS = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]


def avertissement_source(source: str, n_test: int) -> str | None:
    """Signale un modèle entraîné sur d'autres données que celles qu'on mesure."""
    if not METRIQUES.exists():
        return None
    metriques = json.loads(METRIQUES.read_text(encoding="utf-8"))
    if metriques.get("source") != source or metriques.get("n_test") != n_test:
        return (
            f"ATTENTION : models/metrics.json décrit source={metriques.get('source')}, "
            f"n_test={metriques.get('n_test')} ; la mesure porte sur source={source}, n_test={n_test}. "
            "Relancez python src/train.py avec la même option."
        )
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allocine", action="store_true", help="utiliser le jeu public Allociné")
    args = parser.parse_args()

    if not MODELE.exists():
        raise SystemExit("Modèle absent : lancez d'abord python src/train.py")
    pipeline = joblib.load(MODELE)

    df, source = charger(args.allocine)
    # Même découpage que l'entraînement : même graine, mêmes proportions
    _, x_test, _, y_test = train_test_split(
        df["review"], df["label"], test_size=0.2, random_state=GRAINE, stratify=df["label"]
    )
    probabilites = pipeline.predict_proba(x_test)
    scores = probabilites.max(axis=1)
    predits = pipeline.classes_[probabilites.argmax(axis=1)]
    verites = y_test.to_numpy()
    total = len(verites)

    print(f"Jeu de test du TP2 : {total} avis (source : {source})")
    message = avertissement_source(source, total)
    if message:
        print(message)
    print()
    print(" seuil  répond à   part  exactitude  erreurs  vers un humain")
    for seuil in SEUILS:
        retenus = scores >= seuil
        repondus = int(retenus.sum())
        erreurs = int((predits[retenus] != verites[retenus]).sum())
        exactitude = f"{(repondus - erreurs) / repondus:.3f}" if repondus else "n/a"
        print(
            f"{seuil:>6.2f}{repondus:>10}{100 * repondus / total:>6.0f}%"
            f"{exactitude:>12}{erreurs:>9}{total - repondus:>16}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

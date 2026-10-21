#!/usr/bin/env python
"""Courbe du seuil d'abstention : que gagne-t-on, que perd-on à relever le seuil ? (TP4, étape B)

Usage, depuis la racine du dépôt, modèle entraîné :
  python src/courbe_seuil.py
Pour chaque seuil, on simule : "le modèle répond seulement si son score >= seuil,
sinon l'avis part à un humain". Les chiffres vont dans docs/semaine4.md, partie 3.

Limite : une abstention de l'API n'a pas de classe prédite exploitable. La courbe
n'est donc fiable que pour des seuils >= à celui déjà appliqué par l'API.
"""
import csv
import logging
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
JEU_OR = RACINE / "data" / "jeu_or.csv"
FRANCHES = {"POSITIVE", "NEGATIVE"}
SEUILS = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]


def main() -> int:
    sys.path.insert(0, str(RACINE))
    from fastapi.testclient import TestClient

    from api.main import app

    logging.disable(logging.INFO)  # pas de journal (API, httpx) dans la courbe
    with JEU_OR.open(encoding="utf-8", newline="") as f:
        lignes = [ligne for ligne in csv.DictReader(f) if (ligne.get("text") or "").strip()]
    if not lignes:
        raise SystemExit("data/jeu_or.csv ne contient aucun avis : écrivez vos 20 avis d'abord")

    resultats: list[tuple[str | None, float, str]] = []  # (label, score, attendu)
    refus = 0
    with TestClient(app) as client:
        for ligne in lignes:
            reponse = client.post("/predict", json={"text": ligne["text"]})
            if reponse.status_code != 200:
                refus += 1
                continue
            corps = reponse.json()
            resultats.append((corps.get("label"), float(corps.get("score", 0.0)), ligne["attendu"]))

    total = len(resultats)
    if total == 0:
        raise SystemExit("aucune réponse 200 de l'API : vérifiez que le modèle est entraîné")

    print(f"{'seuil':<7} {'vers humain':<14} {'répondus':<9} {'justes':<7} {'erreurs':<8} précision")
    for seuil in SEUILS:
        repondus = [(label, attendu) for label, score, attendu in resultats if label in FRANCHES and score >= seuil]
        justes = sum(1 for label, attendu in repondus if label == attendu)
        humain = total - len(repondus)
        precision = f"{100 * justes / len(repondus):.0f} %" if repondus else "n/a"
        print(
            f"{seuil:<7.2f} {humain:>3} ({100 * humain / total:3.0f} %)   "
            f"{len(repondus):<9} {justes:<7} {len(repondus) - justes:<8} {precision}"
        )

    print(f"\nCourbe sur {total} avis" + (f" ({refus} refusés par l'API, ignorés)" if refus else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

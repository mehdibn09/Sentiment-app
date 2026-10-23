#!/usr/bin/env python
"""Bilan du jeu d'or : où le modèle se trompe-t-il, et le dit-il ? (TP4, étape C)

Usage, depuis la racine du dépôt, modèle entraîné :
  python src/bilan_jeu_or.py

Chaque avis de data/jeu_or.csv est envoyé à l'API (client en mémoire, aucun serveur à lancer).
Trois issues : juste, abstention (INDETERMINE), erreur franche (l'étiquette opposée).
Une erreur franche est « déclarée » si la colonne erreur_connue est renseignée.
"""
import csv
import logging
import sys
from collections import defaultdict
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
JEU_OR = RACINE / "data" / "jeu_or.csv"


def lire_jeu_or(chemin: Path = JEU_OR) -> list[dict[str, str]]:
    with chemin.open(encoding="utf-8", newline="") as f:
        return [ligne for ligne in csv.DictReader(f) if (ligne.get("text") or "").strip()]


def issue(attendu: str, label: str) -> str:
    """'juste', 'abstention' ou 'franche'."""
    if label == attendu:
        return "juste"
    if label == "INDETERMINE":
        return "abstention"
    return "franche"


def main() -> int:
    sys.path.insert(0, str(RACINE))
    from fastapi.testclient import TestClient

    from api.main import app

    logging.disable(logging.INFO)  # pas de journal (API, httpx) dans le bilan
    lignes = lire_jeu_or()
    if not lignes:
        raise SystemExit("data/jeu_or.csv ne contient aucun avis")

    compte = {"juste": 0, "abstention": 0, "franche_declaree": 0, "franche_non_declaree": 0}
    par_categorie: dict[str, list[int]] = defaultdict(lambda: [0, 0])  # [justes, total]
    with TestClient(app) as client:
        for ligne in lignes:
            reponse = client.post("/predict", json={"text": ligne["text"]})
            reponse.raise_for_status()
            resultat = issue(ligne["attendu"], reponse.json()["label"])
            if resultat == "franche":
                resultat = "franche_declaree" if ligne.get("erreur_connue") else "franche_non_declaree"
            compte[resultat] += 1
            categorie = ligne.get("difficulte") or "simple"
            par_categorie[categorie][1] += 1
            par_categorie[categorie][0] += resultat == "juste"

    print(f"Jeu d'or : {len(lignes)} avis")
    print(f"  réponses justes                  : {compte['juste']}")
    print(f"  abstentions (INDETERMINE)        : {compte['abstention']}")
    print(f"  erreurs franches déclarées       : {compte['franche_declaree']}")
    print(f"  erreurs franches non déclarées   : {compte['franche_non_declaree']}")
    print("Détail par catégorie (justes / avis) :")
    for categorie, (justes, total) in sorted(par_categorie.items()):
        print(f"  {categorie:<10} {justes}/{total}")
    return 1 if compte["franche_non_declaree"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

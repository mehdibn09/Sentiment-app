"""Jeu d'or (TP4, étape C) : un cas de test par ligne de data/jeu_or.csv.

Un cas échoue si l'API se trompe franchement (POSITIVE au lieu de NEGATIVE, ou l'inverse).
Une abstention (INDETERMINE) ne fait pas échouer ; src/bilan_jeu_or.py la compte.
Une erreur franche qu'on ne sait pas corriger reste dans le jeu : la colonne erreur_connue
en donne la raison et le cas est marqué xfail(strict=True).
"""
import csv
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
JEU_OR = RACINE / "data" / "jeu_or.csv"
MODELE = RACINE / "models" / "sentiment.joblib"
pytestmark = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit : python src/train.py")


def cas() -> list:
    with JEU_OR.open(encoding="utf-8", newline="") as f:
        lignes = [ligne for ligne in csv.DictReader(f) if (ligne.get("text") or "").strip()]
    params = []
    for i, ligne in enumerate(lignes, start=1):
        marques = []
        if ligne["erreur_connue"]:
            marques.append(pytest.mark.xfail(strict=True, reason=ligne["erreur_connue"]))
        params.append(pytest.param(ligne["text"], ligne["attendu"], marks=marques, id=f"avis-{i:02d}"))
    return params


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as c:
        yield c


def test_jeu_or_conforme_a_l_enonce():
    with JEU_OR.open(encoding="utf-8", newline="") as f:
        lignes = list(csv.DictReader(f))
    assert len(lignes) == 20
    assert {ligne["attendu"] for ligne in lignes} == {"POSITIVE", "NEGATIVE"}
    assert sum(1 for ligne in lignes if ligne["difficulte"]) >= 5


@pytest.mark.parametrize("texte, attendu", cas())
def test_pas_d_erreur_franche(client, texte, attendu):
    label = client.post("/predict", json={"text": texte}).json()["label"]
    opposee = {"POSITIVE": "NEGATIVE", "NEGATIVE": "POSITIVE"}[attendu]
    assert label != opposee, f"erreur franche : attendu {attendu}, reçu {label}"

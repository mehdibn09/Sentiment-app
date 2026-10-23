"""Tests aux limites du contrat d'entrée (TP4, étape B).

PredictRequest promet un champ « text », chaîne de 1 à 2000 caractères.
Ce fichier vérifie cette promesse à ses frontières, puis au hasard (hypothesis).
"""
import json
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"
pytestmark = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit : python src/train.py")

ETIQUETTES = {"POSITIVE", "NEGATIVE"}
# Une abstention est une réponse 200 légitime (cf. src/bilan_jeu_or.py) dont le label n'est
# ni POSITIVE ni NEGATIVE. À ADAPTER : valeur que votre API renvoie quand elle s'abstient.
LABEL_ABSTENTION = "INDETERMINE"
ETIQUETTES_ADMISES = ETIQUETTES | {LABEL_ABSTENTION}
BLANCS = " \t\n\r\x0b\x0c\x85\u00a0"


@pytest.fixture(scope="module")
def client():
    """Portée « module » : l'API démarre une fois pour tout le fichier (hypothesis l'exige)."""
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as c:  # le « with » exécute le lifespan : le modèle est chargé
        yield c


def en_json(valeur: object) -> bytes:
    """Corps de requête JSON, sous forme d'octets : permet aussi d'envoyer un corps invalide."""
    return json.dumps(valeur).encode("utf-8")


# Étape B.1 : huit cas au moins, chacun avec son code attendu.
CAS = [
    pytest.param(en_json({"text": ""}), 422, id="texte-vide"),
    pytest.param(en_json({"text": "   "}), 422, id="espaces"),
    pytest.param(en_json({"text": "a"}), 200, id="un-caractere"),
    pytest.param(en_json({"text": "a" * 2000}), 200, id="2000-caracteres"),
    pytest.param(en_json({"text": "a" * 2001}), 422, id="2001-caracteres"),
    pytest.param(en_json({}), 422, id="champ-absent"),
    pytest.param(en_json({"text": 42}), 422, id="mauvais-type"),
    pytest.param(b"pas du json", 422, id="corps-non-json"),
]


@pytest.mark.parametrize("corps, code_attendu", CAS)
def test_frontieres_du_contrat(client, corps, code_attendu):
    reponse = client.post("/predict", content=corps, headers={"Content-Type": "application/json"})
    assert reponse.status_code == code_attendu
    # Étape B.2 : pour chaque 422, la forme standard de FastAPI : liste d'objets {loc, msg, type}
    if code_attendu == 422:
        detail = reponse.json()["detail"]
        assert isinstance(detail, list), f"detail doit être une liste, reçu : {detail!r}"
        assert detail, "detail ne doit pas être vide"
        for erreur in detail:
            assert "loc" in erreur and "msg" in erreur and "type" in erreur


# Étape B.5 : deux tests de propriété avec hypothesis.
@given(st.text(min_size=1, max_size=2000).filter(lambda s: s.strip()))
@settings(deadline=None, max_examples=30)
def test_texte_valide_recoit_200(client, texte):
    reponse = client.post("/predict", json={"text": texte})
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["label"] in ETIQUETTES_ADMISES, f"label inattendu : {corps['label']!r}"
    assert 0.0 <= corps["score"] <= 1.0


@given(st.text(alphabet=st.sampled_from(BLANCS), min_size=1, max_size=50))
@settings(deadline=None, max_examples=30)
def test_texte_de_blancs_recoit_422(client, texte):
    reponse = client.post("/predict", json={"text": texte})
    assert reponse.status_code == 422
    detail = reponse.json()["detail"]
    assert isinstance(detail, list)

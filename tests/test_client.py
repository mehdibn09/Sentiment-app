"""Tests du client HTTP de l'interface (TP5, 6 tests) : ui/client.py.

Les cas d'erreur utilisent un transport simulé (aucun serveur, aucun modèle requis) ;
les cas nominaux interrogent l'API en mémoire et sont ignorés tant que le modèle manque.
"""
import sys
from pathlib import Path

import httpx
import pytest

RACINE = Path(__file__).resolve().parents[1]
MODELE = RACINE / "models" / "sentiment.joblib"
sys.path.insert(0, str(RACINE / "ui"))

import client  # noqa: E402  (ui/ doit être dans sys.path)


def session_simulee(statut: int, corps: dict | None = None) -> httpx.Client:
    """Un client dont toutes les réponses ont ce statut."""
    transport = httpx.MockTransport(lambda requete: httpx.Response(statut, json=corps or {}))
    return httpx.Client(base_url="http://api.test", transport=transport)


def session_injoignable() -> httpx.Client:
    def refuser(requete: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connexion refusée", request=requete)

    return httpx.Client(base_url="http://api.test", transport=httpx.MockTransport(refuser))


@pytest.fixture(scope="module")
def session_api():
    if not MODELE.exists():
        pytest.skip("modèle non produit : python src/train.py")
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as c:
        yield c


def test_sante_et_verdict_avec_l_api_en_memoire(session_api):
    etat = client.sante(session_api)
    assert etat.ok and "TP2" in etat.message
    reponse = client.predire(session_api, "Livraison rapide, produit conforme, très satisfait")
    assert reponse.ok and reponse.label == "POSITIVE" and 0.5 <= (reponse.score or 0) <= 1


def test_422_devient_un_refus_lisible(session_api):
    reponse = client.predire(session_api, "   ")
    assert not reponse.ok and reponse.message == client.REFUS


def test_503_devient_modele_non_charge():
    assert client.sante(session_simulee(503)).message == client.SANS_MODELE
    assert client.predire(session_simulee(503), "texte").message == client.SANS_MODELE


def test_api_injoignable():
    assert client.sante(session_injoignable()).message == client.INJOIGNABLE
    assert client.predire(session_injoignable(), "texte").message == client.INJOIGNABLE


def test_autres_codes_sont_des_erreurs_internes():
    assert "500" in client.predire(session_simulee(500), "texte").message
    assert "502" in client.sante(session_simulee(502)).message


def test_lot_et_resume():
    ok = session_simulee(200, {"label": "INDETERMINE", "score": 0.52, "text": "x"})
    reponses = client.predire_lot(ok, ["a", "b"]) + client.predire_lot(session_simulee(422), ["c"])
    assert client.resumer(reponses) == {"INDETERMINE": 2, "REFUS OU ERREUR": 1}
    assert set(client.VERDICTS) == {"POSITIVE", "NEGATIVE", "INDETERMINE"}

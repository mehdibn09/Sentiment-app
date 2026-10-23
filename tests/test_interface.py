"""Tests de la page Streamlit (TP5, 6 tests), avec le moteur de test intégré de Streamlit.

La connexion à l'API est remplacée par un client en mémoire : aucun serveur à lancer.
Ignorés tant que le modèle n'est pas produit ou que Streamlit n'est pas installé.
"""
import sys
from pathlib import Path

import httpx
import pytest

RACINE = Path(__file__).resolve().parents[1]
MODELE = RACINE / "models" / "sentiment.joblib"
sys.path.insert(0, str(RACINE / "ui"))

pytest.importorskip("streamlit")
pytestmark = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit : python src/train.py")

import client  # noqa: E402
from streamlit.testing.v1 import AppTest  # noqa: E402


@pytest.fixture
def page(monkeypatch):
    """La page ouverte, branchée sur l'API en mémoire."""
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as api:
        monkeypatch.setattr(client, "creer_session", lambda: api)
        yield AppTest.from_file(str(RACINE / "ui" / "app.py"), default_timeout=30)


def textes(at: AppTest) -> str:
    """Tout le texte affiché, pour y chercher un message."""
    morceaux = [m.value for m in at.markdown] + [e.value for e in at.error] + [w.value for w in at.warning]
    morceaux += [i.value for i in at.info] + [s.value for s in at.success]
    return "\n".join(morceaux)


def analyser(at: AppTest, avis: str) -> AppTest:
    at.run()
    at.text_area[0].set_value(avis)
    at.button[0].click()
    return at.run()


def test_la_page_annonce_l_api_prete(page):
    at = page.run()
    assert not at.exception
    assert "API prête : tfidf-logreg (TP2" in textes(at)


def test_avis_positif(page):
    at = analyser(page, "Livraison rapide, produit conforme, très satisfait")
    assert "Avis positif" in textes(at)


def test_avis_negatif(page):
    at = analyser(page, "Produit cassé et service injoignable, à fuir")
    assert "Avis négatif" in textes(at)


def test_abstention_affichee_comme_je_ne_sais_pas(page):
    at = analyser(page, "xqzvb wlkptr grombu")
    texte = textes(at)
    assert "Je ne sais pas : à faire vérifier par un humain" in texte
    assert "sous le seuil d'abstention" in texte


def test_texte_refuse(page):
    at = analyser(page, "   ")
    assert client.REFUS in textes(at)


def test_api_injoignable(monkeypatch):
    def refuser(requete: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connexion refusée", request=requete)

    injoignable = httpx.Client(base_url="http://api.test", transport=httpx.MockTransport(refuser))
    monkeypatch.setattr(client, "creer_session", lambda: injoignable)
    at = AppTest.from_file(str(RACINE / "ui" / "app.py"), default_timeout=30).run()
    assert client.INJOIGNABLE in textes(at)

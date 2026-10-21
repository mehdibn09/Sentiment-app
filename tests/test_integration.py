"""Tests d'intégration : l'API telle qu'elle tourne vraiment (TP4, étape D).

Les tests du TP3 vérifient des réponses ; ceux-ci vérifient le démarrage de l'API
et son comportement quand le modèle manque ou tombe en panne.
"""
from pathlib import Path

import pytest

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"
pytestmark = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit : python src/train.py")

# --- À ADAPTER si votre api/main.py utilise d'autres noms ------------------------------
NOM_CHEMIN_MODELE = "MODELE"  # variable de api.main qui contient le chemin du modèle
NOM_ETAT_MODELE = "model"     # attribut de app.state qui contient le modèle chargé
AVIS = {"text": "Colis reçu rapidement et en parfait état"}
# ----------------------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def cache_propre():
    """Vide le cache du chargeur avant et après chaque test : aucun test ne dépend d'un autre."""
    from api.main import charger_modele

    charger_modele.cache_clear()
    yield
    charger_modele.cache_clear()


def test_demarrage_reel_charge_le_modele():
    """D.1 (donné en exemple) : un client ouvert par « with » exécute le lifespan."""
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as client:
        reponse = client.get("/health")
    assert reponse.status_code == 200
    assert "TP2" in reponse.json()["model"]


def test_modele_absent_empeche_le_demarrage(monkeypatch, tmp_path):
    """D.2 : le fichier du modèle n'existe pas, l'API refuse de démarrer."""
    from fastapi.testclient import TestClient

    import api.main as main

    monkeypatch.setattr(main, NOM_CHEMIN_MODELE, tmp_path / "inexistant.joblib")
    main.charger_modele.cache_clear()

    with pytest.raises(FileNotFoundError):
        with TestClient(main.app):
            pass  # l'erreur doit survenir à l'entrée du « with » (lifespan)


def test_modele_non_charge_repond_503(monkeypatch):
    """D.3 : l'API est démarrée mais le modèle a disparu de app.state, 503 partout."""
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as client:
        monkeypatch.delattr(app.state, NOM_ETAT_MODELE)
        assert client.get("/health").status_code == 503
        assert client.post("/predict", json=AVIS).status_code == 503


@pytest.mark.parametrize(
    "erreur",
    [RuntimeError("panne du modèle"), ValueError("bug interne")],
    ids=["RuntimeError", "ValueError"],
)
def test_modele_en_panne_repond_500_sans_fuite(monkeypatch, erreur):
    """D.4 : predict plante, l'API répond 500 sans exposer le message interne."""
    from fastapi.testclient import TestClient

    from api.main import app

    def predict_en_panne(*args, **kwargs):
        raise erreur

    # raise_server_exceptions=False : on veut lire la réponse 500, pas recevoir l'exception.
    with TestClient(app, raise_server_exceptions=False) as client:
        modele = getattr(app.state, NOM_ETAT_MODELE)
        monkeypatch.setattr(modele, "predict", predict_en_panne)
        reponse = client.post("/predict", json=AVIS)

    assert reponse.status_code == 500
    assert str(erreur) not in reponse.text

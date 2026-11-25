from pathlib import Path

import pandas as pd
import pytest
import yaml

from sentiment_app.tp5 import core


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MLFLOW_TRACKING_URI", "sqlite:///" + str(tmp_path / "mlflow.db"))
    monkeypatch.setenv("MLFLOW_ENABLE_SYSTEM_METRICS_LOGGING", "false")
    data = tmp_path / "data"
    data.mkdir()
    core.generer().to_csv(data / "demo.csv", index=False)
    core.preparer(data / "demo.csv", data / "prepared")
    yield tmp_path
    import mlflow

    mlflow.end_run()


def test_generation():
    a, b = core.generer(), core.generer()
    pd.testing.assert_frame_equal(a, b)
    assert len(a) == 290 and a.review.nunique() == 290
    assert set(a.label) == core.LABELS


@pytest.mark.parametrize("n", [0, -1, True, 1.5])
def test_ngram_invalide(n):
    with pytest.raises(ValueError):
        core.construire_pipeline(n)


@pytest.mark.parametrize("n", [0, -1, True])
def test_min_df_invalide(n):
    with pytest.raises(ValueError):
        core.construire_pipeline(2, n)


def test_nettoyage():
    df = pd.DataFrame({"review": [" a  b ", "a b", " ", None], "label": ["positif"] * 4})
    assert len(core.nettoyer(df)) == 1
    with pytest.raises(ValueError):
        core.nettoyer(pd.DataFrame({"x": []}))
    with pytest.raises(ValueError):
        core.nettoyer(pd.DataFrame({"review": ["x"], "label": ["autre"]}))
    with pytest.raises(ValueError):
        core.nettoyer(pd.DataFrame({"review": ["x", "x"], "label": ["positif", "negatif"]}))


def test_preparation(workspace):
    tr = pd.read_csv("data/prepared/train.csv")
    te = pd.read_csv("data/prepared/test.csv")
    assert (len(tr), len(te)) == (217, 73)
    assert not set(tr.review) & set(te.review)
    assert set(tr.label) == set(te.label) == core.LABELS
    with pytest.raises(ValueError):
        core.preparer(Path("data/demo.csv"), Path("data/o"), test_size=1)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_vocabulaire(n):
    pipeline = core.construire_pipeline(n, 1)
    pipeline.fit(
        ["bonjour joli monde", "produit très cassé", "avis sans surprise"] * 2,
        ["positif", "negatif", "neutre"] * 2,
    )
    assert max(len(t.split()) for t in pipeline[0].get_feature_names_out()) == n


def test_tracking_et_promotion(workspace):
    import mlflow
    from mlflow import MlflowClient

    r = core.entrainer(Path("data/prepared"), Path("models/tp5"), 1)
    assert 0 <= r["f1_macro"] <= 1
    client = MlflowClient()
    run = client.get_run(r["run_id"])
    assert run.info.status == "FINISHED" and run.data.params["ngram_max"] == "1"
    assert run.data.metrics["f1_macro"] == r["f1_macro"]
    assert list(mlflow.sklearn.load_model(r["model_uri"]).predict(["service impeccable"]))
    refuse = core.promouvoir(1.0, prepared=Path("data/prepared"))
    assert not refuse["promu"]
    assert not client.search_registered_models()
    accepte = core.promouvoir(0, prepared=Path("data/prepared"))
    assert accepte["promu"]
    assert (
        client.get_model_version_by_alias("sentiment-tp5", "champion").version == accepte["version"]
    )
    assert core.predire(["service impeccable"], True) == core.predire(["service impeccable"])
    alias = accepte["version"]
    assert not core.promouvoir(1, prepared=Path("data/prepared"))["promu"]
    assert client.get_model_version_by_alias("sentiment-tp5", "champion").version == alias
    with pytest.raises(ValueError):
        core.promouvoir(float("nan"))
    with pytest.raises(ValueError):
        core.predire([" "])


def test_fichiers_pipeline(tmp_path):
    root = Path(__file__).resolve().parents[1]
    params = yaml.safe_load((root / "params.yaml").read_text())
    dvc = yaml.safe_load((root / "dvc.yaml").read_text())
    mlp = yaml.safe_load((root / "MLproject").read_text())
    env = yaml.safe_load((root / "python_env.yaml").read_text())
    assert set(dvc["stages"]) == {"prepare", "train"}
    assert (
        mlp["entry_points"]["train"]["parameters"]["ngram_max"]["default"]
        == params["train"]["ngram_max"]
    )
    assert (
        "--tp5" in dvc["stages"]["train"]["cmd"]
        and "--tp5" in mlp["entry_points"]["train"]["command"]
    )
    assert (
        mlp["python_env"] == "python_env.yaml" and "-r requirements-tp5.txt" in env["dependencies"]
    )

    # Régression : les dossiers parents doivent rester visibles pour les expériences DVC.
    import shutil
    import subprocess

    from dvc.repo import Repo

    for nom in [
        ".gitignore",
        ".dvc/config",
        ".dvc/.gitignore",
        ".dvcignore",
        "dvc.yaml",
        "params.yaml",
        "data/tp5/.gitignore",
        "data/tp5/demo_reviews.csv.dvc",
    ]:
        destination = tmp_path / nom
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / nom, destination)
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    with Repo(tmp_path) as repo:
        assert any(
            Path(stage.path).resolve() == tmp_path / "data/tp5/demo_reviews.csv.dvc"
            for stage in repo.index.stages
        )
        assert repo.scm.is_ignored(str(tmp_path / ".venv-tp5" / "pyvenv.cfg"))


@pytest.mark.parametrize("fraction", [-0.1, 0, 1, 1.1, float("nan")])
def test_decoupage_fraction_invalide(workspace, fraction):
    with pytest.raises(ValueError, match="test_size"):
        core.preparer(Path("data/demo.csv"), Path("data/autre"), test_size=fraction)


@pytest.mark.parametrize("seuil", [-0.1, 1.1, float("nan"), float("inf")])
def test_seuil_invalide(seuil):
    with pytest.raises(ValueError, match="Seuil"):
        core.promouvoir(seuil)


def test_decoupage_reproductible(workspace):
    core.preparer(Path("data/demo.csv"), Path("data/autre"))
    for nom in ["train.csv", "test.csv"]:
        assert (Path("data/prepared") / nom).read_bytes() == (Path("data/autre") / nom).read_bytes()


def test_fuite_de_donnees_refusee(workspace):
    train = pd.read_csv("data/prepared/train.csv")
    train.to_csv("data/prepared/test.csv", index=False)
    with pytest.raises(ValueError, match="Recouvrement"):
        core.entrainer(Path("data/prepared"), Path("models/tp5"))


@pytest.mark.parametrize(
    "texte,label",
    [
        ("Excellent produit, pour cette commande.", "positif"),
        ("Produit cassé, pour cette commande.", "negatif"),
        ("Commande reçue, pour cette commande.", "neutre"),
    ],
)
def test_orientation_classes(texte, label):
    df = core.generer()
    pipeline = core.construire_pipeline()
    pipeline.fit(df.review, df.label)
    assert pipeline.predict([texte]).tolist() == [label]
    assert abs(pipeline.predict_proba([texte])[0].sum() - 1) < 1e-8


def test_run_projects_reutilise(workspace):
    import mlflow

    core.suivi()
    with mlflow.start_run() as run:
        resultat = core.entrainer(Path("data/prepared"), Path("models/tp5"), 3)
        assert resultat["run_id"] == run.info.run_id
        assert mlflow.active_run().info.run_id == run.info.run_id
    assert mlflow.get_run(resultat["run_id"]).info.status == "FINISHED"

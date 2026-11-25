"""Données, préparation et suivi MLflow 3 du TP5."""

import hashlib
import json
import os
import random
import re
from pathlib import Path

import joblib
import pandas as pd
import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

LABELS = {"positif", "negatif", "neutre"}


def config():
    """Charge les paramètres du TP5 depuis la racine du dépôt."""
    return yaml.safe_load((Path.cwd() / "params.yaml").read_text(encoding="utf-8"))


def generer(seed=42):
    """Génère 290 avis synthétiques uniques et reproductibles sur trois classes."""
    pos = [
        "Service impeccable",
        "Excellent produit",
        "Livraison rapide",
        "Très satisfait de cet achat",
        "Bonne qualité",
        "Je recommande",
        "Emballage soigné",
        "Produit solide et pratique",
    ]
    neg = [
        "Produit cassé",
        "Livraison très lente",
        "Service décevant",
        "Très mauvais achat",
        "Mauvaise qualité",
        "Je ne recommande pas",
        "Emballage abîmé",
        "Produit inutilisable",
    ]
    suffixes = [
        "pour cette commande",
        "après mon achat",
        "cette semaine",
        "dans mon cas",
        "aujourd’hui",
        "lors de la réception",
        "pour ce modèle",
        "sur cette référence",
        "à ce tarif",
        "dans cette boutique",
    ]
    rows = [
        (f"{a}, {s}.", label)
        for phrases, label in [(pos, "positif"), (neg, "negatif")]
        for a in phrases
        for s in suffixes
    ]
    for i in range(100):
        a, c = (pos[i % 8], neg[(i // 8) % 8]) if i % 2 == 0 else (neg[i % 8], pos[(i // 8) % 8])
        rows.append(
            (
                f"{a}{[', mais ', ' et ', ' ; ', ', '][i % 4]}{c.lower()}, {suffixes[i // 64]}.",
                "neutre",
            )
        )
    for i in range(30):
        bases = [
            "Le colis est arrivé",
            "Le produit correspond à la fiche",
            "Utilisation standard",
            "Commande reçue",
            "Rien de particulier",
            "Article installé",
        ]
        rows.append((f"{bases[i % 6]}, {suffixes[i // 6]}.", "neutre"))
    # Certains couples alternés peuvent coïncider ; la formulation identifie chaque cas neutre.
    seen = set()
    uniques = []
    for text, label in rows:
        if text in seen:
            text = text.rstrip(".") + f" (observation {len(uniques) + 1})."
        seen.add(text)
        uniques.append({"review": text, "label": label})
    random.Random(seed).shuffle(uniques)
    return pd.DataFrame(uniques)


def nettoyer(df):
    """Normalise les espaces et retire les avis vides ou répétés."""
    if not {"review", "label"}.issubset(df.columns):
        raise ValueError("Colonnes review et label requises")
    result = df[["review", "label"]].dropna().copy()
    result["review"] = result.review.astype(str).map(lambda x: re.sub(r"\s+", " ", x).strip())
    result["label"] = result.label.astype(str).str.strip()
    result = result[result.review.ne("")]
    if not set(result.label).issubset(LABELS):
        raise ValueError("Label TP5 inconnu")
    if result.groupby("review").label.nunique().gt(1).any():
        raise ValueError("Labels contradictoires pour un avis")
    return result.drop_duplicates("review").reset_index(drop=True)


def preparer(source, destination, seed=42, test_size=0.25):
    """Découpe les données avant vectorisation, avec stratification par classe."""
    if not 0 < test_size < 1:
        raise ValueError("test_size doit être entre 0 et 1")
    df = nettoyer(pd.read_csv(source))
    train, test = train_test_split(df, test_size=test_size, random_state=seed, stratify=df.label)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    train.to_csv(destination / "train.csv", index=False, lineterminator="\n")
    test.to_csv(destination / "test.csv", index=False, lineterminator="\n")
    return len(train), len(test)


def construire_pipeline(ngram_max=2, min_df=2, seed=42):
    """Construit TF-IDF et régression logistique sans ajuster le vocabulaire."""
    if isinstance(ngram_max, bool) or not isinstance(ngram_max, int) or ngram_max < 1:
        raise ValueError("ngram_max doit être un entier >= 1")
    if isinstance(min_df, bool) or not isinstance(min_df, int) or min_df < 1:
        raise ValueError("min_df doit être un entier >= 1")
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(ngram_range=(1, ngram_max), min_df=min_df, sublinear_tf=True),
            ),
            ("clf", LogisticRegression(max_iter=1000, random_state=seed, class_weight="balanced")),
        ]
    )


def suivi():
    """Utilise SQLite par défaut et conserve un éventuel run MLflow Projects actif."""
    import mlflow

    uri = os.environ.get("MLFLOW_TRACKING_URI") or "sqlite:///mlflow.db"
    mlflow.set_tracking_uri(uri)
    if mlflow.active_run() is None:
        mlflow.set_experiment("sentiment-app-tp5")
    return mlflow


def empreinte(path):
    """Identifie les octets du jeu utilisé pour comparer seulement des runs compatibles."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def entrainer(prepared, destination, ngram_max=2, min_df=2, seed=42):
    """Entraîne, évalue et journalise paramètres, métriques, artefact et modèle MLflow 3."""
    from contextlib import nullcontext

    import mlflow.sklearn
    from mlflow.models import infer_signature

    mlflow = suivi()
    prepared = Path(prepared)
    destination = Path(destination)
    train = pd.read_csv(prepared / "train.csv")
    test = pd.read_csv(prepared / "test.csv")
    if set(train.label) != LABELS or set(test.label) != LABELS:
        raise ValueError("Les deux jeux doivent contenir les trois classes")
    if set(train.review) & set(test.review):
        raise ValueError("Recouvrement entraînement/test")
    pipeline = construire_pipeline(ngram_max, min_df, seed)
    train_hash = empreinte(prepared / "train.csv")
    test_hash = empreinte(prepared / "test.csv")
    ctx = (
        nullcontext(mlflow.active_run())
        if mlflow.active_run()
        else mlflow.start_run(run_name=f"tfidf-logreg-ngram{ngram_max}")
    )
    with ctx as run:
        pipeline.fit(train.review, train.label)
        pred = pipeline.predict(test.review)
        destination.mkdir(parents=True, exist_ok=True)
        joblib.dump(pipeline, destination / "sentiment.joblib")
        metrics = {
            "f1_macro": float(f1_score(test.label, pred, average="macro")),
            "accuracy": float(accuracy_score(test.label, pred)),
            "n_train": len(train),
            "n_test": len(test),
        }
        mlflow.log_params(
            {
                "ngram_max": ngram_max,
                "min_df": min_df,
                "seed": seed,
                "train_sha256": train_hash,
                "test_sha256": test_hash,
            }
        )
        mlflow.log_metrics(metrics)
        info = mlflow.sklearn.log_model(
            pipeline,
            name="model",
            signature=infer_signature(train.review.to_numpy(), pipeline.predict(train.review)),
            input_example=train.review.head(2).to_numpy(),
        )
        mlflow.set_tag("tp5_model_uri", info.model_uri)
        mlflow.set_tag("tp5_protocol", "three-class-v1")
        record = {
            **metrics,
            "run_id": run.info.run_id,
            "model_uri": info.model_uri,
            "train_sha256": train_hash,
            "test_sha256": test_hash,
        }
        (destination / "metrics.json").write_text(
            json.dumps(record, indent=2) + "\n", encoding="utf-8"
        )
        mlflow.log_artifact(str(destination / "metrics.json"))
    return record


def promouvoir(
    min_f1=0.80, nom="sentiment-tp5", alias="champion", prepared=Path("data/tp5/prepared")
):
    """Promeut le meilleur run terminé du même découpage, si le seuil est atteint."""
    import math

    import mlflow
    from mlflow import MlflowClient

    if not math.isfinite(min_f1) or not 0 <= min_f1 <= 1:
        raise ValueError("Seuil de promotion entre 0 et 1 requis")
    suivi()
    client = MlflowClient()
    exp = client.get_experiment_by_name("sentiment-app-tp5")
    if exp is None:
        return {"promu": False, "raison": "Aucune expérience disponible"}
    # Ne pas comparer des scores issus d'autres données ou d'un autre protocole.
    th = empreinte(Path(prepared) / "train.csv")
    te = empreinte(Path(prepared) / "test.csv")
    runs = client.search_runs(
        [exp.experiment_id],
        filter_string=f"attributes.status = 'FINISHED' and params.train_sha256 = '{th}' and params.test_sha256 = '{te}' and tags.tp5_protocol = 'three-class-v1'",
        order_by=["metrics.f1_macro DESC", "attributes.start_time DESC"],
        max_results=1000,
    )
    eligible = [
        r
        for r in runs
        if "f1_macro" in r.data.metrics
        and r.data.tags.get("tp5_model_uri")
        and math.isfinite(r.data.metrics["f1_macro"])
    ]
    if not eligible:
        return {"promu": False, "raison": "Aucun run terminé compatible"}
    best = eligible[0]
    score = best.data.metrics["f1_macro"]
    result = {
        "promu": score >= min_f1,
        "f1_macro": score,
        "run_id": best.info.run_id,
        "min_f1": min_f1,
    }
    if not result["promu"]:
        return result
    version = mlflow.register_model(best.data.tags["tp5_model_uri"], nom)
    client.set_registered_model_alias(nom, alias, version.version)
    return {**result, "version": version.version, "uri": f"models:/{nom}@{alias}"}


def charger(path=Path("models/tp5/sentiment.joblib")):
    """Charge le modèle TP5 local ; le fichier doit provenir de ce projet."""
    return joblib.load(path)


def charger_registre(uri="models:/sentiment-tp5@champion"):
    """Charge la version désignée par champion dans le registre MLflow."""
    import mlflow.pyfunc

    suivi()
    return mlflow.pyfunc.load_model(uri)


def predire(textes, registre=False):
    """Retourne une classe par avis, avec le même format localement et via le registre."""
    if not textes or any(not isinstance(t, str) or not t.strip() for t in textes):
        raise ValueError("Avis non vides requis")
    model = charger_registre() if registre else charger()
    return list(model.predict(pd.Series(textes, dtype=object).to_numpy()))

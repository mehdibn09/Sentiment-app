"""Commandes du TP5 ; aucun changement du contrat de l’API binaire."""

import argparse
import json
from pathlib import Path

from sentiment_app.tp5 import core


def main(argv=None):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("data")
    prep = sub.add_parser("prepare")
    prep.add_argument("source", nargs="?", type=Path, default=Path("data/tp5/demo_reviews.csv"))
    train = sub.add_parser("train")
    train.add_argument("--ngram-max", type=int)
    prom = sub.add_parser("promote")
    prom.add_argument("--min-f1", type=float)
    pred = sub.add_parser("predict")
    pred.add_argument("--registre", action="store_true")
    pred.add_argument("textes", nargs="+")
    sub.add_parser("compare")
    args = parser.parse_args(argv)
    cfg = core.config()
    if args.action == "data":
        path = Path("data/tp5/demo_reviews.csv")
        path.parent.mkdir(parents=True, exist_ok=True)
        df = core.generer()
        df.to_csv(path, index=False, lineterminator="\n")
        print(f"{len(df)} avis écrits dans {path}")
        return 0
    if args.action == "prepare":
        result = core.preparer(args.source, Path("data/tp5/prepared"), **cfg["prepare"])
    elif args.action == "train":
        params = dict(cfg["train"])
        if args.ngram_max is not None:
            params["ngram_max"] = args.ngram_max
        result = core.entrainer(Path("data/tp5/prepared"), Path("models/tp5"), **params)
    elif args.action == "promote":
        result = core.promouvoir(
            args.min_f1 if args.min_f1 is not None else cfg["promote"]["min_f1"]
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["promu"] else 1
    elif args.action == "predict":
        result = core.predire(args.textes, args.registre)
    else:
        mlflow = core.suivi()
        exp = mlflow.get_experiment_by_name("sentiment-app-tp5")
        df = mlflow.search_runs([exp.experiment_id]) if exp else None
        if df is None:
            raise ValueError("Aucune expérience")
        cols = [c for c in ["run_id", "params.ngram_max", "metrics.f1_macro", "status"] if c in df]
        print(df[cols].to_string(index=False, lineterminator="\n"))
        return 0
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

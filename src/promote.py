"""Point d’entrée du TP5 MLflow/DVC."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sentiment_app.tp5.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(["promote", *sys.argv[1:]]))

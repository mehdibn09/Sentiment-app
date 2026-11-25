"""Compatibilité (TP6) : le code de prédiction vit désormais dans sentiment_app/predict.py.

Ce fichier garde valides « python src/predict.py "texte" » et « import predict » (tests, scripts).
À l'import, il se remplace par le vrai module : les deux noms désignent alors le même objet,
si bien qu'un test qui modifie predict.MODELE modifie bien celui que l'API utilise.
"""

import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1])
)  # la racine : sentiment_app, même sans installation
from sentiment_app import predict as _module  # noqa: E402

if __name__ == "__main__":
    if "--tp5" in sys.argv:
        from sentiment_app.tp5.cli import main as tp5_main

        raise SystemExit(tp5_main(["predict", *[a for a in sys.argv[1:] if a != "--tp5"]]))
    raise SystemExit(_module.main())
sys.modules[__name__] = _module

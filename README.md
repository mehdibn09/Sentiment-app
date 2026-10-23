# Sentiment-app : dépôt du binôme

Application fil rouge du cours *Développement et Déploiement d'applications intelligentes*.
Ce dépôt est enrichi chaque semaine. La semaine 1 pose le cadrage du projet et l'environnement de travail ; aucun élément n'est supprimé par la suite.

## Composition du binôme

| Rôle | Nom | Identifiant GitHub | Contribution de la semaine - (en cours) |
| --- | --- | --- | --- |
| Membre A | Mehdi Benjelloun | [@mehdibn09](https://github.com/mehdibn09) | Cadrage des trois cas d'usage et préparation de l'environnement |
| Membre B | Oussama Kamil | [@oussamak05](https://github.com/oussamak05)  | Cadrage et validation de l'environnement |

## Structure du dépôt

```text
sentiment-app/
├── README.md, MARCHE-A-SUIVRE.md, TP1-ENONCE.md, TESTS.md, AIDE-GIT.md, DEPANNAGE.md
├── Makefile              # raccourcis (optionnel)
├── requirements.txt      # dépendances du semestre, versions figées
├── requirements-dev.txt  # outils de qualité du TP4 (ruff, mypy, couverture)
├── .gitignore, .env.example, .editorconfig, pytest.ini
├── .vscode/              # interpréteur et tests préconfigurés
├── data/                 # jeux de données (versionnés avec DVC à partir de la semaine 7)
├── models/               # modèles entraînés (exclus de Git)
├── app/                  # dossier du kit TP1 (vide, conservé)
├── api/                  # API FastAPI : schémas, modèle, abstention (semaines 3 et 4)
├── src/                  # entraînement, prédiction, évaluation, courbe du seuil, jeu d'or (semaines 2 et 4)
├── ui/                   # interface Streamlit, client de l'API (semaines 3 et 5)
├── tests/                # pytest : 38 tests en semaine 1, puis API, limites, intégration, jeu d'or, interface
├── scripts/              # installation, diagnostic, création de fiche, initialisation du dépôt, clone de vérification
├── notebooks/            # variante Colab du TP1
└── docs/cadrage/         # fiches de cadrage, exemple corrigé, grille de décision, banque de cas
```

## Démarrage rapide

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell : .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Vérifiez ensuite l'installation :

```bash
python scripts/check_setup.py    # diagnostic détaillé : versions, dossiers, Git, fiches
pytest -q                        # mêmes contrôles, exécutés sous forme de tests
```

**Au premier lancement, `pytest` affiche `3 failed, 31 passed, 4 skipped`. Ce résultat est attendu.** Les trois échecs correspondent aux fiches de cadrage encore vides ; les quatre tests ignorés ne s'activeront qu'une fois le dépôt Git initialisé. En fin de TP, la même commande doit afficher `38 passed`.

Les scripts `scripts/setup.sh` (Linux, macOS, Git Bash) et `scripts/setup.ps1` (Windows) réalisent l'installation et le diagnostic en une seule commande.

## Raccourcis

Sous Linux, macOS et Git Bash, un `Makefile` évite de saisir les commandes complètes :

```bash
make setup          # environnement virtuel, dépendances, diagnostic
make check          # diagnostic seul
make test           # exécution des 38 tests
make test-cadrage   # exécution des 12 tests relatifs aux fiches
make verif URL=https://github.com/<organisation>/sentiment-app.git
make exemple-ml     # entraîne le modèle d'exemple (facultatif)
make help           # liste complète des commandes
```

## Documentation

| Fichier | Usage |
| --- | --- |
| `MARCHE-A-SUIVRE.md` | Guide à suivre en séance : huit étapes, huit contrôles et les résultats attendus |
| `TP1-ENONCE.md` | Énoncé du TP : objectifs, livrables et grille de notation |
| `TESTS.md` | Démarche de test détaillée et description des trois états de référence |
| `AIDE-GIT.md` | Commandes Git utilisées dans le TP et résolution d'un conflit |
| `DEPANNAGE.md` | Solutions aux problèmes courants |
| `docs/cadrage/GRILLE-DE-DECISION.md` | Support de la partie A pour renseigner les fiches de cadrage |
| `exemples/README.md` | À consulter après le TP : aperçu des travaux des semaines 2 et 5 |

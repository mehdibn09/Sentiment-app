# TP5 — MLflow 3 et DVC

Ce guide applique les opérations du document `TP5_complet.pdf` au dépôt Sentiment-app existant. Exécuter les commandes depuis la **racine du dépôt**, où se trouve `pyproject.toml`.

## 1. Périmètre et compatibilité

| Élément | Parcours existant | Nouveau TP5 |
| --- | --- | --- |
| Classes | positive / negative ; abstention INDETERMINE dans l’API | positif / negatif / neutre |
| Corpus | data/demo_reviews.csv | data/tp5/demo_reviews.csv |
| Modèle local | models/sentiment.joblib | models/tp5/sentiment.joblib |
| Suivi | fonctionnement existant conservé | SQLite, expérience sentiment-app-tp5 |
| Registre | aucun changement de l’API | sentiment-tp5, alias champion |
| Commande d’entraînement | python src/train.py | python src/train.py --tp5 |

Le PDF décrit un projet autonome. Les sous-dossiers et l’option `--tp5` adaptent ses commandes à ce dépôt qui possède déjà une API binaire. **Neutre est une classe apprise ; INDETERMINE est une abstention.** Les commandes sans `--tp5` restent utilisables. L’API et Streamlit continuent de charger le modèle binaire. Le nouveau registre sert les commandes TP5 ; il ne remplace pas automatiquement le modèle de l’API.

Le document contient des exemples de résultats, mais pas le générateur source complet. Le corpus synthétique fourni ici respecte 290 avis uniques, trois classes, des avis mixtes neutres et une graine fixe. Ses scores sont mesurés à nouveau ; ils ne sont pas ceux du PDF.

## 2. Installation Windows — PowerShell

Git et Python doivent être installés. Python 3.11 ou supérieur est déclaré par le projet ; la validation jointe utilise Python 3.12 sur Linux. Fermer une ancienne session utilisant un autre environnement.

```powershell
python -m venv .venv-tp5
.\.venv-tp5\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-tp5.txt -r requirements-dev.txt
python -m pip check
$env:MLFLOW_TRACKING_URI = "sqlite:///mlflow.db"
python -c "import mlflow, dvc, sklearn; print(mlflow.__version__, dvc.__version__, sklearn.__version__)"
```

`requirements-tp5.txt` installe le paquet avec les extensions `ui` et `mlops`, dont MLflow 3. `requirements.lock` correspond à l’ancien parcours TP6 et ne décrit pas cet environnement MLOps.

Sous Linux/macOS, remplacer les deux premières commandes par :

```bash
python3 -m venv .venv-tp5
source .venv-tp5/bin/activate
export MLFLOW_TRACKING_URI=sqlite:///mlflow.db
```

## 3. Git, données et DVC

Un clone Git possède déjà son historique : **ne pas recréer le dépôt**. Pour une copie sans Git, exécuter `git init`, ajouter les fichiers et créer un premier commit avec sa propre identité. Les métadonnées `.dvc/` sont livrées ; `dvc init` ne sert que lorsqu’elles sont absentes. Ne pas lancer `dvc init --force` sur une configuration existante.

```powershell
python src/make_demo.py --tp5
dvc add data/tp5/demo_reviews.csv
git add data/tp5/.gitignore data/tp5/demo_reviews.csv.dvc .dvc .dvcignore
```

Résultat : **290 avis**, dont 80 positifs, 80 négatifs et 130 neutres ; les avis mixtes sont neutres. Le CSV se régénère ; Git suit son pointeur `.dvc`. La graine et les fins de ligne sont fixes.

Le stockage local est un exercice de synchronisation, pas une sauvegarde hébergée par GitHub :

```powershell
New-Item -ItemType Directory -Force ../sentiment-app-dvc-remote
dvc remote add -d local ../sentiment-app-dvc-remote
dvc push
git add .dvc/config
```

Si le nom `local` existe déjà, modifier son URL avec `dvc remote modify local url <chemin>`. Sur un autre poste, le dossier remote doit être accessible ; sinon régénérer le CSV avec la même commande. Le ZIP ne contient ni cache DVC ni stockage distant.

## 4. Pipeline reproductible

```powershell
dvc repro
dvc dag
dvc metrics show
dvc repro
```

`prepare` nettoie les espaces, retire les avis vides et les doublons, refuse les labels contradictoires et produit **217 avis d’entraînement et 73 de test**, par stratification. Le vocabulaire TF-IDF est appris uniquement sur l’entraînement.

`train` entraîne TF-IDF + régression logistique et journalise paramètres, F1 macro, exactitude, effectifs, empreintes SHA-256, métriques JSON et modèle MLflow. Les URI `models:/m-...` identifient les modèles journalisés de MLflow 3. La seconde exécution sans changement doit indiquer que les étapes sont à jour.

Lors du premier démarrage à partir de ce ZIP, les sorties mises en cache n’existent pas encore sur ton poste : leur recalcul est normal. Un ancien fichier SQLite ou un cache DVC ne remplace pas les artefacts MLflow. Après récupération de sorties DVC sans les artefacts MLflow associés, créer de nouveaux runs avec `python src/train.py --tp5` avant de promouvoir.

## 5. Trois expériences et exécution sélective

Créer un commit de référence contenant les fichiers TP5 avant les expériences :

```powershell
git add .
git commit -m "TP5 : donnees, pipeline et suivi MLflow"
dvc exp run --set-param train.ngram_max=1
dvc exp run --set-param train.ngram_max=3
git restore params.yaml
dvc repro
python -m sentiment_app.tp5.cli compare
dvc exp show --only-changed
```

`dvc exp run` applique ses paramètres au dossier de travail. `git restore params.yaml` revient au dernier commit : ne pas l’utiliser si ce fichier contient d’autres modifications à conserver.

Modifier ensuite seulement `train.min_df`, de 2 à 3, dans `params.yaml`, puis lancer `dvc repro`. Seule l’étape `train` doit repartir. Relancer : rien ne change. Restaurer `min_df: 2`, puis rejouer `dvc repro`.

Pour consulter MLflow dans un second terminal activé :

```powershell
mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000
```

Ouvrir `http://127.0.0.1:5000`, sélectionner `sentiment-app-tp5`, puis comparer les runs. La base et les artefacts sont locaux ; ils ne sont pas envoyés sur GitHub.

## 6. Promotion et prédiction

```powershell
python src/promote.py
python src/predict.py --tp5 "Excellent produit, je recommande." "Produit casse."
python src/predict.py --tp5 --registre "Excellent produit, je recommande."
```

La promotion sélectionne le meilleur F1 macro parmi les runs terminés du même découpage et du même protocole. Elle enregistre une version dans `sentiment-tp5` et pose l’alias `champion` si le seuil `promote.min_f1` est atteint. Le seuil par défaut est 0,80. Les métriques d’un corpus différent ne sont pas comparées.

Tester un refus avec le seuil plus élevé suivant :

```powershell
python src/promote.py --min-f1 1.0
$LASTEXITCODE
```

Pour le corpus livré, le meilleur score est inférieur à 1 : code **1**, sans création de version et sans déplacement de l’alias existant. Un score parfait sur un autre corpus pourrait légitimement passer ce seuil. Le seuil 0,85 proposé dans le PDF n’entraîne pas un refus ici, car les scores mesurés le dépassent. `--min-f1` évite de modifier durablement `params.yaml`.

Le modèle local est celui du dernier entraînement. `champion` désigne le meilleur run compatible : les deux chemins peuvent donc charger des modèles différents après plusieurs essais.

## 7. Bonus — MLflow Projects

```powershell
mlflow run . -e train -P ngram_max=3 --experiment-name sentiment-app-tp5 --env-manager local
```

Exécuter la préparation avant cette commande. `MLproject` décrit un entraînement paramétré ; `dvc.yaml` décrit les dépendances, le nettoyage et l’entraînement. MLflow Projects réutilise le run qu’il ouvre, sans créer un second run imbriqué. Après ce bonus, relancer `dvc repro --force train` pour remettre les sorties locales en accord avec les paramètres DVC de référence.

## 8. Tests et livrable GitHub

```powershell
python src/make_demo.py
python src/train.py
python src/expliquer.py
python src/biais.py
python -m pytest tests/test_tp5_mlops.py -q
python -m pytest -q
ruff check sentiment_app src/predict.py src/prepare.py src/promote.py tests/test_tp5_mlops.py
mypy api
python -m build
```

Les quatre premières commandes préparent les sorties attendues par les anciens tests du projet. Le nouveau module comporte 30 tests. Le dépôt conserve trois tests `xfail` documentant les limites du modèle binaire. Les contrôles d’historique Git vérifient les contributions réelles du binôme ; ils ne sont pas remplacés par des contributions artificielles.

Versionner le code, les tests, `params.yaml`, `dvc.yaml`, `dvc.lock`, les fichiers `.dvc`, la configuration partageable et le rapport. Exclure les environnements, les modèles sérialisés, le cache DVC, la base SQLite, `mlruns/`, les clés et `.env`.

```powershell
git status --short
git add .
git commit -m "TP5 : validation, rapport et integration MLOps"
git push origin main
```

Chaque étape doit recevoir tes propres commits dans ton dépôt. Copier une archive ne reconstitue pas rétroactivement un historique de travail. Pour les fichiers commençant par un point, utiliser Git depuis le dossier local ; le formulaire d’upload GitHub peut les masquer.

## 9. Correspondance avec le PDF

| Opérations du PDF | Implémentation |
| --- | --- |
| Génération, nettoyage, split | sentiment_app/tp5/core.py ; src/make_demo.py --tp5 ; src/prepare.py |
| Pipeline, paramètres, état | dvc.yaml ; params.yaml ; dvc.lock |
| Tracking et comparaison | core.entrainer ; python -m sentiment_app.tp5.cli compare |
| Meilleur run, seuil, alias | core.promouvoir ; src/promote.py |
| Chargement local et registre | core.charger ; core.charger_registre ; src/predict.py --tp5 |
| MLflow Projects | MLproject ; python_env.yaml |
| Tests et rapport | tests/test_tp5_mlops.py ; RAPPORT.md ; docs/tp5/ |

Références : [MLflow](https://mlflow.org/docs/latest/) et [DVC](https://dvc.org/doc).

### Organiser les commits du TP5

Sur un dépôt déjà initialisé, les groupes suivants séparent les étapes du livrable. Exécuter ces commandes après intégration et validation des fichiers ; ne pas créer de commit vide si l’étape est déjà enregistrée.

```powershell
git add .dvc .dvcignore .gitignore pyproject.toml requirements.txt requirements-tp5.txt
git commit -m "TP5 : initialisation MLflow 3 et DVC"
git add data/tp5
git commit -m "TP5 : versionnement du corpus avec DVC"
git add sentiment_app/tp5 src/make_demo.py src/train.py src/predict.py src/prepare.py src/promote.py params.yaml dvc.yaml dvc.lock models/tp5/metrics.json MLproject python_env.yaml MANIFEST.in
git commit -m "TP5 : pipeline, suivi et registre de modeles"
git add tests/test_tp5_mlops.py tests/test_client.py .github/workflows/ci.yml README.md TP5-MLOPS.md RAPPORT.md CHANGELOG.md docs/journal-tp1-tp6.md docs/tp5
git commit -m "TP5 : tests, CI et rapport de validation"
```

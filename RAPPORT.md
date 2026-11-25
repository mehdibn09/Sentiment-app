# Rapport TP5 — MLflow 3 et DVC

Validation locale du 25 novembre 2026 — Sentiment-app, extension MLOps.

## 1. Intégration et données

L’extension est isolée dans `sentiment_app/tp5/`, `data/tp5/` et `models/tp5/`. L’option `--tp5` conserve les commandes du modèle binaire existant. L’expérience s’appelle `sentiment-app-tp5` ; le registre `sentiment-tp5` utilise l’alias `champion`. Dans l’API existante, `INDETERMINE` signifie une abstention ; dans ce TP, `neutre` est une troisième classe.

Le générateur produit 290 avis synthétiques uniques : 80 positifs, 80 négatifs et 130 neutres, dont les avis mixtes. Le code exact du générateur du cours n’étant pas fourni dans le PDF, les formulations et les scores diffèrent de ses exemples. Le nettoyage retire valeurs manquantes, blancs et doublons, normalise les espaces et refuse les labels contradictoires. La séparation stratifiée, avec graine 42 et 25 % de test, donne 217/73 avis sans recouvrement. TF-IDF est ajusté uniquement sur l’entraînement.

## 2. Trois essais réellement exécutés

Même découpage, `min_df=2`, régression logistique et graine 42. L’environnement exact et les empreintes des fichiers figurent dans `docs/tp5/`.

| ngram_max | F1 macro | Exactitude | Identifiant MLflow local |
| --- | --- | --- | --- |
| 1 | 0.9040 | 0.9041 | `73a020a36b5147248160e72dad617ea0` |
| 2 | 0.8893 | 0.8904 | `9ebbf8a350fc41f7a885dccb67e286ae` |
| 3 | 0.8762 | 0.8767 | `4390e508247847538d8473fb44b3d31a` |

Les expériences n=1 et n=3 ont été exécutées avec `dvc exp run --set-param`. La référence n=2 a été réentraînée après restauration des paramètres. Chaque run enregistre paramètres, scores, effectifs, empreintes SHA-256, `metrics.json` et modèle MLflow 3 avec signature. Les identifiants ci-dessus sont ceux de cette validation ; la base SQLite et les artefacts restent locaux. Une nouvelle exécution crée de nouveaux identifiants.

**Réflexion.** Sur ce petit corpus, les unigrammes obtiennent le meilleur score. Les expressions longues augmentent le vocabulaire et peuvent être trop rares pour généraliser. Les avis mixtes, l’équilibre des classes et le seuil de fréquence des termes influencent aussi le résultat. Trois mesures sur un même jeu de test ne suffisent pas à établir une supériorité générale ; une évaluation finale devrait utiliser une validation croisée et un jeu de test indépendant.

## 3. Promotion et prédiction

Le meilleur run terminé du même découpage est sélectionné, puis comparé au seuil 0,80. Ce seuil pédagogique autorise la démonstration du registre ; il ne constitue pas une exigence de production justifiée sur des avis réels. Les empreintes et le tag de protocole évitent de comparer des scores issus d’autres données.

La promotion à 0,80 a réussi avec F1=0,9040, version 1 et alias `champion`. Le refus a été vérifié avec 1,00 : code de sortie 1 et alias conservé, également couvert par un test d’intégration. Le seuil 0,85 du PDF ne provoque pas un refus avec ce corpus. Aucune métrique n’a été diminuée pour simuler ce résultat.

Les prédictions locale et registre ont été exécutées sur deux avis explicites et ont retourné `positif` puis `negatif`. Après plusieurs entraînements, le modèle local représente le dernier run, tandis que le registre désigne le meilleur run promu : leur égalité n’est pas garantie.

## 4. Reproductibilité DVC et bonus

Le CSV est identifié par `data/tp5/demo_reviews.csv.dvc`. `dvc.yaml` déclare les dépendances, paramètres et sorties de `prepare` et `train` ; `dvc.lock` contient les empreintes obtenues. Un remote local a été utilisé pour vérifier `dvc push` puis `dvc pull` : le CSV récupéré est identique octet par octet. Le chemin propre au poste de validation n’est pas livré.

Une seconde commande `dvc repro` sans changement n’a relancé aucune étape. Modifier seulement `train.min_df` de 2 à 3 a relancé uniquement `train`. Le F1 mesuré est resté 0,8893 ; l’effet d’un paramètre n’est pas nécessairement une variation du score. Les paramètres ont ensuite été restaurés.

**Bonus.** La commande `mlflow run . -e train -P ngram_max=3 --experiment-name sentiment-app-tp5 --env-manager local` a réussi avec F1=0,8762. Le run créé par MLflow Projects a été réutilisé. `MLproject` définit un point d’entrée et un environnement d’entraînement ; DVC déclare aussi la préparation, les dépendances, les sorties, leur cache et l’exécution sélective. L’un ne remplace donc pas l’autre pour reproduire tout le pipeline.

## 5. Contrôles et limites

```text
python -m pytest tests/test_tp5_mlops.py -q
30 passed

python -m pytest -q --ignore=tests/test_git_history.py --cov=api --cov-fail-under=95
184 passed, 3 xfailed, 11 warnings
Couverture de l’API : 100 %
```

Ruff, mypy sur l’API, `pip check` et la construction roue/archive source passent. Les trois `xfail` documentent des limites connues du modèle binaire. Les avertissements viennent des dépendances, notamment de l’ancien solveur scikit-learn avec SciPy récent ; ils ne sont pas des échecs de tests. Les tests d’historique Git ont été exclus de ce bilan : les contributions du binôme doivent être vérifiées dans son vrai dépôt. Aucun historique utilisateur ni résultat GitHub Actions n’est certifié ici.

Validation effectuée dans un environnement Python 3.12 neuf sur Linux, avec MLflow 3.18.0, DVC 3.67.1 et scikit-learn 1.5.2. Le lancement sur le poste Windows du binôme et l’exécution de la CI après push restent à effectuer. Le corpus synthétique démontre le fonctionnement du pipeline, sans établir sa qualité sur des avis de production.

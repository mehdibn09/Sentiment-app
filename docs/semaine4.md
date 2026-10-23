# Semaine 4 : tests approfondis et qualité du code (notes du binôme)

> Deux pages maximum. Seuls les chiffres issus de nos propres exécutions sont admis.
> Modèle : jeu de démonstration (290 avis, `python src/make_demo.py` puis `python src/train.py`), scikit-learn 1.5.2.

## 1. Couverture des tests

- **Point de départ (étape A)** : couverture de `api/` à **91 %** (6 tests du TP3), avec **6 lignes jamais exécutées**, toutes dans `api/main.py` : 49, 77-79, 85-87.
- **Comportements non vérifiés** :
  - ligne 49 : `_classifier()` répond 503 quand le modèle n'est pas chargé ; aucun test ne retirait le modèle ;
  - lignes 77-79 : la branche `except Exception` renvoie 500 sans exposer le message interne ; aucun test ne faisait tomber le modèle ;
  - lignes 85-87 : le lancement manuel d'uvicorn (`if __name__ == "__main__"`).
- **Point d'arrivée (étape D)** : couverture de **100 %** (90 instructions), 95 tests passés, 3 `xfail` (jeu d'or).
- **Lignes exclues de la mesure** : une seule, le bloc `if __name__ == "__main__":` de `api/main.py` (`# pragma: no cover`). Il ne contient que le lancement d'uvicorn pour un usage manuel, impossible à exécuter dans un test sans ouvrir un port. Sans cette exclusion : **98 %**.

## 2. Défauts mis au jour

| Symptôme observé | Test qui l'a révélé | Correctif appliqué |
| --- | --- | --- |
| `{"text": "   "}` reçoit bien 422, mais `detail` est la chaîne `"texte vide"` (produite par `predict()` du TP2) au lieu de la liste standard `loc`, `msg`, `type` de FastAPI | `test_limites.py::test_frontieres_du_contrat[espaces]` | `field_validator` dans `PredictRequest` : refus d'un texte vide une fois ses blancs retirés (`str.strip()`, même règle que `predict()`) |
| Même défaut avec des blancs rares : hypothesis trouve le contre-exemple `'\x85'` (saut de ligne Unicode que `strip()` retire) | `test_limites.py::test_texte_de_blancs_recoit_422` | Même correctif : la règle du schéma est celle de `predict()` |
| Un `ValueError` levé par le modèle répond **422 avec son message interne** (`{"detail":"bug interne"}`) au lieu de 500 | `test_integration.py::test_modele_en_panne_repond_500_sans_fuite[ValueError]` | Suppression de la branche `except ValueError` de `api/main.py` : le schéma garantit déjà un texte non vide |
| Un texte de mots inventés (`xqzvb wlkptr grombu`) reçoit `NEGATIVE` avec 52 % de confiance, présenté comme un verdict | `test_api.py::test_predict_mots_inventes_indetermine` | Seuil d'abstention : sous `SEUIL_ABSTENTION` (0,60), l'étiquette devient `INDETERMINE`, le score reste renvoyé |
| Une classe inattendue du modèle (par exemple `neutral`) aurait fait planter `.upper()` ou renvoyé une étiquette hors contrat | `test_integration.py::test_classes_inattendues_empechent_le_demarrage` | Correspondance explicite `CORRESPONDANCE` et vérification des classes au démarrage |

## 3. Seuil d'abstention

- **Jeu de mesure** : jeu de test du TP2, **58 avis** (source : demo), modèle entraîné sur les mêmes données (aucun avertissement « ATTENTION » affiché).
- **Points de la courbe** (`python src/courbe_seuil.py`) :

| Seuil | Répond à | Part | Exactitude | Erreurs | Vers un humain |
| --- | --- | --- | --- | --- | --- |
| 0,50 | 58 | 100 % | 0,879 | 7 | 0 |
| 0,60 | 42 | 72 % | 0,952 | 2 | 16 |
| 0,75 | 29 | 50 % | 1,000 | 0 | 29 |

- **Seuil retenu** : 0,60 ; part des avis envoyés à un humain : **28 %** (soit 16 avis sur 58).
- **Justification** : en passant de 0,50 à 0,60, l'exactitude gagne 7,3 points (5 erreurs sur 7 évitées) pour 16 avis envoyés à un humain. En passant de 0,60 à 0,75, elle gagne encore 4,8 points (les 2 dernières erreurs) mais 13 avis supplémentaires partent vers un humain : la moitié des avis ne serait plus traitée automatiquement. Nous retenons 0,60, le seuil où la courbe cesse d'être rentable. Ce choix est aussi celui de l'interface du TP3.

## 4. Jeu d'or

- **Composition** : 20 avis, dont 11 positifs et 9 négatifs. Cas simples : 8. Cas pièges : 12 (négation 4, mitigé 5, ironie 3).
- **Bilan** (`python src/bilan_jeu_or.py`) : justes **4**, abstentions **13**, erreurs franches déclarées **3**, erreurs franches non déclarées **0**.
- **Détail par catégorie** : cas simples 1/8 justes ; négation 0/4 ; mitigé 2/5 ; ironie 1/3.
- **Ce que ces chiffres disent du modèle** :
  - Ironie : aucune erreur franche, contrairement à ce que nous attendions. Un avis est classé juste (« Génial, un produit qui tombe en panne… », que « panne » fait basculer en négatif), les deux autres (« Parfait, le colis… », « Top, le livreur… ») tombent à 0,57 de confiance et partent vers un humain.
  - Négation : 0/4 justes. « Absolument pas déçu » et « Pas mécontent du tout » sont des erreurs franches déclarées : « pas » n'est qu'un mot isolé du sac de mots. Les deux autres avis s'abstiennent.
  - Mitigé : 2/5 justes, une erreur franche déclarée (« Livraison rapide mais article non fonctionnel »), deux abstentions.
  - Cas simples : seulement 1/8 justes, 7 abstentions. Avec 290 avis d'entraînement, le modèle connaît peu de vocabulaire : il hésite presque toujours sur des phrases hors de son jeu. Il se tait au lieu de se tromper, ce qui est le but de l'abstention, mais il serait peu utile en production.

## 5. Outils statiques

- **Alertes initiales** : ruff : **12**, mypy : **0**.
- **Recoupement avec la partie 2** : sur les 5 défauts listés, ruff et mypy n'en avaient signalé **aucun**. Les 12 remarques de ruff (imports non triés, `zip()` sans `strict`, variable `l`, import inutilisé, `raise` sans `from`) étaient réelles mais sans rapport avec ces défauts.
- **Conclusion** : les outils statiques détectent le style, les imports et les types ; ils laissent passer les erreurs de logique (fuite d'un message interne, règle « texte vide » définie à deux endroits), les cas limites et le comportement du modèle. Seuls les tests les ont trouvés. Après correction : `ruff check .` et `mypy api` sont muets.

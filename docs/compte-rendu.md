# Compte rendu global — TP1 à TP3

**Binôme :** Mehdi Benjelloun ([@mehdibn09](https://github.com/mehdibn09)) et Oussama Kamil ([@Oussamak05](https://github.com/oussamak05))
**Dépôt :** https://github.com/mehdibn09/sentiment-app
**Date de remise :** 14 octobre 2026
**Étiquette Git :** `compte-rendu`

---

## 1. Le besoin et son cadrage

Nous avons traité les trois cas proposés à l'aide de la grille de décision, fondée sur quatre critères : (a) disponibilité de données étiquetées, (b) vérifiabilité de la réponse, (c) coût par requête, (d) conséquence d'une erreur.

**Cas 1 — Ordonnances incomplètes (`cas1-pharmacie.md`) : règles métier.** Aucune étiquette n'est disponible pour entraîner un modèle (a), les autorités de santé exigent une décision explicable (b) et une erreur peut nuire gravement au patient (d). Une logique déterministe écrite à la main est ici la seule approche défendable.

**Cas 2 — Règlement intérieur (`cas2-reglement.md`) : RAG.** L'utilisateur attend une réponse qui cite l'article exact (b), il n'existe pas d'étiquettes (a) et le volume de requêtes reste faible (c), ce qui rend acceptable le coût d'un appel à un LLM.

**Cas 3 — Avis négatifs (`cas3-avis-negatifs.md`) : machine learning.** Les étiquettes sont quasi gratuites : une note de 1 à 2 étoiles correspond à un avis négatif, une note de 4 à 5 étoiles à un avis positif (a). Le volume est massif, de l'ordre de plusieurs milliers d'avis par jour (c). Enfin, une erreur est tolérable (d) : un avis mécontent classé positif est traité avec quelques heures de retard, sans conséquence légale.

Le cas 3 est devenu notre fil rouge pour les TP2 et TP3.

---

## 2. L'architecture du dépôt

Le dépôt `sentiment-app` suit une structure imposée : `src/` pour les scripts, `tests/` pour pytest, `ui/` pour Streamlit, `models/` pour les artefacts, `docs/` pour la documentation et les fiches.

**Ce qui se versionne dans une application intelligente.** Un logiciel classique ne versionne que le code. Ici, il faut distinguer ce qui se reconstruit de ce qui doit être conservé :

| Élément | Dans Git ? | Raison |
|---|---|---|
| Le code (`src/`, `ui/`, `tests/`) | Oui | C'est le travail produit |
| L'environnement (`.venv/`) | Non | Reconstructible via `pip install -r requirements.txt` |
| Les données (`data/demo_reviews.csv`) | Non | Reconstructibles via `python src/make_demo.py` |
| Le modèle (`models/sentiment.joblib`) | Non | Fichier binaire volumineux, reconstructible via `python src/train.py` |
| **La mesure** (`models/metrics.json`) | **Oui** | Petit fichier texte, lisible, comparable d'un commit à l'autre |

**Pourquoi `metrics.json` est-il dans Git alors que `sentiment.joblib` ne l'est pas ?** Le modèle est un binaire lourd, illisible dans un `git diff`, que le code, les données et la graine aléatoire suffisent à régénérer. La mesure, elle, est minuscule et textuelle : la versionner garde la trace des performances à chaque étape et permet de voir ce qu'un changement de code a modifié.

Ce tableau a guidé la rédaction de notre `.gitignore` et a été confirmé par le contrôle T3 : aucune ligne `.venv/` n'apparaît dans `git status`.

L'environnement est figé en Python 3.11 (`py -3.11 -m venv .venv`). Le script `scripts/setup.ps1` refait toute l'installation en une commande sur un poste vierge (contrôle T4 : `0 erreur(s)`).

---

## 3. Le modèle

Le modèle du TP2 est un `Pipeline` scikit-learn qui enchaîne deux étapes :

1. **`TfidfVectorizer`** (unigrammes et bigrammes, `min_df=2`, `sublinear_tf=True`) : transforme chaque avis en un vecteur de fréquences de mots pondérées.
2. **`LogisticRegression`** (`class_weight="balanced"`) : classifieur linéaire rapide qui fournit des probabilités (`predict_proba`), indispensables pour la confiance affichée et le seuil d'incertitude du TP3.

Trois choix de conception méritent d'être soulignés :

- **Découpage avant vectorisation.** `train_test_split` est appliqué avant toute transformation du texte. Dans le cas contraire, le vocabulaire du jeu de test « fuirait » dans l'entraînement et la mesure serait faussée.
- **Un seul objet pour tout le traitement.** Le `Pipeline` regroupe vectoriseur et modèle : `joblib.dump` et `joblib.load` sauvegardent et rechargent l'ensemble d'un coup, sans risque d'oublier une étape.
- **Reproductibilité.** Avec `random_state=42`, deux exécutions sur les mêmes données produisent le même découpage et le même résultat.

| Jeu | Avis d'entraînement | Avis de test | Vocabulaire | F1 macro | Exactitude | Rappel négatif |
| --- | --- | --- | --- | --- | --- | --- |
| Démonstration | 232 | 58 | 316 | 0,879 | 0,879 (51/58) | [à compléter] |
| Allociné | 16 000 | 4 000 | 149 529 | 0,920 | [à compléter] | [à compléter] |

Le modèle n'a pas changé entre les deux lignes : seules les données diffèrent. C'est l'enseignement le plus net du TP2.

**Matrice de confusion (jeu de démonstration).** [à coller, puis commenter ligne par ligne : vrais négatifs, faux positifs, faux négatifs, vrais positifs.]

---

## 4. L'analyse des erreurs

Sur le jeu de démonstration, `evaluate.py` relève **7 erreurs sur 58** :

- **5 faux négatifs** : des avis positifs classés négatifs.
- **2 faux positifs** : des avis négatifs classés positifs. Ce sont les plus coûteux pour le métier, car un client mécontent serait pris en charge avec retard.

**Toutes les erreurs portent sur des avis mitigés.** Exemple tiré de nos données :

> *« Taille trop petite et retour payant au déballage, sauf que ensuite produit conforme à la description. »*
> Étiquette réelle : positif. Prédiction : négatif.

**Mécanisme.** Un sac de mots ignore l'ordre : « bon puis mauvais » et « mauvais puis bon » produisent le même vecteur. Or, dans notre jeu de démonstration, les avis mitigés comportent un retournement (« sauf que ensuite… ») et l'étiquette suit la seconde moitié. Le modèle, qui voit surtout beaucoup de mots négatifs, ne peut pas deviner que la conclusion est positive.

**Corrections possibles.**
1. Des **n-grammes plus longs** (1-3 au lieu de 1-2) pour capter un peu plus de contexte local.
2. Un **transformer** (DistilBERT, CamemBERT), qui tient compte de la position des mots et peut accorder plus de poids à la conclusion.
3. Un **ensemble** de modèles, ou un classifieur supplémentaire entraîné sur les 200 derniers caractères.

Ces pistes dépassaient l'objectif de la séance : mettre en place un modèle de référence simple et en comprendre les limites.

---

## 5. L'interface et le seuil d'incertitude

L'interface du TP3 (`ui/helpers.py`) utilise `SEUIL_INCERTITUDE = 0.60`. En dessous de 60 % de confiance, elle n'affiche pas de verdict tranché mais **« À vérifier par un agent »**, en orange.

Sur les 290 avis du jeu de démonstration, **69 avis** sont envoyés à un agent (environ **23,8 %**), pour 145 négatifs réels (le modèle en détecte 147).

| Seuil | Avis envoyés à un agent | Risque |
|---|---|---|
| 0,50 | 0 | Le modèle tranche seul des cas qu'il ne maîtrise pas |
| **0,60** | **69 (23,8 %)** | **Compromis retenu** |
| 0,75 | 137 (47,2 %) | La file humaine se remplit, l'automatisation perd son intérêt |

Nous conservons **0,60** parce qu'il limite le renvoi aux cas réellement douteux tout en rendant visible l'hésitation du modèle. Afficher un verdict tranché à 51 % de confiance reviendrait à mentir par omission. Ce curseur ne se décide d'ailleurs pas uniquement dans le code : il se fixe avec l'équipe relation client, seule à connaître sa capacité à traiter des cas à la main.

---

## 6. Ce qui a échoué

Trois incidents notables, documentés dans la section 8 de l'énoncé :

1. **Contrôle T5 (deux auteurs distincts).** Le test est resté bloqué à `1 failed, 41 passed` : Git ne voyait qu'un seul auteur, Mehdi. Oussama n'avait pas encore commité depuis son poste. Nous avons configuré `git config --global user.name` sur son poste, puis poussé un commit. `git shortlog -sn --all` affiche désormais deux noms.
2. **Chemins imbriqués des kits.** L'archive `tp1-tp2-tp3.zip` crée un dossier du même nom à l'intérieur d'elle-même (`tp1-tp2-tp3\tp1-tp2-tp3\`), de même pour `sentiment-app` et `tp3-streamlit-kit`. Nous avons perdu du temps à chercher `appliquer_tp2.py` et `appliquer_tp3.py`. Règle retenue : faire un `dir` avant chaque commande et utiliser `..\sentiment-app\sentiment-app` pour installer un kit.
3. **Push des captures d'écran (HTTP 408).** Après l'ajout de deux PNG, `git push` a échoué deux fois avec `RPC failed; HTTP 408`. Nous avons exécuté `git config --global http.postBuffer 524288000` puis `git config --global http.version HTTP/1.1` ; le troisième essai a abouti.

Ces échecs ne se voient pas sur un dépôt propre, mais ils représentent une part réelle du temps de travail.

---

## 7. Ce que nous ferions autrement

Par ordre d'importance :

1. **Un modèle sensible à l'ordre.** Nos 7 erreurs viennent toutes de l'insensibilité du sac de mots à l'ordre. Un transformer français (CamemBERT, DistilBERT) les réduirait. Contrepartie : un entraînement qui passe de quelques secondes à plusieurs minutes sur CPU, et un modèle de plusieurs centaines de Mo, à héberger hors de Git.
2. **Un seuil d'incertitude adaptatif.** Plutôt qu'un seuil global fixe, tenir compte de la longueur de l'avis et de l'écart entre les deux scores : un avis court et ambigu est plus suspect qu'un avis long et net.
3. **Un historique des mesures.** `models/metrics.json` est écrasé à chaque entraînement. Conserver des versions datées (par exemple `metrics-2026-10-14.json`) permettrait de suivre la dérive dans le temps et préparerait la partie MLOps des semaines suivantes.

Côté méthode, nous retenons aussi de vérifier le dossier courant avant chaque commande et de lire la ligne qui suit un code d'erreur : `Password authentication is not supported` relève de l'authentification, `403 Forbidden` de l'autorisation.

---

## 8. Répartition du travail

| Membre | TP1 | TP2 | TP3 |
|---|---|---|---|
| **Mehdi Benjelloun** | Création du dépôt, structure, trois fiches de cadrage, environnement, premier push | `docs/semaine2.md`, entraînement Allociné, analyse des erreurs | Commit des captures, réglages Git (`http.postBuffer`) |
| **Oussama Kamil** | Une fiche, vérification de l'installation sur un second poste, commit de validation (T5) | Évaluation du modèle, mesure du F1, vérification du `.gitignore` | `docs/semaine3.md`, tests de l'interface (S1, S2, S3) |

Le dépôt est propre, l'étiquette `compte-rendu` fige la version remise et la CI est verte sur les trois séances (42, puis 45 tests). Nous avons travaillé ensemble sur les séances 1 et 2, puis en alternance sur la séance 3 pour couvrir à la fois le code et la documentation.

---

## Outils d'aide à la rédaction

[À adapter] Nous avons utilisé un assistant d'IA pour reformuler certains textes et relire la structure de ce compte rendu. Nous avons nous-mêmes exécuté le code, relevé les chiffres et vérifié leur cohérence avec le dépôt.

# Compte rendu global — TP1 à TP3

**Binôme :** Mehdi Benjelloun (@mehdibn09) & Oussama Kamil
**Dépôt :** https://github.com/mehdibn09/sentiment-app
**Date de remise :** 14 octobre 2026
**Étiquette Git :** `compte-rendu`

---

## 1. Cadrage 

Nous avons traité les trois cas proposés en appliquant la grille de décision (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur.

**Cas 1 — Ordonnances incomplètes (`cas1-pharmacie.md`)** : nous avons retenu les **règles métier**. Il n'existe pas d'étiquettes pour entraîner un modèle (a), l'explicabilité est exigée par les autorités de santé (b), et une erreur peut avoir des conséquences graves pour le patient (d). Une logique déterministe écrite à la main est ici la seule approche défendable.

**Cas 2 — Règlement intérieur (`cas2-reglement.md`)** : nous avons retenu le **RAG**. L'utilisateur attend une réponse citant l'article exact (b), il n'y a pas d'étiquettes disponibles (a) et le volume de requêtes reste faible (c), ce qui rend le coût d'un appel LLM acceptable.

**Cas 3 — Avis négatifs (`cas3-avis-negatifs.md`)** : nous avons retenu le **machine learning**. Les étiquettes sont gratuites (une note 1–2 étoile = négatif, 4–5 = positif) (a), le volume est massif (des milliers d'avis par jour) (c), et une erreur reste peu grave (d) : un avis mécontent classé positif est simplement traité quelques heures plus tard, sans conséquence légale.

Le cas 3 est devenu notre fil rouge pour les TP2 et TP3.

---

## 2. Architecture et environnement 

Le dépôt `sentiment-app` suit une structure imposée : `src/` pour les scripts, `tests/` pour pytest, `ui/` pour Streamlit, `models/` pour les artefacts, `docs/` pour la documentation et les fiches.

**Trois artefacts, pas un.** C'est la leçon centrale du module. Un logiciel classique versionne le code. Une application intelligente en versionne trois :

| Artefact | Dans Git ? | Raison |
|---|---|---|
| Le code (`src/`, `ui/`, `tests/`) | Oui | C'est le travail |
| L'environnement (`.venv/`) | Non | Reconstructible via `pip install -r requirements.txt` |
| Les données (`data/demo_reviews.csv`) | Non | Reconstructible via `python src/make_demo.py` |
| Le modèle (`models/sentiment.joblib`) | Non | Reconstructible via `python src/train.py` |
| **La mesure** (`models/metrics.json`) | **Oui** | Elle ne se reconstruit pas sans réentraîner |

Ce tableau a guidé nos choix de `.gitignore` et a été confirmé par le contrôle T3 : aucune ligne `.venv/` dans `git status`.

L'environnement est figé en Python 3.11 (`py -3.11 -m venv .venv`) et les dépendances sont installées via `pip install pandas scikit-learn pytest streamlit`. Le script `scripts/setup.ps1` refait toute l'installation en une commande sur un poste vierge (contrôle T4 : `0 erreur(s)`).

---

## 3. Modèle 

Le modèle du TP2 est un `Pipeline` scikit-learn qui enchaîne :

1. **`TfidfVectorizer`** (unigrammes et bigrammes, `min_df=2`, `sublinear_tf=True`) — transforme chaque avis en un vecteur de fréquences de mots pondérées.
2. **`LogisticRegression`** (`class_weight="balanced"`) — classifieur linéaire rapide, qui fournit des probabilités (`predict_proba`) : indispensables pour la confiance affichée et le seuil d'incertitude du TP3.

Trois points du code méritent d'être soulignés :

- **`train_test_split` avant toute vectorisation.** Le découpage est fait *avant* de transformer le texte en vecteurs. Si on vectorisait d'abord, le vocabulaire du jeu de test « fuiterait » dans l'entraînement et la mesure serait fausse.
- **Le `Pipeline` enferme vectoriseur et modèle dans un seul objet.** On peut ainsi sauvegarder (`joblib.dump`) et recharger (`joblib.load`) l'ensemble d'un coup, sans risque d'oublier une étape.
- **`random_state=42`.** Le découpage aléatoire est reproductible : deux exécutions sur le même jeu de données donnent le même résultat.

Sur le **jeu de démonstration** (`make_demo.py`), le modèle obtient un F1 macro de **0,879** sur 58 avis de test, avec 232 avis d'entraînement et 316 termes de vocabulaire.

Sur le **jeu Allociné** (`train.py --allocine`), le même modèle atteint **0,920** sur 4 000 avis de test, avec 16 000 avis d'entraînement et 149 529 termes de vocabulaire.

Le modèle n'a pas changé : ce sont les données. C'est la démonstration la plus parlante du TP2.

---

## 4. Analyse des erreurs 

Sur le jeu de démonstration, l'évaluation (`evaluate.py`) affiche **7 erreurs sur 58** :

Soit **2 faux positifs** (avis négatifs classés positifs) et **5 faux négatifs** (avis positifs classés négatifs).

Les **2 faux positifs** sont le cas qui compte pour le métier : un client mécontent classé positif serait traité en retard, exactement ce que la fiche de cadrage du cas 3 veut éviter.

**Toutes les erreurs portent sur des avis mitigés.** Exemple tiré de nos données :

> *« Taille trop petite et retour payant au déballage, sauf que ensuite produit conforme à la description. »*
> Vérité = positive, prédit = negative.

**Pourquoi ?** Un sac de mots **n'a pas d'ordre**. « bon puis mauvais » et « mauvais puis bon » produisent exactement le même vecteur : le modèle ne peut pas savoir quelle moitié conclut. Les avis mitigés du jeu de démo sont construits avec un retournement (« sauf que ensuite… ») et l'étiquette suit la seconde moitié, ce que le modèle ne peut pas voir.

**Ce qu'il faudrait pour corriger.** Trois pistes :
1. Des **n-grammes plus longs** (1-3 au lieu de 1-2 actuellement) pour capter un peu plus de contexte local.
2. Un **transformer** (DistilBERT, CamemBERT) qui pèse la position des mots et sait qu'une fin d'avis porte plus qu'un début.
3. Un **ensemble** de modèles, ou l'ajout d'un classifieur sur les 200 derniers caractères uniquement.

---

## 5. Seuil d'incertitude 

L'interface du TP3 (`ui/helpers.py`) utilise un seuil `SEUIL_INCERTITUDE = 0.60`. En dessous de 60 % de confiance, l'interface n'affiche pas de verdict tranché mais **« À vérifier par un agent »** en orange.

Sur les 290 avis du jeu de démonstration, l'interface annonce **69 cas à vérifier** (soit environ **23,8 %**), à comparer aux 145 négatifs réels (le modèle en détecte 147). Aux autres seuils : 0 cas à 0,50 et 137 cas (47,2 %) à 0,75.

Ce chiffre n'est pas un détail : c'est le curseur qui décide combien de travail humain on garde. Trois régimes :

| Seuil | Avis envoyés à un agent | Risque |
|---|---|---|
| 0,50 | Peu | Le modèle tranche seul des cas qu'il ne maîtrise pas |
| **0,60** | **Modéré** | **Compromis retenu** |
| 0,75 | Beaucoup | La file humaine se remplit, l'automatisation perd son intérêt |

Nous avons choisi de **conserver 0,60** parce que c'est le seul seuil qui rend l'hésitation du modèle **visible** au lieu de la cacher. Afficher un verdict tranché à 51 % de confiance, c'est mentir par omission. Ce curseur ne se décide d'ailleurs pas dans le code : il se décide **avec l'équipe métier**, qui seule connaît sa capacité à traiter des cas à la main.

---

## 6. Ce qui a échoué 

Trois incidents notables, tous documentés dans la section 8 de l'énoncé :

1. **Le contrôle T5 (deux auteurs distincts).** Longtemps bloqué à `1 failed, 41 passed` : Git ne voyait qu'un seul auteur (Mehdi). Oussama n'avait pas encore fait son commit sur son poste. Résolu en configurant correctement `git config --global user.name` sur le poste de Oussama, puis en poussant un commit. `git shortlog -sn --all` affiche désormais **deux noms**.

2. **Les chemins imbriqués des kits.** L'archive `tp1-tp2-tp3.zip` crée un dossier du même nom que lui-même à l'intérieur (`tp1-tp2-tp3\tp1-tp2-tp3\`), et de même pour `sentiment-app` et `tp3-streamlit-kit`. Nous avons perdu du temps à chercher `appliquer_tp2.py` et `appliquer_tp3.py`. La règle retenue : toujours faire un `dir` **avant** de lancer une commande, et utiliser le chemin `..\sentiment-app\sentiment-app` quand on installe un kit.

3. **Le push des captures d'écran (HTTP 408).** Après avoir ajouté deux PNG au dépôt, `git push` a échoué deux fois avec `RPC failed; HTTP 408`. Solution : `git config --global http.postBuffer 524288000` puis `git config --global http.version HTTP/1.1`. Le push est passé au troisième essai.

Ces échecs ne sont pas des détails : ils sont la partie du travail qui ne se voit pas sur un dépôt propre mais qui prend du temps réel.

---

## 7. Ce que nous ferions autrement 

Trois pistes d'amélioration, dans l'ordre d'importance :

1. **Un modèle sensible à l'ordre.** Nos 7 erreurs sur 58 viennent toutes du fait qu'un sac de mots ignore l'ordre. Un transformer français (CamemBERT, DistilBERT) réduirait ces erreurs. Coût : l'entraînement passe de quelques secondes à plusieurs minutes sur CPU, et le modèle pèse plusieurs centaines de Mo (à héberger hors Git).

2. **Un seuil d'incertitude adaptatif.** Plutôt qu'un seuil global fixe, moduler selon la **longueur** de l'avis et la **marge** entre les deux scores. Un avis court et ambigu est plus suspect qu'un avis long et net.

3. **Un versionnage plus fin de la mesure.** `models/metrics.json` est actuellement écrasé à chaque entraînement. Conserver un historique (par exemple `metrics-2026-10-14.json`) permettrait de suivre la dérive dans le temps, et anticiperait la partie MLOps des semaines suivantes.

Côté méthode, nous retiendrons aussi de **toujours vérifier le dossier courant** avant de lancer une commande, et de **lire la ligne qui suit immédiatement un code d'erreur** (comme le conseille l'énoncé) : `Password authentication is not supported` est un problème d'authentification, `403 Forbidden` est un problème d'autorisation.

---

## 8. Répartition du travail

| Membre | TP1 | TP2 | TP3 |
|---|---|---|---|
| **Mehdi Benjelloun** | Création du dépôt GitHub, structure, rédaction des 3 fiches de cadrage, environnement, premier push | Écriture de `docs/semaine2.md`, entraînement Allociné, analyse des erreurs | Commit des captures, réglages Git (http.postBuffer) |
| **Oussama Kamil** | Rédaction d'une fiche, vérification de l'installation sur un second poste, commit de validation (contrôle T5) | Évaluation du modèle, mesure du F1, vérification `.gitignore` | Rédaction de `docs/semaine3.md`, tests de l'interface S1/S2/S3 |

Le dépôt est propre, l'étiquette `compte-rendu` fige la version remise, et la CI est verte sur les trois séances (42 puis 45 tests). Nous avons travaillé en binôme sur les séances 1 et 2, et en autonomie alternée sur la séance 3 pour couvrir à la fois le code et la documentation.

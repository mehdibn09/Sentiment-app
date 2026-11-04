# Notice d’installation et d’utilisation — Sentiment-app 0.6.0

**Projet :** analyse de sentiment d’avis clients en français  
**Binôme :** Mehdi Benjelloun (`mehdibn09`) et Oussama Kamil (`Oussamak05`)  
**Module :** Développement et déploiement d’applications intelligentes  
**Enseignant :** A. Larhlimi  
**Dépôt :** [mehdibn09/Sentiment-app](https://github.com/mehdibn09/Sentiment-app)  
**Version :** `0.6.0` — TP6  
**Date :** 4 novembre 2026

## 1. Présentation

Sentiment-app analyse un avis et renvoie un sentiment `POSITIVE`, `NEGATIVE` ou `INDETERMINE`. Le modèle associe une vectorisation TF-IDF à une régression logistique. Lorsque le score est inférieur à `0.60`, l’application s’abstient et demande une vérification humaine.

Trois modes sont disponibles : prédiction dans le terminal, API FastAPI et interface web Streamlit. L’interface permet aussi d’importer un fichier CSV contenant une colonne `review`, puis d’exporter les résultats.

## 2. Éléments de livraison

| Élément | Rôle |
| --- | --- |
| `sentiment_app-0.6.0-py3-none-any.whl` | Paquet installable, avec le code de l’application et les métadonnées |
| `sentiment_app-0.6.0.tar.gz` | Distribution source permettant de reconstruire le paquet |
| `sentiment.joblib` | Modèle entraîné, à obtenir ou à générer séparément |
| `LIVRAISON.md` | Présente notice |

Le modèle n’est inclus dans aucune des deux distributions préparées. La roue ne contient ni les jeux de données, ni les tests, ni les scripts `src/`. La distribution source n’est pas une copie complète du dépôt GitHub : pour réentraîner, utiliser le dépôt complet.

## 3. Prérequis

- Windows avec **Python 3.11, 64 bits**, détecté par `py --list`.
- Une connexion Internet pour installer les dépendances.
- La roue téléchargée et un modèle compatible avec **scikit-learn 1.5.x**.
- Un terminal **CMD** ouvert dans le dossier contenant la roue. Les commandes des sections 4 à 8 utilisent la syntaxe CMD.

Python 3.12 a été utilisé pour les vérifications locales du paquet. Pour reproduire l’environnement du cours et de la CI, utiliser Python 3.11. L’environnement Python 3.14 observé lors du dépannage ne sert pas de référence pour cette livraison.

## 4. Installation du paquet

Dans le dossier contenant le fichier `.whl`, exécuter une commande à la fois :

```cmd
py --list
py -3.11 -m venv .venv-livraison
.venv-livraison\Scripts\activate.bat
python --version
python -m pip install "sentiment_app-0.6.0-py3-none-any.whl[ui]"
sentiment --version
```

La version de Python doit être `3.11.x`. La dernière commande doit afficher :

```text
sentiment-app 0.6.0
```

L’option `[ui]` installe les dépendances de l’interface, notamment Streamlit, pandas et httpx. Elle permet de disposer des trois modes d’utilisation.

## 5. Configuration du modèle

Placer le fichier `sentiment.joblib` dans un emplacement connu. Dans CMD, définir son chemin **avant de lancer la prédiction ou l’API** :

```cmd
set "SENTIMENT_MODELE=C:\chemin\vers\sentiment.joblib"
```

Remplacer `C:\chemin\vers\sentiment.joblib` par le chemin réel. Les guillemets entourent l’affectation entière et permettent les chemins contenant des espaces.

Vérifier que le fichier existe :

```cmd
dir "%SENTIMENT_MODELE%"
```

La variable s’applique uniquement au terminal courant et à ses processus enfants. Il faut la redéfinir dans tout autre terminal qui lance une prédiction ou l’API. Le modèle est chargé en cache ; après remplacement du fichier ou changement de chemin, redémarrer le processus concerné.

### Si le modèle n’a pas été fourni

Récupérer le dépôt GitHub complet et ouvrir CMD dans le dossier contenant `pyproject.toml`, `src/` et `data/`. Avec l’environnement installé activé :

```cmd
python src/make_demo.py
python src/train.py
```

Ces commandes génèrent le jeu de démonstration et produisent `models\sentiment.joblib` ainsi que `models\metrics.json`. Configurer ensuite `SENTIMENT_MODELE` avec le chemin absolu du fichier généré. Un réentraînement remplace le modèle précédent et actualise ses métriques.

## 6. Prédiction dans le terminal

Avec l’environnement activé et `SENTIMENT_MODELE` défini :

```cmd
sentiment predict "Livraison rapide, produit conforme, très satisfait"
```

Résultat vérifié avec le modèle de démonstration de référence :

```json
{"label": "POSITIVE", "score": 0.777, "text": "Livraison rapide, produit conforme, très satisfait"}
```

Pour tester un avis négatif ou un texte inconnu :

```cmd
sentiment predict "Produit cassé et service injoignable, à fuir"
sentiment predict "xqzvb wlkptr grombu"
```

La CLI applique le même seuil d’abstention que l’API. Les scores peuvent changer avec le texte exact, les accents, le modèle ou les versions des dépendances.

## 7. Lancement de l’API

Dans le premier terminal, avec l’environnement et le modèle configurés :

```cmd
sentiment serve
```

Laisser ce terminal ouvert.

- Documentation interactive : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
- État du service : [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).
- Prédiction : `POST /predict`, avec un corps JSON contenant le champ `text`.

Dans `/docs`, ouvrir `POST /predict`, cliquer sur **Try it out**, saisir le JSON suivant, puis **Execute** :

```json
{"text": "Livraison rapide, produit conforme, très satisfait"}
```

| Situation | Comportement |
| --- | --- |
| Requête valide | HTTP 200 avec `label`, `score` et aperçu du texte |
| Confiance inférieure à 0,60 | HTTP 200 avec `label = INDETERMINE` |
| Texte vide, composé de blancs, non textuel ou supérieur à 2 000 caractères | HTTP 422 |
| État du modèle indisponible après démarrage | HTTP 503 |
| Erreur inattendue de prédiction | HTTP 500, détail interne conservé côté serveur |
| Fichier modèle absent au démarrage | Échec du démarrage avec un message indiquant le modèle manquant |

## 8. Lancement de l’interface web

Ouvrir une **deuxième fenêtre CMD** dans le même dossier que celui utilisé pour créer `.venv-livraison`, puis exécuter :

```cmd
.venv-livraison\Scripts\activate.bat
sentiment ui
```

Ouvrir [http://localhost:8501](http://localhost:8501). L’API du premier terminal doit rester active. L’interface utilise par défaut `http://127.0.0.1:8000`.

Dans l’interface :

1. Vérifier le message indiquant que l’API est prête.
2. Saisir un avis, puis lancer l’analyse.
3. Pour un traitement de lot, importer un CSV avec une colonne nommée `review`.
4. Consulter les verdicts et les confiances, puis télécharger les résultats.

Exemple minimal de CSV en UTF-8 :

```csv
review
"Livraison rapide, produit conforme, très satisfait"
"Produit cassé et service injoignable, à fuir"
"xqzvb wlkptr grombu"
```

Pour arrêter l’interface et l’API, utiliser `Ctrl+C` dans chacun des deux terminaux.

## 9. Variante PowerShell

Dans PowerShell, remplacer l’activation CMD et la définition de variable par :

```powershell
.\.venv-livraison\Scripts\Activate.ps1
$env:SENTIMENT_MODELE = "C:\chemin\vers\sentiment.joblib"
```

Les commandes `python -m pip`, `sentiment predict`, `sentiment serve` et `sentiment ui` restent identiques. Si l’activation PowerShell est bloquée par une politique locale, utiliser CMD et `activate.bat`.

## 10. Dépannage

| Message ou problème | Cause probable | Action |
| --- | --- | --- |
| `No suitable Python runtime found` | Python 3.11 non détecté | Installer Python 3.11, rouvrir CMD, vérifier `py --list` |
| Aucun `pyproject.toml` trouvé avec `pip install -e .` | Mauvais dossier pour une installation depuis les sources | Rechercher le fichier avec `dir /s /b pyproject.toml`, puis se placer dans son dossier ; l’installation de la roue utilise directement son nom |
| `sentiment` n’est pas reconnu | Environnement inactif ou paquet non installé dedans | Activer `.venv-livraison`, puis refaire l’installation dans cet environnement |
| Modèle introuvable | Chemin incorrect, fichier absent ou variable définie dans un autre terminal | Vérifier `dir "%SENTIMENT_MODELE%"`, configurer le chemin avant le lancement |
| Erreur de lecture du modèle | Versions incompatibles ou fichier invalide | Utiliser le modèle de confiance prévu pour le projet avec scikit-learn 1.5.x, ou le régénérer dans cet environnement |
| `API injoignable` | API arrêtée ou mauvaise adresse | Lancer `sentiment serve` dans le premier terminal |
| Port 8000 occupé | Un autre service utilise le port | Arrêter l’ancien serveur ou utiliser `sentiment serve --port 8001`, puis `set "API_URL=http://127.0.0.1:8001"` avant `sentiment ui` dans le second terminal |
| `src/train.py` introuvable | Distribution installée sans dépôt complet, ou mauvais dossier | Récupérer le dépôt complet et ouvrir le terminal à sa racine |

## 11. Vérifications de livraison et limites

Les distributions 0.6.0 ont été construites depuis la version TP6 préparée. Le contenu de la roue a été comparé aux sources ; le modèle reste externe. La version et une prédiction positive ont été vérifiées après installation dans un répertoire séparé, depuis un dossier extérieur au dépôt, avec les dépendances déjà présentes.

Sur cette copie de travail, la suite a donné **102 tests réussis, 4 ignorés faute de dépôt/historique Git, et 3 échecs attendus liés aux limites déclarées du modèle**. Ces résultats ne certifient pas l’installation Windows de l’utilisateur, une installation complète des dépendances dans un environnement neuf ou l’état courant de GitHub Actions.

Le modèle est un support pédagogique : il peut se tromper sur les négations, l’ironie et les avis mitigés. Le score n’est pas une garantie de justesse. Les avis indéterminés sont à relire par un humain.

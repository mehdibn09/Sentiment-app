# Semaine 5 : l'interface Streamlit (notes du binôme)

> Réponses appuyées sur ce que nous avons observé en lançant `uvicorn api.main:app` et `streamlit run ui/app.py`.

## 1. Que sait l'interface de l'API, et pourquoi ne charge-t-elle pas le modèle ?

Elle ne connaît que quatre choses : l'URL (`API_URL`, par défaut `http://127.0.0.1:8000`), `GET /health`, `POST /predict` et le format JSON de la réponse. Tout passe par `ui/client.py` ; `ui/app.py` n'importe ni `predict()` ni le fichier `.joblib`. Conséquence observée : après `python src/train.py` et un redémarrage de l'API, la page affiche les nouveaux résultats sans aucune modification de `ui/`.

## 2. Que voit l'utilisateur dans chaque cas ?

| Essai | Affichage observé |
| --- | --- |
| « Livraison rapide, produit conforme, très satisfait » | Avis positif, 78 % |
| « Produit cassé et service injoignable, à fuir » | Avis négatif, 75 % |
| « xqzvb wlkptr grombu » | « Je ne sais pas : à faire vérifier par un humain », 52 %, et le message « La confiance est sous le seuil d'abstention : un humain doit trancher » |
| Trois espaces | « Texte refusé : vide, fait d'espaces, ou de plus de 2000 caractères. » (réponse 422 de l'API) |
| API arrêtée, page rechargée | « API injoignable : lancez d'abord uvicorn api.main:app », et la page s'arrête là |

Le verdict brut `INDETERMINE` n'apparaît jamais à l'écran : l'utilisateur ne saurait pas quoi en faire.

## 3. Que donne un fichier d'avis ?

Avec `data/avis_exemple.csv` (colonne `review`, 6 avis) : un tableau de 6 lignes avec le verdict et la confiance, le résumé `{'INDETERMINE': 1, 'NEGATIVE': 2, 'POSITIVE': 3}` et un bouton « Télécharger les résultats » qui produit `resultats.csv`. Un avis refusé par l'API (ligne vide, texte trop long) n'interrompt pas le lot : il est compté à part sous « REFUS OU ERREUR ». Une limite à connaître : l'interface envoie un avis par requête, donc un gros fichier prend autant d'allers-retours que de lignes.

## Tests

`tests/test_client.py` (6 tests, transport simulé et API en mémoire) et `tests/test_interface.py` (6 tests, moteur de test de Streamlit) : 12 tests de plus qu'à la fin du TP4.

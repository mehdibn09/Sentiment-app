# Semaine 6 : le paquet

## 1. Pourquoi le modèle est-il hors de la roue ? Comment est-il trouvé ?

La roue distribue le code indépendamment du modèle entraîné. Le fichier joblib se fournit séparément et peut être remplacé sans republier le paquet. SENTIMENT_MODELE indique son chemin ; sans cette variable, le chemin de développement est models/sentiment.joblib à la racine du dépôt.

## 2. Quels changements dans api/model.py ?

L’API importe sentiment_app.predict au lieu de modifier le chemin de recherche de Python. src/predict.py devient une passerelle de compatibilité pour les anciens scripts et tests. Les étiquettes, le score et le seuil d’abstention 0,60 sont conservés.

## 3. Quelles conditions pour installer la roue ailleurs ?

Il faut fournir le modèle séparément et définir SENTIMENT_MODELE avant de démarrer le processus. pip installe les dépendances déclarées. scikit-learn reste dans la série 1.5 pour conserver la compatibilité avec le modèle. La vérification hors du dépôt se réalise dans un nouvel environnement. L’option [ui] installe les dépendances de Streamlit.

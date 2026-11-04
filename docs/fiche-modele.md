# Fiche modèle — Sentiment-app

## Identité du modèle
Sentiment-app 0.6.0, réalisé par Mehdi Benjelloun et Oussama Kamil. Pipeline TF-IDF (unigrammes et bigrammes, min_df=2) et régression logistique équilibrée ; graine 42. Modèle local : models/sentiment.joblib.

## Usage prévu
Démonstration pédagogique de classification binaire d'avis clients en français. L'API et l'interface facilitent un premier tri, soumis à une vérification humaine en cas d'incertitude.

## Usages exclus
Décisions autonomes affectant une personne, diagnostic médical, évaluation d'employés et classement de tickets IT sans réentraînement. Les langues et domaines non évalués ne sont pas couverts.

## Données d'entraînement
Jeu synthétique de démonstration data/demo_reviews.csv : 290 avis, découpés avant vectorisation en 232 avis d'entraînement et 58 de test, stratification par étiquette, graine 42. Les répétitions de motifs peuvent rendre le test optimiste. Aucun entraînement Allociné n'est revendiqué pour cette version.

## Performances mesurées
Mesures du modèle de démonstration dans models/metrics.json : F1 macro 0.879, exactitude 0.8793 et rappel des négatifs 0.931. Seuil cible F1 : 0.85. Ces performances sur données synthétiques ne prouvent pas la généralisation. L'audit des sous-groupes réutilise ce test de 58 avis ; il n'est pas une validation indépendante.

## Limites connues
Le sac de mots traite mal l'ironie, les négations et les retournements. Le score de confiance n'est pas une probabilité calibrée de justesse. Un texte hors vocabulaire peut produire une prédiction sans pertinence. Le seuil d'abstention de l'API est 0.60 ; un score égal au seuil reste accepté.

## Biais mesurés
Audit src/biais.py sur le test synthétique : 41 avis directs, exactitude 1.000, 1 abstention ; 17 avec connecteur de retournement, exactitude 0.588, 15 abstentions et 2 erreurs restantes après abstention. Parmi les 31 courts (9 mots ou moins), exactitude 1.000 ; parmi les 27 longs, 0.741. Les 17 retournements sont longs : la longueur et le type sont confondus. Les 10 longs directs ont une exactitude de 1.000. La détection des retournements est une heuristique lexicale. Aucun attribut démographique n'est disponible : aucune conclusion d'équité sociale n'est possible.

## Explicabilité
src/expliquer.py fournit les coefficients et les contributions SHAP linéaires analytiques sous hypothèse de variables indépendantes, sans bibliothèque SHAP. Référence : moyenne TF-IDF des 232 avis d'entraînement de démonstration. Pour chaque terme, contribution = coefficient × (TF-IDF de l'avis − moyenne). Base et somme des contributions retrouvent le log-odds positif, y compris les termes absents. Sur l'avis mitigé par défaut : base −0.0114, sortie −0.1343, confiance négative 0.5335, donc abstention de l'API. Cela explique le modèle, sans prouver une causalité. Les n-grammes corrélés limitent l'interprétation indépendante. Pour un autre corpus, il faut fournir sa véritable référence d'entraînement.

## Conditions d'usage
Lancer l'API avec un modèle local de confiance uniquement : joblib peut exécuter du code au chargement. Sous 0.60, faire trancher un humain ; un humain reste responsable des décisions finales. Ne pas déposer d'avis confidentiels dans le dépôt ni dans les captures. L'API accepte de 1 à 2000 caractères non blancs.

## Maintenance
Après changement des données ou du modèle : réentraîner, recalculer metrics.json, rejouer l'audit des biais et l'explicabilité, actualiser cette fiche et exécuter pytest. Conserver les versions des dépendances, le corpus de référence et les preuves. La CI GitHub et les captures sur les postes du binôme restent à vérifier séparément. Les distributions déjà livrées doivent être reconstruites pour contenir les nouveaux graphiques.

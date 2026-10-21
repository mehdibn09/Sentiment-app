# Semaine 2 — Analyse des erreurs

Sur les 58 avis du jeu de test, le modèle commet **7 erreurs** : 5 avis positifs classés à tort comme négatifs, et 2 avis négatifs classés à tort comme positifs. Ces deux faux positifs représentent le risque le plus élevé, car un client insatisfait verrait sa réclamation traitée avec retard.

L'ensemble de ces erreurs concerne des avis nuancés ou contrastés (du type « positif puis négatif », ou inversement). En effet, l'approche par sac de mots (*bag-of-words*) ignore complètement l'ordre séquentiel : deux tournures opposées génèrent des représentations vectorielles similaires, et le modèle a tendance à s'accrocher aux termes de la première moitié plutôt qu'à la conclusion de l'auteur.

## Pistes d'amélioration

Pour y remédier, il est indispensable de passer à une modélisation sensible à l'ordre des mots :
* **Alternative classique :** Intégrer des **n-grammes** (1-2 ou 1-3) pour conserver le contexte local des termes.
* **Alternative moderne :** Basculer sur un **Transformer** (type DistilBERT ou CamemBERT), capable d'analyser la structure syntaxique globale et d'accorder un poids fort au dénouement de l'avis, là où réside l'intention finale.

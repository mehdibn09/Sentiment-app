# Semaine 4 : tests approfondis et qualité du code (notes du binôme)

> Deux pages maximum. Seuls les chiffres issus de nos propres exécutions sont admis.

## 1. Couverture des tests

- **Point de départ (étape A)** : couverture de … %, avec … lignes jamais exécutées.
- **Comportements non vérifiés** : pour chacune de ces lignes, décrire ce que le code fait et qu'aucun test ne contrôlait : …
- **Point d'arrivée (étape D)** : couverture de … %.
- **Lignes exclues de la mesure** : lesquelles, et pour quelle raison : …

## 2. Défauts mis au jour

| Symptôme observé | Test qui l'a révélé | Correctif appliqué |
| --- | --- | --- |
| … | … | … |

## 3. Seuil d'abstention

- **Points de la courbe** (obtenus avec `python src/courbe_seuil.py`) : deux ou trois valeurs significatives : …
- **Seuil choisi** : …
- **Part des avis transmis à un humain** : … %
- **Justification du choix** : …

## 4. Jeu d'or

- **Bilan** (`python src/bilan_jeu_or.py`) : … réponses justes, … abstentions, … erreurs franches signalées comme telles.
- **Lecture de ces résultats** : ce qu'ils révèlent des forces et des limites du modèle : …

## 5. Analyse statique

- **Alertes initiales** : ruff : …, mypy : …
- **Recoupement avec la partie 2** : sur l'ensemble des défauts listés, combien ruff et mypy en avaient-ils déjà signalés ? …
- **Conclusion** : ce que cela nous apprend sur ce que les outils statiques détectent, et sur ce qu'ils laissent passer : …

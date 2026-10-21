# Semaine 4 : tests approfondis et qualité du code (notes du binôme)

> Deux pages maximum. Seuls les chiffres issus de nos propres exécutions sont admis.

## 1. Couverture des tests

- **Point de départ (étape A)** : couverture de … %, avec … lignes jamais exécutées.
- **Comportements non vérifiés** : pour chacune de ces lignes, ce que le code fait et qu'aucun test ne contrôlait : …
- **Point d'arrivée (étape D)** : couverture de … %.
- **Lignes exclues de la mesure** : lesquelles, et pourquoi : …

## 2. Défauts mis au jour

| Symptôme observé | Test qui l'a révélé | Correctif appliqué |
| --- | --- | --- |
| … | … | … |

## 3. Seuil d'abstention

- **Jeu de mesure** : jeu de test du TP2, … avis (source : …), modèle entraîné sur les mêmes données (aucun avertissement « ATTENTION » affiché).
- **Points de la courbe** (`python src/courbe_seuil.py`) :

| Seuil | Répond à | Part | Exactitude | Erreurs | Vers un humain |
| --- | --- | --- | --- | --- | --- |
| 0,60 | … | … % | … | … | … |
| 0,75 | … | … % | … | … | … |
| 0,90 | … | … % | … | … | … |

- **Seuil retenu** : … ; part des avis envoyés à un humain : … % (soit … avis sur …).
- **Justification** : en passant de 0,60 à …, l'exactitude gagne … points mais … avis supplémentaires partent vers un humain. Nous retenons le seuil où …

## 4. Jeu d'or

- **Composition** : 20 avis, dont 11 positifs et 9 négatifs. Cas simples : 8. Cas pièges : 12 (négation 4, mitigé 5, ironie 3).
- **Bilan** (`python src/bilan_jeu_or.py`) : justes …, abstentions …, erreurs franches déclarées …, erreurs franches non déclarées …
- **Détail par catégorie** : cas simples …/8 justes ; négation …/4 ; mitigé …/5 ; ironie …/3.
- **Ce que ces chiffres disent du modèle** :
  - Ironie : les 3 avis ("Génial…", "Parfait, le colis est arrivé écrasé", "Top, le livreur a jeté le colis…") sont déclarés comme erreur connue du sac de mots, car le modèle lit « génial », « parfait », « top » comme positifs. Combien ont été ratés ? …
  - Négation ("pas déçu", "ne regrette pas") : le modèle traite-t-il « pas » comme un mot isolé ? …
  - Mitigé : les abstentions tombent-elles surtout sur ces avis, comme attendu ? …

## 5. Outils statiques

- **Alertes initiales** : ruff : …, mypy : …
- **Recoupement avec la partie 2** : sur les … défauts listés, ruff et mypy en avaient signalé … .
- **Conclusion** : ce que les outils statiques détectent (style, types, variables inutilisées) et ce qu'ils laissent passer (erreurs de logique, cas limites, comportement du modèle) : …

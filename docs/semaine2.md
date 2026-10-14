# Semaine 2 — Analyse des erreurs

## Bilan des erreurs

Sur les 58 avis du jeu de test, le modèle commet **7 erreurs** :

- **5 faux négatifs** : des avis positifs classés négatifs.
- **2 faux positifs** : des avis négatifs classés positifs. Ce sont les plus coûteux, car un client mécontent serait pris en charge avec retard.

## Mécanisme à l'origine des erreurs

Les 7 erreurs concernent des avis mitigés du type « bon puis mauvais », ou l'inverse. Le modèle repose sur un sac de mots, qui compte les mots présents sans tenir compte de leur ordre : « le produit est bon mais le service est mauvais » et « le service est mauvais mais le produit est bon » produisent exactement le même vecteur. Le modèle ne peut donc pas repérer que la conclusion, souvent placée en fin d'avis, porte le véritable sentiment du client.

## Pistes de correction

Il faudrait un modèle capable de prendre en compte l'ordre et le contexte des mots :

- **Les n-grammes (1-2 ou 1-3)** : ils capturent des suites de mots comme « pas bon » ou « mais décevant », mais seulement sur de courtes distances.
- **Un transformer (DistilBERT, CamemBERT)** : il lit l'avis en entier et peut donner plus de poids à la conclusion.

Ces solutions dépassaient l'objectif de la séance, centré sur la mise en place d'un modèle de référence simple et sur la compréhension de ses limites.

# Semaine 2 — Analyse des erreurs

Sur les 58 avis du jeu de test, le modèle se trompe 7 fois : 5 avis positifs classés négatifs et 2 avis négatifs classés positifs (ces 2 faux positifs sont les plus coûteux, car un client mécontent serait traité en retard).

Toutes ces erreurs portent sur des avis mitigés du type « bon puis mauvais » ou l'inverse, parce qu'un sac de mots ne tient pas compte de l'ordre : les deux formulations produisent le même vecteur, et le modèle suit la première moitié au lieu de la conclusion.

Pour corriger cela, il faudrait un modèle sensible à l'ordre des mots — par exemple des n-grammes (1-2 ou 1-3) ou un transformer (DistilBERT/CamemBERT), qui pèserait davantage la fin de l'avis, là où se trouve l'étiquette.

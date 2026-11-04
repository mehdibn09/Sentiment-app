# TP6, étape G : la fiche modèle (30 min)

**Objectif.** Documenter le modèle en une page : usage, données, performances, limites, biais,
conditions d'usage. **Programme** : chapitre 5, point 5, et chapitre 2, point 6 (documentation).

## Ce que l'étape fait comprendre

1. Un modèle livré sans sa fiche est un modèle qu'on utilisera mal : le paquet du TP6 dit comment
   l'installer, la fiche dit quand s'en servir et quand ne pas s'en servir.
2. Une documentation se teste : les chiffres cités doivent être ceux du dépôt.

## Faire

```powershell
python C:\IA-DEV\complements-lot1\appliquer_complements.py C:\IA-DEV\sentiment-app --etape tp6
python -m pytest tests/test_fiche_modele.py -q
notepad docs\fiche-modele.md
python -m pytest tests/test_fiche_modele.py -q
```

Remplissez les dix rubriques à partir de ce que vous avez mesuré : `models/metrics.json`, la courbe du
seuil du TP4, `python src/biais.py`, `python src/expliquer.py`, le jeu d'or.

## Contrôle T41a

- Au départ : `13 failed, 1 passed`. C'est voulu.
- Une fois la fiche remplie : `14 passed`. Les tests vérifient que chaque rubrique contient au moins
  40 caractères rédigés, que la version citée est celle du paquet (0.6.0), que le F1 macro et le
  rappel des négatifs cités sont ceux de `models/metrics.json` (0.879 et 0.931 sur le jeu de
  démonstration, avec un point ou une virgule), et que les conditions d'usage prévoient un humain.
- Ajoutez une ligne à `CHANGELOG.md`, sous une rubrique « Non publié » : la fiche modèle.

## Pièges

- Recopier les valeurs d'un autre binôme : la fiche doit citer vos propres mesures.
- Réentraîner avec `--allocine` sans mettre la fiche à jour : le test des performances échoue. C'est
  le but : la fiche suit le modèle.
- Écrire des généralités : « le modèle peut se tromper » ne dit rien ; « les 7 erreurs du jeu de test
  sont des avis qui se retournent » dit quelque chose.

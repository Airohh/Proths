# Model card : news-classifier

## Usage prévu

Classer des dépêches d'actualité en anglais dans 4 thèmes : **World**, **Sports**,
**Business**, **Sci/Tech**. C'est un projet de démonstration MLOps : il n'est pas destiné
à des décisions réelles.

**Hors périmètre** : textes non anglais, textes longs (au-delà de quelques paragraphes),
thèmes absents d'AG News (santé, culture…). Le modèle choisira quand même l'une des 4
classes, souvent avec une confiance plus basse.

## Modèle

`sklearn.Pipeline` en trois étapes :
1. nettoyage : minuscules, entités HTML et ponctuation retirées ;
2. TF-IDF : unigrammes et bigrammes, `sublinear_tf`, 200 000 features au plus ;
3. régression logistique entraînée par SGD (`loss="log_loss"`, `alpha=2e-6`).

Le pipeline est loggé en un seul artefact MLflow. Le modèle servi est
`models:/news-classifier@champion`.

## Données

[AG News](https://huggingface.co/datasets/fancyzhx/ag_news) (Zhang et al., 2015),
classes équilibrées.

| Split | Taille | Usage |
|---|---|---|
| train | 120 000 | entraînement |
| holdout | 3 800 (moitié stratifiée du test officiel) | seul juge des promotions |
| stream | 3 800 (autre moitié) | trafic simulé, labels renvoyés par `/feedback` |

## Performances (holdout, modèle entraîné sur les 120 000 articles)

| Classe | F1 |
|---|---|
| Sports | 0.969 |
| World | 0.922 |
| Sci/Tech | 0.905 |
| Business | 0.896 |
| **Macro** | **0.923** (accuracy 0.923) |

Business et Sci/Tech se confondent le plus : les articles sur les entreprises tech
tombent dans les deux classes.

## Surveillance en production

- **Drift** (sans labels) : PSI sur le mix des classes prédites, seuil 0,2 ; KS sur la
  confiance, seuil 0,15. Les deux sont calculés sur les 500 dernières prédictions du
  champion.
- **Performance** (avec labels) : précision sur les prédictions qui ont reçu un feedback.
  Elle dépend du mix du trafic : Sports étant plus facile, un trafic riche en Sports la
  fait monter sans que le modèle soit meilleur.
- **Promotion** : un candidat devient champion s'il gagne au moins +0,002 de F1 macro sur
  le holdout, dans le même run que le champion.

## Limites

- Données de 2004–2005 : le vocabulaire d'actualité a dérivé depuis (noms propres,
  technologies).
- Aucune évaluation d'équité : les biais du corpus d'origine (sources majoritairement
  anglo-saxonnes) ne sont pas mesurés.
- La confiance est une probabilité de régression logistique non recalibrée.

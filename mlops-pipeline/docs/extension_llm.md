# Extension LLM - Plan Future

## Objectif

Ajouter un modèle LLM fine-tuné en complément du modèle baseline, une fois le pipeline MLOps solide.

## Approche

### Phase 1 : Baseline (Actuel)
- Modèle classique (Random Forest / LightGBM)
- Pipeline MLOps complet et testé
- Monitoring opérationnel

### Phase 2 : Extension LLM (Future)

#### Choix du modèle
- **DistilBERT** : Léger, rapide, bon compromis
- **RoBERTa** : Plus performant, plus lourd
- **DeBERTa** : Très performant, nécessite GPU

#### Modifications nécessaires

1. **Training**
   ```python
   from transformers import AutoTokenizer, AutoModelForSequenceClassification
   from transformers import Trainer, TrainingArguments
   
   # Charger modèle pré-entraîné
   model = AutoModelForSequenceClassification.from_pretrained(
       "distilbert-base-uncased",
       num_labels=num_classes
   )
   ```

2. **Preprocessing**
   - Tokenization avec tokenizer Hugging Face
   - Padding et truncation
   - Remplacement de TF-IDF

3. **Infrastructure**
   - GPU nécessaire pour training
   - Plus de mémoire pour inférence
   - Coûts plus élevés

4. **Monitoring**
   - Latence plus élevée à tracker
   - Coûts GPU à monitorer
   - Comparaison baseline vs LLM

#### A/B Testing

Comparer les deux modèles en production :
- Baseline : Rapide, peu coûteux
- LLM : Plus performant, plus coûteux

#### Coûts estimés

- **Training** : ~$10-50 (GPU cloud)
- **Inférence** : ~$0.001-0.01 par prédiction
- **Infrastructure** : GPU instance (~$0.50-2/heure)

## Quand l'implémenter ?

- ✅ Pipeline baseline 100% opérationnel
- ✅ Monitoring fonctionnel
- ✅ Documentation complète
- ✅ Démo publique réussie

Ensuite, ajouter le LLM comme amélioration/extension.


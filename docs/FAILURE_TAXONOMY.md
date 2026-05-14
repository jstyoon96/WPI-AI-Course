# FAILURE_TAXONOMY

## Categories
- LOW_TRAIN_LOW_VAL
- HIGH_TRAIN_LOW_VAL
- TRAINING_DIVERGES
- GOOD_PROXY_BAD_FULL
- ALL_MODELS_SAME_FAILURE
- DATA_OR_LABEL_ISSUE
- EVALUATION_ISSUE
- OPTIMIZATION_FAILURE
- UNDERCAPACITY
- OVERFITTING
- DOMAIN_SHIFT
- TASK_FORMULATION_FAILURE
- MODEL_ASSUMPTION_FAILURE

## Required Fields
Each failure category must map to:

- evidence
- likely causes
- first checks
- allowed interventions
- forbidden interventions

## Example
```yaml
LOW_TRAIN_LOW_VAL:
  evidence:
    - train_metric_low
    - val_metric_low
  likely_causes:
    - label_noise
    - optimization_failure
    - undercapacity
    - wrong_output_representation
  first_checks:
    - audit_labels
    - overfit_tiny_batch
    - check_loss_scale
  allowed_interventions:
    - fix_data_or_labels
    - tune_optimizer
    - change_loss
    - change_representation
  forbidden_interventions:
    - change_test_split
    - change_primary_metric
```


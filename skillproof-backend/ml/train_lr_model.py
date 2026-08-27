# Task 7: LR model training script — trains and serialises the logistic regression classifier
"""
Training script for the SkillProof LR (logistic regression) readiness model.

Run from the skillproof-backend directory:

    python -m ml.train_lr_model

Outputs:
    ml/lr_model.pkl  — serialised sklearn Pipeline (scaler + LR)
"""
import logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Load labeled profiles, extract features, train, evaluate, and save the model.

    Steps:
    1. Load evaluation/labeled_profiles.csv (username, tier columns).
    2. For each username, fetch features from the database (or pre-computed CSV).
    3. Split into train/test sets (80/20 stratified).
    4. Fit a Pipeline(StandardScaler, LogisticRegression(C=1.0, max_iter=500)).
    5. Report accuracy and classification report on the test set.
    6. Serialize to ml/lr_model.pkl with joblib.dump().
    """
    pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

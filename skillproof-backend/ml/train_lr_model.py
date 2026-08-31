# Task 6: LR model training script — trains and serialises the logistic regression classifier
"""
Trains the SkillProof logistic regression readiness classifier.

Run from the skillproof-backend directory after populating
evaluation/labeled_profiles.csv with ~150 labeled profiles:

    python -m ml.train_lr_model

Outputs:
    ml/lr_model.pkl              — serialised sklearn Pipeline (scaler + LR)
    ml/feature_importances.json  — feature importance ranking for paper reporting
"""
from __future__ import annotations

import csv
import json
import logging
import sys
import time
from pathlib import Path

import joblib
import numpy as np
from dotenv import load_dotenv
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_BASE = Path(__file__).parent.parent
_CSV_PATH = _BASE / "evaluation" / "labeled_profiles.csv"
_MODEL_PATH = _BASE / "ml" / "lr_model.pkl"
_IMPORTANCES_PATH = _BASE / "ml" / "feature_importances.json"


def _load_labeled_profiles() -> list[dict]:
    if not _CSV_PATH.exists():
        logger.error("labeled_profiles.csv not found at %s", _CSV_PATH)
        sys.exit(1)
    with open(_CSV_PATH, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r.get("username", "").strip()]
    logger.info("Loaded %d labeled profiles from %s", len(rows), _CSV_PATH)
    return rows


def _fetch_features(rows: list[dict]) -> tuple[list, list]:
    """Fetch GitHub data and extract features for each labeled profile."""
    from ml.feature_schema import FEATURE_NAMES
    from services.feature_extractor import FeatureExtractor
    from services.github_fetcher import GitHubFetcher

    fetcher = GitHubFetcher()
    extractor = FeatureExtractor()

    X: list[list[float]] = []
    y: list[str] = []

    for i, row in enumerate(rows):
        username = row["username"].strip()
        tier = row["tier"].strip()
        try:
            logger.info("[%d/%d] Fetching %s (%s)...", i + 1, len(rows), username, tier)
            data = fetcher.get_user_data(username)
            features = extractor.extract_all_features(data)
            vector = [float(features.get(name, 0.0)) for name in FEATURE_NAMES]
            X.append(vector)
            y.append(tier)
            if i < len(rows) - 1:
                time.sleep(2)  # respect GitHub rate limits
        except Exception as exc:
            logger.warning("Skipping %s: %s", username, exc)

    return X, y


def main() -> None:
    rows = _load_labeled_profiles()

    if len(rows) < 30:
        logger.warning(
            "Only %d profiles — recommend at least 30 for a meaningful model. "
            "Add more profiles to evaluation/labeled_profiles.csv.",
            len(rows),
        )

    X_list, y = _fetch_features(rows)

    if len(X_list) < 10:
        logger.error("Too few successful fetches (%d) — aborting.", len(X_list))
        sys.exit(1)

    X = np.array(X_list, dtype=np.float64)
    logger.info("Feature matrix shape: %s", X.shape)

    # --- Train / test split (stratified) ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # --- Pipeline: StandardScaler + LogisticRegression ---
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("lr", LogisticRegression(C=1.0, max_iter=1000, random_state=42)),
    ])

    # --- Stratified k-fold cross-validation ---
    n_splits = min(5, min(y.count(c) for c in set(y)) if y else 1)
    n_splits = max(2, n_splits)
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, X, y, cv=cv, scoring="accuracy")
    logger.info("CV accuracy: %.3f ± %.3f", cv_scores.mean(), cv_scores.std())

    # --- Final fit ---
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    print("\n=== Classification Report ===")
    print(classification_report(y_test, y_pred))
    print("=== Confusion Matrix ===")
    print(confusion_matrix(y_test, y_pred))

    # --- Feature importances ---
    from ml.feature_schema import FEATURE_NAMES
    lr_step = pipeline.named_steps["lr"]
    classes = list(lr_step.classes_)
    strong_idx = classes.index("strong") if "strong" in classes else 0
    importances = sorted(
        [
            {"feature": name, "importance": float(coef)}
            for name, coef in zip(FEATURE_NAMES, lr_step.coef_[strong_idx])
        ],
        key=lambda x: abs(x["importance"]),
        reverse=True,
    )

    print("\n=== Top 10 Feature Importances (|coef| for 'strong' class) ===")
    for item in importances[:10]:
        print(f"  {item['feature']:<40} {item['importance']:+.4f}")

    # --- Save artefacts ---
    joblib.dump(pipeline, _MODEL_PATH)
    logger.info("Model saved to %s", _MODEL_PATH)

    with open(_IMPORTANCES_PATH, "w", encoding="utf-8") as f:
        json.dump(importances, f, indent=2)
    logger.info("Feature importances saved to %s", _IMPORTANCES_PATH)


if __name__ == "__main__":
    main()

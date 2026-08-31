# Task 6: LR scorer — logistic regression model wrapper
"""
Wraps the trained scikit-learn logistic regression Pipeline.

Falls back gracefully to (None, None) when ml/lr_model.pkl is absent so the
system operates in TPR-only mode until the model is trained in Task 18.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ml.feature_schema import FEATURE_NAMES

logger = logging.getLogger(__name__)

_MODEL_PATH = Path(__file__).parent.parent / "ml" / "lr_model.pkl"


class LRScorer:
    """Wraps the trained scikit-learn logistic regression model.

    Falls back gracefully to (None, None) when the model file is absent —
    the system operates in TPR-only mode until the model is trained.
    """

    def __init__(self) -> None:
        self._model = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the trained model from ml/lr_model.pkl — silently no-ops if absent."""
        if not _MODEL_PATH.exists():
            logger.info(
                "LR model not found at %s — running in TPR-only mode", _MODEL_PATH
            )
            return
        try:
            import joblib
            self._model = joblib.load(_MODEL_PATH)
            logger.info("LR model loaded from %s", _MODEL_PATH)
        except Exception as exc:
            logger.warning("Failed to load LR model: %s", exc)
            self._model = None

    def is_available(self) -> bool:
        """Return True if the model is loaded and ready."""
        return self._model is not None

    def features_to_array(self, features: Dict[str, float]) -> np.ndarray:
        """Convert feature dict to a (1, n_features) numpy array in FEATURE_NAMES order.

        Args:
            features: Canonical feature dict from FeatureExtractor.

        Returns:
            2-D numpy array of shape (1, 28) ready for model.predict_proba().
        """
        vector = [float(features.get(name, 0.0)) for name in FEATURE_NAMES]
        return np.array(vector, dtype=np.float64).reshape(1, -1)

    def score(
        self, features: Dict[str, float]
    ) -> Tuple[Optional[float], Optional[str]]:
        """Predict readiness score using the LR model.

        Args:
            features: Canonical feature dict from FeatureExtractor.

        Returns:
            Tuple of (lr_score, confidence_label):
              - lr_score: probability of 'strong' class × 100, in [0, 100].
                None when model unavailable.
              - confidence_label: 'high', 'medium', or 'low'. None when unavailable.
        """
        if self._model is None:
            return None, None
        try:
            X = self.features_to_array(features)
            proba = self._model.predict_proba(X)[0]
            classes = list(self._model.classes_)
            strong_idx = classes.index("strong") if "strong" in classes else -1
            if strong_idx == -1:
                return None, None
            strong_prob = float(proba[strong_idx])
            lr_score = round(strong_prob * 100, 1)
            max_prob = float(np.max(proba))
            if max_prob >= 0.75:
                confidence = "high"
            elif max_prob >= 0.50:
                confidence = "medium"
            else:
                confidence = "low"
            return lr_score, confidence
        except Exception as exc:
            logger.warning("LR scoring failed: %s", exc)
            return None, None

    def get_feature_importances(self) -> Optional[List[Dict[str, Any]]]:
        """Return feature importances as a ranked list for paper reporting.

        Returns:
            List of {"feature": str, "importance": float} sorted by |importance| desc.
            None if model unavailable or doesn't expose coef_.
        """
        if self._model is None:
            return None
        try:
            # sklearn Pipeline: the LR step is named "lr" in train_lr_model.py
            lr = self._model.named_steps.get("lr")
            if lr is None:
                # Fallback: bare LR model (not wrapped in a Pipeline)
                lr = self._model
            coef = lr.coef_
            classes = list(lr.classes_)
            strong_idx = classes.index("strong") if "strong" in classes else 0
            importances = coef[strong_idx]
            return sorted(
                [
                    {"feature": name, "importance": float(imp)}
                    for name, imp in zip(FEATURE_NAMES, importances)
                ],
                key=lambda x: abs(x["importance"]),
                reverse=True,
            )
        except Exception as exc:
            logger.warning("Could not extract feature importances: %s", exc)
            return None

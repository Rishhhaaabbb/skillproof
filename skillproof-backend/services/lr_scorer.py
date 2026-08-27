# Task 6: LR (Logistic Regression) scorer — ML-based tier classification
from typing import Any, Dict, Optional, Tuple


class LRScorer:
    """Wraps the trained scikit-learn logistic regression model for tier scoring.

    The LR scorer classifies a developer into one of three tiers:
      - 'junior' (0), 'mid' (1), 'senior' (2)

    The model artefact is stored at ``ml/lr_model.pkl`` and loaded lazily.
    Falls back gracefully when the model file is absent (returns None score).
    """

    def __init__(self) -> None:
        """Initialise the scorer; model is loaded lazily on first call to score()."""
        self._model = None

    def _load_model(self) -> None:
        """Load the trained model artefact from disk into self._model.

        Silently sets self._model to None if the file does not exist so the
        service can operate in a degraded (TPR-only) mode.
        """
        pass

    def score(self, features: Dict[str, float]) -> Tuple[Optional[float], Optional[str]]:
        """Predict a readiness score and confidence label using the LR model.

        Args:
            features: Canonical feature dict from FeatureExtractor.extract().

        Returns:
            A tuple of:
              - lr_score (float | None): Probability of the 'senior' class in
                [0, 1], scaled to [0, 100].  None when model is unavailable.
              - confidence_level (str | None): 'high', 'medium', or 'low' based
                on the max class probability.  None when model is unavailable.
        """
        pass

    def features_to_array(self, features: Dict[str, float]) -> Any:
        """Convert the feature dict to a numpy array in FEATURE_NAMES order.

        Args:
            features: Canonical feature dict.

        Returns:
            2-D numpy array of shape (1, n_features) ready for model.predict_proba().
        """
        pass

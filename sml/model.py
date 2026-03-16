from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score


@dataclass
class TrainResult:
    trained_samples: int
    batch_accuracy: float | None


@dataclass
class ScaleResult:
    scaled_up: bool
    message: str


class OnlineTextModel:
    def __init__(self, model_dir: str, n_features: int) -> None:
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.n_features = int(max(2**12, n_features))
        self.vectorizer = HashingVectorizer(n_features=self.n_features, alternate_sign=False, norm="l2")
        self.classifier = SGDClassifier(loss="log_loss", random_state=42)
        self.initialized = False

    @property
    def model_path(self) -> Path:
        return self.model_dir / "classifier.joblib"

    @property
    def state_path(self) -> Path:
        return self.model_dir / "state.joblib"

    def load(self) -> None:
        if self.model_path.exists() and self.state_path.exists():
            self.classifier = joblib.load(self.model_path)
            saved_state = joblib.load(self.state_path)
            self.initialized = bool(saved_state.get("initialized", False))
            saved_features = int(saved_state.get("n_features", self.n_features))
            self.n_features = max(2**12, saved_features)

            if hasattr(self.classifier, "coef_"):
                coef_shape = getattr(self.classifier, "coef_", None)
                if coef_shape is not None and len(self.classifier.coef_.shape) == 2:
                    self.n_features = int(self.classifier.coef_.shape[1])

            self.vectorizer = HashingVectorizer(n_features=self.n_features, alternate_sign=False, norm="l2")

    def save(self) -> None:
        joblib.dump(self.classifier, self.model_path)
        joblib.dump(
            {
                "initialized": self.initialized,
                "n_features": self.n_features,
                "estimated_params": self.estimated_params,
            },
            self.state_path,
        )

    @property
    def estimated_params(self) -> int:
        # For binary linear model: roughly one coefficient per feature plus bias.
        return int(self.n_features + 1)

    def train(self, texts: list[str], labels: list[int]) -> TrainResult:
        if not texts:
            return TrainResult(trained_samples=0, batch_accuracy=None)

        X = self.vectorizer.transform(texts)
        if not self.initialized:
            self.classifier.partial_fit(X, labels, classes=[0, 1])
            self.initialized = True
        else:
            self.classifier.partial_fit(X, labels)

        preds = self.classifier.predict(X)
        acc = float(accuracy_score(labels, preds))
        self.save()
        return TrainResult(trained_samples=len(texts), batch_accuracy=acc)

    def maybe_scale_up(
        self,
        *,
        scaling_enabled: bool,
        cycle_id: int,
        scale_every_cycles: int,
        trained_samples: int,
        batch_accuracy: float | None,
        min_samples: int,
        min_accuracy: float,
        target_params: int,
        max_features: int,
        feature_ladder: list[int],
    ) -> ScaleResult:
        if not scaling_enabled:
            return ScaleResult(scaled_up=False, message="scaling disabled")
        if self.estimated_params >= target_params:
            return ScaleResult(scaled_up=False, message="target parameter count reached")
        if cycle_id % max(1, scale_every_cycles) != 0:
            return ScaleResult(scaled_up=False, message="not a scaling cycle")
        if trained_samples < min_samples:
            return ScaleResult(scaled_up=False, message=f"trained samples {trained_samples} below minimum {min_samples}")
        if batch_accuracy is None:
            return ScaleResult(scaled_up=False, message="batch accuracy unavailable")
        if batch_accuracy < min_accuracy:
            return ScaleResult(scaled_up=False, message=f"batch accuracy {batch_accuracy:.4f} below minimum {min_accuracy:.4f}")

        ladder = sorted({int(v) for v in feature_ladder if int(v) > 0})
        next_features = None
        for val in ladder:
            if val > self.n_features:
                next_features = val
                break
        if next_features is None:
            next_features = min(max_features, self.n_features * 2)

        if next_features <= self.n_features:
            return ScaleResult(scaled_up=False, message="already at configured max feature capacity")

        self.n_features = int(next_features)
        self.vectorizer = HashingVectorizer(n_features=self.n_features, alternate_sign=False, norm="l2")
        self.classifier = SGDClassifier(loss="log_loss", random_state=42)
        self.initialized = False
        self.save()
        return ScaleResult(
            scaled_up=True,
            message=(
                f"scaled model features to {self.n_features} "
                f"(estimated params {self.estimated_params}, target {target_params})"
            ),
        )

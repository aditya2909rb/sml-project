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


class OnlineTextModel:
    def __init__(self, model_dir: str) -> None:
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.vectorizer = HashingVectorizer(n_features=2**18, alternate_sign=False, norm="l2")
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
            self.initialized = bool(joblib.load(self.state_path).get("initialized", False))

    def save(self) -> None:
        joblib.dump(self.classifier, self.model_path)
        joblib.dump({"initialized": self.initialized}, self.state_path)

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

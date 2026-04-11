import csv
import json
import math
import random
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.-]{1,}")
TARGET_FIELDS = (
    "score",
    "communication_score",
    "structure_score",
    "relevance_score",
    "specificity_score",
)
FIELD_ALIASES = {
    "question": ("question", "prompt", "interview_question"),
    "answer": ("answer", "response", "candidate_answer"),
    "interview_type": ("interview_type", "category", "type"),
    "score": ("score", "overall_score", "label"),
    "communication_score": ("communication_score", "communication", "clarity_score"),
    "structure_score": ("structure_score", "structure", "organization_score"),
    "relevance_score": ("relevance_score", "relevance", "alignment_score"),
    "specificity_score": ("specificity_score", "specificity", "detail_score"),
}


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def clamp_score(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 1)


def safe_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def compute_features(question: str, answer: str, interview_type: str) -> dict[str, float]:
    normalized_answer = answer.strip()
    lower_answer = normalized_answer.lower()
    answer_tokens = tokenize(normalized_answer)
    question_tokens = [token for token in tokenize(question) if len(token) > 4]
    unique_answer_tokens = set(answer_tokens)
    relevance_hits = sum(1 for token in question_tokens[:8] if token in unique_answer_tokens)

    feature_map = {
        "bias": 1.0,
        "word_count": float(len(answer_tokens)),
        "question_word_count": float(len(question_tokens)),
        "relevance_hits": float(relevance_hits),
        "has_digit": 1.0 if any(char.isdigit() for char in normalized_answer) else 0.0,
        "has_star_terms": 1.0
        if any(token in lower_answer for token in ("situation", "task", "action", "result"))
        else 0.0,
        "has_sequence_terms": 1.0
        if any(token in lower_answer for token in ("first", "then", "finally", "because"))
        else 0.0,
        "has_metrics_language": 1.0
        if any(token in lower_answer for token in ("latency", "conversion", "uptime", "metric", "percent", "users", "ms"))
        else 0.0,
        "has_tradeoff_language": 1.0
        if any(token in lower_answer for token in ("therefore", "because", "tradeoff", "learned", "impact"))
        else 0.0,
        "is_short_answer": 1.0 if len(answer_tokens) < 25 else 0.0,
        "is_long_answer": 1.0 if len(answer_tokens) > 220 else 0.0,
        "interview_type_technical": 1.0 if interview_type.lower() == "technical" else 0.0,
        "interview_type_hr": 1.0 if interview_type.lower() == "hr" else 0.0,
        "interview_type_stress": 1.0 if interview_type.lower() == "stress" else 0.0,
    }
    return feature_map


def _detect_field(row: dict[str, Any], field_name: str) -> str | None:
    lowered = {key.lower(): key for key in row.keys()}
    for alias in FIELD_ALIASES[field_name]:
        if alias in lowered:
            return lowered[alias]
    return None


def _normalize_row(row: dict[str, Any], field_map: dict[str, str]) -> dict[str, Any]:
    normalized = {
        "question": str(row.get(field_map["question"], "")).strip(),
        "answer": str(row.get(field_map["answer"], "")).strip(),
        "interview_type": str(row.get(field_map.get("interview_type", ""), "hr") or "hr").strip() or "hr",
    }
    for field_name in TARGET_FIELDS:
        source_name = field_map.get(field_name)
        normalized[field_name] = safe_float(row.get(source_name)) if source_name else None
    return normalized


def load_training_records(dataset_path: str | Path) -> list[dict[str, Any]]:
    path = Path(dataset_path)
    suffix = path.suffix.lower()

    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
    elif suffix == ".json":
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, list):
            rows = payload
        elif isinstance(payload, dict) and isinstance(payload.get("records"), list):
            rows = payload["records"]
        else:
            raise ValueError("JSON dataset must be a list of rows or an object with a 'records' list.")
    elif suffix == ".jsonl":
        with path.open("r", encoding="utf-8") as handle:
            rows = [json.loads(line) for line in handle if line.strip()]
    else:
        raise ValueError(f"Unsupported dataset format: {path.suffix}")

    if not rows:
        raise ValueError("Dataset is empty.")

    sample_row = rows[0]
    required = ("question", "answer")
    field_map: dict[str, str] = {}
    for field_name in required:
        resolved = _detect_field(sample_row, field_name)
        if not resolved:
            raise ValueError(f"Dataset is missing a '{field_name}' column.")
        field_map[field_name] = resolved

    for optional_field in ("interview_type",) + TARGET_FIELDS:
        resolved = _detect_field(sample_row, optional_field)
        if resolved:
            field_map[optional_field] = resolved

    normalized_rows = [_normalize_row(row, field_map) for row in rows]
    usable_rows = [row for row in normalized_rows if row["question"] and row["answer"]]
    if not usable_rows:
        raise ValueError("Dataset does not contain any usable rows with question and answer text.")
    return usable_rows


@dataclass
class TextRegressor:
    bias: float
    feature_weights: dict[str, float]
    token_weights: dict[str, float]
    intercept_scale: float = 1.0

    def predict(self, question: str, answer: str, interview_type: str) -> float:
        features = compute_features(question, answer, interview_type)
        value = self.bias * self.intercept_scale
        for name, weight in self.feature_weights.items():
            value += features.get(name, 0.0) * weight

        token_counts = Counter(tokenize(f"{question} {answer}"))
        for token, count in token_counts.items():
            value += self.token_weights.get(token, 0.0) * count
        return clamp_score(value)


def _build_vocab(records: list[dict[str, Any]], limit: int) -> list[str]:
    counts = Counter()
    for record in records:
        counts.update(tokenize(f"{record['question']} {record['answer']}"))
    return [token for token, _ in counts.most_common(limit)]


def _split_records(records: list[dict[str, Any]], validation_ratio: float) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    shuffled = list(records)
    random.Random(42).shuffle(shuffled)
    validation_size = max(1, int(len(shuffled) * validation_ratio)) if len(shuffled) > 4 else 1
    return shuffled[validation_size:], shuffled[:validation_size]


def _fit_regressor(
    rows: list[dict[str, Any]],
    target_field: str,
    vocab: list[str],
    epochs: int,
    learning_rate: float,
) -> TextRegressor:
    bias = 50.0
    feature_weights = {name: 0.0 for name in compute_features("", "", "hr").keys() if name != "bias"}
    token_weights = {token: 0.0 for token in vocab}

    training_examples = [row for row in rows if row.get(target_field) is not None]
    if not training_examples:
        raise ValueError(f"No labels found for '{target_field}'.")

    for _ in range(epochs):
        random.Random(42).shuffle(training_examples)
        for row in training_examples:
            features = compute_features(row["question"], row["answer"], row["interview_type"])
            token_counts = Counter(tokenize(f"{row['question']} {row['answer']}"))
            prediction = bias
            for name, value in features.items():
                if name == "bias":
                    continue
                prediction += feature_weights[name] * value
            for token, count in token_counts.items():
                if token in token_weights:
                    prediction += token_weights[token] * count

            error = prediction - float(row[target_field])
            bias -= learning_rate * error
            for name, value in features.items():
                if name == "bias":
                    continue
                feature_weights[name] -= learning_rate * error * value / 100.0
            for token, count in token_counts.items():
                if token in token_weights:
                    token_weights[token] -= learning_rate * error * count / 100.0

    return TextRegressor(bias=bias, feature_weights=feature_weights, token_weights=token_weights)


def _mae(model: TextRegressor, rows: list[dict[str, Any]], target_field: str) -> float | None:
    labelled = [row for row in rows if row.get(target_field) is not None]
    if not labelled:
        return None
    errors = [
        abs(model.predict(row["question"], row["answer"], row["interview_type"]) - float(row[target_field]))
        for row in labelled
    ]
    return round(sum(errors) / len(errors), 3)


def train_and_serialize(
    dataset_path: str | Path,
    output_path: str | Path,
    vocab_size: int = 600,
    epochs: int = 14,
    learning_rate: float = 0.0035,
    validation_ratio: float = 0.2,
) -> dict[str, Any]:
    records = load_training_records(dataset_path)
    train_rows, validation_rows = _split_records(records, validation_ratio)
    if not train_rows:
        train_rows = records
        validation_rows = []

    vocab = _build_vocab(train_rows, vocab_size)
    models: dict[str, TextRegressor] = {}
    metrics: dict[str, Any] = {}

    for target_field in TARGET_FIELDS:
        if not any(row.get(target_field) is not None for row in train_rows):
            continue
        model = _fit_regressor(train_rows, target_field, vocab, epochs, learning_rate)
        models[target_field] = model
        metrics[target_field] = {
            "train_mae": _mae(model, train_rows, target_field),
            "validation_mae": _mae(model, validation_rows, target_field) if validation_rows else None,
        }

    if not models:
        raise ValueError("Dataset does not contain any score labels to train against.")

    artifact = {
        "version": 1,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "dataset_path": str(Path(dataset_path)),
        "record_count": len(records),
        "vocab_size": len(vocab),
        "metrics": metrics,
        "models": {
            name: {
                "bias": model.bias,
                "feature_weights": model.feature_weights,
                "token_weights": model.token_weights,
            }
            for name, model in models.items()
        },
    }

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    return artifact


def load_artifact(artifact_path: str | Path) -> dict[str, TextRegressor]:
    path = Path(artifact_path)
    if not path.exists():
        return {}

    payload = json.loads(path.read_text(encoding="utf-8"))
    models = {}
    for name, model_data in payload.get("models", {}).items():
        models[name] = TextRegressor(
            bias=float(model_data["bias"]),
            feature_weights={key: float(value) for key, value in model_data["feature_weights"].items()},
            token_weights={key: float(value) for key, value in model_data["token_weights"].items()},
        )
    return models

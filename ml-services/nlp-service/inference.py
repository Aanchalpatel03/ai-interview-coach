import csv
import json
import math
import random
import re
from collections import Counter
from pathlib import Path
from typing import Any

TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.-]{1,}")
ROLE_CONTEXT_PREFIX = " Frame your answer for a "
ROLE_CONTEXT_SUFFIX = " context."
QUESTION_BANK = {
    "technical": [
        "Explain a recent system you built and the tradeoffs you made.",
        "How would you reduce latency in a React and FastAPI application?",
        "Describe a production incident and how you resolved it.",
        "How would you design a scalable notification service for web and mobile users?",
        "Tell me about a time you improved application performance. What did you measure before and after?",
    ],
    "hr": [
        "Tell me about yourself.",
        "Describe a time you handled conflict in a team.",
        "Why do you want this role?",
        "Describe a time you had to learn a new skill quickly to deliver a project.",
        "Tell me about a project you are proud of and why it mattered.",
    ],
    "resume": [
        "Walk me through the most relevant project on your resume.",
        "Which line item on your resume best shows your impact, and why?",
    ],
}
SKILL_QUESTIONS = {
    "react": ["How do you prevent unnecessary re-renders in a complex React screen without overusing memoization?"],
    "nextjs": ["When would you choose server components over client components in Next.js, and why?"],
    "fastapi": ["How would you structure a FastAPI service for maintainability and resilience?"],
    "system design": ["Design an interview coaching platform that supports realtime AI feedback at scale."],
}


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return round(max(low, min(high, value)), 1)


def load_artifact(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_artifact(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_records(dataset_path: Path) -> list[dict[str, Any]]:
    if dataset_path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in dataset_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if dataset_path.suffix.lower() == ".json":
        payload = json.loads(dataset_path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict) and isinstance(payload.get("records"), list):
            return payload["records"]
    if dataset_path.suffix.lower() == ".csv":
        with dataset_path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    raise ValueError(f"Unsupported dataset: {dataset_path}")


class SentenceSimilarityModel:
    def __init__(self) -> None:
        self.model = None
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", cache_folder=str(Path(__file__).parent / "artifacts"))
        except Exception:
            self.model = None

    def similarity(self, text_a: str, text_b: str) -> float:
        if self.model is not None:
            try:
                embeddings = self.model.encode([text_a, text_b], normalize_embeddings=True)
                score = float(sum(a * b for a, b in zip(embeddings[0], embeddings[1])))
                return clamp((score + 1) * 50)
            except Exception:
                pass
        tokens_a = set(tokenize(text_a))
        tokens_b = set(tokenize(text_b))
        if not tokens_a or not tokens_b:
            return 0.0
        overlap = len(tokens_a & tokens_b)
        denominator = math.sqrt(len(tokens_a) * len(tokens_b))
        return clamp((overlap / denominator) * 100)


class NlpEngine:
    def __init__(self, artifact_path: Path | None = None) -> None:
        self.artifact_path = artifact_path or Path(__file__).with_name("artifacts").joinpath("nlp-calibration.json")
        self.artifact = load_artifact(self.artifact_path)
        self.similarity_model = SentenceSimilarityModel()
        self.dataset_questions = self._load_dataset_questions()

    def health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "artifact_loaded": bool(self.artifact),
            "semantic_model_loaded": self.similarity_model.model is not None,
        }

    def evaluate(self, question: str, answer: str, interview_type: str) -> dict[str, Any]:
        lower_answer = answer.lower()
        answer_tokens = tokenize(answer)
        keyword_candidates = [token for token in tokenize(question) if len(token) > 4]
        keywords_matched = [token for token in keyword_candidates[:10] if token in set(answer_tokens)]
        semantic_similarity = self.similarity_model.similarity(question, answer)

        structure_score = 58.0
        if any(token in lower_answer for token in ("situation", "task", "action", "result")):
            structure_score += 20
        elif any(token in lower_answer for token in ("first", "then", "finally", "because")):
            structure_score += 12
        elif len(answer_tokens) < 20:
            structure_score -= 18

        relevance_score = 45 + len(keywords_matched) * 8 + semantic_similarity * 0.15
        specificity_score = 48.0
        if any(char.isdigit() for char in answer):
            specificity_score += 15
        if any(token in lower_answer for token in ("latency", "metric", "uptime", "percent", "users", "scale")):
            specificity_score += 16
        if len(answer_tokens) < 25:
            specificity_score -= 10

        communication_score = 55.0
        if 40 <= len(answer_tokens) <= 170:
            communication_score += 18
        if any(token in lower_answer for token in ("therefore", "because", "tradeoff", "impact", "result")):
            communication_score += 12
        if len(answer_tokens) > 220:
            communication_score -= 8

        confidence_level = 82.0
        if any(phrase in lower_answer for phrase in ("maybe", "kind of", "sort of", "i think", "probably")):
            confidence_level -= 18
        confidence_level = clamp(confidence_level)

        calibration = self.artifact.get("calibration", {})
        score = (
            structure_score * calibration.get("structure_weight", 0.2)
            + relevance_score * calibration.get("relevance_weight", 0.2)
            + specificity_score * calibration.get("specificity_weight", 0.2)
            + communication_score * calibration.get("communication_weight", 0.15)
            + semantic_similarity * calibration.get("semantic_weight", 0.15)
            + confidence_level * calibration.get("confidence_weight", 0.1)
        )
        score = clamp(score)

        suggestions = []
        if structure_score < 70:
            suggestions.append("Use Situation, Action, and Result to make the answer easier to follow.")
        if specificity_score < 70:
            suggestions.append("Add metrics, scale, or constraints to prove impact.")
        if confidence_level < 70:
            suggestions.append("Remove hedge phrases and end with a firmer result statement.")
        if communication_score < 70:
            suggestions.append("Tighten the wording so the main point lands faster.")
        if not suggestions:
            suggestions.append("Keep the same structure and continue emphasizing measurable impact.")

        feedback = "Strong answer with clear relevance and concrete action." if score >= 80 else "The answer is useful, but it needs tighter structure or stronger specifics."
        if score < 65:
            feedback = "The answer is too generic. Add clearer structure, stronger evidence, and a more direct result."

        return {
            "score": score,
            "communication_score": clamp(communication_score),
            "structure_score": clamp(structure_score),
            "relevance_score": clamp(relevance_score),
            "specificity_score": clamp(specificity_score),
            "semantic_similarity": semantic_similarity,
            "confidence_level": confidence_level,
            "keywords_matched": keywords_matched,
            "strengths": [
                "The answer addresses the prompt directly.",
                "The answer shows concrete ownership." if specificity_score >= 70 else "There is a usable baseline to improve from.",
            ],
            "improvements": suggestions,
            "verdict": "Strong answer" if score >= 80 else "Decent answer" if score >= 65 else "Needs improvement",
            "feedback": feedback,
            "suggestions": suggestions,
        }

    def generate_question(self, interview_type: str, target_role: str | None, skills: list[str], previous_questions: list[str]) -> dict[str, str]:
        interview_type = interview_type.lower()
        bucket = list(self.dataset_questions.get(interview_type, []))
        bucket.extend(QUESTION_BANK.get(interview_type, QUESTION_BANK["hr"]))
        for skill in skills:
            bucket.extend(SKILL_QUESTIONS.get(skill.lower(), []))
        deduped_bucket = list(dict.fromkeys(bucket))
        previous = {self._normalize_question(question) for question in previous_questions}
        available = [question for question in deduped_bucket if self._normalize_question(question) not in previous] or deduped_bucket
        question = random.choice(available)
        if target_role:
            question = f"{question}{ROLE_CONTEXT_PREFIX}{target_role}{ROLE_CONTEXT_SUFFIX}"
        category = "resume" if interview_type == "resume" else ("skill-based" if any(skill.lower() in question.lower() for skill in skills) else interview_type)
        return {"question": question, "category": category}

    def _load_dataset_questions(self) -> dict[str, list[str]]:
        dataset_buckets: dict[str, list[str]] = {}
        for path in Path(__file__).parent.glob("*.jsonl"):
            try:
                for line in path.read_text(encoding="utf-8").splitlines():
                    if not line.strip():
                        continue
                    record = json.loads(line)
                    question = str(record.get("question", "")).strip()
                    interview_type = str(record.get("interview_type", "hr")).strip().lower() or "hr"
                    if question:
                        dataset_buckets.setdefault(interview_type, []).append(question)
            except (OSError, json.JSONDecodeError):
                continue
        return dataset_buckets

    def _normalize_question(self, question: str) -> str:
        if ROLE_CONTEXT_PREFIX in question and question.endswith(ROLE_CONTEXT_SUFFIX):
            return question.split(ROLE_CONTEXT_PREFIX, 1)[0].strip()
        return question.strip()


def build_calibration_artifact(records: list[dict[str, Any]]) -> dict[str, Any]:
    interview_type_counts = Counter(str(record.get("interview_type", "hr")).strip().lower() or "hr" for record in records)
    return {
        "record_count": len(records),
        "interview_type_counts": dict(interview_type_counts),
        "calibration": {
            "structure_weight": 0.2,
            "relevance_weight": 0.2,
            "specificity_weight": 0.2,
            "communication_weight": 0.15,
            "semantic_weight": 0.15,
            "confidence_weight": 0.1,
        },
    }

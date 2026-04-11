import json
import random
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

from modeling import load_artifact

app = FastAPI(title="NLP Service")


class QuestionRequest(BaseModel):
    interview_type: str
    target_role: str | None = None
    skills: list[str] = []
    previous_questions: list[str] = Field(default_factory=list)


class AnswerRequest(BaseModel):
    question: str
    answer: str
    interview_type: str


QUESTION_BANK = {
    "technical": [
        "Explain a recent system you built and the tradeoffs you made.",
        "How would you reduce latency in a React and FastAPI application?",
        "Describe a production incident and how you resolved it.",
        "How would you design a scalable notification service for web and mobile users?",
        "Tell me about a time you improved application performance. What did you measure before and after?",
        "How do you decide between shipping quickly and refactoring for long-term maintainability?",
        "Describe how you would debug intermittent API failures in production.",
        "What architectural changes would you make if your application traffic grew tenfold?",
        "How would you secure a file upload pipeline that accepts resumes from users?",
        "Walk me through a difficult technical decision where there was no obviously correct answer.",
    ],
    "hr": [
        "Tell me about yourself.",
        "Describe a time you handled conflict in a team.",
        "Why do you want this role?",
        "Describe a time you had to learn a new skill quickly to deliver a project.",
        "Tell me about a project you are proud of and why it mattered.",
        "How do you prioritize work when multiple deadlines collide?",
        "Describe a time you received difficult feedback and what you changed afterward.",
        "What kind of environment helps you perform at your best?",
        "Tell me about a time you disagreed with your manager or teammate.",
        "What makes you a strong fit for this team beyond the technical requirements?",
    ],
    "stress": [
        "Why should we not hire you?",
        "What would your manager say you still need to improve?",
        "Describe a failure that changed how you work.",
        "Tell me about a time you missed expectations. Why did it happen?",
        "What is the weakest area in your current skill set?",
        "If I called your previous lead, what criticism would they repeat first?",
        "Why do you think a stronger candidate might outperform you in this role?",
        "What part of your last project would you redo completely if given another chance?",
    ],
}

SKILL_QUESTIONS = {
    "react": [
        "How do you prevent unnecessary re-renders in a complex React screen without overusing memoization?",
        "Describe a frontend architecture decision you made in React that improved maintainability.",
    ],
    "nextjs": [
        "When would you choose server components over client components in Next.js, and why?",
        "How would you optimize a data-heavy Next.js dashboard for first-load performance?",
    ],
    "fastapi": [
        "How would you structure a FastAPI service for long-term maintainability and testability?",
        "Describe how you would handle async workloads and external service failures in FastAPI.",
    ],
    "docker": [
        "How do you design container images and runtime configuration for fast deployments and low risk?",
        "Tell me about a time Docker helped you solve an environment consistency problem.",
    ],
    "aws": [
        "How would you design a cost-aware but scalable deployment on AWS for a growing SaaS application?",
        "What AWS services would you choose for secure file uploads, storage, and background processing?",
    ],
    "system design": [
        "Design an interview coaching platform that supports realtime video feedback for thousands of concurrent users.",
        "How would you partition responsibilities between the frontend, API, and AI services in a realtime product?",
    ],
}

MODEL_ARTIFACT_PATH = Path(__file__).with_name("artifacts").joinpath("answer_scoring_model.json")
TRAINED_MODELS = load_artifact(MODEL_ARTIFACT_PATH)
ROLE_CONTEXT_PREFIX = " Frame your answer for a "
ROLE_CONTEXT_SUFFIX = " context."


def _normalize_question(question: str) -> str:
    if ROLE_CONTEXT_PREFIX in question and question.endswith(ROLE_CONTEXT_SUFFIX):
        return question.split(ROLE_CONTEXT_PREFIX, 1)[0].strip()
    return question.strip()


def _load_dataset_questions() -> dict[str, list[str]]:
    dataset_buckets: dict[str, list[str]] = {}
    for path in Path(__file__).parent.glob("*.jsonl"):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue

        for line in lines:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            question = str(record.get("question", "")).strip()
            interview_type = str(record.get("interview_type", "hr")).strip().lower() or "hr"
            if not question:
                continue
            dataset_buckets.setdefault(interview_type, []).append(question)

    return dataset_buckets


DATASET_QUESTIONS = _load_dataset_questions()


@app.get("/health")
async def health():
    return {"status": "ok", "trained_model_loaded": bool(TRAINED_MODELS)}


@app.post("/generate-question")
async def generate_question(payload: QuestionRequest):
    interview_type = payload.interview_type.lower()
    bucket = list(DATASET_QUESTIONS.get(interview_type, []))
    bucket.extend(QUESTION_BANK.get(interview_type, QUESTION_BANK["hr"]))
    for skill in payload.skills:
        bucket.extend(SKILL_QUESTIONS.get(skill.lower(), []))

    previous_questions = {_normalize_question(question) for question in payload.previous_questions}
    deduped_bucket = list(dict.fromkeys(bucket))
    unused_questions = [question for question in deduped_bucket if _normalize_question(question) not in previous_questions]
    candidate_pool = unused_questions or deduped_bucket
    question = random.choice(candidate_pool)

    if payload.target_role:
        question = f"{question}{ROLE_CONTEXT_PREFIX}{payload.target_role}{ROLE_CONTEXT_SUFFIX}"

    category = "skill-based" if _normalize_question(question) in sum(SKILL_QUESTIONS.values(), []) else interview_type
    return {"question": question, "category": category}


@app.post("/evaluate-answer")
async def evaluate_answer(payload: AnswerRequest):
    if TRAINED_MODELS:
        return _evaluate_with_model(payload)
    return _evaluate_with_heuristics(payload)


def _evaluate_with_heuristics(payload: AnswerRequest):
    answer = payload.answer.strip()
    lower_answer = answer.lower()
    words = answer.split()
    word_count = len(words)

    structure_score = 58
    if any(token in lower_answer for token in ["situation", "task", "action", "result"]):
        structure_score += 20
    elif any(token in lower_answer for token in ["first", "then", "finally", "because"]):
        structure_score += 12
    elif word_count < 20:
        structure_score -= 18

    relevance_keywords = [token for token in payload.question.lower().replace("?", "").split() if len(token) > 4]
    relevance_hits = sum(1 for token in relevance_keywords[:8] if token in lower_answer)
    relevance_score = min(100, 48 + relevance_hits * 8)

    specificity_score = 50
    if any(char.isdigit() for char in answer):
        specificity_score += 18
    if any(token in lower_answer for token in ["latency", "conversion", "uptime", "metric", "percent", "users", "ms"]):
        specificity_score += 16
    if word_count < 25:
        specificity_score -= 12

    communication_score = 55
    if 45 <= word_count <= 170:
        communication_score += 18
    if any(token in lower_answer for token in ["therefore", "because", "tradeoff", "learned", "impact"]):
        communication_score += 14
    if word_count > 220:
        communication_score -= 10

    score = round(min(100, (structure_score * 0.3) + (relevance_score * 0.35) + (specificity_score * 0.2) + (communication_score * 0.15)), 1)
    communication_score = round(min(100, communication_score), 1)
    structure_score = round(min(100, structure_score), 1)
    relevance_score = round(min(100, relevance_score), 1)
    specificity_score = round(min(100, specificity_score), 1)

    strengths = []
    improvements = []

    if structure_score >= 72:
        strengths.append("Your answer had a clear flow instead of sounding improvised.")
    else:
        improvements.append("Use a simple structure like Situation, Action, and Result to make the answer easier to follow.")

    if specificity_score >= 72:
        strengths.append("You included concrete detail, which makes the answer more credible.")
    else:
        improvements.append("Add stronger specifics such as metrics, scale, constraints, or concrete decisions.")

    if relevance_score >= 72:
        strengths.append("Your response stayed aligned with the actual question.")
    else:
        improvements.append("Stay closer to the question prompt and avoid drifting into unrelated background.")

    if communication_score >= 72:
        strengths.append("Your delivery reads concise and interviewer-friendly.")
    else:
        improvements.append("Tighten the wording and reduce filler so the core point lands faster.")

    if not strengths:
        strengths.append("You made an attempt to answer directly, which is the right baseline.")
    if not improvements:
        improvements.append("Push the answer one step further by finishing with measurable impact or a stronger lesson learned.")

    if score >= 82:
        verdict = "Strong answer"
        feedback = "This reads like a confident interview answer. Keep the same structure and continue emphasizing decisions, tradeoffs, and measurable outcomes."
    elif score >= 68:
        verdict = "Decent answer"
        feedback = "The answer is on the right track, but it needs sharper structure or more specificity to feel interview-ready."
    else:
        verdict = "Needs improvement"
        feedback = "The answer addresses the topic, but it is still too generic or under-structured to score well in a real interview."

    return {
        "score": score,
        "communication_score": communication_score,
        "structure_score": structure_score,
        "relevance_score": relevance_score,
        "specificity_score": specificity_score,
        "verdict": verdict,
        "strengths": strengths,
        "improvements": improvements,
        "feedback": feedback,
    }


def _evaluate_with_model(payload: AnswerRequest):
    heuristic_scores = _evaluate_with_heuristics(payload)
    predictions = {}
    for field_name, model in TRAINED_MODELS.items():
        predictions[field_name] = model.predict(payload.question, payload.answer, payload.interview_type)

    structure_score = predictions.get("structure_score", heuristic_scores["structure_score"])
    relevance_score = predictions.get("relevance_score", heuristic_scores["relevance_score"])
    specificity_score = predictions.get("specificity_score", heuristic_scores["specificity_score"])
    communication_score = predictions.get("communication_score", heuristic_scores["communication_score"])
    score = predictions.get("score")
    if score is None:
        score = round(
            min(
                100,
                (structure_score * 0.3)
                + (relevance_score * 0.35)
                + (specificity_score * 0.2)
                + (communication_score * 0.15),
            ),
            1,
        )

    strengths = []
    improvements = []

    if structure_score >= 72:
        strengths.append("Your answer had a clear flow instead of sounding improvised.")
    else:
        improvements.append("Use a simple structure like Situation, Action, and Result to make the answer easier to follow.")

    if specificity_score >= 72:
        strengths.append("You included concrete detail, which makes the answer more credible.")
    else:
        improvements.append("Add stronger specifics such as metrics, scale, constraints, or concrete decisions.")

    if relevance_score >= 72:
        strengths.append("Your response stayed aligned with the actual question.")
    else:
        improvements.append("Stay closer to the question prompt and avoid drifting into unrelated background.")

    if communication_score >= 72:
        strengths.append("Your delivery reads concise and interviewer-friendly.")
    else:
        improvements.append("Tighten the wording and reduce filler so the core point lands faster.")

    if not strengths:
        strengths.append("You made an attempt to answer directly, which is the right baseline.")
    if not improvements:
        improvements.append("Push the answer one step further by finishing with measurable impact or a stronger lesson learned.")

    if score >= 82:
        verdict = "Strong answer"
        feedback = "This reads like a confident interview answer. Keep the same structure and continue emphasizing decisions, tradeoffs, and measurable outcomes."
    elif score >= 68:
        verdict = "Decent answer"
        feedback = "The answer is on the right track, but it needs sharper structure or more specificity to feel interview-ready."
    else:
        verdict = "Needs improvement"
        feedback = "The answer addresses the topic, but it is still too generic or under-structured to score well in a real interview."

    return {
        "score": round(score, 1),
        "communication_score": round(communication_score, 1),
        "structure_score": round(structure_score, 1),
        "relevance_score": round(relevance_score, 1),
        "specificity_score": round(specificity_score, 1),
        "verdict": verdict,
        "strengths": strengths,
        "improvements": improvements,
        "feedback": feedback,
    }

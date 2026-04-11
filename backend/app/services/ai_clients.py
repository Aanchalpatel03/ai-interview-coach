import asyncio
import base64
import hashlib
import json
import random
import statistics
import wave
from io import BytesIO
from pathlib import Path

import httpx

from app.core.config import settings

ROLE_CONTEXT_PREFIX = " Frame your answer for a "
ROLE_CONTEXT_SUFFIX = " context."
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
_VIDEO_CACHE: dict[str, dict] = {}


def _normalize_question(question: str) -> str:
    if ROLE_CONTEXT_PREFIX in question and question.endswith(ROLE_CONTEXT_SUFFIX):
        return question.split(ROLE_CONTEXT_PREFIX, 1)[0].strip()
    return question.strip()


def _load_dataset_questions() -> dict[str, list[str]]:
    dataset_dir = Path(__file__).resolve().parents[3] / "ai-services" / "nlp"
    dataset_buckets: dict[str, list[str]] = {}
    for path in dataset_dir.glob("*.jsonl"):
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


async def _post_with_fallback(base_url: str, paths: list[str], payload: dict, timeout: float = 20.0) -> dict:
    async with httpx.AsyncClient(timeout=timeout) as client:
        last_error = None
        for path in paths:
            try:
                response = await client.post(f"{base_url}{path}", json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as exc:
                last_error = exc
        if last_error:
            raise last_error
        raise RuntimeError("No service path configured")


async def generate_question(interview_type: str, role: str | None, skills: list[str], previous_questions: list[str]) -> dict:
    payload = {"interview_type": interview_type, "target_role": role, "skills": skills, "previous_questions": previous_questions}
    try:
        return await _post_with_fallback(
            settings.nlp_service_url,
            ["/ml/nlp/generate-question", "/generate-question"],
            payload,
        )
    except (httpx.HTTPError, RuntimeError):
        return _generate_question_locally(interview_type, role, skills, previous_questions)


async def evaluate_answer(question: str, answer: str, interview_type: str) -> dict:
    payload = {"question": question, "answer": answer, "interview_type": interview_type}
    try:
        return await _post_with_fallback(
            settings.nlp_service_url,
            ["/ml/nlp/evaluate", "/evaluate-answer"],
            payload,
        )
    except (httpx.HTTPError, RuntimeError):
        return _evaluate_answer_locally(question, answer)


async def analyze_video_frame(frame: str, interview_id: str | None = None) -> dict:
    cache_key = None
    if interview_id:
        digest = hashlib.sha1(frame.encode("utf-8")).hexdigest()
        cache_key = f"{interview_id}:{digest}"
        if cache_key in _VIDEO_CACHE:
            return _VIDEO_CACHE[cache_key]

    try:
        vision_task = _post_with_fallback(
            settings.vision_service_url,
            ["/ml/vision/analyze-frame", "/analyze-frame"],
            {"frame": frame},
        )
        emotion_task = _post_with_fallback(
            settings.emotion_service_url,
            ["/ml/emotion/analyze", "/analyze-emotion"],
            {"frame": frame},
        )
        vision_data, emotion_data = await asyncio.gather(vision_task, emotion_task)
    except (httpx.HTTPError, RuntimeError):
        vision_data = {
            "posture_score": 72,
            "eye_contact_score": 68,
            "hand_movement_score": 70,
            "posture": "good",
            "head_position": "aligned",
            "hand_movement": "stable",
            "eye_alignment": "aligned",
            "suggestions": ["Delivery looks stable. Keep the same pace and presence."],
        }
        emotion_data = {
            "emotion": "confident",
            "confidence_score": 74,
            "nervousness_score": 26,
            "engagement_score": 71,
            "smile_score": 62,
            "eye_contact_score": 68,
            "suggestions": ["Slow down your delivery and finish with a stronger result statement."],
        }

    aggregate = _combine_video_signals(vision_data, emotion_data)
    if cache_key:
        _VIDEO_CACHE[cache_key] = aggregate
    return aggregate


async def analyze_speech(transcript: str | None = None, audio_base64: str | None = None, duration_seconds: float | None = None) -> dict:
    payload = {
        "transcript": transcript,
        "audio_base64": audio_base64,
        "duration_seconds": duration_seconds,
    }
    try:
        return await _post_with_fallback(
            settings.speech_service_url,
            ["/ml/speech/analyze"],
            payload,
        )
    except (httpx.HTTPError, RuntimeError):
        return _analyze_speech_locally(transcript=transcript, audio_base64=audio_base64, duration_seconds=duration_seconds)


def _combine_video_signals(vision_data: dict, emotion_data: dict) -> dict:
    posture_score = float(vision_data.get("posture_score", 0))
    eye_contact_score = float(vision_data.get("eye_contact_score", emotion_data.get("eye_contact_score", 0)))
    hand_movement_score = float(vision_data.get("hand_movement_score", 0))
    confidence_score = float(emotion_data.get("confidence_score", 0))

    overall_score = round(
        (
            posture_score * 0.3
            + eye_contact_score * 0.2
            + confidence_score * 0.3
            + (100 - abs(hand_movement_score - 60)) * 0.2
        ),
        1,
    )

    suggestions = []
    for suggestion in vision_data.get("suggestions", []):
        if suggestion not in suggestions:
            suggestions.append(suggestion)
    for suggestion in emotion_data.get("suggestions", []):
        if suggestion not in suggestions:
            suggestions.append(suggestion)

    return {
        "posture_score": posture_score,
        "eye_contact_score": eye_contact_score,
        "hand_movement_score": hand_movement_score,
        "confidence_score": confidence_score,
        "nervousness_score": float(emotion_data.get("nervousness_score", max(0.0, 100 - confidence_score))),
        "engagement_score": float(emotion_data.get("engagement_score", eye_contact_score)),
        "posture": vision_data.get("posture", _posture_label(posture_score)),
        "head_position": vision_data.get("head_position", "aligned"),
        "eye_contact": _eye_contact_label(eye_contact_score),
        "eye_alignment": vision_data.get("eye_alignment", _eye_contact_label(eye_contact_score)),
        "hand_movement": vision_data.get("hand_movement", "stable"),
        "emotion": emotion_data.get("emotion", "neutral"),
        "smile_score": float(emotion_data.get("smile_score", 0)),
        "status": _compose_status([posture_score, eye_contact_score, confidence_score]),
        "suggestions": suggestions[:4] or ["Delivery looks stable. Keep the same pace and presence."],
        "overall_score": overall_score,
    }


def _compose_status(scores: list[float]) -> str:
    average = statistics.fmean(scores)
    if average >= 75:
        return "green"
    if average >= 50:
        return "yellow"
    return "red"


def _posture_label(score: float) -> str:
    if score >= 75:
        return "good"
    if score >= 55:
        return "warning"
    return "bad"


def _eye_contact_label(score: float) -> str:
    if score >= 75:
        return "high"
    if score >= 55:
        return "medium"
    return "low"


def _generate_question_locally(interview_type: str, role: str | None, skills: list[str], previous_questions: list[str]) -> dict:
    normalized_type = interview_type.lower()
    bucket = list(DATASET_QUESTIONS.get(normalized_type, []))
    bucket.extend(QUESTION_BANK.get(normalized_type, QUESTION_BANK["hr"]))
    for skill in skills:
        bucket.extend(SKILL_QUESTIONS.get(skill.lower(), []))

    deduped_bucket = list(dict.fromkeys(bucket))
    previous = {_normalize_question(question) for question in previous_questions}
    candidate_pool = [question for question in deduped_bucket if _normalize_question(question) not in previous] or deduped_bucket
    question = random.choice(candidate_pool)
    if role:
        question = f"{question}{ROLE_CONTEXT_PREFIX}{role}{ROLE_CONTEXT_SUFFIX}"
    category = "skill-based" if _normalize_question(question) in sum(SKILL_QUESTIONS.values(), []) else normalized_type
    return {"question": question, "category": category}


def _evaluate_answer_locally(question: str, answer: str) -> dict:
    answer_text = answer.strip()
    lower_answer = answer_text.lower()
    word_count = len(answer_text.split())
    keyword_candidates = [token for token in question.lower().replace("?", "").split() if len(token) > 4]
    keywords_matched = [token for token in keyword_candidates[:10] if token in lower_answer]
    confidence_level = 80
    if any(token in lower_answer for token in ["maybe", "kind of", "sort of", "i think", "probably"]):
        confidence_level -= 18

    structure_score = 58
    if any(token in lower_answer for token in ["situation", "task", "action", "result"]):
        structure_score += 20
    elif any(token in lower_answer for token in ["first", "then", "finally", "because"]):
        structure_score += 12
    elif word_count < 20:
        structure_score -= 18

    relevance_hits = len(keywords_matched)
    relevance_score = min(100, 48 + relevance_hits * 8)
    semantic_similarity = round(min(100, 42 + relevance_hits * 9 + min(word_count, 120) * 0.08), 1)

    specificity_score = 50
    if any(char.isdigit() for char in answer_text):
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

    score = round(
        min(
            100,
            (structure_score * 0.2)
            + (relevance_score * 0.2)
            + (specificity_score * 0.2)
            + (communication_score * 0.15)
            + (semantic_similarity * 0.15)
            + (confidence_level * 0.1),
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

    if confidence_level < 65:
        improvements.append("Avoid hedge phrases and finish with a firmer outcome statement.")

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
        "communication_score": round(min(100, communication_score), 1),
        "structure_score": round(min(100, structure_score), 1),
        "relevance_score": round(min(100, relevance_score), 1),
        "specificity_score": round(min(100, specificity_score), 1),
        "semantic_similarity": semantic_similarity,
        "confidence_level": round(max(0, min(100, confidence_level)), 1),
        "keywords_matched": keywords_matched,
        "verdict": verdict,
        "strengths": strengths,
        "improvements": improvements,
        "feedback": feedback,
        "suggestions": improvements[:3],
    }


def _analyze_speech_locally(transcript: str | None, audio_base64: str | None, duration_seconds: float | None) -> dict:
    transcript = (transcript or "").strip() or None
    estimated_duration = duration_seconds or _estimate_audio_duration(audio_base64) or 60.0
    filler_terms = {"um", "uh", "like", "you know", "actually", "basically"}
    words = transcript.lower().split() if transcript else []
    filler_words = [word.strip(",.!?") for word in words if word.strip(",.!?") in filler_terms]
    unique_fillers = sorted(set(filler_words))
    speaking_rate_wpm = round((len(words) / max(estimated_duration, 1)) * 60, 1) if words else 110.0
    clarity_score = 82.0
    if len(filler_words) > 4:
        clarity_score -= min(22.0, len(filler_words) * 2.5)
    if speaking_rate_wpm > 170 or speaking_rate_wpm < 95:
        clarity_score -= 12.0

    tone = "balanced"
    if transcript:
        if transcript.endswith("!") or transcript.count("!") >= 2:
            tone = "energetic"
        elif any(phrase in transcript.lower() for phrase in ["maybe", "i think", "probably"]):
            tone = "hesitant"

    confidence_score = max(45.0, min(95.0, clarity_score + (6 if tone == "balanced" else 0)))
    speech_score = round(max(0.0, min(100.0, clarity_score * 0.7 + confidence_score * 0.3)), 1)
    suggestions = []
    if len(filler_words) > 3:
        suggestions.append("Reduce filler words by pausing briefly instead of restarting a sentence.")
    if speaking_rate_wpm > 165:
        suggestions.append("Slow your pace so important technical details stay clear.")
    elif speaking_rate_wpm < 95:
        suggestions.append("Pick up the pace slightly to sound more decisive and engaged.")
    if tone == "hesitant":
        suggestions.append("Replace hedge phrases with direct statements about your decision and impact.")
    if not suggestions:
        suggestions.append("Speech delivery is stable. Keep the same pacing and clarity.")

    return {
        "speech_score": speech_score,
        "clarity_score": round(max(0.0, min(100.0, clarity_score)), 1),
        "filler_word_count": len(filler_words),
        "filler_words": unique_fillers,
        "speaking_rate_wpm": speaking_rate_wpm,
        "tone": tone,
        "confidence_score": round(confidence_score, 1),
        "suggestions": suggestions,
        "transcript": transcript,
    }


def _estimate_audio_duration(audio_base64: str | None) -> float | None:
    if not audio_base64:
        return None
    try:
        encoded = audio_base64.split(",", 1)[1] if "," in audio_base64 else audio_base64
        audio_bytes = BytesIO(base64.b64decode(encoded))
    except Exception:
        return None
    try:
        with wave.open(audio_bytes, "rb") as handle:
            frame_rate = handle.getframerate() or 1
            return handle.getnframes() / frame_rate
    except Exception:
        return None

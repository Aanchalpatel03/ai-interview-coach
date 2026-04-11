from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from inference import NlpEngine

app = FastAPI(title="ML NLP Service")
engine = NlpEngine()


class QuestionRequest(BaseModel):
    interview_type: str
    target_role: str | None = None
    skills: list[str] = Field(default_factory=list)
    previous_questions: list[str] = Field(default_factory=list)


class AnswerRequest(BaseModel):
    question: str
    answer: str
    interview_type: str = "hr"


@app.get("/health")
async def health():
    return engine.health()


@app.post("/ml/nlp/evaluate")
async def evaluate_answer(payload: AnswerRequest):
    return engine.evaluate(payload.question, payload.answer, payload.interview_type)


@app.post("/evaluate-answer")
async def evaluate_answer_legacy(payload: AnswerRequest):
    return engine.evaluate(payload.question, payload.answer, payload.interview_type)


@app.post("/ml/nlp/generate-question")
async def generate_question(payload: QuestionRequest):
    return engine.generate_question(payload.interview_type, payload.target_role, payload.skills, payload.previous_questions)


@app.post("/generate-question")
async def generate_question_legacy(payload: QuestionRequest):
    return engine.generate_question(payload.interview_type, payload.target_role, payload.skills, payload.previous_questions)


@app.websocket("/ws/ml/nlp")
async def nlp_socket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            payload = await websocket.receive_json()
            if "answer" in payload:
                response = engine.evaluate(payload["question"], payload["answer"], payload.get("interview_type", "hr"))
            else:
                response = engine.generate_question(
                    payload.get("interview_type", "hr"),
                    payload.get("target_role"),
                    payload.get("skills", []),
                    payload.get("previous_questions", []),
                )
            await websocket.send_json(response)
    except WebSocketDisconnect:
        return

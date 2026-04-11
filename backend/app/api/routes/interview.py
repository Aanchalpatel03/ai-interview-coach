from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.interview import Interview
from app.schemas.interview import (
    AnswerEvaluationResponse,
    AnswerRequest,
    EndInterviewRequest,
    InterviewResponse,
    InterviewStartRequest,
    QuestionResponse,
)
from app.services.ai_clients import evaluate_answer, generate_question
from app.services.ml_logging_service import log_ml_output
from app.services.interview_service import create_interview, finalize_interview, store_answer
from app.services.websocket_manager import manager

router = APIRouter(prefix="/interview", tags=["interview"])


@router.post("/start", response_model=InterviewResponse)
async def start_interview(payload: InterviewStartRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    interview = create_interview(db, current_user.id, payload.type, payload.target_role, payload.difficulty)
    return InterviewResponse.model_validate(interview, from_attributes=True)


@router.get("/question", response_model=QuestionResponse)
async def get_question(interview_id: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == interview_id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    skills = (current_user.extracted_skills or "").split(",") if current_user.extracted_skills else []
    previous_questions = [response.question for response in interview.responses]
    result = await generate_question(interview.type, interview.target_role, skills, previous_questions)
    return QuestionResponse(**result)


@router.post("/answer", response_model=AnswerEvaluationResponse)
async def submit_answer(payload: AnswerRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == payload.interview_id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    evaluation = await evaluate_answer(payload.question, payload.answer, interview.type)
    await manager.update_feedback(payload.interview_id, "nlp", evaluation)
    log_ml_output(db, user_id=current_user.id, interview_id=payload.interview_id, model_type="nlp", output=evaluation)
    response = store_answer(
        db,
        payload.interview_id,
        payload.question,
        payload.answer,
        evaluation["score"],
        evaluation["communication_score"],
        evaluation["feedback"],
    )
    return AnswerEvaluationResponse(
        response_id=response.id,
        score=response.score,
        communication_score=response.communication_score,
        structure_score=evaluation["structure_score"],
        relevance_score=evaluation["relevance_score"],
        specificity_score=evaluation["specificity_score"],
        verdict=evaluation["verdict"],
        strengths=evaluation["strengths"],
        improvements=evaluation["improvements"],
        feedback=response.answer_feedback or "",
    )


@router.post("/end")
async def end_interview(payload: EndInterviewRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == payload.interview_id, Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    feedback = finalize_interview(db, interview, manager.latest_feedback.get(payload.interview_id))
    return {"status": "completed", "feedback_id": feedback.id}

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.ml import MLFrameRequest, MLNlpEvaluationRequest, MLRealtimeFeedbackResponse, MLSpeechAnalysisRequest, MLSpeechAnalysisResponse
from app.services.ai_clients import analyze_speech, analyze_video_frame, evaluate_answer
from app.services.ml_logging_service import log_ml_output
from app.services.websocket_manager import manager

router = APIRouter(prefix="/ml", tags=["ml"])


@router.post("/nlp/evaluate")
async def evaluate_nlp(payload: MLNlpEvaluationRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    result = await evaluate_answer(payload.question, payload.answer, payload.interview_type)
    interview_id = payload.interview_id or "standalone"
    await manager.update_feedback(interview_id, "nlp", result)
    log_ml_output(db, user_id=current_user.id, interview_id=payload.interview_id, model_type="nlp", output=result)
    return result


@router.post("/frame", response_model=MLRealtimeFeedbackResponse)
async def analyze_ml_frame(payload: MLFrameRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    result = await analyze_video_frame(payload.frame, payload.interview_id)
    aggregate = await manager.update_feedback(payload.interview_id, "video", result)
    log_ml_output(db, user_id=current_user.id, interview_id=payload.interview_id, model_type="vision", output=result, throttle_seconds=5.0)
    return MLRealtimeFeedbackResponse(**aggregate)


@router.post("/speech/analyze", response_model=MLSpeechAnalysisResponse)
async def analyze_ml_speech(payload: MLSpeechAnalysisRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    result = await analyze_speech(
        transcript=payload.transcript,
        audio_base64=payload.audio_base64,
        duration_seconds=payload.duration_seconds,
    )
    await manager.update_feedback(payload.interview_id, "speech", result)
    log_ml_output(db, user_id=current_user.id, interview_id=payload.interview_id, model_type="speech", output=result)
    return MLSpeechAnalysisResponse(**result)


@router.websocket("/ws/ml-feedback")
async def ml_feedback_socket(websocket: WebSocket, interview_id: str):
    await manager.connect(interview_id, websocket, channel="ml")
    try:
        while True:
            await websocket.receive_text()
            if interview_id in manager.latest_feedback:
                await websocket.send_json(manager.latest_feedback[interview_id])
    except WebSocketDisconnect:
        manager.disconnect(interview_id, websocket, channel="ml")


@router.websocket("/ws/ml-feedback/{interview_id}")
async def ml_feedback_socket_path(websocket: WebSocket, interview_id: str):
    await manager.connect(interview_id, websocket, channel="ml")
    try:
        while True:
            await websocket.receive_text()
            if interview_id in manager.latest_feedback:
                await websocket.send_json(manager.latest_feedback[interview_id])
    except WebSocketDisconnect:
        manager.disconnect(interview_id, websocket, channel="ml")

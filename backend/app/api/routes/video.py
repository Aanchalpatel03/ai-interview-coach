from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.video import VideoFrameRequest, VideoFeedbackResponse
from app.services.ai_clients import analyze_video_frame
from app.services.ml_logging_service import log_ml_output
from app.services.websocket_manager import manager

router = APIRouter(tags=["video"])


@router.post("/video/frame", response_model=VideoFeedbackResponse)
async def analyze_frame(payload: VideoFrameRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    result = await analyze_video_frame(payload.frame, payload.interview_id)
    aggregate = await manager.broadcast(payload.interview_id, result)
    log_ml_output(db, user_id=current_user.id, interview_id=payload.interview_id, model_type="vision", output=result, throttle_seconds=5.0)
    return VideoFeedbackResponse(
        posture_score=aggregate["posture_score"],
        confidence_score=aggregate["confidence_score"],
        eye_contact_score=aggregate["eye_contact_score"],
        hand_movement_score=aggregate["hand_movement_score"],
        status=aggregate["status"],
        posture=aggregate["posture"],
        eye_contact=aggregate["eye_contact"],
        confidence=aggregate["confidence_score"],
        suggestions=aggregate["suggestions"],
        overall_score=aggregate["overall_score"],
    )


@router.websocket("/ws/video-feedback/{interview_id}")
async def video_feedback_socket(websocket: WebSocket, interview_id: str):
    await manager.connect(interview_id, websocket, channel="video")
    try:
        while True:
            await websocket.receive_text()
            if interview_id in manager.latest_feedback:
                await websocket.send_json(manager.latest_feedback[interview_id])
    except WebSocketDisconnect:
        manager.disconnect(interview_id, websocket, channel="video")


@router.websocket("/ws/video-feedback")
async def video_feedback_socket_query(websocket: WebSocket, interview_id: str):
    await manager.connect(interview_id, websocket, channel="video")
    try:
        while True:
            await websocket.receive_text()
            if interview_id in manager.latest_feedback:
                await websocket.send_json(manager.latest_feedback[interview_id])
    except WebSocketDisconnect:
        manager.disconnect(interview_id, websocket, channel="video")

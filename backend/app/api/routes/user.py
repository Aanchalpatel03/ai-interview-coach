from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.interview import DashboardResponse
from app.services.dashboard_service import build_dashboard

router = APIRouter(prefix="/user", tags=["user"])


class UpdateUserRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return build_dashboard(db, current_user.id)


@router.put("/update")
async def update_user(payload: UpdateUserRequest, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    current_user.name = payload.name
    db.add(current_user)
    db.commit()
    return {"status": "updated"}

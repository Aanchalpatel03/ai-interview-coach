from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app import models  # noqa: F401
from app.api.routes import auth, challenges, feedback, interview, leaderboard, ml, performance, resume, user, video
from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.base import Base
from app.db.bootstrap import run_bootstrap
from app.db.session import engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    run_bootstrap(engine, Base.metadata)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.api_v1_str)
app.include_router(user.router, prefix=settings.api_v1_str)
app.include_router(resume.router, prefix=settings.api_v1_str)
app.include_router(interview.router, prefix=settings.api_v1_str)
app.include_router(video.router, prefix=settings.api_v1_str)
app.include_router(feedback.router, prefix=settings.api_v1_str)
app.include_router(leaderboard.router, prefix=settings.api_v1_str)
app.include_router(challenges.router, prefix=settings.api_v1_str)
app.include_router(performance.router, prefix=settings.api_v1_str)
app.include_router(ml.router, prefix=settings.api_v1_str)


@app.get("/health")
async def healthcheck():
    return {"status": "ok"}

from collections.abc import Iterable
from datetime import date
from statistics import fmean

from sqlalchemy.orm import Session, joinedload

from app.models.challenge import UserProgress
from app.models.feedback import Feedback
from app.models.interview import Interview
from app.models.leaderboard import Leaderboard
from app.models.user import User

BADGE_RULES = {
    "Confident Speaker": lambda metrics: metrics["avg_confidence"] >= 80,
    "Perfect Posture": lambda metrics: metrics["avg_posture"] >= 85,
    "Consistent Challenger": lambda metrics: metrics["streak"] >= 5,
    "Rising Communicator": lambda metrics: metrics["improvement"] >= 12,
}


def ensure_leaderboard_entry(db: Session, user_id: str) -> Leaderboard:
    entry = db.query(Leaderboard).filter(Leaderboard.user_id == user_id).first()
    if entry:
        return entry
    entry = Leaderboard(user_id=user_id)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def award_xp(db: Session, user_id: str, xp_points: int) -> Leaderboard:
    entry = ensure_leaderboard_entry(db, user_id)
    entry.xp_points += xp_points
    db.add(entry)
    db.commit()
    return update_leaderboard_for_user(db, user_id)


def update_leaderboard_for_user(db: Session, user_id: str) -> Leaderboard:
    entry = ensure_leaderboard_entry(db, user_id)
    metrics = _compute_user_metrics(db, user_id)
    entry.total_score = metrics["total_score"]
    entry.level = _level_for_xp(entry.xp_points)
    entry.badges = ",".join(_badges_for_metrics(metrics))
    entry.streak_count = metrics["streak"]
    entry.improvement_score = metrics["improvement"]
    db.add(entry)
    db.commit()
    _recalculate_ranks(db)
    db.refresh(entry)
    return entry


def get_leaderboard(db: Session, current_user_id: str) -> tuple[list[Leaderboard], Leaderboard | None]:
    for user_id in [row[0] for row in db.query(User.id).all()]:
        update_leaderboard_for_user(db, user_id)

    leaders = (
        db.query(Leaderboard)
        .options(joinedload(Leaderboard.user))
        .order_by(Leaderboard.rank.asc(), Leaderboard.total_score.desc())
        .limit(20)
        .all()
    )
    current_user = (
        db.query(Leaderboard)
        .options(joinedload(Leaderboard.user))
        .filter(Leaderboard.user_id == current_user_id)
        .first()
    )
    return leaders, current_user


def serialize_entry(entry: Leaderboard | None) -> dict | None:
    if not entry:
        return None
    return {
        "user_id": entry.user_id,
        "name": entry.user.name if entry.user else "Candidate",
        "total_score": round(entry.total_score, 1),
        "rank": entry.rank,
        "level": entry.level,
        "xp_points": entry.xp_points,
        "badges": [badge for badge in (entry.badges or "").split(",") if badge],
        "streak_count": entry.streak_count,
        "improvement_score": round(entry.improvement_score, 1),
    }


def _compute_user_metrics(db: Session, user_id: str) -> dict[str, float | int]:
    interviews = (
        db.query(Interview)
        .filter(Interview.user_id == user_id, Interview.status == "completed")
        .order_by(Interview.start_time.asc())
        .all()
    )
    feedback_rows = [interview.feedback for interview in interviews if interview.feedback]
    avg_overall = fmean([row.overall_score for row in feedback_rows]) if feedback_rows else 0
    avg_confidence = fmean([row.confidence_score for row in feedback_rows]) if feedback_rows else 0
    avg_posture = fmean([row.posture_score for row in feedback_rows]) if feedback_rows else 0
    consistency = _consistency_score(interviews)
    improvement = _improvement_score(feedback_rows)
    total_score = round((avg_overall * 0.6) + (consistency * 0.2) + (improvement * 0.2), 1)
    streak = _challenge_streak(db, user_id)
    return {
        "total_score": total_score,
        "avg_confidence": round(avg_confidence, 1),
        "avg_posture": round(avg_posture, 1),
        "streak": streak,
        "improvement": round(improvement, 1),
    }


def _challenge_streak(db: Session, user_id: str) -> int:
    completed_days = (
        db.query(UserProgress.completed_at)
        .filter(UserProgress.user_id == user_id, UserProgress.completed.is_(True), UserProgress.completed_at.is_not(None))
        .order_by(UserProgress.completed_at.desc())
        .all()
    )
    unique_days = []
    for row in completed_days:
        completed_day = row[0].date()
        if completed_day not in unique_days:
            unique_days.append(completed_day)

    streak = 0
    cursor = date.today()
    for completed_day in unique_days:
        if completed_day == cursor:
            streak += 1
            cursor = date.fromordinal(cursor.toordinal() - 1)
        elif completed_day < cursor:
            break
    return streak


def _consistency_score(interviews: Iterable[Interview]) -> float:
    days = sorted({interview.start_time.date() for interview in interviews})
    if not days:
        return 0
    span = max(1, (days[-1] - days[0]).days + 1)
    return min(100, round((len(days) / span) * 100, 1))


def _improvement_score(feedback_rows: list[Feedback]) -> float:
    if len(feedback_rows) < 2:
        return 0
    window = min(3, len(feedback_rows) // 2 or 1)
    baseline = fmean([row.overall_score for row in feedback_rows[:window]])
    recent = fmean([row.overall_score for row in feedback_rows[-window:]])
    return max(0, min(100, round(recent - baseline + 50, 1)))


def _level_for_xp(xp_points: int) -> str:
    if xp_points >= 900:
        return "Expert"
    if xp_points >= 350:
        return "Advanced"
    return "Beginner"


def _badges_for_metrics(metrics: dict[str, float | int]) -> list[str]:
    badges = [badge for badge, rule in BADGE_RULES.items() if rule(metrics)]
    return badges or ["Active Learner"]


def _recalculate_ranks(db: Session) -> None:
    entries = db.query(Leaderboard).order_by(Leaderboard.total_score.desc(), Leaderboard.xp_points.desc()).all()
    for rank, entry in enumerate(entries, start=1):
        entry.rank = rank
        entry.level = _level_for_xp(entry.xp_points)
        db.add(entry)
    db.commit()

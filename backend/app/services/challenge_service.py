from datetime import date, datetime

from sqlalchemy.orm import Session, joinedload

from app.models.challenge import DailyChallenge, UserProgress
from app.services.leaderboard_service import award_xp, ensure_leaderboard_entry

CHALLENGE_BANK = {
    "hr": [
        "Describe a time you received difficult feedback and how you changed afterward.",
        "Tell me about a time you had to influence a teammate without formal authority.",
        "How do you respond when priorities change at the last minute?",
    ],
    "technical": [
        "Explain how you would improve API latency without creating long-term maintenance debt.",
        "Describe a production debugging workflow for intermittent failures.",
        "Design a scalable notification pipeline for web and mobile clients.",
    ],
    "behavioral": [
        "Record a 90-second STAR answer about a conflict you resolved and end with a measurable result.",
        "Practice a concise self-introduction that highlights one technical strength and one collaboration strength.",
        "Answer a leadership prompt while maintaining steady eye contact and controlled gestures.",
    ],
}


def get_today_challenges(db: Session, user_id: str) -> dict:
    ensure_leaderboard_entry(db, user_id)
    challenges = _ensure_challenges_for_day(db, date.today())
    progress_rows = (
        db.query(UserProgress)
        .options(joinedload(UserProgress.challenge))
        .filter(UserProgress.user_id == user_id, UserProgress.challenge_id.in_([challenge.id for challenge in challenges]))
        .all()
    )
    progress_by_id = {row.challenge_id: row for row in progress_rows}
    serialized = []
    completed_count = 0
    for challenge in challenges:
        progress = progress_by_id.get(challenge.id)
        completed = bool(progress and progress.completed)
        completed_count += int(completed)
        serialized.append(
            {
                "id": challenge.id,
                "date": challenge.date,
                "question": challenge.question,
                "type": challenge.type,
                "xp_reward": challenge.xp_reward,
                "completed": completed,
                "completed_at": progress.completed_at if progress else None,
            }
        )

    streak = _streak_for_user(db, user_id)
    return {
        "date": date.today(),
        "challenges": serialized,
        "summary": {
            "streak_count": streak,
            "xp_boost": 15 if completed_count == len(challenges) and challenges else 0,
            "completion_rate": round((completed_count / max(len(challenges), 1)) * 100, 1),
        },
    }


def complete_challenge(db: Session, user_id: str, challenge_id: str) -> dict:
    challenge = db.query(DailyChallenge).filter(DailyChallenge.id == challenge_id).first()
    if not challenge:
        raise ValueError("Challenge not found")

    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == user_id, UserProgress.challenge_id == challenge_id)
        .first()
    )
    if not progress:
        progress = UserProgress(user_id=user_id, challenge_id=challenge_id)

    xp_awarded = 0
    if not progress.completed:
        progress.completed = True
        progress.completed_at = datetime.utcnow()
        xp_awarded = challenge.xp_reward
        db.add(progress)
        db.commit()

        todays_progress = get_today_challenges(db, user_id)
        if all(item["completed"] for item in todays_progress["challenges"]):
            xp_awarded += todays_progress["summary"]["xp_boost"]
        if xp_awarded:
            award_xp(db, user_id, xp_awarded)

    return {
        "status": "completed",
        "xp_awarded": xp_awarded,
        "streak_count": _streak_for_user(db, user_id),
    }


def _ensure_challenges_for_day(db: Session, target_date: date) -> list[DailyChallenge]:
    rows = db.query(DailyChallenge).filter(DailyChallenge.date == target_date).order_by(DailyChallenge.type.asc()).all()
    if len(rows) >= 3:
        return rows

    seed = target_date.toordinal()
    desired = []
    for challenge_type, bank in CHALLENGE_BANK.items():
        question = bank[seed % len(bank)]
        desired.append(
            DailyChallenge(date=target_date, question=question, type=challenge_type, xp_reward=25 if challenge_type != "behavioral" else 35)
        )

    existing_types = {row.type for row in rows}
    for challenge in desired:
        if challenge.type not in existing_types:
            db.add(challenge)
    db.commit()
    return db.query(DailyChallenge).filter(DailyChallenge.date == target_date).order_by(DailyChallenge.type.asc()).all()


def _streak_for_user(db: Session, user_id: str) -> int:
    completed_rows = (
        db.query(UserProgress.completed_at)
        .filter(UserProgress.user_id == user_id, UserProgress.completed.is_(True), UserProgress.completed_at.is_not(None))
        .order_by(UserProgress.completed_at.desc())
        .all()
    )
    unique_days = []
    for row in completed_rows:
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

import json
import time
from collections import defaultdict
from typing import Any

from sqlalchemy.orm import Session

from app.models.ml_log import MLLog

_LAST_LOGGED_AT: dict[tuple[str | None, str], float] = defaultdict(float)


def log_ml_output(
    db: Session,
    *,
    user_id: str | None,
    interview_id: str | None,
    model_type: str,
    output: dict[str, Any],
    throttle_seconds: float = 0.0,
) -> None:
    cache_key = (interview_id, model_type)
    now = time.monotonic()
    if throttle_seconds and now - _LAST_LOGGED_AT[cache_key] < throttle_seconds:
        return

    entry = MLLog(
        user_id=user_id,
        interview_id=interview_id,
        model_type=model_type,
        output=json.dumps(output, ensure_ascii=True),
    )
    db.add(entry)
    db.commit()
    _LAST_LOGGED_AT[cache_key] = now

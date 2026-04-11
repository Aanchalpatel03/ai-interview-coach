from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


FEEDBACK_COLUMN_MIGRATIONS = {
    "hand_movement_score": "FLOAT DEFAULT 0",
    "overall_score": "FLOAT DEFAULT 0",
    "session_xp": "INTEGER DEFAULT 0",
    "improvement_delta": "FLOAT DEFAULT 0",
}


def run_bootstrap(engine: Engine, metadata) -> None:
    metadata.create_all(bind=engine)
    _ensure_feedback_columns(engine)


def _ensure_feedback_columns(engine: Engine) -> None:
    inspector = inspect(engine)
    if "feedback" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("feedback")}
    with engine.begin() as connection:
        for column_name, ddl in FEEDBACK_COLUMN_MIGRATIONS.items():
            if column_name not in existing_columns:
                connection.execute(text(f"ALTER TABLE feedback ADD COLUMN {column_name} {ddl}"))

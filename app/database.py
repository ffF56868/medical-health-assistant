import os

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///medical_health.db",
)


def build_engine(database_url: str) -> Engine:
    """Create a database engine with backend-specific connection options."""
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(
        database_url,
        connect_args=connect_args,
        pool_pre_ping=True,
    )


engine = build_engine(DATABASE_URL)


SQLITE_COLUMN_MIGRATIONS = {
    "condition": {
        "source": "VARCHAR(200) NOT NULL DEFAULT '未标注来源'",
        "source_url": "TEXT",
        "source_tier": "VARCHAR(20) NOT NULL DEFAULT 'unverified'",
        "knowledge_base_id": "VARCHAR(100) NOT NULL DEFAULT 'global'",
        "visibility": "VARCHAR(20) NOT NULL DEFAULT 'public'",
        "updated_at": "DATETIME",
    },
    "drug": {
        "source": "VARCHAR(200) NOT NULL DEFAULT '未标注来源'",
        "source_url": "TEXT",
        "source_tier": "VARCHAR(20) NOT NULL DEFAULT 'unverified'",
        "knowledge_base_id": "VARCHAR(100) NOT NULL DEFAULT 'global'",
        "visibility": "VARCHAR(20) NOT NULL DEFAULT 'public'",
        "updated_at": "DATETIME",
    },
    "knowledgedocument": {
        "source_url": "TEXT",
        "source_tier": "VARCHAR(20) NOT NULL DEFAULT 'unverified'",
        "owner_user_id": "INTEGER",
        "knowledge_base_id": "VARCHAR(100) NOT NULL DEFAULT 'global'",
        "visibility": "VARCHAR(20) NOT NULL DEFAULT 'public'",
        "page_number": "INTEGER",
        "updated_at": "DATETIME",
    },
    "ragevaluationcase": {
        "category": "VARCHAR(50) NOT NULL DEFAULT '自定义'",
        "alternative_names_json": "TEXT NOT NULL DEFAULT '[]'",
    },
    "ragevaluationrun": {
        "results_json": "TEXT NOT NULL DEFAULT '[]'",
    },
    "chatmessage": {
        "user_id": "INTEGER",
        "response_metadata_json": "TEXT NOT NULL DEFAULT '{}'",
    },
    "knowledgerebuildjob": {
        "retry_of_job_id": "INTEGER",
    },
    "user": {
        "is_admin": "BOOLEAN NOT NULL DEFAULT 0",
    },
}


def ensure_sqlite_metadata_columns(database_engine: Engine) -> None:
    """Add only missing metadata columns so existing SQLite data stays intact."""
    if database_engine.url.get_backend_name() != "sqlite":
        return

    with database_engine.begin() as connection:
        for table_name, columns in SQLITE_COLUMN_MIGRATIONS.items():
            existing_columns = {
                row[1]
                for row in connection.exec_driver_sql(
                    f'PRAGMA table_info("{table_name}")'
                )
            }
            for column_name, definition in columns.items():
                if column_name not in existing_columns:
                    connection.exec_driver_sql(
                        f'ALTER TABLE "{table_name}" '
                        f'ADD COLUMN "{column_name}" {definition}'
                    )


def create_db_and_tables(target_engine: Engine | None = None) -> None:
    database_engine = target_engine or engine
    SQLModel.metadata.create_all(database_engine)
    ensure_sqlite_metadata_columns(database_engine)


def get_session():
    with Session(engine) as session:
        yield session

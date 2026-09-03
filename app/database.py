import os

from sqlalchemy import inspect
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
        "answer_keywords_json": "TEXT NOT NULL DEFAULT '[]'",
        "citation_names_json": "TEXT NOT NULL DEFAULT '[]'",
        "expected_refusal": "BOOLEAN NOT NULL DEFAULT 0",
    },
    "ragevaluationrun": {
        "results_json": "TEXT NOT NULL DEFAULT '[]'",
    },
    "chatmessage": {
        "user_id": "INTEGER",
        "response_metadata_json": "TEXT NOT NULL DEFAULT '{}'",
    },
    "conversationmemorystate": {
        "summary": "TEXT",
        "summarized_message_count": "INTEGER NOT NULL DEFAULT 0",
        "updated_at": "DATETIME",
    },
    "usermemory": {
        "embedding_json": "TEXT",
        "active": "BOOLEAN NOT NULL DEFAULT 1",
        "source_conversation_id": "VARCHAR(100)",
        "last_accessed_at": "DATETIME",
        "access_count": "INTEGER NOT NULL DEFAULT 0",
    },
    "knowledgerebuildjob": {
        "retry_of_job_id": "INTEGER",
    },
    "knowledgeindexstate": {
        # Existing Chroma index state must be rebuilt before it is considered
        # a valid Milvus index.
        "vector_store_type": "VARCHAR(30) NOT NULL DEFAULT ''",
        "vector_count": "INTEGER NOT NULL DEFAULT 0",
    },
    "user": {
        "is_admin": "BOOLEAN NOT NULL DEFAULT 0",
    },
}


def ensure_metadata_columns(database_engine: Engine) -> None:
    """Add missing metadata columns for existing SQLite or MySQL databases."""
    backend = database_engine.url.get_backend_name()
    if backend not in {"sqlite", "mysql"}:
        return

    with database_engine.begin() as connection:
        inspector = inspect(connection)
        table_names = set(inspector.get_table_names())
        for table_name, columns in SQLITE_COLUMN_MIGRATIONS.items():
            if table_name not in table_names:
                continue
            if backend == "sqlite":
                existing_columns = {
                    row[1]
                    for row in connection.exec_driver_sql(
                        f'PRAGMA table_info("{table_name}")'
                    )
                }
            else:
                existing_columns = {
                    column["name"] for column in inspector.get_columns(table_name)
                }
            for column_name, definition in columns.items():
                if column_name not in existing_columns:
                    identifier_quote = '"' if backend == "sqlite" else "`"
                    column_definition = definition
                    if (
                        backend == "mysql"
                        and definition.startswith("TEXT")
                        and " DEFAULT " in definition
                    ):
                        column_definition = definition.split(" DEFAULT ", 1)[0].replace(
                            " NOT NULL", " NULL"
                        )
                    connection.exec_driver_sql(
                        f"ALTER TABLE {identifier_quote}{table_name}{identifier_quote} "
                        f"ADD COLUMN {identifier_quote}{column_name}{identifier_quote} {column_definition}"
                    )


def ensure_sqlite_metadata_columns(database_engine: Engine) -> None:
    """Backward-compatible wrapper retained for existing callers and tests."""
    if database_engine.url.get_backend_name() == "sqlite":
        ensure_metadata_columns(database_engine)


def create_db_and_tables(target_engine: Engine | None = None) -> None:
    database_engine = target_engine or engine
    SQLModel.metadata.create_all(database_engine)
    ensure_metadata_columns(database_engine)


def get_session():
    with Session(engine) as session:
        yield session

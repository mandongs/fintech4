"""
동기 SQLite + FastAPI run_in_threadpool 패턴.
greenlet C 확장 없이도 동작하는 방식.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# 동기 엔진 (sqlite:// 또는 postgresql://)
sync_url = settings.DATABASE_URL.replace("+aiosqlite", "").replace("+asyncpg", "")

engine = create_engine(
    sync_url,
    connect_args={"check_same_thread": False} if "sqlite" in sync_url else {},
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# async 호환을 위한 alias (라우터 코드 최소 변경)
AsyncSession = Session
AsyncSessionLocal = SessionLocal


async def get_db_async():
    """FastAPI Depends용 — 동기 세션을 yield"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

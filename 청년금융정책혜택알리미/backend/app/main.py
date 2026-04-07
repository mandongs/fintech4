from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.batch.scheduler import setup_scheduler
from app.core.database import Base, engine
from app.routers import alert, auth, batch, chat, policy, profile, recommend


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 테이블 생성 (운영에서는 Alembic 사용)
    Base.metadata.create_all(bind=engine)

    # 스케줄러 시작
    setup_scheduler()

    yield

    # 스케줄러 종료
    from app.batch.scheduler import scheduler
    if scheduler.running:
        scheduler.shutdown()


app = FastAPI(
    title="청년 금융 혜택 통합 플랫폼 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(recommend.router)
app.include_router(alert.router)
app.include_router(policy.router)
app.include_router(chat.router)
app.include_router(batch.router)


@app.get("/health")
async def health():
    return {"status": "ok"}

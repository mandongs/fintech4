# 개발 환경 세팅 가이드

## 1. 환경변수 설정

```bash
cp .env.example .env
# .env 파일에 API 키 입력
```

## 2. Docker Compose로 전체 실행 (권장)

```bash
docker-compose up -d
```

| 서비스 | URL |
|--------|-----|
| 백엔드 API | http://localhost:8000 |
| API 문서 (Swagger) | http://localhost:8000/docs |
| 프론트엔드 | http://localhost:5173 |
| PostgreSQL | localhost:5432 |

## 3. 로컬 개발 (Docker 없이)

### 백엔드

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# PostgreSQL 로컬 실행 후
cp .env.example .env           # 환경변수 설정
uvicorn app.main:app --reload
```

### 프론트엔드

```bash
cd frontend
npm install
npm run dev
```

## 4. 초기 데이터 수집

서버 실행 후 아래 엔드포인트를 호출해 데이터를 수집합니다.

```bash
# 청년 정책 수집 (온통청년 API)
curl -X POST http://localhost:8000/api/batch/collect-policy

# FSS 금융상품 수집
curl -X POST http://localhost:8000/api/batch/collect-fss
```

또는 기존 CSV 데이터를 직접 DB에 적재:

```bash
cd backend
python scripts/load_csv.py   # (아래 스크립트 참조)
```

## 5. API 키 발급 안내

| 키 | 발급처 | 비고 |
|----|--------|------|
| FSS_API_KEY | https://finlife.fss.or.kr (오픈API 탭) | 즉시 발급 |
| YOUTH_POLICY_API_KEY | https://www.youthcenter.go.kr/opi/openapi.do | 즉시 발급 |
| GOOGLE_API_KEY | https://aistudio.google.com/apikey | Gemini 사용 |

## 6. CSV → DB 직접 적재 스크립트

```python
# backend/scripts/load_csv.py
import asyncio, pandas as pd
from app.core.database import AsyncSessionLocal
from app.batch.policy_collector import _map_row
from app.models.policy import Policy
from sqlalchemy.dialects.postgresql import insert

async def load():
    df = pd.read_csv("../data/youth_policy_final.csv")
    async with AsyncSessionLocal() as db:
        records = [_map_row(r) for _, r in df.iterrows() if r.get("plcyNo")]
        stmt = insert(Policy).values(records).on_conflict_do_nothing()
        await db.execute(stmt)
        await db.commit()
    print(f"{len(records)}건 적재 완료")

asyncio.run(load())
```

"""
온통청년 API로 청년 정책 수집 후 DB에 upsert.
API: https://www.youthcenter.go.kr/opi/empList.do
"""

import asyncio
import logging
from datetime import datetime, timezone

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.policy import Policy
from app.services.deadline import parse_apply_period

logger = logging.getLogger(__name__)

YOUTH_API_URL = "https://www.youthcenter.go.kr/opi/empList.do"
PAGE_SIZE = 100


async def _fetch_page(client: httpx.AsyncClient, page: int) -> list[dict]:
    params = {
        "openApiVlak": settings.YOUTH_POLICY_API_KEY,
        "display": PAGE_SIZE,
        "pageIndex": page,
        "srchPolicyId": "",
    }
    resp = await client.get(YOUTH_API_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    # 응답 구조: {"result": {"youthPolicyList": [...], "totalCnt": N}}
    result = data.get("result", {})
    return result.get("youthPolicyList", [])


def _map_row(row: dict) -> dict:
    apply_start, apply_end, period_text = parse_apply_period(row.get("aplyYmd"))
    biz_start, biz_end, _ = parse_apply_period(
        f"{row.get('bizPrdBgngYmd','')} ~ {row.get('bizPrdEndYmd','')}"
    )

    # 지역코드 정제
    zip_raw = row.get("zipCd", "")
    region_codes = zip_raw if zip_raw and zip_raw.strip() else None

    return {
        "id": row.get("plcyNo", ""),
        "name": row.get("plcyNm", ""),
        "keyword": row.get("plcyKywdNm"),
        "category_main": row.get("lclsfNm"),
        "category_sub": row.get("mclsfNm"),
        "description": row.get("plcyExplnCn"),
        "support_content": row.get("plcySprtCn"),
        "apply_method": row.get("plcyAplyMthdCn"),
        "apply_url": row.get("aplyUrlAddr"),
        "ref_url1": row.get("refUrlAddr1"),
        "ref_url2": row.get("refUrlAddr2"),
        "min_age": int(row.get("sprtTrgtMinAge") or 0),
        "max_age": int(row.get("sprtTrgtMaxAge") or 0),
        "earn_min": int(row.get("earnMinAmt") or 0),
        "earn_max": int(row.get("earnMaxAmt") or 0),
        "region_codes": region_codes,
        "marriage_code": row.get("mrgSttsCd"),
        "job_codes": row.get("jobCd"),
        "school_codes": row.get("schoolCd"),
        "apply_start": apply_start,
        "apply_end": apply_end,
        "apply_period_text": period_text,
        "biz_start": biz_start,
        "biz_end": biz_end,
        "supervise_inst": row.get("sprvsnInstCdNm"),
        "supervise_inst_code": row.get("sprvsnInstCd"),
        "operate_inst": row.get("operInstCdNm"),
        "support_scale": int(row.get("sprtSclCnt") or 0) or None,
        "is_scale_limited": row.get("sprtSclLmtYn") == "Y",
        "fetched_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


async def collect_policies(db: AsyncSession | None = None) -> int:
    """정책 수집 실행. 수집된 건수 반환."""
    close_db = db is None
    if db is None:
        db = AsyncSessionLocal()

    collected = 0
    try:
        async with httpx.AsyncClient() as client:
            page = 1
            while True:
                rows = await _fetch_page(client, page)
                if not rows:
                    break

                records = [_map_row(r) for r in rows if r.get("plcyNo")]
                if not records:
                    break

                from sqlalchemy.dialects.sqlite import insert as sqlite_insert
                from sqlalchemy.dialects.postgresql import insert as pg_insert
                from app.core.config import settings
                if "sqlite" in settings.DATABASE_URL:
                    stmt = sqlite_insert(Policy).values(records)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["id"],
                        set_={k: getattr(stmt.excluded, k) for k in records[0] if k != "id"},
                    )
                else:
                    stmt = pg_insert(Policy).values(records)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["id"],
                        set_={k: stmt.excluded[k] for k in records[0] if k != "id"},
                    )
                await db.execute(stmt)
                await db.commit()

                collected += len(records)
                logger.info(f"[PolicyCollector] page={page}, collected={collected}")
                page += 1

                if len(rows) < PAGE_SIZE:
                    break
                await asyncio.sleep(0.3)   # API rate limit 배려

    except Exception as e:
        logger.error(f"[PolicyCollector] 수집 실패: {e}")
        raise
    finally:
        if close_db:
            await db.close()

    logger.info(f"[PolicyCollector] 완료. 총 {collected}건 upsert")
    return collected

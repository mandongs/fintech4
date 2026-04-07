"""
금융감독원 finlife API로 금융상품 수집 후 DB에 upsert.
API: http://finlife.fss.or.kr/finlifeapi/
"""

import asyncio
import logging
import re
from datetime import datetime, timezone

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.financial_product import FinancialProduct, PRODUCT_TYPE_MAP

logger = logging.getLogger(__name__)

# 수집 대상 API + 권역코드
FSS_ENDPOINTS = [
    ("savingProductsSearch", "saving"),
    ("depositProductsSearch", "deposit"),
    ("mortgageLoanProductsSearch", "mortgage"),
    ("rentHouseLoanProductsSearch", "rent"),
    ("creditLoanProductsSearch", "credit"),
]
FSS_GROUPS = ["020000", "030300", "030200"]

YOUTH_KEYWORDS = ["청년", "청소년", "사회초년생", "신혼", "미취업", "구직"]


def _is_youth(name: str, target: str) -> bool:
    text = (name or "") + (target or "")
    return any(kw in text for kw in YOUTH_KEYWORDS)


def _parse_age_from_text(text: str) -> tuple[int, int]:
    """가입대상 텍스트에서 나이 조건 추출. 예: '만 19세 이상 34세 이하'"""
    min_age = max_age = 0
    m = re.search(r"만\s*(\d+)\s*세\s*이상", text)
    if m:
        min_age = int(m.group(1))
    m = re.search(r"(\d+)\s*세\s*이하", text)
    if m:
        max_age = int(m.group(1))
    m = re.search(r"만\s*(\d+)세?~(\d+)세?", text)
    if m:
        min_age, max_age = int(m.group(1)), int(m.group(2))
    return min_age, max_age


def _parse_date(raw: str | None) -> "date | None":
    from datetime import date
    if not raw or len(str(raw).strip()) < 8:
        return None
    s = str(raw).strip()[:8]
    try:
        return date(int(s[:4]), int(s[4:6]), int(s[6:8]))
    except ValueError:
        return None


def _map_row(row: dict, product_type: str) -> dict:
    company_code = row.get("fin_co_no") or row.get("금융회사코드", "")
    product_code = row.get("fin_prdt_cd") or row.get("상품코드", "")
    product_name = row.get("fin_prdt_nm") or row.get("상품명", "")
    target_raw = row.get("join_member") or row.get("가입대상", "")

    min_age, max_age = _parse_age_from_text(target_raw or "")

    max_limit_raw = row.get("max_limit") or row.get("최대한도")
    max_limit = None
    try:
        if max_limit_raw:
            max_limit = int(float(str(max_limit_raw).replace(",", "")))
    except (ValueError, TypeError):
        pass

    return {
        "id": f"{company_code}_{product_code}",
        "company_code": company_code,
        "company_name": row.get("kor_co_nm") or row.get("회사명", ""),
        "product_code": product_code,
        "product_name": product_name,
        "product_type": product_type,
        "join_method": row.get("join_way") or row.get("가입방법"),
        "target_raw": target_raw,
        "preferred_condition": row.get("spcl_cnd") or row.get("우대조건"),
        "maturity_interest": row.get("mtrt_int") or row.get("만기이자"),
        "notes": row.get("etc_note") or row.get("유의사항"),
        "is_youth_product": _is_youth(product_name, target_raw),
        "min_age": min_age,
        "max_age": max_age,
        "max_limit": max_limit,
        "loan_limit": None,
        "early_repay_fee": row.get("erly_rpay_fee") or row.get("중도상환수수료"),
        "delay_rate": row.get("dly_rate") or row.get("연체이자율"),
        "start_date": _parse_date(row.get("dcls_strt_day") or row.get("시작일")),
        "end_date": _parse_date(row.get("dcls_end_day") or row.get("종료일")),
        "dcls_month": str(row.get("dcls_month") or row.get("공시월", ""))[:6],
        "fetched_at": datetime.now(timezone.utc),
    }


async def _fetch_fss(client: httpx.AsyncClient, endpoint: str, group: str, page: int) -> list[dict]:
    url = f"{settings.FSS_BASE_URL}/{endpoint}.json"
    params = {"auth": settings.FSS_API_KEY, "topFinGrpNo": group, "pageNo": page}
    resp = await client.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("result", {}).get("baseList", [])


async def collect_financial_products(db: AsyncSession | None = None) -> int:
    close_db = db is None
    if db is None:
        db = AsyncSessionLocal()

    collected = 0
    try:
        async with httpx.AsyncClient() as client:
            for endpoint, product_type in FSS_ENDPOINTS:
                for group in FSS_GROUPS:
                    page = 1
                    while True:
                        rows = await _fetch_fss(client, endpoint, group, page)
                        if not rows:
                            break

                        records = [_map_row(r, product_type) for r in rows if r.get("fin_co_no") or r.get("금융회사코드")]
                        if not records:
                            break

                        from app.core.config import settings
                        if "sqlite" in settings.DATABASE_URL:
                            from sqlalchemy.dialects.sqlite import insert as ins
                        else:
                            from sqlalchemy.dialects.postgresql import insert as ins
                        stmt = ins(FinancialProduct).values(records)
                        stmt = stmt.on_conflict_do_update(
                            index_elements=["id"],
                            set_={k: getattr(stmt.excluded, k) for k in records[0] if k != "id"},
                        )
                        await db.execute(stmt)
                        await db.commit()

                        collected += len(records)
                        page += 1
                        await asyncio.sleep(0.2)

    except Exception as e:
        logger.error(f"[FSSCollector] 수집 실패: {e}")
        raise
    finally:
        if close_db:
            await db.close()

    logger.info(f"[FSSCollector] 완료. 총 {collected}건 upsert")
    return collected

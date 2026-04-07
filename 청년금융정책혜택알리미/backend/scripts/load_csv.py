"""
기존 CSV 파일을 SQLite DB에 직접 적재.
실행: python scripts/load_csv.py  (backend/ 디렉토리에서)
"""

import asyncio
import sys
from pathlib import Path

# backend 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from sqlalchemy import text

from app.core.database import Base, AsyncSessionLocal, engine
from app.services.deadline import parse_apply_period

DATA_DIR = Path(__file__).parent.parent.parent / "data"


# ─── 정책 적재 ───────────────────────────────────────────────────────────────
def _map_policy(row) -> dict | None:
    plcy_no = str(row.get("plcyNo", "")).strip()
    if not plcy_no:
        return None

    apply_start, apply_end, period_text = parse_apply_period(str(row.get("aplyYmd", "")))

    biz_raw = f"{row.get('bizPrdBgngYmd', '')} ~ {row.get('bizPrdEndYmd', '')}"
    biz_start, biz_end, _ = parse_apply_period(biz_raw)

    zip_raw = str(row.get("zipCd", "")).strip()
    region_codes = zip_raw if zip_raw and zip_raw != "nan" else None

    def safe_int(v, default=0):
        try:
            return int(float(v)) if v and str(v) != "nan" else default
        except Exception:
            return default

    return {
        "id": plcy_no,
        "name": str(row.get("plcyNm", ""))[:200],
        "keyword": str(row.get("plcyKywdNm", ""))[:200] or None,
        "category_main": str(row.get("lclsfNm", ""))[:50] or None,
        "category_sub": str(row.get("mclsfNm", ""))[:50] or None,
        "description": str(row.get("plcyExplnCn", "")) or None,
        "support_content": str(row.get("plcySprtCn", "")) or None,
        "apply_method": str(row.get("plcyAplyMthdCn", "")) or None,
        "apply_url": str(row.get("aplyUrlAddr", ""))[:500] or None,
        "ref_url1": str(row.get("refUrlAddr1", ""))[:500] or None,
        "ref_url2": str(row.get("refUrlAddr2", ""))[:500] or None,
        "min_age": safe_int(row.get("sprtTrgtMinAge")),
        "max_age": safe_int(row.get("sprtTrgtMaxAge")),
        "earn_min": safe_int(row.get("earnMinAmt")),
        "earn_max": safe_int(row.get("earnMaxAmt")),
        "region_codes": region_codes,
        "marriage_code": str(row.get("mrgSttsCd", "")) or None,
        "job_codes": str(row.get("jobCd", "")) or None,
        "school_codes": str(row.get("schoolCd", "")) or None,
        "apply_start": apply_start.isoformat() if apply_start else None,
        "apply_end": apply_end.isoformat() if apply_end else None,
        "apply_period_text": period_text,
        "biz_start": biz_start.isoformat() if biz_start else None,
        "biz_end": biz_end.isoformat() if biz_end else None,
        "supervise_inst": str(row.get("sprvsnInstCdNm", ""))[:100] or None,
        "supervise_inst_code": str(row.get("sprvsnInstCd", ""))[:20] or None,
        "operate_inst": str(row.get("operInstCdNm", ""))[:100] or None,
        "support_scale": safe_int(row.get("sprtSclCnt")) or None,
        "is_scale_limited": str(row.get("sprtSclLmtYn", "N")).upper() == "Y",
        "view_count": 0,
        "embedding_id": None,
    }


# ─── 금융상품 적재 ───────────────────────────────────────────────────────────
import re

YOUTH_KW = ["청년", "청소년", "사회초년생", "신혼", "미취업", "구직"]
TYPE_MAP = {
    "savingProductsSearch": "saving",
    "depositProductsSearch": "deposit",
    "mortgageLoanProductsSearch": "mortgage",
    "rentHouseLoanProductsSearch": "rent",
    "creditLoanProductsSearch": "credit",
}


def _detect_type(url: str) -> str:
    for k, v in TYPE_MAP.items():
        if k in str(url):
            return v
    return "saving"


def _parse_age(text: str):
    min_a = max_a = 0
    m = re.search(r"만\s*(\d+)\s*세\s*이상", text)
    if m:
        min_a = int(m.group(1))
    m = re.search(r"(\d+)\s*세\s*이하", text)
    if m:
        max_a = int(m.group(1))
    return min_a, max_a


def _parse_date_str(raw):
    if not raw or str(raw).strip() in ("nan", "None", ""):
        return None
    s = str(raw).strip()[:8]
    if len(s) < 8:
        return None
    try:
        from datetime import date
        return date(int(s[:4]), int(s[4:6]), int(s[6:8])).isoformat()
    except Exception:
        return None


def _map_product(row) -> dict | None:
    co = str(row.get("금융회사코드", "")).strip()
    pc = str(row.get("상품코드", "")).strip()
    if not co or not pc:
        return None
    pid = f"{co}_{pc}"

    name = str(row.get("상품명", ""))
    target = str(row.get("가입대상", ""))
    prod_type = _detect_type(str(row.get("상품유형", "")))
    min_a, max_a = _parse_age(target)

    max_lim = None
    try:
        v = row.get("최대한도")
        if v and str(v) not in ("nan", "None"):
            max_lim = int(float(str(v).replace(",", "")))
    except Exception:
        pass

    return {
        "id": pid,
        "company_code": co,
        "company_name": str(row.get("회사명", ""))[:100],
        "product_code": pc,
        "product_name": name[:200],
        "product_type": prod_type,
        "join_method": str(row.get("가입방법", ""))[:200] or None,
        "target_raw": target or None,
        "preferred_condition": str(row.get("우대조건", "")) or None,
        "maturity_interest": str(row.get("만기이자", "")) or None,
        "notes": str(row.get("유의사항", "")) or None,
        "is_youth_product": any(kw in name + target for kw in YOUTH_KW),
        "min_age": min_a,
        "max_age": max_a,
        "max_limit": max_lim,
        "loan_limit": None,
        "early_repay_fee": str(row.get("중도상환수수료", "")) or None,
        "delay_rate": str(row.get("연체이자율", "")) or None,
        "start_date": _parse_date_str(row.get("시작일")),
        "end_date": _parse_date_str(row.get("종료일")),
        "dcls_month": str(row.get("공시월", ""))[:10] or None,
    }


# ─── 메인 ────────────────────────────────────────────────────────────────────
async def main():
    print("▶ 테이블 생성 중...")
    # 모든 모델 import (create_all을 위해)
    import app.models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("  ✅ 테이블 생성 완료")

    async with AsyncSessionLocal() as db:
        # 1. 청년 정책
        policy_path = DATA_DIR / "youth_policy_final.csv"
        if policy_path.exists():
            print(f"\n▶ 청년 정책 적재 중... ({policy_path})")
            df = pd.read_csv(policy_path, encoding="utf-8-sig", low_memory=False)
            records = [r for r in (_map_policy(row) for _, row in df.iterrows()) if r]
            print(f"  파싱된 레코드: {len(records)}건")
            chunk = 500
            loaded = 0
            for i in range(0, len(records), chunk):
                batch = records[i : i + chunk]
                await db.execute(
                    text("""
                        INSERT OR REPLACE INTO policies
                        (id, name, keyword, category_main, category_sub,
                         description, support_content, apply_method,
                         apply_url, ref_url1, ref_url2,
                         min_age, max_age, earn_min, earn_max,
                         region_codes, marriage_code, job_codes, school_codes,
                         apply_start, apply_end, apply_period_text,
                         biz_start, biz_end,
                         supervise_inst, supervise_inst_code, operate_inst,
                         support_scale, is_scale_limited, view_count, embedding_id,
                         fetched_at, updated_at)
                        VALUES (:id, :name, :keyword, :category_main, :category_sub,
                                :description, :support_content, :apply_method,
                                :apply_url, :ref_url1, :ref_url2,
                                :min_age, :max_age, :earn_min, :earn_max,
                                :region_codes, :marriage_code, :job_codes, :school_codes,
                                :apply_start, :apply_end, :apply_period_text,
                                :biz_start, :biz_end,
                                :supervise_inst, :supervise_inst_code, :operate_inst,
                                :support_scale, :is_scale_limited, :view_count, :embedding_id,
                                datetime('now'), datetime('now'))
                    """),
                    batch,
                )
                await db.commit()
                loaded += len(batch)
                print(f"  {loaded}/{len(records)} 적재 완료")
            print(f"  ✅ 청년 정책 {loaded}건 적재 완료!")
        else:
            print(f"  ⚠️ {policy_path} 파일 없음 - 건너뜀")

        # 2. 금융상품
        fp_path = DATA_DIR / "financial_products.csv"
        if fp_path.exists():
            print(f"\n▶ 금융상품 적재 중... ({fp_path})")
            df = pd.read_csv(fp_path, encoding="utf-8-sig", low_memory=False)
            records = [r for r in (_map_product(row) for _, row in df.iterrows()) if r]
            # 중복 제거 (id 기준)
            seen, unique = set(), []
            for r in records:
                if r["id"] not in seen:
                    seen.add(r["id"])
                    unique.append(r)
            print(f"  파싱된 레코드: {len(unique)}건")
            chunk = 200
            loaded = 0
            for i in range(0, len(unique), chunk):
                batch = unique[i : i + chunk]
                await db.execute(
                    text("""
                        INSERT OR REPLACE INTO financial_products
                        (id, company_code, company_name, product_code, product_name,
                         product_type, join_method, target_raw, preferred_condition,
                         maturity_interest, notes, is_youth_product, min_age, max_age,
                         max_limit, loan_limit, early_repay_fee, delay_rate,
                         start_date, end_date, dcls_month, fetched_at)
                        VALUES (:id, :company_code, :company_name, :product_code, :product_name,
                                :product_type, :join_method, :target_raw, :preferred_condition,
                                :maturity_interest, :notes, :is_youth_product, :min_age, :max_age,
                                :max_limit, :loan_limit, :early_repay_fee, :delay_rate,
                                :start_date, :end_date, :dcls_month, datetime('now'))
                    """),
                    batch,
                )
                await db.commit()
                loaded += len(batch)
                print(f"  {loaded}/{len(unique)} 적재 완료")
            print(f"  ✅ 금융상품 {loaded}건 적재 완료!")
        else:
            print(f"  ⚠️ {fp_path} 파일 없음 - 건너뜀")

    print("\n🎉 모든 데이터 적재 완료!")


if __name__ == "__main__":
    asyncio.run(main())

"""
CSV → SQLite 직접 적재 (동기 방식 - greenlet 의존성 없음)
실행: python scripts/load_csv_sync.py  (backend/ 디렉토리에서)
"""

import io
import re
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path

# Windows 콘솔 UTF-8 강제 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from app.services.deadline import parse_apply_period

BASE = Path(__file__).parent.parent
DATA_DIR = BASE.parent / "data"
DB_PATH = BASE / "youth_finance.db"

YOUTH_KW = ["청년", "청소년", "사회초년생", "신혼", "미취업", "구직"]

TYPE_MAP = {
    "savingProductsSearch": "saving",
    "depositProductsSearch": "deposit",
    "mortgageLoanProductsSearch": "mortgage",
    "rentHouseLoanProductsSearch": "rent",
    "creditLoanProductsSearch": "credit",
}


# ─── DB 초기화 ────────────────────────────────────────────────────────────────
def init_db(conn: sqlite3.Connection):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS user_profiles (
        id TEXT PRIMARY KEY,
        user_id TEXT UNIQUE NOT NULL,
        birth_date TEXT,
        annual_income INTEGER,
        region_code TEXT,
        region_name TEXT,
        marriage_status TEXT,
        job_code TEXT,
        school_code TEXT,
        employment_type TEXT,
        persona TEXT,
        updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS user_bookmarks (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        policy_id TEXT NOT NULL,
        notify_enabled INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS policies (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        keyword TEXT,
        category_main TEXT,
        category_sub TEXT,
        description TEXT,
        support_content TEXT,
        apply_method TEXT,
        apply_url TEXT,
        ref_url1 TEXT,
        ref_url2 TEXT,
        min_age INTEGER DEFAULT 0,
        max_age INTEGER DEFAULT 0,
        earn_min INTEGER DEFAULT 0,
        earn_max INTEGER DEFAULT 0,
        region_codes TEXT,
        marriage_code TEXT,
        job_codes TEXT,
        school_codes TEXT,
        apply_start TEXT,
        apply_end TEXT,
        apply_period_text TEXT,
        biz_start TEXT,
        biz_end TEXT,
        supervise_inst TEXT,
        supervise_inst_code TEXT,
        operate_inst TEXT,
        support_scale INTEGER,
        is_scale_limited INTEGER DEFAULT 0,
        view_count INTEGER DEFAULT 0,
        embedding_id INTEGER,
        fetched_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS financial_products (
        id TEXT PRIMARY KEY,
        company_code TEXT NOT NULL,
        company_name TEXT NOT NULL,
        product_code TEXT NOT NULL,
        product_name TEXT NOT NULL,
        product_type TEXT NOT NULL,
        join_method TEXT,
        target_raw TEXT,
        preferred_condition TEXT,
        maturity_interest TEXT,
        notes TEXT,
        is_youth_product INTEGER DEFAULT 0,
        min_age INTEGER DEFAULT 0,
        max_age INTEGER DEFAULT 0,
        max_limit INTEGER,
        loan_limit INTEGER,
        early_repay_fee TEXT,
        delay_rate TEXT,
        start_date TEXT,
        end_date TEXT,
        dcls_month TEXT,
        fetched_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS notification_logs (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        policy_id TEXT NOT NULL,
        days_left INTEGER,
        sent_at TEXT DEFAULT (datetime('now'))
    );
    """)
    conn.commit()
    print("  ✅ 테이블 생성 완료")


# ─── 정책 적재 ────────────────────────────────────────────────────────────────
def safe_int(v, default=0):
    try:
        return int(float(v)) if v and str(v) not in ("nan", "None", "") else default
    except Exception:
        return default


def to_iso(d):
    return d.isoformat() if d else None


def map_policy(row):
    pid = str(row.get("plcyNo", "")).strip()
    if not pid:
        return None
    apply_start, apply_end, period_text = parse_apply_period(str(row.get("aplyYmd", "")))
    biz_start, biz_end, _ = parse_apply_period(
        f"{row.get('bizPrdBgngYmd', '')} ~ {row.get('bizPrdEndYmd', '')}"
    )
    zip_raw = str(row.get("zipCd", "")).strip()
    region_codes = zip_raw if zip_raw and zip_raw != "nan" else None
    return (
        pid,
        str(row.get("plcyNm", ""))[:200],
        str(row.get("plcyKywdNm", ""))[:200] or None,
        str(row.get("lclsfNm", ""))[:50] or None,
        str(row.get("mclsfNm", ""))[:50] or None,
        str(row.get("plcyExplnCn", "")) or None,
        str(row.get("plcySprtCn", "")) or None,
        str(row.get("plcyAplyMthdCn", "")) or None,
        str(row.get("aplyUrlAddr", ""))[:500] or None,
        str(row.get("refUrlAddr1", ""))[:500] or None,
        str(row.get("refUrlAddr2", ""))[:500] or None,
        safe_int(row.get("sprtTrgtMinAge")),
        safe_int(row.get("sprtTrgtMaxAge")),
        safe_int(row.get("earnMinAmt")),
        safe_int(row.get("earnMaxAmt")),
        region_codes,
        str(row.get("mrgSttsCd", "")) or None,
        str(row.get("jobCd", "")) or None,
        str(row.get("schoolCd", "")) or None,
        to_iso(apply_start),
        to_iso(apply_end),
        period_text,
        to_iso(biz_start),
        to_iso(biz_end),
        str(row.get("sprvsnInstCdNm", ""))[:100] or None,
        str(row.get("sprvsnInstCd", ""))[:20] or None,
        str(row.get("operInstCdNm", ""))[:100] or None,
        safe_int(row.get("sprtSclCnt")) or None,
        1 if str(row.get("sprtSclLmtYn", "N")).upper() == "Y" else 0,
    )


def load_policies(conn: sqlite3.Connection):
    path = DATA_DIR / "youth_policy_final.csv"
    if not path.exists():
        print(f"  ⚠️ {path} 없음 - 건너뜀")
        return
    print(f"\n▶ 청년 정책 적재 중... ({path.name})")
    df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    records = [r for r in (map_policy(row) for _, row in df.iterrows()) if r]
    print(f"  파싱 완료: {len(records)}건")
    conn.executemany("""
        INSERT OR REPLACE INTO policies
        (id, name, keyword, category_main, category_sub,
         description, support_content, apply_method,
         apply_url, ref_url1, ref_url2,
         min_age, max_age, earn_min, earn_max,
         region_codes, marriage_code, job_codes, school_codes,
         apply_start, apply_end, apply_period_text,
         biz_start, biz_end,
         supervise_inst, supervise_inst_code, operate_inst,
         support_scale, is_scale_limited)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, records)
    conn.commit()
    print(f"  ✅ {len(records)}건 적재 완료!")


# ─── 금융상품 적재 ────────────────────────────────────────────────────────────
def detect_type(url: str) -> str:
    for k, v in TYPE_MAP.items():
        if k in str(url):
            return v
    return "saving"


def parse_age(text: str):
    min_a = max_a = 0
    m = re.search(r"만\s*(\d+)\s*세\s*이상", text)
    if m:
        min_a = int(m.group(1))
    m = re.search(r"(\d+)\s*세\s*이하", text)
    if m:
        max_a = int(m.group(1))
    return min_a, max_a


def parse_date_str(raw):
    if not raw or str(raw).strip() in ("nan", "None", ""):
        return None
    s = str(raw).strip()[:8]
    if len(s) < 8:
        return None
    try:
        return date(int(s[:4]), int(s[4:6]), int(s[6:8])).isoformat()
    except Exception:
        return None


def map_product(row):
    co = str(row.get("금융회사코드", "")).strip()
    pc = str(row.get("상품코드", "")).strip()
    if not co or not pc or co == "nan" or pc == "nan":
        return None
    pid = f"{co}_{pc}"
    name = str(row.get("상품명", ""))
    target = str(row.get("가입대상", ""))
    min_a, max_a = parse_age(target)
    max_lim = None
    try:
        v = row.get("최대한도")
        if v and str(v) not in ("nan", "None", ""):
            max_lim = int(float(str(v).replace(",", "")))
    except Exception:
        pass
    return (
        pid, co,
        str(row.get("회사명", ""))[:100],
        pc,
        name[:200],
        detect_type(str(row.get("상품유형", ""))),
        str(row.get("가입방법", ""))[:200] or None,
        target or None,
        str(row.get("우대조건", "")) or None,
        str(row.get("만기이자", "")) or None,
        str(row.get("유의사항", "")) or None,
        1 if any(kw in name + target for kw in YOUTH_KW) else 0,
        min_a, max_a,
        max_lim,
        None,
        str(row.get("중도상환수수료", "")) or None,
        str(row.get("연체이자율", "")) or None,
        parse_date_str(row.get("시작일")),
        parse_date_str(row.get("종료일")),
        str(row.get("공시월", ""))[:10] or None,
    )


def load_financial(conn: sqlite3.Connection):
    path = DATA_DIR / "financial_products.csv"
    if not path.exists():
        print(f"  ⚠️ {path} 없음 - 건너뜀")
        return
    print(f"\n▶ 금융상품 적재 중... ({path.name})")
    df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    records_raw = [r for r in (map_product(row) for _, row in df.iterrows()) if r]
    # 중복 제거
    seen, records = set(), []
    for r in records_raw:
        if r[0] not in seen:
            seen.add(r[0])
            records.append(r)
    print(f"  파싱 완료: {len(records)}건")
    conn.executemany("""
        INSERT OR REPLACE INTO financial_products
        (id, company_code, company_name, product_code, product_name,
         product_type, join_method, target_raw, preferred_condition,
         maturity_interest, notes, is_youth_product, min_age, max_age,
         max_limit, loan_limit, early_repay_fee, delay_rate,
         start_date, end_date, dcls_month)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, records)
    conn.commit()
    print(f"  ✅ {len(records)}건 적재 완료!")


# ─── 메인 ────────────────────────────────────────────────────────────────────
def main():
    print(f"▶ DB 경로: {DB_PATH}")
    print("▶ 테이블 생성 중...")
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    init_db(conn)
    load_policies(conn)
    load_financial(conn)
    conn.close()

    size_mb = DB_PATH.stat().st_size / 1024 / 1024
    print(f"\n🎉 완료! DB 크기: {size_mb:.1f} MB → {DB_PATH}")


if __name__ == "__main__":
    main()

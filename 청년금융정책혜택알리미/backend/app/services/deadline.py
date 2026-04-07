"""
신청기간 파서 — youth_policy_final.csv의 aplyYmd 컬럼은 아래처럼 다양한 형태로 들어옴:
  "20260301 ~ 20260430"
  "2026-03-01~2026-04-30"
  "연중"
  "상시"
  "20260101 ~ 20261231"
  ""  (빈값)
  "20260401 ~ 20260430(예정)"
  None
"""

import re
from datetime import date, datetime, timezone


_DATE_PATTERNS = [
    r"(\d{4})(\d{2})(\d{2})",       # 20260301
    r"(\d{4})-(\d{2})-(\d{2})",     # 2026-03-01
    r"(\d{4})\.(\d{2})\.(\d{2})",   # 2026.03.01
    r"(\d{4})/(\d{2})/(\d{2})",     # 2026/03/01
]

_ALWAYS_KEYWORDS = {"연중", "상시", "수시", "연중무휴", "해당없음", "상시모집"}


def _extract_date(text: str) -> date | None:
    """텍스트에서 첫 번째 날짜를 추출."""
    for pattern in _DATE_PATTERNS:
        m = re.search(pattern, text)
        if m:
            try:
                return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except ValueError:
                continue
    return None


def parse_apply_period(raw: str | None) -> tuple[date | None, date | None, str | None]:
    """
    Returns:
        (apply_start, apply_end, period_text)
        - 연중/상시이면 (None, None, "연중")
        - 파싱 실패 시 (None, None, raw)
    """
    if not raw or not str(raw).strip():
        return None, None, None

    text = str(raw).strip()

    # 연중/상시 키워드 체크
    for kw in _ALWAYS_KEYWORDS:
        if kw in text:
            return None, None, "연중"

    # "날짜 ~ 날짜" 또는 "날짜~날짜" 패턴
    parts = re.split(r"\s*[~\-–—]\s*", text, maxsplit=1)
    if len(parts) == 2:
        start = _extract_date(parts[0])
        end = _extract_date(parts[1])
        if start or end:
            return start, end, text

    # 단일 날짜 (마감일만 표기)
    single = _extract_date(text)
    if single:
        return None, single, text

    return None, None, text


def days_to_deadline(apply_end: date | None) -> int | None:
    """마감까지 남은 일수. apply_end가 없으면 None(상시)."""
    if apply_end is None:
        return None
    today = datetime.now(timezone.utc).date()
    delta = (apply_end - today).days
    return delta


def deadline_badge(days: int | None) -> str:
    """D-day 라벨."""
    if days is None:
        return "상시"
    if days < 0:
        return "마감"
    if days == 0:
        return "D-DAY"
    if days <= 3:
        return f"D-{days} 🔴"
    if days <= 7:
        return f"D-{days} 🟡"
    return f"D-{days}"

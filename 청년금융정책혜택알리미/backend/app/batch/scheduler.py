"""
APScheduler 기반 배치 스케줄러.
- 청년정책 수집: 매일 오전 3시
- FSS 금융상품 수집: 매월 1일 오전 4시
- D-day 알림 발송: 매일 오전 9시
"""

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.batch.fss_collector import collect_financial_products
from app.batch.policy_collector import collect_policies
from app.services.notification import send_deadline_alerts

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="Asia/Seoul")


def setup_scheduler():
    # 청년정책 — 매일 03:00
    scheduler.add_job(
        _run_policy_collect,
        CronTrigger(hour=3, minute=0),
        id="collect_policies",
        replace_existing=True,
    )

    # FSS 금융상품 — 매월 1일 04:00
    scheduler.add_job(
        _run_fss_collect,
        CronTrigger(day=1, hour=4, minute=0),
        id="collect_fss",
        replace_existing=True,
    )

    # D-day 알림 — 매일 09:00
    scheduler.add_job(
        _run_send_alerts,
        CronTrigger(hour=9, minute=0),
        id="send_alerts",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("[Scheduler] 스케줄러 시작됨")


async def _run_policy_collect():
    try:
        count = await collect_policies()
        logger.info(f"[Scheduler] 정책 수집 완료: {count}건")
    except Exception as e:
        logger.error(f"[Scheduler] 정책 수집 실패: {e}")


async def _run_fss_collect():
    try:
        count = await collect_financial_products()
        logger.info(f"[Scheduler] FSS 수집 완료: {count}건")
    except Exception as e:
        logger.error(f"[Scheduler] FSS 수집 실패: {e}")


async def _run_send_alerts():
    try:
        count = await send_deadline_alerts()
        logger.info(f"[Scheduler] 알림 발송 완료: {count}건")
    except Exception as e:
        logger.error(f"[Scheduler] 알림 발송 실패: {e}")

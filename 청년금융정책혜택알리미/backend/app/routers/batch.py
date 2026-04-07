"""배치 수동 트리거 (개발/운영 편의용)."""

from fastapi import APIRouter, BackgroundTasks

from app.batch.fss_collector import collect_financial_products
from app.batch.policy_collector import collect_policies
from app.services.notification import send_deadline_alerts

router = APIRouter(prefix="/api/batch", tags=["batch"])


@router.post("/collect-policy")
async def trigger_policy_collect(background_tasks: BackgroundTasks):
    background_tasks.add_task(collect_policies)
    return {"message": "청년정책 수집을 백그라운드에서 시작했습니다."}


@router.post("/collect-fss")
async def trigger_fss_collect(background_tasks: BackgroundTasks):
    background_tasks.add_task(collect_financial_products)
    return {"message": "FSS 금융상품 수집을 백그라운드에서 시작했습니다."}


@router.post("/send-alerts")
async def trigger_send_alerts(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_deadline_alerts)
    return {"message": "D-day 알림 발송을 백그라운드에서 시작했습니다."}

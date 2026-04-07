"""D-day 기반 이메일 알림 발송."""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.policy import NotificationLog, Policy
from app.models.user import User, UserBookmark

logger = logging.getLogger(__name__)

ALERT_DAYS = [7, 3, 1]   # D-7, D-3, D-1에 발송


async def send_deadline_alerts() -> int:
    """북마크된 정책 중 마감 임박 사용자에게 이메일 발송."""
    sent_count = 0
    today = datetime.now(timezone.utc).date()

    async with AsyncSessionLocal() as db:
        for d in ALERT_DAYS:
            target_date = today + timedelta(days=d)

            # 마감일이 target_date인 정책 조회
            result = await db.execute(
                select(Policy).where(Policy.apply_end == target_date)
            )
            policies = result.scalars().all()
            if not policies:
                continue

            for policy in policies:
                # 해당 정책을 북마크한 사용자 조회
                bm_result = await db.execute(
                    select(UserBookmark, User)
                    .join(User, UserBookmark.user_id == User.id)
                    .where(
                        and_(
                            UserBookmark.policy_id == policy.id,
                            UserBookmark.notify_enabled == True,
                        )
                    )
                )
                rows = bm_result.fetchall()

                for bm, user in rows:
                    # 중복 발송 방지
                    dup = await db.execute(
                        select(NotificationLog).where(
                            and_(
                                NotificationLog.user_id == user.id,
                                NotificationLog.policy_id == policy.id,
                                NotificationLog.days_left == d,
                            )
                        )
                    )
                    if dup.scalar_one_or_none():
                        continue

                    # 이메일 발송
                    success = await _send_email(
                        to=user.email,
                        policy_name=policy.name,
                        days_left=d,
                        apply_url=policy.apply_url,
                    )
                    if success:
                        log = NotificationLog(
                            user_id=user.id,
                            policy_id=policy.id,
                            days_left=d,
                        )
                        db.add(log)
                        sent_count += 1

            await db.commit()

    logger.info(f"[Notification] {sent_count}건 발송 완료")
    return sent_count


async def _send_email(to: str, policy_name: str, days_left: int, apply_url: str | None) -> bool:
    """aiosmtplib을 사용한 비동기 이메일 발송."""
    try:
        import aiosmtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[청년혜택알리미] '{policy_name}' 신청 마감 D-{days_left}"
        msg["From"] = settings.SMTP_USER
        msg["To"] = to

        body = f"""
        <html><body>
        <h2>📢 신청 마감이 {days_left}일 남았습니다!</h2>
        <p><b>{policy_name}</b></p>
        <p>놓치지 마세요. 지금 바로 신청하세요.</p>
        {"<p><a href='" + apply_url + "'>신청 바로가기 →</a></p>" if apply_url else ""}
        <hr><p style='color:gray;font-size:12px'>청년 금융 혜택 통합 플랫폼</p>
        </body></html>
        """
        msg.attach(MIMEText(body, "html", "utf-8"))

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        return True

    except Exception as e:
        logger.warning(f"[Notification] 이메일 발송 실패 ({to}): {e}")
        return False

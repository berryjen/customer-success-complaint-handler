# app/services/actions.py
import structlog
from app.database import SessionLocal
from app.models import Complaint, ComplaintStatus
from app.services.classifier import ClassificationResult
from app.services.notifier import notify_slack, send_auto_reply

logger = structlog.get_logger()


async def execute_action(complaint_id: int, classification: ClassificationResult) -> None:
    """
    Execute business rules based on AI classification.

    Rules:
    - CRITICAL: Immediate Slack alert + escalate to human
    - HIGH + billing: Auto-reply + escalate
    - HIGH (other): Escalate
    - MEDIUM/LOW: Log to low-priority channel
    """
    db = SessionLocal()
    try:
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            logger.warning("complaint_not_found_for_action", complaint_id=complaint_id)
            return

        # Update complaint with classification results
        complaint.severity = classification.severity
        complaint.category = classification.category
        complaint.summary = classification.summary
        complaint.sentiment_score = classification.sentiment_score
        complaint.suggested_action = classification.suggested_action
        complaint.status = ComplaintStatus.PROCESSING

        # ── Rule Engine ──────────────────────────────────────────

        if classification.severity == "critical":
            complaint.status = ComplaintStatus.ESCALATED
            await notify_slack(
                f"""🚨 *CRITICAL COMPLAINT* 🚨
*ID:* {complaint.id}
*Category:* {classification.category}
*Sentiment:* {classification.sentiment_score}/10
*Summary:* {classification.summary}
*Content:* {complaint.raw_content[:200]}...""",
                channel="#support-urgent",
            )
            logger.info("complaint_escalated_critical", complaint_id=complaint.id)

        elif classification.severity == "high":
            if classification.category == "billing":
                complaint.status = ComplaintStatus.ESCALATED
                if complaint.customer_email:
                    await send_auto_reply(
                        to_email=complaint.customer_email,
                        template="billing_escalation",
                    )
                await notify_slack(
                    f"""⚠️ *HIGH PRIORITY - BILLING*
*ID:* {complaint.id}
*Sentiment:* {classification.sentiment_score}/10
*Summary:* {classification.summary}""",
                    channel="#support-billing",
                )
                logger.info("complaint_escalated_billing", complaint_id=complaint.id)
            else:
                complaint.status = ComplaintStatus.ESCALATED
                await notify_slack(
                    f"""⚠️ *HIGH PRIORITY*
*ID:* {complaint.id}
*Category:* {classification.category}
*Summary:* {classification.summary}""",
                    channel="#support",
                )
                logger.info("complaint_escalated_high", complaint_id=complaint.id)

        elif classification.suggested_action == "auto_reply":
            if complaint.customer_email:
                await send_auto_reply(
                    to_email=complaint.customer_email,
                    template="general_acknowledgment",
                )
            complaint.status = ComplaintStatus.RESOLVED
            logger.info("complaint_auto_replied", complaint_id=complaint.id)

        else:
            # MEDIUM / LOW or REVIEW
            await notify_slack(
                f"""📥 New Complaint
*ID:* {complaint.id} | *Severity:* {classification.severity}
*Category:* {classification.category}
*Summary:* {classification.summary}""",
                channel="#support-low",
            )
            complaint.status = ComplaintStatus.RESOLVED
            logger.info("complaint_logged_low_priority", complaint_id=complaint.id)

        db.commit()

    except Exception as exc:
        db.rollback()
        logger.error("action_execution_failed", complaint_id=complaint_id, error=str(exc))
        raise
    finally:
        db.close()
"""
Jobs Controller - Endpoints for manual job execution.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from robbot.api.v1.dependencies import get_current_user, get_db
from robbot.domain.shared.enums import Role
from robbot.infra.persistence.models.user_model import UserModel
from robbot.infra.jobs.reengagement_job import run_reengagement_job

router = APIRouter()


@router.post("/reengagement", tags=["Jobs"])
def trigger_reengagement_job(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Trigger re-engagement job manually (admin only).

    Requires JWT authentication and admin role.

    This job:
    - Finds inactive conversations (> 48h without messages)
    - Sends automated re-engagement messages
    - Updates conversation status to AWAITING_RESPONSE
    """
    # Check admin permission
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        result = run_reengagement_job()

        return {
            "message": "Re-engagement job completed",
            "result": result,
        }
    except Exception as e:  # noqa: BLE001 (blind exception)
        raise HTTPException(status_code=500, detail=f"Failed to run re-engagement job: {str(e)}")


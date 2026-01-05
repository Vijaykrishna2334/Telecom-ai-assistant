"""
Telecom plans API endpoints.
"""
from typing import List

from fastapi import APIRouter, HTTPException, status
from app.core.logging import get_logger
from app.models.schemas import PlanResponse
from app.services.telecom import fetch_plan_data

logger = get_logger(__name__)
router = APIRouter()


@router.get(
    "/plans",
    response_model=List[PlanResponse],
    status_code=status.HTTP_200_OK,
    tags=["Plans"],
)
async def list_plans() -> List[PlanResponse]:
    """
    List all available telecom plans.

    Returns:
        List of plans
    """
    try:
        logger.info("Listing plans")

        result = await fetch_plan_data()
        plans_data = result.get("plans", [])

        # Convert to response model
        from datetime import datetime
        plans = [
            PlanResponse(
                id=i + 1,
                plan_id=p["id"],
                name=p["name"],
                price=p["price"],
                data=p["data"],
                calls=p["calls"],
                sms=p["sms"],
                features=p["features"],
                is_active=True,
                created_at=datetime.utcnow(),
            )
            for i, p in enumerate(plans_data)
        ]

        return plans

    except Exception as e:
        logger.error("Failed to list plans", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve plans",
        )


@router.get(
    "/plans/{plan_id}",
    response_model=PlanResponse,
    status_code=status.HTTP_200_OK,
    tags=["Plans"],
)
async def get_plan(plan_id: str) -> PlanResponse:
    """
    Get details of a specific plan.

    Args:
        plan_id: Plan identifier

    Returns:
        Plan details
    """
    try:
        logger.info("Getting plan details", plan_id=plan_id)

        result = await fetch_plan_data(plan_id=plan_id)
        plans_data = result.get("plans", [])

        if not plans_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan {plan_id} not found",
            )

        plan_data = plans_data[0]
        from datetime import datetime
        return PlanResponse(
            id=1,
            plan_id=plan_data["id"],
            name=plan_data["name"],
            price=plan_data["price"],
            data=plan_data["data"],
            calls=plan_data["calls"],
            sms=plan_data["sms"],
            features=plan_data["features"],
            is_active=True,
            created_at=datetime.utcnow(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get plan", plan_id=plan_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve plan",
        )

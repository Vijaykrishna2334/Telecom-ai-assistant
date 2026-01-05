"""
Plan management service for telecom operations.
"""
from typing import List, Optional

from app.core.logging import get_logger
from app.models.schemas import PlanResponse

logger = get_logger(__name__)


async def fetch_plan_data(
    plan_id: Optional[str] = None,
    price_range: Optional[str] = None,
    data_requirement: Optional[str] = None,
) -> dict[str, any]:
    """
    Fetch telecom plan data.

    Args:
        plan_id: Optional specific plan ID
        price_range: Optional price range filter
        data_requirement: Optional minimum data requirement

    Returns:
        Dict with plan data
    """
    logger.info(
        "Fetching plan data",
        plan_id=plan_id,
        price_range=price_range,
        data_requirement=data_requirement,
    )

    # Mock data - would fetch from database in production
    plans = [
        {
            "id": "basic-30",
            "name": "Basic 30",
            "price": 30,
            "data": "5GB",
            "calls": "Unlimited",
            "sms": "100",
            "features": ["Voicemail", "Caller ID"],
        },
        {
            "id": "standard-50",
            "name": "Standard 50",
            "price": 50,
            "data": "20GB",
            "calls": "Unlimited",
            "sms": "Unlimited",
            "features": ["Voicemail", "Caller ID", "Hotspot 5GB"],
        },
        {
            "id": "premium-80",
            "name": "Premium 80",
            "price": 80,
            "data": "Unlimited",
            "calls": "Unlimited",
            "sms": "Unlimited",
            "features": [
                "Voicemail",
                "Caller ID",
                "Hotspot Unlimited",
                "International Calls 100min",
            ],
        },
    ]

    if plan_id:
        plans = [p for p in plans if p["id"] == plan_id]

    return {"plans": plans, "count": len(plans)}


async def get_plan_recommendations(
    budget: float, data_usage: str, features: List[str]
) -> dict[str, any]:
    """
    Get plan recommendations based on requirements.

    Args:
        budget: Maximum budget
        data_usage: Estimated data usage
        features: Required features

    Returns:
        Dict with recommended plans
    """
    logger.info(
        "Getting plan recommendations",
        budget=budget,
        data_usage=data_usage,
        features=features,
    )

    result = await fetch_plan_data()
    plans = result["plans"]

    # Filter by budget
    recommended = [p for p in plans if p["price"] <= budget]

    return {"recommended_plans": recommended, "count": len(recommended)}

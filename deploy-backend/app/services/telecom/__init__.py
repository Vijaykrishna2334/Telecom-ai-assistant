"""
Telecom services for plan management, billing, network status, and troubleshooting.
"""
from app.services.telecom.billing import check_billing_status, process_payment
from app.services.telecom.network import check_network_status, verify_network_coverage
from app.services.telecom.plans import fetch_plan_data, get_plan_recommendations
from app.services.telecom.troubleshooting import (
    diagnose_connectivity_issue,
    escalate_to_agent,
    initiate_speed_test,
)

__all__ = [
    "fetch_plan_data",
    "get_plan_recommendations",
    "check_billing_status",
    "process_payment",
    "verify_network_coverage",
    "check_network_status",
    "initiate_speed_test",
    "diagnose_connectivity_issue",
    "escalate_to_agent",
]

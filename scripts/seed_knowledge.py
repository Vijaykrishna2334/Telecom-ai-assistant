#!/usr/bin/env python3
"""
Seed knowledge base with documents.
"""
import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.core import get_logger
from app.services.rag import knowledge_base

logger = get_logger(__name__)


async def load_plans() -> None:
    """Load telecom plans into knowledge base."""
    plans_file = Path(__file__).parent.parent / "knowledge" / "plans" / "telecom_plans.json"
    
    with open(plans_file) as f:
        data = json.load(f)
    
    for plan in data["plans"]:
        text = f"""Plan: {plan['name']}
Price: ${plan['price']}/month
Data: {plan['data']}
Calls: {plan['calls']}
SMS: {plan['sms']}
Features: {', '.join(plan['features'])}
Description: {plan['description']}
"""
        await knowledge_base.add_document(text, {"type": "plan", "plan_id": plan["id"]})
    
    logger.info("Loaded plans", count=len(data["plans"]))


async def load_faqs() -> None:
    """Load FAQs into knowledge base."""
    faqs_file = Path(__file__).parent.parent / "knowledge" / "faqs" / "billing_faqs.md"
    
    with open(faqs_file) as f:
        content = f.read()
    
    # Split into sections
    sections = content.split("##")
    for section in sections[1:]:  # Skip first empty section
        if section.strip():
            await knowledge_base.add_document(
                "## " + section.strip(),
                {"type": "faq", "category": "billing"}
            )
    
    logger.info("Loaded FAQs")


async def load_troubleshooting() -> None:
    """Load troubleshooting guides into knowledge base."""
    guide_file = Path(__file__).parent.parent / "knowledge" / "troubleshooting" / "network_issues.md"
    
    with open(guide_file) as f:
        content = f.read()
    
    # Split into sections
    sections = content.split("##")
    for section in sections[1:]:  # Skip first empty section
        if section.strip():
            await knowledge_base.add_document(
                "## " + section.strip(),
                {"type": "troubleshooting", "category": "network"}
            )
    
    logger.info("Loaded troubleshooting guides")


async def main() -> None:
    """Seed knowledge base."""
    try:
        logger.info("Initializing knowledge base...")
        await knowledge_base.initialize()
        
        logger.info("Seeding knowledge base...")
        await load_plans()
        await load_faqs()
        await load_troubleshooting()
        
        logger.info("Knowledge base seeded successfully!")
    except Exception as e:
        logger.error("Failed to seed knowledge base", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

"""
Telecom-specific prompt templates.
"""
from typing import List, Optional

# System prompts - Now uses RAG context instead of hardcoded data
TELECOM_SYSTEM_PROMPT = """You are JioCare, the official AI assistant for Reliance Jio.

# CRITICAL INSTRUCTION - YOU MUST FOLLOW THIS

You will be given CONTEXT containing Jio's official plan data. 
**YOUR RESPONSES MUST BE BASED EXCLUSIVELY ON THIS CONTEXT.**

## STRICT RULES:

1. **ONLY USE DATA FROM CONTEXT** - Never invent plan names, prices, or features
2. **IF NOT IN CONTEXT, SAY SO** - Reply: "I don't have information about that. Please check MyJio app or call 1800-88-99999"
3. **NO COMPETITORS** - Never mention Airtel, Vi, Vodafone, BSNL, or any other telecom
4. **QUOTE EXACT VALUES** - Only mention prices/speeds that appear exactly in the context
5. **NO ASSUMPTIONS** - Don't assume plans exist. If a plan type isn't in context, say "I don't have that information"
6. **MINIMUM PRICES** - Jio mobile prepaid plans start at ₹199. NEVER mention any mobile plan under ₹199.

## 🚨🚨🚨 BLACKLISTED FAKE PLANS - NEVER MENTION THESE 🚨🚨🚨
These are NOT real Jio plans. NEVER say these exist:
❌ "Basic 30" or any plan for ₹30
❌ "Standard 50" or any plan for ₹50  
❌ "Premium 80" or any plan for ₹80
❌ "Daily Data Pack" with made-up prices
❌ "Happy Hours" or "Night Data"
❌ Any mobile plan under ₹100

If you find yourself about to say "Basic 30", "Standard 50", or "Premium 80" - STOP! These are FAKE. Use ONLY plans from the CONTEXT.

## CLARIFY USER INTENT:
When user asks about "plans" without specifying, ASK:
"Are you looking for **Prepaid** (recharge) or **Postpaid** (monthly bill) plans?"

## RESPONSE FORMAT - VERY IMPORTANT:

Keep responses SHORT and CLEAR. Use this format:

**For prepaid plans (recharge):**
📱 **Prepaid Plans**

| Price | Data/Day | Validity | Calls |
|-------|----------|----------|-------|
| ₹199 | 1.5 GB | 18 days | Unlimited |
| ₹249 | 1.5 GB | 28 days | Unlimited |
| ₹299 | 2 GB | 28 days | Unlimited |

**For postpaid plans:**
📱 **Postpaid Plans**

| Price | Data | OTT Benefits |
|-------|------|--------------|
| ₹399 | 25 GB | Data rollover |
| ₹599 | 50 GB | Netflix, Prime |

**For troubleshooting, use numbered steps:**
1. Step one
2. Step two

**RULES:**
- Show MAX 3-4 plans at a time (not all plans)
- Use tables for plans - easier to read
- Keep responses under 5 lines when possible
- End with: "Anything else?"

REMEMBER: If not in context, say "I don't have that info. Call 1800-88-99999\""""


VOICE_SYSTEM_PROMPT = """You are JioCare voice assistant for Reliance Jio.

# ABSOLUTE RULE - READ THIS FIRST

You will receive CONTEXT with Jio's official data.
USE ONLY DATA FROM THE CONTEXT. NEVER INVENT ANYTHING.

## BLACKLISTED FAKE PLANS - NEVER SAY THESE
- "Basic 30" for 30 rupees - DOES NOT EXIST
- "Standard 50" for 50 rupees - DOES NOT EXIST  
- "Premium 80" for 80 rupees - DOES NOT EXIST
- Any mobile plan under 199 rupees - FAKE

Jio prepaid plans START at 199 rupees. If you're about to say a plan under 199 rupees, STOP and check context!

## STRICT RULES:
1. Only mention plans/prices that are EXACTLY in the context
2. If asked about something not in context: "I don't have that info. Call 1800-88-99999"
3. Never say "we have a plan" unless that exact plan is in the context
4. No competitors (Airtel, Vi, Vodafone, BSNL)
5. Real Jio mobile prepaid: 199, 209, 249, 299, 349, 479 rupees, etc.

## VOICE OUTPUT FORMAT - CRITICAL:
- DO NOT use symbols like emojis, bullet points, or special characters
- DO NOT use markdown formatting like ** or tables
- Write prices as "199 rupees" not "₹199"
- Use plain conversational English only
- Speak naturally as if talking on a phone call

## FORBIDDEN:
- Inventing plan names like "Basic 30", "Daily Data", "Happy Hours"
- Guessing prices not in context
- Any price under 100 rupees for mobile plans
- Using emojis, tables, or markdown in voice responses

## CORRECT VOICE RESPONSE STYLE:
- "Based on our data, the prepaid plan costs 199 rupees for 18 days with 1.5 GB per day."
- "I don't have that specific plan info. Please check MyJio app or call 1800-88-99999."

## VOICE STYLE:
- Keep SHORT (2-3 sentences max)
- Be warm and friendly
- Greeting: "Namaste! How may I help you?"
- End: "Anything else?\""""


def create_chat_prompt(
    user_message: str,
    context: Optional[str] = None,
    conversation_history: Optional[List[dict[str, str]]] = None,
) -> List[dict[str, str]]:
    """
    Create a chat prompt with context and history.

    Args:
        user_message: Current user message
        context: Retrieved context from RAG
        conversation_history: Previous messages

    Returns:
        List of messages for chat completion
    """
    messages = [{"role": "system", "content": TELECOM_SYSTEM_PROMPT}]
    
    # Add conversation history if provided
    if conversation_history:
        for msg in conversation_history:
            messages.append(msg)
    
    # Add RAG context if available - INJECT STRONGLY
    if context:
        messages.append({
            "role": "user",
            "content": f"""Here is the OFFICIAL JIO DATA you must use. Only mention plans from this data:

<OFFICIAL_JIO_DATA>
{context}
</OFFICIAL_JIO_DATA>

IMPORTANT: If the user asks about something NOT in the above data, say "I don't have that information. Please check MyJio app or call 1800-88-99999."

Now respond to the user's question using ONLY the data above."""
        })
    
    # Add user message
    messages.append({"role": "user", "content": user_message})
    
    return messages


def create_voice_prompt(
    user_message: str,
    context: Optional[str] = None,
    conversation_history: Optional[List[dict[str, str]]] = None,
) -> List[dict[str, str]]:
    """
    Create a voice-optimized prompt with RAG context.
    
    Args:
        user_message: Current user message
        context: Retrieved context from RAG (knowledge base)
        conversation_history: Previous messages
    
    Returns:
        List of messages for chat completion
    """
    messages = [{"role": "system", "content": VOICE_SYSTEM_PROMPT}]
    
    # Add conversation history if provided
    if conversation_history:
        for msg in conversation_history:
            messages.append(msg)
    
    # Add RAG context if available - CRITICAL for accurate responses
    if context:
        messages.append({
            "role": "user",
            "content": f"""� IMPORTANT: Here is the ONLY DATA you can use. DO NOT invent any other plans or prices:

---START OF AUTHORIZED DATA---
{context}
---END OF AUTHORIZED DATA---

REMEMBER: Only mention plans/prices from AUTHORIZED DATA above. If something is not listed, say you'll check with the helpline."""
        })
    
    # Add user message
    messages.append({"role": "user", "content": user_message})
    
    return messages


# Function definitions for LLM function calling
AVAILABLE_FUNCTIONS = [
    "fetch_plan_data",
    "check_billing_status",
    "verify_network_coverage",
    "initiate_speed_test",
    "escalate_to_agent"
]


def get_function_definitions() -> list[dict]:
    """
    Get function definitions for LLM function calling.
    
    Returns:
        List of function definition dicts
    """
    return [
        {
            "name": "fetch_plan_data",
            "description": "Fetch plan data for a specific plan type (prepaid, postpaid, fiber, airfiber)",
            "parameters": {
                "type": "object",
                "properties": {
                    "plan_type": {
                        "type": "string",
                        "enum": ["prepaid", "postpaid", "fiber", "airfiber"],
                        "description": "Type of plan to fetch"
                    },
                    "price_range": {
                        "type": "string",
                        "description": "Optional price range filter (e.g. '200-500')"
                    }
                },
                "required": ["plan_type"]
            }
        },
        {
            "name": "check_billing_status",
            "description": "Check billing status for a customer account",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "Customer phone number"
                    }
                },
                "required": ["phone_number"]
            }
        },
        {
            "name": "verify_network_coverage",
            "description": "Verify network coverage for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "pincode": {
                        "type": "string",
                        "description": "Area pincode"
                    },
                    "service_type": {
                        "type": "string",
                        "enum": ["mobile", "fiber", "airfiber", "5g"],
                        "description": "Type of service to check"
                    }
                },
                "required": ["pincode", "service_type"]
            }
        },
        {
            "name": "initiate_speed_test",
            "description": "Initiate a speed test for customer connection",
            "parameters": {
                "type": "object",
                "properties": {
                    "connection_id": {
                        "type": "string",
                        "description": "Customer connection ID"
                    }
                },
                "required": ["connection_id"]
            }
        },
        {
            "name": "escalate_to_agent",
            "description": "Escalate issue to human agent",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_type": {
                        "type": "string",
                        "description": "Type of issue requiring escalation"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "Priority level"
                    }
                },
                "required": ["issue_type"]
            }
        }
    ]

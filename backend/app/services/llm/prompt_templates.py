"""
Telecom-specific prompt templates.
"""
from typing import List, Optional

# System prompts - Now uses RAG context instead of hardcoded data
TELECOM_SYSTEM_PROMPT = """You are JioCare, a STRICT factual assistant for Reliance Jio.

# 🚨 ABSOLUTE RULE: COPY DATA EXACTLY FROM CONTEXT

You will receive REFERENCE DATA containing official Jio plan tables.
**YOUR ONLY JOB**: Extract and present data EXACTLY as written. CHARACTER-BY-CHARACTER accuracy.

## ⛔ NEVER DO:
- NEVER invent plans that don't exist in the context
- NEVER guess prices, data, or validity
- NEVER round/change values (₹399 stays ₹399, 40 GB stays 40 GB)
- NEVER skip plans from a table
- NEVER add plans not in the context

## ✅ ALWAYS DO:
- Copy plan names EXACTLY (Postpaid Lite, Postpaid Basic, Postpaid Value, etc.)
- Copy prices EXACTLY from the Price column
- Copy data amounts EXACTLY from the Data column
- List ALL rows from a table, not just some
- If a plan has "40 GB", say "40 GB" - not "30 GB"!

# 📊 TABLE EXTRACTION RULES

When you see a table like:
| Plan Name | Price | Data |
| Postpaid Lite | ₹349 | 30 GB |
| Postpaid Basic | ₹399 | 40 GB |

You MUST output:
- Postpaid Lite: ₹349, 30 GB
- Postpaid Basic: ₹399, 40 GB

**DO NOT** change 40 GB to 30 GB or skip Postpaid Lite!

# 🎯 SERVICE TYPE SEPARATION

FOUR DISTINCT SERVICES - NEVER CONFUSE:
1. **PREPAID** = Mobile SIM recharge, daily data (1GB/day, 2GB/day), validity in days (28/56/84/365)
2. **POSTPAID** = Monthly billing, plan names: Postpaid Lite → Basic → Value → Plus → Max → Pro → Ultra
3. **JioFiber** = Wired fiber optic, FUP = 3,300 GB
4. **JioAirFiber** = Wireless 5G, FUP = 1,000 GB (1 TB) for ALL plans

## POSTPAID PLAN NAMES (in order):
- Postpaid Lite (₹349)
- Postpaid Basic (₹399)  
- Postpaid Value (₹599)
- Postpaid Plus (₹649)
- Postpaid Max (₹799)
- Postpaid Pro (₹999)
- Postpaid Ultra (₹1,549)

## FAMILY POSTPAID PLANS:
- Family Value (₹449)
- Family Plus (₹749)
- Family Premium (₹899)
- Family Ultra (₹1,099)

**There is NO "Family Max" plan!**

# 📋 RESPONSE FORMAT

1. Start with answer immediately (no preamble)
2. Use Markdown tables with ALL columns
3. Include EVERY plan from context
4. End with: "Is there anything else I can help you with?"

# ✅ PRE-RESPONSE CHECKLIST

Before responding, verify:
□ Did I copy data EXACTLY from context? (character-by-character)
□ Did I include ALL plans from the table? (count rows!)
□ Did I avoid inventing any plan names?
□ Is Postpaid Lite (₹349) included if showing postpaid?
□ Are data values EXACT? (40 GB not 30 GB, etc.)

ACCURACY IS MANDATORY. 100% faithful to context data."""

# Dictionary for duration mapping
DURATION_MAPPING = {
    "1 month": "28 days",
    "2 months": "56 days",
    "3 months": "84 or 90 days",
    "1 year": "365 days",
    "annual": "365 days"
}


VOICE_SYSTEM_PROMPT = """You are JioCare, a friendly voice assistant for Reliance Jio.

# 🚨 CRITICAL: THIS IS VOICE OUTPUT - NO FORMATTING!

Your response will be READ ALOUD by a text-to-speech engine.
You MUST output ONLY plain spoken text that sounds natural when spoken.

## ⛔ ABSOLUTELY FORBIDDEN (TTS will speak these literally!):
- NO markdown tables (no | pipes, no dashes like ---)
- NO asterisks (* or **)
- NO checkmarks (✅ ❌)
- NO bullet symbols (•, -, *)
- NO emojis of any kind
- NO special symbols (₹ → say "rupees" instead)
- NO formatted lists with dashes or numbers followed by periods
- NO colons in list format (like "Plan: 599")

## ✅ CORRECT VOICE FORMAT:

WRONG (TTS reads symbols): "| Plan | Price | Speed |" or "**Netflix Basic**" or "✅ Included"
RIGHT (speakable): "The 599 rupees plan gives you 30 Mbps speed with 13 OTT apps included."

WRONG: "₹599 for 30 Mbps with 1 TB FUP"
RIGHT: "The plan costs 599 rupees with 30 Mbps speed and 1 terabyte data limit."

WRONG: "• Netflix ✅ • Prime ✅ • Hotstar ✅"
RIGHT: "This plan includes Netflix, Prime Video, and Hotstar."

## VOICE RESPONSE STYLE:
- Speak naturally as if talking to a customer on the phone
- Use complete sentences, not bullet points
- Say prices as "599 rupees" not "₹599"
- Say data as "2 gigabytes per day" or "1 terabyte limit"
- Keep responses concise (3-5 sentences max)
- Be warm, helpful, and conversational

# SERVICE TYPES (Don't Confuse):
1. PREPAID = Mobile recharge, daily data, validity in days
2. POSTPAID = Monthly billing, plan names: Lite, Basic, Value, Plus, Max, Pro, Ultra
3. JioFiber = Wired broadband, 3300 GB limit
4. JioAirFiber = Wireless 5G, 1 TB limit for all plans

# DATA ACCURACY RULES:
- Read prices and data EXACTLY from the provided context
- If info not in context, say "I don't have that specific information. Please call 1800-88-99999."
- List all relevant plans when asked, don't skip any
- JioFiber FUP is always 3300 GB, JioAirFiber FUP is always 1 TB

# EXAMPLE GOOD RESPONSES:

"For 599 rupees, you get the JioAirFiber plan with 30 Mbps speed and 1 terabyte data limit. It includes 13 plus OTT apps like Hotstar, Sony LIV, and ZEE5. Would you like to know about faster plans?"

"The prepaid plan at 399 rupees gives you 2.5 gigabytes of data per day for 28 days with unlimited voice calls. Is there anything else you'd like to know?"

Remember: Your output must sound natural when spoken aloud. No formatting whatsoever!"""


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
    
    # Add RAG context - Minimal and clear to avoid echoing
    if context:
        messages.append({
            "role": "system",  # Change to system role to reduce user mimicry
            "content": f"""📋 OFFICIAL JIO DATA (COPY EXACTLY - DO NOT MODIFY):
---
{context}
---
⚠️ CRITICAL REMINDERS:
• COPY all prices, data amounts, and plan names CHARACTER-BY-CHARACTER from above
• If table shows "40 GB" → say "40 GB", NOT "30 GB"
• Include ALL plans from tables (don't skip Postpaid Lite or any other)
• There is NO "Family Max" plan - only Family Value/Plus/Premium/Ultra
• JioFiber FUP = 3,300 GB | JioAirFiber FUP = 1 TB
• If info not in data above, say "I don't have that specific information."
• NEVER invent or guess plan details"""
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
            "role": "system",
            "content": f"""REFERENCE DATA (extract info but DO NOT copy formatting):
---
{context}
---
VOICE OUTPUT REMINDER:
- Extract the prices, speeds, data, and features from above
- But respond in PLAIN SPOKEN SENTENCES only
- NO tables, NO symbols, NO bullets, NO markdown
- Say "599 rupees" not the rupee symbol
- Say "1 terabyte" not "1 TB"
- Sound natural when read aloud by TTS"""
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

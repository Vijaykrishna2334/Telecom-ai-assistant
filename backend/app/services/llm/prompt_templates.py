"""
Telecom-specific prompt templates.
"""
from typing import List, Optional

# System prompts
TELECOM_SYSTEM_PROMPT = """You are an intelligent AI assistant for a telecommunications company. Your role is to help customers with:

1. Plan information and recommendations
2. Billing inquiries and payment issues
3. Network coverage and signal problems
4. Troubleshooting connectivity issues
5. General account management

Guidelines:
- Be professional, friendly, and empathetic
- Provide clear and concise information
- Use simple language avoiding technical jargon when possible
- If you don't know something, be honest and offer to escalate to a human agent
- Always prioritize customer satisfaction and data privacy
- For sensitive issues (billing disputes, account access), gather information before taking action

You have access to several functions to help customers:
- fetch_plan_data: Get details about telecom plans
- check_billing_status: Check billing and payment information
- verify_network_coverage: Check network coverage in an area
- initiate_speed_test: Run network diagnostics
- escalate_to_agent: Transfer to a human agent

Use these functions when appropriate to provide accurate information."""

VOICE_SYSTEM_PROMPT = """You are a voice AI assistant for a telecommunications company. Keep responses:

- Brief and conversational (2-3 sentences max)
- Natural and friendly
- Clear and easy to understand when spoken
- Action-oriented

For complex information, summarize and offer to send details via SMS or email.
Ask one question at a time. Confirm understanding before proceeding."""


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

    if conversation_history:
        messages.extend(conversation_history)

    user_content = user_message
    if context:
        user_content = f"Context information:\n{context}\n\nUser question: {user_message}"

    messages.append({"role": "user", "content": user_content})
    return messages


def create_voice_prompt(
    user_message: str,
    context: Optional[str] = None,
) -> List[dict[str, str]]:
    """
    Create a voice-optimized prompt.

    Args:
        user_message: Current user message
        context: Retrieved context from RAG

    Returns:
        List of messages for chat completion
    """
    messages = [{"role": "system", "content": VOICE_SYSTEM_PROMPT}]

    user_content = user_message
    if context:
        user_content = f"Context: {context}\n\nUser: {user_message}"

    messages.append({"role": "user", "content": user_content})
    return messages


def create_function_call_prompt(
    function_name: str, function_description: str, parameters: dict[str, str]
) -> str:
    """
    Create a prompt for function calling.

    Args:
        function_name: Name of the function
        function_description: Description of what the function does
        parameters: Function parameters with descriptions

    Returns:
        Formatted prompt string
    """
    param_desc = "\n".join([f"- {k}: {v}" for k, v in parameters.items()])

    return f"""Function: {function_name}
Description: {function_description}
Parameters:
{param_desc}

When the user's request matches this function, respond with a JSON object:
{{"function": "{function_name}", "arguments": {{"param1": "value1", "param2": "value2"}}}}"""


# Function definitions for the LLM
AVAILABLE_FUNCTIONS = {
    "fetch_plan_data": {
        "description": "Retrieve details about telecom plans including pricing, data allowances, and features",
        "parameters": {
            "plan_id": "Optional plan ID to get specific plan details",
            "price_range": "Optional price range filter (e.g., '30-50')",
            "data_requirement": "Optional minimum data requirement (e.g., '20GB')",
        },
    },
    "check_billing_status": {
        "description": "Check billing information, payment status, and account balance",
        "parameters": {
            "user_id": "User identifier",
            "include_history": "Whether to include payment history (true/false)",
        },
    },
    "verify_network_coverage": {
        "description": "Check network coverage and signal strength for a location",
        "parameters": {
            "location": "Location address or coordinates",
            "network_type": "Network type (4G, 5G, LTE)",
        },
    },
    "initiate_speed_test": {
        "description": "Run network speed and connectivity diagnostics",
        "parameters": {
            "user_id": "User identifier",
            "test_type": "Type of test (speed, latency, full)",
        },
    },
    "escalate_to_agent": {
        "description": "Transfer the conversation to a human customer service agent",
        "parameters": {
            "reason": "Reason for escalation",
            "priority": "Priority level (low, medium, high)",
        },
    },
}


def get_function_definitions() -> str:
    """
    Get formatted function definitions for the LLM.

    Returns:
        Formatted string with all function definitions
    """
    definitions = ["Available functions:"]
    for name, info in AVAILABLE_FUNCTIONS.items():
        definitions.append(f"\n{name}:")
        definitions.append(f"  {info['description']}")
        definitions.append("  Parameters:")
        for param, desc in info["parameters"].items():
            definitions.append(f"    - {param}: {desc}")
    return "\n".join(definitions)

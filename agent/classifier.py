import json

from client import client
from agent.prompts import CLASSIFICATION_PROMPT


VALID_INTENTS = {
    "customer_support",
    "meeting_request",
    "complaint",
    "lead",
    "payment",
    "order",
    "general"
}

VALID_PRIORITIES = {
    "low",
    "normal",
    "high",
    "urgent"
}


def classify_message(message):

    prompt = CLASSIFICATION_PROMPT.replace(
        "{message}",
        message
    )

    response = client.models.generate_content(
        model="models/gemini-3.5-flash-lite",
        contents=prompt
    )

    text = response.text.strip()

    try:
        result = json.loads(text)

    except json.JSONDecodeError:

        print("Invalid classifier response:", text)

        return {
            "intent": "general",
            "priority": "normal",
            "requires_owner": False
        }

    intent = result.get("intent")
    priority = result.get("priority")
    requires_owner = result.get("requires_owner")

    if intent not in VALID_INTENTS:

        print("Invalid intent:", intent)

        intent = "general"

    if priority not in VALID_PRIORITIES:

        print("Invalid priority:", priority)

        priority = "normal"

    if not isinstance(requires_owner, bool):

        print("Invalid requires_owner:", requires_owner)

        requires_owner = False

    return {
        "intent": intent,
        "priority": priority,
        "requires_owner": requires_owner
    }
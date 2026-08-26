from client import client


def generate_response(
    message,
    classification,
    conversation_history=None,
    memories=None
):
    """
    Generate a business-appropriate response
    based on the customer's message and context.
    """

    conversation_history = conversation_history or []
    memories = memories or []

    intent = classification["intent"]
    priority = classification["priority"]

    prompt = f"""
You are an AI business communication assistant.

Your job is to respond professionally and naturally to customers on WhatsApp.

Customer message:
{message}

Intent:
{intent}

Priority:
{priority}

Customer memories:
{memories}

Recent conversation:
{conversation_history}

Rules:

1. Be helpful, professional, and concise.
2. Do not invent business information.
3. Do not promise actions that have not been performed.
4. If information is missing, ask the customer for it.
5. Never claim that a meeting was scheduled unless the scheduling system actually scheduled it.
6. Never claim that a payment was verified unless a payment system verified it.
7. For complaints, acknowledge the issue and collect the information needed to resolve it.
8. For meeting requests, acknowledge the request but do not confirm a time yet.
9. If the message requires business-owner involvement, remain helpful without pretending to be the owner.
10. Respond naturally for WhatsApp.

Return ONLY the message that should be sent to the customer.
"""

    response = client.models.generate_content(
        model="models/gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text.strip()
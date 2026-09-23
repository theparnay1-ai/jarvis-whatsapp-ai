from client import client


def generate_response(
    message,
    classification,
    conversation_history=None,
    memories=None,
    knowledge=None
):
    """
    Generate a business-appropriate response
    based on the customer's message and context.
    """

    conversation_history = conversation_history or []
    memories = memories or []
    knowledge = knowledge or []

    intent = classification["intent"]
    priority = classification["priority"]

    if intent == "lead":
        if any(x in message.lower() for x in ["it should", "it must", "it needs", "also want", "also need"]):
            return "Got it! I've added those requirements to your project details."
        return "Thanks for sharing that! I'd be happy to help with your project. Could you tell me a little more about what you'd like to build and the features you need?"

    if not knowledge and intent == "customer_support" and (
    "?" in message or
    message.lower().startswith((
        "do ", "does ", "is ", "are ", "can ", "will ",
        "what ", "how ", "which ", "where ", "when ",
        "why ", "price", "cost"
    ))
)   and not conversation_history:
        return "I don't have that information available right now. Would you like me to have the business owner assist you?"


    prompt = f"""
You are an AI business communication assistant for a real business.

Your job is to respond professionally and naturally to customers on WhatsApp.

Customer message:
{message}

Intent:
{intent}

Priority:
{priority}

Customer memories:
{memories}

BUSINESS KNOWLEDGE:
{knowledge}

Recent conversation:
{conversation_history}

STRICT RULES:

1. Business knowledge is the ONLY source of truth about the business.
2. Never assume or invent that the business provides a product, service, price, feature, policy, or capability.
3. If the customer's question is answered by the business knowledge, answer using that information.
4. If the business knowledge does NOT contain the answer, clearly say that you don't have that information and ask the customer for more details or offer to have the business owner assist.
5a. Use conversation history only to understand the current message and resolve references or follow-ups.
5b. Do not mention unrelated projects, services, or details from conversation history.
5c. If the current question is already answered by business knowledge, answer directly using that knowledge without adding unrelated conversation details.
6. Never invent prices, services, policies, guarantees, availability, or features.
7. Do not infer that the business provides a service merely because the customer asks about it.
8. Never claim that a meeting was scheduled unless the scheduling system actually scheduled it.
9. Never claim that a payment was verified unless a payment system verified it.
10. Focus primarily on the current customer message. Use previous conversation only when necessary to understand it.
11. For meeting requests, acknowledge the request but do not confirm a time unless the scheduling system confirms it.
12. If business-owner involvement is required, remain helpful without pretending to be the owner.
13. Respond naturally and concisely for WhatsApp.
14. Conversation history is context, not content to repeat.
15. Do not mention previous conversation details unless they are directly necessary to answer the current message.
16. When the current message can be answered using business knowledge alone, ignore conversation history when generating the response.
17. Never mention an old project, requirement, or topic simply because it appears in conversation history.

Return ONLY the message that should be sent to the customer.
"""

    response = client.models.generate_content(
        model="models/gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text.strip()
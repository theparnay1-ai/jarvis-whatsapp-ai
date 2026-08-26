# agent/tools/customer_support.py

from agent.responder import generate_response


def handle_customer_support(
    message,
    classification,
    conversation_history=None,
    memories=None
):
    """
    Handle routine customer-support messages.
    """

    response = generate_response(
        message=message,
        classification=classification,
        conversation_history=conversation_history,
        memories=memories
    )

    return {
        "success": True,
        "response": response,
        "requires_owner": classification.get(
            "requires_owner",
            False
        )
    }
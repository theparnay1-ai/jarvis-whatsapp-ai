from database import (
    get_recent_messages,
    get_memories
)


def get_customer_context(sender, message_limit=10):
    """
    Retrieve recent conversation history and long-term
    memories for a WhatsApp customer.
    """

    recent_messages = get_recent_messages(
        sender,
        limit=message_limit
    )

    memories = get_memories(sender)

    conversation_history = []

    for item in recent_messages:

        conversation_history.append({
            "message": item.message,
            "response": item.response
        })

    memory_list = [
        item.memory
        for item in memories
    ]

    return {
        "conversation_history": conversation_history,
        "memories": memory_list
    }
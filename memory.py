from client import extract_memory
from database import (
    save_memory,
    get_memories,
    update_memory
)


def process_memory(sender, message):
    """
    Extract and manage long-term memory for a user.
    """

    memory = extract_memory(message)

    if not memory:
        return None

    existing_memories = get_memories(sender)

    # Check for exact duplicate
    for existing in existing_memories:

        if existing.memory.strip().lower() == memory.strip().lower():

            print("Duplicate memory ignored:", memory)

            return existing.memory

    # Check whether the new memory updates an existing memory
    for existing in existing_memories:

        prompt = f"""
You are managing long-term memory for an AI assistant.

Determine whether the NEW memory updates or replaces the EXISTING memory.

Reply with ONLY:
YES
or
NO

Existing memory:
{existing.memory}

New memory:
{memory}
"""

        from client import client

        response = client.models.generate_content(
            model="models/gemini-3.5-flash-lite",
            contents=prompt
        )

        is_update = response.text.strip().upper() == "YES"

        if is_update:

            updated = update_memory(
                existing.id,
                memory
            )

            print(
                "Memory updated:",
                existing.memory,
                "→",
                memory
            )

            return updated.memory

    # No related memory found
    save_memory(
        sender,
        memory
    )

    print("New memory saved:", memory)

    return memory
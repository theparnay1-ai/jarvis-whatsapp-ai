from client import extract_memory, client
from database import (
    save_memory,
    get_memories,
    update_memory
)


def process_memory(business_id, sender, message):
    """
    Extract and manage long-term memory for a user.
    """

    # Extract useful information from the message
    memory = extract_memory(message)

    if not memory:
        return None

    # Get existing memories
    existing_memories = get_memories(
    business_id,
    sender
)

    # If there are no existing memories, create a new one
    if not existing_memories:

        save_memory(
    business_id,
    sender,
    memory
)

        print("New memory saved:", memory)

        return memory

    # Prepare existing memories for Gemini
    memories_text = "\n".join(
        f"{memory_item.id}: {memory_item.memory}"
        for memory_item in existing_memories
    )

    prompt = f"""
You are managing long-term memory for an AI assistant.

A new memory has been extracted from the user's message.

Determine what should happen to this memory.

You must choose exactly one action:

CREATE
UPDATE
DUPLICATE

Rules:

CREATE:
Use CREATE if the new memory contains information that is not
already represented by an existing memory.

UPDATE:
Use UPDATE if the new memory changes, replaces, or corrects
an existing memory.

DUPLICATE:
Use DUPLICATE if the new memory contains the same information
as an existing memory.

If the action is UPDATE, also provide the ID of the existing
memory that should be updated.

Return ONLY in this format:

ACTION: CREATE

or:

ACTION: UPDATE
ID: 123

or:

ACTION: DUPLICATE

Existing memories:
{memories_text}

New memory:
{memory}
"""

    response = client.models.generate_content(
        model="models/gemini-3.5-flash-lite",
        contents=prompt
    )

    result = response.text.strip()

    print("Memory decision:", result)

    # Parse decision
    lines = [
        line.strip()
        for line in result.splitlines()
        if line.strip()
    ]

    action = None
    memory_id = None

    for line in lines:

        if line.upper().startswith("ACTION:"):

            action = line.split(
                ":", 1
            )[1].strip().upper()

        elif line.upper().startswith("ID:"):

            try:
                memory_id = int(
                    line.split(
                        ":", 1
                    )[1].strip()
                )

            except ValueError:
                memory_id = None

    # Handle duplicate
    if action == "DUPLICATE":

        print(
            "Duplicate memory ignored:",
            memory
        )

        return memory

    # Handle update
    if action == "UPDATE" and memory_id:

        updated = update_memory(
    business_id,
    memory_id,
    memory
)

        if updated:

            print(
                "Memory updated:",
                memory
            )

            return updated.memory

    # Default to creating a new memory
    save_memory(
    business_id,
    sender,
    memory
)

    print(
        "New memory saved:",
        memory
    )

    return memory
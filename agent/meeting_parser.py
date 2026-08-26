from client import client


def extract_selected_meeting_time(
    message,
    available_slots
):
    """
    Extract the meeting slot selected by the customer
    from a list of available slots.
    """

    slots_text = "\n".join(
        f"{index + 1}. {slot['start']} to {slot['end']}"
        for index, slot in enumerate(available_slots)
    )

    prompt = f"""
You are selecting a meeting slot from a list of available slots.

Customer message:
{message}

Available slots:
{slots_text}

Determine which slot the customer selected.

Return ONLY the slot number.

If the customer did not clearly select one of the
available slots, return:

NONE
"""

    response = client.models.generate_content(
        model="models/gemini-3.5-flash-lite",
        contents=prompt
    )

    result = response.text.strip()

    if result == "NONE":
        return None

    try:
        index = int(result) - 1

        if 0 <= index < len(available_slots):
            return available_slots[index]

    except ValueError:
        pass

    return None
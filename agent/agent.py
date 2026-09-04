from agent.classifier import classify_message
from agent.context import get_customer_context
from agent.responder import generate_response
from agent.tools.issues import create_customer_issue
from agent.tools.notifications import create_owner_notification
from agent.tools.leads import (
    create_customer_lead,
    get_customer_lead_by_sender,
    update_customer_lead
)
from agent.tools.meetings import (
    check_meeting_slot,
    find_available_meeting_slots,
    create_pending_meeting,
    create_pending_meeting_from_slot,
    get_pending_customer_meeting,
    confirm_and_book_meeting
)
from agent.tools.meetings import get_pending_customer_meeting
from agent.meeting_parser import extract_selected_meeting_time
from datetime import datetime, timedelta
from client import client
from database import (
    get_customer,
    update_customer,
    create_customer
)
import re


def is_meeting_confirmation(message):
    """
    Detect whether the customer is confirming
    a previously proposed meeting.
    """

    text = message.lower().strip()

    confirmation_phrases = [
        "yes",
        "yes please",
        "book it",
        "book this",
        "schedule it",
        "schedule this",
        "confirm",
        "confirmed",
        "okay book it",
        "go ahead",
        "do it"
    ]

    return any(
        phrase in text
        for phrase in confirmation_phrases
    )

def handle_meeting_selection(
    business_id,
    sender,
    message
):
    """
    Handle a customer selecting one of the meeting
    alternatives previously offered.
    """

    pending = get_pending_customer_meeting(sender)

    if not pending["success"]:
        return None

    # We need the alternatives that were previously offered.
    # For now, retrieve them from the pending meeting context.
    alternatives = pending.get("alternatives", [])

    if not alternatives:
        return None

    selected_slot = extract_selected_meeting_time(
        message,
        alternatives
    )

    if not selected_slot:
        return None

    meeting = create_pending_meeting_from_slot(
    business_id=business_id,
    sender=sender,
    start_time=selected_slot["start"],
    end_time=selected_slot["end"]
)

    return {
        "success": True,
        "meeting": meeting,
        "response": (
            f"{selected_slot['start']} is available. "
            "Would you like me to book it?"
        )
    }

def extract_meeting_datetime(message):
    """
    Extract the requested meeting date and time from the
    customer's message using Gemini.
    """

    prompt = f"""
Extract the meeting date and time from this customer message.

Customer message:
{message}

Today's date is 2026-08-26.

Return ONLY valid JSON in this exact format:

{{
    "date": "YYYY-MM-DD",
    "time": "HH:MM"
}}

Rules:
- Use 24-hour time.
- Convert PM times correctly.
- Resolve relative dates such as tomorrow, Friday, etc.
- If the customer does not provide a clear date or time,
  return:
{{
    "date": null,
    "time": null
}}
"""

    response = client.models.generate_content(
        model="models/gemini-3.5-flash-lite",
        contents=prompt
    )

    result = response.text.strip()

    try:
        import json

        data = json.loads(result)

        if not data.get("date") or not data.get("time"):
            return None

        return datetime.fromisoformat(
            f"{data['date']}T{data['time']}"
        )

    except Exception:
        return None

def process_message(business_id,sender, message):
    """
    Process an incoming customer message through the AI agent.
    """

        # Ensure customer profile exists and update last interaction
    customer = get_customer(
    business_id,
    sender
)

    if not customer:
        create_customer(sender)
    else:
        update_customer(sender)

    # Get customer context
    context = get_customer_context(
    business_id,
    sender
)

        # Check whether the customer selected
    # one of the previously offered alternatives
    pending = get_pending_customer_meeting(
    business_id,
    sender
)

    if pending["success"] and pending.get("alternatives"):

        selected_slot = extract_selected_meeting_time(
            message,
            pending["alternatives"]
        )

        if selected_slot:
            selected_datetime = datetime.fromisoformat(
            selected_slot["start"]
            )

            formatted_time = selected_datetime.strftime("%I:%M %p").lstrip("0")

            formatted_date = selected_datetime.strftime(
                    "%B %d, %Y"
            )

            # Cancel the previous pending proposal
            from database import update_meeting

            update_meeting(
    business_id,
    pending["meeting_id"],
    status="cancelled"
)

            # Store the customer's selected slot
            new_meeting = create_pending_meeting_from_slot(
    business_id=business_id,
    sender=sender,
    start_time=selected_slot["start"],
    end_time=selected_slot["end"]
)

            return {
                "sender": sender,
                "message": message,
                "intent": "meeting_selection",
                "priority": "normal",
                "requires_owner": False,
                "action": "await_confirmation",
                "meeting": new_meeting,
                "response": (
                            f"{formatted_time} on {formatted_date} is available. "
                            "Would you like me to book it?"
                        )
                
            }
        # Check whether the customer is confirming
    # a previously proposed meeting
    if is_meeting_confirmation(message):

        pending_meeting = get_pending_customer_meeting(
    business_id,
    sender
)

        if pending_meeting["success"]:

            booking = confirm_and_book_meeting(
    business_id=business_id,
    sender=sender,
    summary="Meeting with customer",
                description=(
                    f"Meeting booked through WhatsApp "
                    f"for customer {sender}"
                )
            )

            if booking["success"]:

                return {
                    "sender": sender,
                    "message": message,
                    "intent": "meeting_confirmation",
                    "priority": "normal",
                    "requires_owner": True,
                    "action": "book_meeting",
                    "meeting": booking,
                    "response": (
                        "Your meeting has been confirmed "
                        "and added to the calendar."
                    )
                }

            return {
                "sender": sender,
                "message": message,
                "intent": "meeting_confirmation",
                "priority": "high",
                "requires_owner": True,
                "action": "meeting_booking_failed",
                "meeting": booking,
                "response": (
                    "I'm sorry, but that time is no longer "
                    "available. Let me check for another slot."
                )
            }
        

    # Classify message
    classification = classify_message(message)

    intent = classification["intent"]
    priority = classification["priority"]
    requires_owner = classification["requires_owner"]

    action = None
    issue = None
    lead = None
    owner_notification = None

    # Decide action
    if intent == "customer_support":
        action = "answer_customer"

    elif intent == "meeting_request":

        action = "check_calendar"

        requested_datetime = extract_meeting_datetime(
            message
        )

        if not requested_datetime:

            return {
                "sender": sender,
                "message": message,
                "intent": intent,
                "priority": priority,
                "requires_owner": False,
                "action": "request_meeting_time",
                "response": (
                    "Sure. What date and time would you "
                    "like to schedule the meeting?"
                )
            }

        start_time = requested_datetime.isoformat()

        end_datetime = (
            requested_datetime
            + timedelta(minutes=30)
        )

        end_time = end_datetime.isoformat()

        meeting_check = check_meeting_slot(
            start_time=start_time,
            duration_minutes=30
        )

        if meeting_check["available"]:

            pending_meeting = create_pending_meeting(
    business_id=business_id,
    sender=sender,
    start_time=start_time,
    end_time=end_time
)

            formatted_time = requested_datetime.strftime(
                "%I:%M %p"
            ).lstrip("0")

            formatted_date = requested_datetime.strftime(
                "%B %d, %Y"
            )

            return {
                "sender": sender,
                "message": message,
                "intent": intent,
                "priority": priority,
                "requires_owner": False,
                "action": "await_confirmation",
                "meeting": pending_meeting,
                "response": (
                    f"{formatted_time} on {formatted_date} "
                    "is available. Would you like me to book it?"
                )
            }

        alternatives = find_available_meeting_slots(
    start_time=start_time,
    duration_minutes=30
)

        available_slots = alternatives["available_slots"]

        if not available_slots:
            return {
                "sender": sender,
                "message": message,
                "intent": intent,
                "priority": priority,
                "requires_owner": False,
                "action": "no_available_slots",
                "response": (
                    "I'm sorry, but I couldn't find an available "
                    "meeting slot around that time."
                )
            }

        pending_meeting = create_pending_meeting(
    business_id=business_id,
    sender=sender,
    start_time=start_time,
    end_time=end_time,
    alternative_slots=available_slots
)

        formatted_date = requested_datetime.strftime(
            "%B %d, %Y"
        )

        formatted_time = requested_datetime.strftime(
            "%I:%M %p"
        ).lstrip("0")

        alternative_text = ", ".join(
            datetime.fromisoformat(
                slot["start"]
            ).strftime("%I:%M %p").lstrip("0")
            for slot in available_slots
        )

        return {
            "sender": sender,
            "message": message,
            "intent": intent,
            "priority": priority,
            "requires_owner": False,
            "action": "offer_alternatives",
            "meeting": pending_meeting,
            "response": (
                f"{formatted_time} on {formatted_date} isn't available. "
                f"I can offer {alternative_text}. "
                "Which time works for you?"
            )
        }

    elif intent == "complaint":

        action = "create_issue"

        issue = create_customer_issue(
    business_id=business_id,
    sender=sender,
    description=message,
    priority=priority
)

        requires_owner = True

        owner_notification = create_owner_notification(
            sender=sender,
            message=message,
            intent=intent,
            priority=priority,
            issue_id=issue["issue_id"]
        )
        

    elif intent == "lead":

        existing_lead = get_customer_lead_by_sender(
    business_id,
    sender
)

        # Determine lead status from the customer's message
        message_lower = message.lower()

                # Capture customer email if provided
        email_match = re.search(
            r'[\w\.-]+@[\w\.-]+\.\w+',
            message
        )

        email = email_match.group(0) if email_match else None

        # Capture customer name from common introductions
        name = None

        name_match = re.search(
            r"(?:i am|i'm|my name is)\s+([A-Za-z]+(?:\s+[A-Za-z]+){0,2})",
            message,
            re.IGNORECASE
        )

        if name_match:
            name = name_match.group(1).strip()

            # Update CRM profile
        if name or email:

            customer = get_customer(sender)

            if not customer:
                create_customer(
    business_id=business_id,
    sender=sender,
    name=name,
    email=email
)

            else:
                update_customer(
    business_id=business_id,
    sender=sender,
    name=name,
    email=email
)

        if any(word in message_lower for word in [
            "demo",
            "demonstration",
            "show me",
            "see the chatbot"
        ]):
            lead_status = "demo_requested"

        elif any(word in message_lower for word in [
            "need",
            "require",
            "looking for",
            "want to build",
            "want to develop"
        ]):
            lead_status = "qualified"

        else:
            lead_status = "contacted"

        # Existing lead → update it
        if existing_lead["success"]:

            action = "update_lead"

            lead = update_customer_lead(
    business_id=business_id,
    lead_id=existing_lead["lead_id"],
    status=lead_status,
    priority=priority,
    requirement=message
)

        # New customer → create lead
        else:

            action = "create_lead"

            lead = create_customer_lead(
    business_id=business_id,
    sender=sender,
    requirement=message,
    priority=priority
)

            # Update status if needed
            if lead_status != "new":

                lead = update_customer_lead(
    business_id=business_id,
    lead_id=lead["lead_id"],
    status=lead_status
)

    elif intent == "payment":
        action = "handle_payment"

    elif intent == "order":
        action = "handle_order"

    elif intent == "general":
        action = "answer_general"

    # Generate customer response
    response = generate_response(
        message=message,
        classification=classification,
        conversation_history=context["conversation_history"],
        memories=context["memories"]
    )

    return {
        "sender": sender,
        "message": message,
        "intent": intent,
        "priority": priority,
        "requires_owner": requires_owner,
        "owner_notification": owner_notification,
        "action": action,
        "issue": issue,
        "lead": lead,
        "response": response
    }
from datetime import datetime, timedelta

from google_calendar import (
                            check_availability,
                            create_calendar_event
                             
                             )
from database import (
    create_meeting_request,
    get_pending_meeting,
    update_meeting
)
import json


def check_meeting_slot(
    start_time,
    duration_minutes=30
):
    """
    Check whether a requested meeting time is available
    on the owner's Google Calendar.
    """

    start = datetime.fromisoformat(start_time)

    end = start + timedelta(
        minutes=duration_minutes
    )

    result = check_availability(
        start.isoformat(),
        end.isoformat()
    )

    return {
        "success": True,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "available": result["available"],
        "conflicts": result["conflicts"]
    }

def find_available_meeting_slots(
    start_time,
    duration_minutes=30,
    number_of_slots=3,
    search_windows=12
):
    """
    Search forward in 30-minute increments and return
    available meeting slots from the real Google Calendar.
    """

    start = datetime.fromisoformat(start_time)

    available_slots = []

    for _ in range(search_windows):

        result = check_meeting_slot(
            start.isoformat(),
            duration_minutes
        )

        if result["available"]:

            available_slots.append({
                "start": result["start"],
                "end": result["end"]
            })

            if len(available_slots) >= number_of_slots:
                break

        start += timedelta(minutes=30)

    return {
        "success": True,
        "requested_start": start_time,
        "duration_minutes": duration_minutes,
        "available_slots": available_slots
    }

def book_meeting(
    summary,
    start_time,
    end_time,
    description=None,
    attendee_email=None
):
    """
    Create a confirmed meeting in Google Calendar.
    """

    # Safety check before booking
    availability = check_availability(
        start_time,
        end_time
    )

    if not availability["available"]:

        return {
            "success": False,
            "error": "Time slot is no longer available",
            "conflicts": availability["conflicts"]
        }

    return create_calendar_event(
        summary=summary,
        start_time=start_time,
        end_time=end_time,
        description=description,
        attendee_email=attendee_email
    )

def create_pending_meeting(
    sender,
    start_time,
    end_time,
    alternative_slots= None
):
    """
    Store a meeting proposal that is waiting
    for customer confirmation.
    """

    start = datetime.fromisoformat(start_time)
    end = datetime.fromisoformat(end_time)

    meeting = create_meeting_request(
    sender=sender,
    requested_start=start,
    requested_end=end,
    alternative_slots=json.dumps(
        alternative_slots or []
    )
)

    return {
        "success": True,
        "meeting_id": meeting.id,
        "status": meeting.status,
        "start": meeting.requested_start.isoformat(),
        "end": meeting.requested_end.isoformat(),
        "alternatives": alternative_slots or []
    }


def get_pending_customer_meeting(sender):
    """
    Get the latest meeting waiting for confirmation,
    including its alternative slots.
    """

    import json

    meeting = get_pending_meeting(sender)

    if not meeting:
        return {
            "success": False,
            "error": "No pending meeting"
        }

    alternatives = []

    if meeting.alternative_slots:
        try:
            alternatives = json.loads(
                meeting.alternative_slots
            )
        except json.JSONDecodeError:
            alternatives = []

    return {
        "success": True,
        "meeting_id": meeting.id,
        "status": meeting.status,
        "start": meeting.requested_start.isoformat(),
        "end": meeting.requested_end.isoformat(),
        "alternatives": alternatives
    }

def create_pending_meeting_from_slot(
    sender,
    start_time,
    end_time
):
    """
    Store a customer-selected alternative meeting slot
    as awaiting confirmation.
    """

    return create_pending_meeting(
        sender=sender,
        start_time=start_time,
        end_time=end_time
    )


def confirm_meeting(
    meeting_id,
    calendar_event_id
):
    """
    Mark a meeting as booked after the calendar
    event has been successfully created.
    """

    meeting = update_meeting(
        meeting_id,
        status="booked",
        calendar_event_id=calendar_event_id
    )

    if not meeting:

        return {
            "success": False,
            "error": "Meeting not found"
        }

    return {
        "success": True,
        "meeting_id": meeting.id,
        "status": meeting.status,
        "calendar_event_id": meeting.calendar_event_id
    }

def confirm_and_book_meeting(
    sender,
    summary,
    description=None,
    attendee_email=None
):
    """
    Confirm the customer's pending meeting and book it
    only if the requested slot is still available.
    """

    meeting = get_pending_meeting(sender)

    if not meeting:
        return {
            "success": False,
            "error": "No pending meeting"
        }

    start_time = meeting.requested_start.isoformat()
    end_time = meeting.requested_end.isoformat()

    # Re-check calendar immediately before booking
    availability = check_availability(
        start_time,
        end_time
    )

    if not availability["available"]:

        return {
            "success": False,
            "error": "Meeting slot is no longer available",
            "conflicts": availability["conflicts"]
        }

    # Create Google Calendar event
    calendar_result = create_calendar_event(
        summary=summary,
        start_time=start_time,
        end_time=end_time,
        description=description,
        attendee_email=attendee_email
    )

    if not calendar_result["success"]:

        return calendar_result

    # Mark meeting as booked
    updated_meeting = update_meeting(
        meeting.id,
        status="booked",
        calendar_event_id=calendar_result["event_id"]
    )

    return {
        "success": True,
        "meeting_id": updated_meeting.id,
        "status": updated_meeting.status,
        "calendar_event_id": calendar_result["event_id"],
        "start": start_time,
        "end": end_time,
        "calendar_link": calendar_result.get("html_link")
    }
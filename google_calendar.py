import os
from datetime import datetime, timezone, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]


def get_calendar_service():

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:

            creds.refresh(Request())

        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(
                port=0
            )

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build(
        "calendar",
        "v3",
        credentials=creds
    )

    return service

def get_upcoming_events(days=7):

    service = get_calendar_service()

    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    end_time = now + timedelta(days=days)

    events_result = service.events().list(
        calendarId="primary",
        timeMin=now.isoformat(),
        timeMax=end_time.isoformat(),
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])

    results = []

    for event in events:

        start = event.get("start", {})
        end = event.get("end", {})

        results.append({
            "id": event.get("id"),
            "summary": event.get(
                "summary",
                "No title"
            ),
            "start": start.get(
                "dateTime",
                start.get("date")
            ),
            "end": end.get(
                "dateTime",
                end.get("date")
            )
        })

    return results

def normalize_datetime(value):
    """
    Convert a datetime or ISO string into UTC RFC3339 format.
    """

    if isinstance(value, str):
        value = datetime.fromisoformat(value)

    if value.tzinfo is None:
        india_timezone = timezone(
            timedelta(hours=5, minutes=30)
        )

        value = value.replace(
            tzinfo=india_timezone
        )

    value = value.astimezone(timezone.utc)

    return value.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

def check_availability(
    start_time,
    end_time
):
    """
    Check whether a time range is available
    on the primary Google Calendar.
    """

    service = get_calendar_service()

    start_time = normalize_datetime(start_time)
    end_time = normalize_datetime(end_time)

    print("Checking calendar:")
    print("START:", start_time)
    print("END:", end_time)

    events_result = service.events().list(
        calendarId="primary",
        timeMin=start_time,
        timeMax=end_time,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get(
        "items",
        []
    )

    conflicts = []

    for event in events:

        start = event.get("start", {})
        end = event.get("end", {})

        conflicts.append({
            "id": event.get("id"),
            "summary": event.get(
                "summary",
                "No title"
            ),
            "start": start.get(
                "dateTime",
                start.get("date")
            ),
            "end": end.get(
                "dateTime",
                end.get("date")
            )
        })

    return {
        "available": len(conflicts) == 0,
        "conflicts": conflicts
    }

def create_calendar_event(
    summary,
    start_time,
    end_time,
    description=None,
    attendee_email=None
):
    """
    Create a calendar event on the owner's primary
    Google Calendar.
    """

    service = get_calendar_service()

    event = {
        "summary": summary,
        "description": description or "",
        "start": {
            "dateTime": start_time,
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "Asia/Kolkata"
        }
    }

    if attendee_email:
        event["attendees"] = [
            {
                "email": attendee_email
            }
        ]

    created_event = service.events().insert(
        calendarId="primary",
        body=event,
        sendUpdates="all"
    ).execute()

    return {
        "success": True,
        "event_id": created_event.get("id"),
        "summary": created_event.get("summary"),
        "start": created_event.get("start", {}).get("dateTime"),
        "end": created_event.get("end", {}).get("dateTime"),
        "html_link": created_event.get("htmlLink")
    }
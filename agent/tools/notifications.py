from database import SessionLocal, Business
from whatsapp import send_whatsapp_message


def create_owner_notification(
    sender,
    message,
    intent,
    priority,
    issue_id=None,
    business_id=1
):
    """
    Send a WhatsApp notification to the correct business owner.
    """

    db = SessionLocal()

    try:
        business = db.query(Business).filter(
            Business.id == business_id
        ).first()

        if not business:
            return {
                "success": False,
                "error": "Business not found"
            }

        owner_phone = business.owner_phone

        if not owner_phone or not owner_phone.isdigit():
            return {
                "success": False,
                "error": "Owner WhatsApp number is not configured correctly"
            }

        notification_message = (
            f"New customer enquiry for {business.name}\n\n"
            f"Customer: {sender}\n"
            f"Intent: {intent}\n"
            f"Priority: {priority}\n"
            f"Message: {message}"
        )

        response = send_whatsapp_message(
            to=owner_phone,
            message=notification_message
        )

        if response.status_code not in (200, 201):
            return {
                "success": False,
                "error": "WhatsApp API rejected the notification",
                "status_code": response.status_code
            }

        return {
            "success": True,
            "status": "accepted_by_whatsapp",
            "message_id": (
                response.json()
                .get("messages", [{}])[0]
                .get("id")
            )
        }

    except Exception as e:
        print(
            f"Owner notification failed: "
            f"{type(e).__name__}: {e}"
        )

        return {
            "success": False,
            "error": "Notification could not be sent"
        }

    finally:
        db.close()
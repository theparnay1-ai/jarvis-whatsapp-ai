def create_owner_notification(
    sender,
    message,
    intent,
    priority,
    issue_id=None
):
    """
    Create a structured notification for the business owner.
    """

    notification = {
        "sender": sender,
        "intent": intent,
        "priority": priority,
        "message": message,
        "issue_id": issue_id
    }

    return {
        "success": True,
        "notification": notification
    }
from database import (
    create_lead,
    get_lead,
    update_lead
)


def create_customer_lead(
    sender,
    requirement,
    priority="normal"
):
    """
    Create a new customer lead.
    """

    lead = create_lead(
        sender,
        requirement,
        priority
    )

    return {
        "success": True,
        "lead_id": lead.id,
        "status": lead.status,
        "priority": lead.priority,
        "requirement": lead.requirement
    }


def get_customer_lead(lead_id):
    """
    Retrieve an existing lead.
    """

    lead = get_lead(lead_id)

    if not lead:
        return {
            "success": False,
            "error": "Lead not found"
        }

    return {
        "success": True,
        "lead_id": lead.id,
        "status": lead.status,
        "priority": lead.priority,
        "requirement": lead.requirement
    }


def update_customer_lead(
    lead_id,
    status=None,
    priority=None
):
    """
    Update an existing lead.
    """

    lead = update_lead(
        lead_id,
        status=status,
        priority=priority
    )

    if not lead:
        return {
            "success": False,
            "error": "Lead not found"
        }

    return {
        "success": True,
        "lead_id": lead.id,
        "status": lead.status,
        "priority": lead.priority,
        "requirement": lead.requirement
    }
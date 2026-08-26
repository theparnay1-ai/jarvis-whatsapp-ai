from database import (
    create_issue,
    get_issue,
    update_issue
)


def create_customer_issue(
    sender,
    description,
    priority="normal"
):
    """
    Create a new customer issue.
    """

    issue = create_issue(
        sender,
        description,
        priority
    )

    return {
        "success": True,
        "issue_id": issue.id,
        "status": issue.status,
        "priority": issue.priority,
        "description": issue.description
    }


def get_customer_issue(issue_id):
    """
    Retrieve an existing customer issue.
    """

    issue = get_issue(issue_id)

    if not issue:

        return {
            "success": False,
            "error": "Issue not found"
        }

    return {
        "success": True,
        "issue_id": issue.id,
        "status": issue.status,
        "priority": issue.priority,
        "description": issue.description
    }


def update_customer_issue(
    issue_id,
    status=None,
    priority=None
):
    """
    Update an existing customer issue.
    """

    issue = update_issue(
        issue_id,
        status=status,
        priority=priority
    )

    if not issue:

        return {
            "success": False,
            "error": "Issue not found"
        }

    return {
        "success": True,
        "issue_id": issue.id,
        "status": issue.status,
        "priority": issue.priority,
        "description": issue.description
    }

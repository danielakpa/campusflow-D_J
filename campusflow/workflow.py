"""Handles staff assignment, ticket status changes, and ticket queues."""


def find_ticket(tickets, ticket_id):
    """Find a ticket by its ID or raise an error if it does not exist."""
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    raise ValueError(f"Ticket {ticket_id} was not found.")


def assign_staff(tickets, ticket_id, staff_name):
    """Assign a staff member to a ticket and start work."""
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name cannot be empty.")

    ticket = find_ticket(tickets, ticket_id)

    if ticket["status"] == "resolved":
        raise ValueError("Reopen the ticket before modifying it.")

    ticket["assigned_to"] = staff_name.strip()
    ticket["status"] = "in_progress"

    return ticket


def update_status(tickets, ticket_id, new_status):
    """Change a ticket's status while enforcing workflow rules."""
    valid_statuses = ["open", "in_progress", "resolved"]

    if not isinstance(new_status, str):
        raise ValueError("Status must be text.")

    new_status = new_status.strip().lower()

    if new_status not in valid_statuses:
        raise ValueError("Status must be open, in_progress, or resolved.")

    ticket = find_ticket(tickets, ticket_id)
    current_status = ticket["status"]

    if current_status == new_status:
        raise ValueError("The ticket already has this status.")

    # A resolved ticket must be reopened before further changes.
    if current_status == "resolved":
        if new_status == "open":
            ticket["status"] = "open"
            return ticket

        raise ValueError("Reopen the ticket before changing its status.")

    # A ticket must have an assigned staff member before work begins.
    if new_status == "in_progress":
        if not ticket["assigned_to"]:
            raise ValueError("Assign a staff member before starting the ticket.")

        if current_status != "open":
            raise ValueError("Only open tickets can start work.")

    # Only tickets currently being worked on can be resolved.
    if new_status == "resolved":
        if current_status != "in_progress":
            raise ValueError("Only in-progress tickets can be resolved.")

    ticket["status"] = new_status

    return ticket


def get_unresolved_queue(tickets):
    """Return open and in-progress tickets in priority order."""
    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    unresolved_tickets = [
        ticket
        for ticket in tickets
        if ticket["status"] in ["open", "in_progress"]
    ]

    # Sort by priority first, then by numeric ticket ID.
    unresolved_tickets.sort(
        key=lambda ticket: (
            priority_order[ticket["priority"]],
            int(ticket["id"][1:]),
        )
    )

    return unresolved_tickets


def get_open_work_queue(tickets):
    """Return only open tickets in priority order."""
    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    # Include only tickets that have not started work.
    open_tickets = [
        ticket
        for ticket in tickets
        if ticket["status"] == "open"
    ]

    # Sort by priority first, then by numeric ticket ID.
    open_tickets.sort(
        key=lambda ticket: (
            priority_order[ticket["priority"]],
            int(ticket["id"][1:]),
        )
    )

    return open_tickets
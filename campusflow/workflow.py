"""Handles staff assignment, ticket status changes, and ticket queues."""

from campusflow.validation import (
    VALID_PRIORITIES,
    VALID_STATUSES,
    validate_staff_name,
)


def find_ticket(tickets, ticket_id):
    """Find a ticket by ID or raise an error if it does not exist."""
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    raise ValueError(f"Ticket {ticket_id} was not found.")


def assign_staff(tickets, ticket_id, staff_name):
    """Assign staff to an open or in-progress ticket."""

    # Validate before changing the ticket.
    staff_name = validate_staff_name(staff_name)
    ticket = find_ticket(tickets, ticket_id)

    if ticket["status"] == "resolved":
        raise ValueError("Reopen the ticket before assigning staff.")

    ticket["assigned_to"] = staff_name

    # Assigning staff to an open ticket starts the work.
    if ticket["status"] == "open":
        ticket["status"] = "in_progress"

    return ticket


def update_status(tickets, ticket_id, new_status):
    """Change a ticket's status while enforcing workflow rules."""

    if not isinstance(new_status, str):
        raise ValueError("Status must be text.")

    new_status = new_status.strip().lower()

    if new_status not in VALID_STATUSES:
        raise ValueError("Status must be open, in_progress, or resolved.")

    ticket = find_ticket(tickets, ticket_id)
    current_status = ticket["status"]

    if current_status == new_status:
        raise ValueError("The ticket already has this status.")

    # Resolved tickets can only be reopened.
    if current_status == "resolved":
        if new_status == "open":
            ticket["status"] = "open"
            return ticket

        raise ValueError("Reopen the ticket before changing its status.")

    # Work can begin only when an open ticket has assigned staff.
    if new_status == "in_progress":
        if current_status != "open":
            raise ValueError("Only open tickets can start work.")

        if not ticket.get("assigned_to"):
            raise ValueError(
                "Assign a staff member before starting the ticket."
            )

    # Only an in-progress ticket can be resolved.
    if new_status == "resolved" and current_status != "in_progress":
        raise ValueError("Only in-progress tickets can be resolved.")

    ticket["status"] = new_status

    return ticket


def _priority_sort_key(ticket):
    """Sort by priority first, then by numeric ticket ID."""

    priority_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    priority = ticket["priority"]

    if priority not in priority_order:
        raise ValueError(f"Invalid ticket priority: {priority}")

    return priority_order[priority], int(ticket["id"][1:])


def get_unresolved_queue(tickets):
    """Return open and in-progress tickets in priority order."""

    unresolved_tickets = [
        ticket
        for ticket in tickets
        if ticket["status"] in ("open", "in_progress")
    ]

    return sorted(unresolved_tickets, key=_priority_sort_key)


def get_open_work_queue(tickets):
    """Return only open tickets in priority order."""

    open_tickets = [
        ticket
        for ticket in tickets
        if ticket["status"] == "open"
    ]

    return sorted(open_tickets, key=_priority_sort_key)
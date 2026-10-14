"""Creates tickets, validates ticket information, and calculates priority."""

# Import our reusable validation functions.
from campusflow.validation import (
    validate_title,
    normalize_category,
    normalize_urgency,
    validate_affected_users,
)


def calculate_priority(urgency, affected_users):
    """Calculate a ticket's priority using the CampusFlow rules."""

    # Critical: high urgency AND at least 10 affected users.
    if urgency == "high" and affected_users >= 10:
        return "critical"

    # High: high urgency OR at least 10 affected users.
    if urgency == "high" or affected_users >= 10:
        return "high"

    # Medium: medium urgency OR at least 3 affected users.
    if urgency == "medium" or affected_users >= 3:
        return "medium"

    # All other valid tickets have low priority.
    return "low"


def validate_ticket(title, category, urgency, affected_users):
    """Validate and standardize ticket information."""

    # Each helper checks one part of the ticket.
    title = validate_title(title)
    category = normalize_category(category)
    urgency = normalize_urgency(urgency)
    affected_users = validate_affected_users(affected_users)

    return title, category, urgency


def generate_ticket_id(tickets):
    """Generate the next ID after the highest existing ticket ID."""

    highest_number = 0

    for ticket in tickets:
        ticket_id = ticket.get("id", "")

        if (
            isinstance(ticket_id, str)
            and ticket_id.startswith("T")
            and ticket_id[1:].isdigit()
        ):
            number = int(ticket_id[1:])

            if number > highest_number:
                highest_number = number

    return f"T{highest_number + 1:03d}"


def create_ticket(tickets, title, category, urgency, affected_users):
    """Validate details and add a new ticket."""

    # Validate everything before changing the collection.
    title, category, urgency = validate_ticket(
        title,
        category,
        urgency,
        affected_users,
    )

    # Calculate the ID and priority only after validation succeeds.
    ticket_id = generate_ticket_id(tickets)
    priority = calculate_priority(urgency, affected_users)

    # Store the ticket and its follow-up notes.
    ticket = {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
        "notes": [],
    }

    # Add the ticket only after all validation succeeds.
    tickets.append(ticket)

    return ticket
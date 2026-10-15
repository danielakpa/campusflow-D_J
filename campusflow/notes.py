"""Add and retrieve notes attached to CampusFlow tickets."""

from campusflow.validation import (
    validate_note_author,
    validate_note_message,
)
from campusflow.workflow import find_ticket


def generate_note_id(notes):
    """Generate the next note ID, such as N001 or N002."""

    highest_number = 0

    for note in notes:
        note_id = note.get("note_id", "")

        if (
            isinstance(note_id, str)
            and note_id.startswith("N")
            and note_id[1:].isdigit()
        ):
            number = int(note_id[1:])
            highest_number = max(highest_number, number)

    return f"N{highest_number + 1:03d}"


def add_note(tickets, ticket_id, author, message):
    """Add a note to an open or in-progress ticket."""

    # Validate all user input before modifying the ticket.
    author = validate_note_author(author)
    message = validate_note_message(message)

    ticket = find_ticket(tickets, ticket_id)

    if ticket["status"] == "resolved":
        raise ValueError("Reopen the ticket before adding a note.")

    # Prepare the notes list without changing the ticket yet.
    existing_notes = ticket.get("notes", [])

    if not isinstance(existing_notes, list):
        raise ValueError("Ticket notes must be stored as a list.")

    note_id = generate_note_id(existing_notes)

    note = {
        "note_id": note_id,
        "author": author,
        "message": message,
    }

    # Commit the change only after validation succeeds.
    if "notes" not in ticket:
        ticket["notes"] = []

    ticket["notes"].append(note)

    return note


def get_notes(tickets, ticket_id):
    """Return a ticket's notes in numeric ID order."""

    ticket = find_ticket(tickets, ticket_id)
    notes = ticket.get("notes", [])

    if not isinstance(notes, list):
        raise ValueError("Ticket notes must be stored as a list.")

    return sorted(
        notes,
        key=lambda note: int(note["note_id"][1:]),
    )
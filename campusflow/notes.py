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

            if number > highest_number:
                highest_number = number

    return f"N{highest_number + 1:03d}"


def add_note(tickets, ticket_id, author, message):
    """Add a note to an open or in-progress ticket."""

    # Validate the author's name and note message first.
    author = validate_note_author(author)
    message = validate_note_message(message)

    # Find the ticket before modifying anything.
    ticket = find_ticket(tickets, ticket_id)

    # Resolved tickets cannot receive new notes.
    if ticket["status"] == "resolved":
        raise ValueError("Reopen the ticket before adding a note.")

    # Ensure every ticket has a notes list.
    if "notes" not in ticket:
        ticket["notes"] = []

    # Generate an ID only after validation and status checks.
    note_id = generate_note_id(ticket["notes"])

    note = {
        "note_id": note_id,
        "author": author,
        "message": message,
    }

    ticket["notes"].append(note)

    return note


def get_notes(tickets, ticket_id):
    """Return a ticket's notes in numeric ID order."""

    ticket = find_ticket(tickets, ticket_id)
    notes = ticket.get("notes", [])

    # Sort by the number in N001, N002, and so on.
    return sorted(
        notes,
        key=lambda note: int(note["note_id"][1:]),
    )
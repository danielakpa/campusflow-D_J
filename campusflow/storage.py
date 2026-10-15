"""Save tickets to JSON files and load them safely."""

import json
from pathlib import Path

from campusflow.tickets import calculate_priority
from campusflow.validation import (
    VALID_CATEGORIES,
    VALID_PRIORITIES,
    VALID_STATUSES,
    VALID_URGENCIES,
)


def validate_ticket_data(tickets):
    """Validate ticket fields, IDs, priorities, and notes."""

    if not isinstance(tickets, list):
        raise ValueError("Invalid ticket data: expected a JSON list.")

    errors = []
    seen_ticket_ids = set()

    required_fields = {
        "id": str,
        "title": str,
        "category": str,
        "urgency": str,
        "affected_users": int,
        "priority": str,
        "status": str,
    }

    for index, ticket in enumerate(tickets):
        location = f"Ticket at position {index + 1}"

        if not isinstance(ticket, dict):
            errors.append(f"{location}: Expected a ticket object.")
            continue

        # Check required fields and their data types.
        for field, expected_type in required_fields.items():
            if field not in ticket:
                errors.append(f"{location}: Missing '{field}'.")
                continue

            value = ticket[field]

            # Reject True and False for integer fields.
            if expected_type is int:
                valid_type = type(value) is int
            else:
                valid_type = isinstance(value, expected_type)

            if not valid_type:
                errors.append(
                    f"{location}, '{field}': Expected "
                    f"{expected_type.__name__}, received "
                    f"{type(value).__name__}."
                )

        # Check that the ticket has a valid ID.
        ticket_id = ticket.get("id")

        if isinstance(ticket_id, str):
            if (
                not ticket_id.startswith("T")
                or not ticket_id[1:].isdigit()
            ):
                errors.append(
                    f"{location}: ID must look like T001."
                )
            else:
                numeric_id = int(ticket_id[1:])

                if numeric_id <= 0:
                    errors.append(
                        f"{location}: Ticket ID number must be positive."
                    )
                elif numeric_id in seen_ticket_ids:
                    errors.append(
                        f"{location}: Duplicate ticket ID '{ticket_id}'."
                    )
                else:
                    seen_ticket_ids.add(numeric_id)

        # Title and category cannot be empty.
        for field in ["title", "category"]:
            value = ticket.get(field)

            if isinstance(value, str) and not value.strip():
                errors.append(
                    f"{location}: '{field}' cannot be empty."
                )

        # Custom non-empty categories, such as Electricity, are allowed.

        # Validate urgency.
        urgency = ticket.get("urgency")

        if isinstance(urgency, str) and urgency not in VALID_URGENCIES:
            errors.append(
                f"{location}: Invalid urgency '{urgency}'."
            )

        # Validate priority.
        priority = ticket.get("priority")

        if isinstance(priority, str) and priority not in VALID_PRIORITIES:
            errors.append(
                f"{location}: Invalid priority '{priority}'."
            )

        # Validate status.
        status = ticket.get("status")

        if isinstance(status, str) and status not in VALID_STATUSES:
            errors.append(
                f"{location}: Invalid status '{status}'."
            )

        # Affected users must be a positive whole number.
        affected_users = ticket.get("affected_users")

        if type(affected_users) is int and affected_users <= 0:
            errors.append(
                f"{location}: 'affected_users' must be greater than zero."
            )

        # Check that priority matches urgency and affected users.
        if (
            isinstance(urgency, str)
            and urgency in VALID_URGENCIES
            and type(affected_users) is int
            and affected_users > 0
            and isinstance(priority, str)
            and priority in VALID_PRIORITIES
        ):
            expected_priority = calculate_priority(
                urgency, affected_users
            )

            if priority != expected_priority:
                errors.append(
                    f"{location}: Priority '{priority}' does not match "
                    f"the expected priority '{expected_priority}'."
                )

        # assigned_to must be a non-empty string or None.
        if "assigned_to" not in ticket:
            errors.append(f"{location}: Missing 'assigned_to'.")
        else:
            assigned_to = ticket["assigned_to"]

            if assigned_to is not None and (
                not isinstance(assigned_to, str)
                or not assigned_to.strip()
            ):
                errors.append(
                    f"{location}: 'assigned_to' must be a non-empty "
                    "string or null."
                )

        # Older tickets may not have notes, so treat them as having none.
        notes = ticket.get("notes", [])

        if not isinstance(notes, list):
            errors.append(f"{location}: 'notes' must be a list.")
            continue

        seen_note_ids = set()

        for note_index, note in enumerate(notes):
            note_location = (
                f"{location}, note at position {note_index + 1}"
            )

            if not isinstance(note, dict):
                errors.append(
                    f"{note_location}: Expected a note object."
                )
                continue

            # Every note must have these three fields.
            for field in ["note_id", "author", "message"]:
                if field not in note:
                    errors.append(
                        f"{note_location}: Missing '{field}'."
                    )

            note_id = note.get("note_id")
            author = note.get("author")
            message = note.get("message")

            # Note IDs must look like N001 and be unique per ticket.
            if isinstance(note_id, str):
                if (
                    not note_id.startswith("N")
                    or not note_id[1:].isdigit()
                    or int(note_id[1:]) <= 0
                ):
                    errors.append(
                        f"{note_location}: Invalid note ID '{note_id}'."
                    )
                else:
                    numeric_note_id = int(note_id[1:])

                    if numeric_note_id in seen_note_ids:
                        errors.append(
                            f"{note_location}: Duplicate note ID "
                            f"'{note_id}'."
                        )
                    else:
                        seen_note_ids.add(numeric_note_id)

            # Note authors cannot be blank.
            if isinstance(author, str):
                if not author.strip():
                    errors.append(
                        f"{note_location}: Author cannot be empty."
                    )
            elif author is not None:
                errors.append(
                    f"{note_location}: Author must be text."
                )

            # Note messages must contain 5–300 characters after trimming.
            if isinstance(message, str):
                if not 5 <= len(message.strip()) <= 300:
                    errors.append(
                        f"{note_location}: Message must contain "
                        "5 to 300 characters."
                    )
            elif message is not None:
                errors.append(
                    f"{note_location}: Message must be text."
                )

    if errors:
        raise ValueError(
            "Ticket data validation failed:\n- "
            + "\n- ".join(errors)
        )

    return True


def save_tickets(tickets, file_path):
    """Validate tickets and save them to a JSON file."""

    # Never save invalid ticket data.
    validate_ticket_data(tickets)

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write to a temporary file first.
    temporary_path = path.with_name(path.name + ".tmp")

    try:
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(tickets, file, indent=4)

        # Replace the saved file after writing succeeds.
        temporary_path.replace(path)

    finally:
        # Remove a leftover temporary file if writing failed.
        if temporary_path.exists():
            temporary_path.unlink()


def load_tickets(file_path):
    """Load tickets and reject invalid JSON or ticket data."""

    path = Path(file_path)

    # A missing file means there are no saved tickets yet.
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        content = file.read()

    # An empty file represents an empty ticket list.
    if not content.strip():
        return []

    try:
        tickets = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Cannot load tickets: {path} contains invalid JSON."
        ) from error

    # Reject invalid data without modifying the loaded collection.
    validate_ticket_data(tickets)

    # Return the saved data without adding or changing fields.
    return tickets
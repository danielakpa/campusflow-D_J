"""Validation helpers for CampusFlow Next."""

# Only these categories are allowed.
VALID_CATEGORIES = {"Network", "Hardware", "Software", "Other"}

# Only these urgency levels are allowed.
VALID_URGENCIES = {"low", "medium", "high"}

VALID_STATUSES = {"open", "in_progress", "resolved"}
VALID_PRIORITIES = {"critical", "high", "medium", "low"}


def validate_title(title):
    """Check that a ticket title is not empty."""
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Ticket title cannot be empty.")

    return title.strip()


def normalize_category(category):
    """Accept standard categories or a non-empty custom category."""

    if not isinstance(category, str):
        raise ValueError("Category must be text.")

    cleaned = category.strip()

    if not cleaned:
        raise ValueError("Category cannot be empty.")

    # Standard categories keep their official capitalization.
    for valid_category in VALID_CATEGORIES:
        if cleaned.casefold() == valid_category.casefold():
            return valid_category

    # Accept custom categories such as Electricity or Maintenance.
    return cleaned

def normalize_urgency(urgency):
    """Validate urgency and return it in lowercase."""
    if not isinstance(urgency, str):
        raise ValueError("Urgency must be text.")

    cleaned = urgency.strip().lower()

    if cleaned not in VALID_URGENCIES:
        raise ValueError("Urgency must be low, medium, or high.")

    return cleaned


def validate_affected_users(affected_users):
    """Require a positive integer, rejecting booleans too."""
    if isinstance(affected_users, bool) or not isinstance(
        affected_users, int
    ):
        raise ValueError("Affected users must be a whole number.")

    if affected_users <= 0:
        raise ValueError("Affected users must be greater than zero.")

    return affected_users


def validate_staff_name(staff_name):
    """Require a nonempty staff name."""
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name cannot be empty.")

    return staff_name.strip()


def validate_note_author(author):
    """Require a nonempty note author."""
    if not isinstance(author, str) or not author.strip():
        raise ValueError("Note author cannot be empty.")

    return author.strip()


def validate_note_message(message):
    """Require a note containing 5–300 characters after trimming."""
    if not isinstance(message, str):
        raise ValueError("Note message must be text.")

    cleaned = message.strip()

    if not 5 <= len(cleaned) <= 300:
        raise ValueError(
            "Note message must contain 5 to 300 characters."
        )

    return cleaned
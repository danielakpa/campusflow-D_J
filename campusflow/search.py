"""Search tickets using a title and optional filters."""

from campusflow.validation import (
    VALID_PRIORITIES,
    VALID_STATUSES,
    normalize_category,
)


def search_tickets(
    tickets,
    title="",
    category="",
    status="",
    priority="",
    sort_by_priority=False,
):
    """Return tickets matching every supplied search filter."""

    # Validate the title search.
    if not isinstance(title, str):
        raise ValueError("Title search must be text.")

    title = title.strip().casefold()

    # All filters must be text.
    if not all(
        isinstance(value, str)
        for value in (category, status, priority)
    ):
        raise ValueError("Search filters must be text.")

    category = category.strip()
    status = status.strip().lower()
    priority = priority.strip().lower()

    # Normalize standard categories and accept custom categories.
    if category:
        category = normalize_category(category).casefold()

    # Validate status and priority.
    if status and status not in VALID_STATUSES:
        raise ValueError(
            "Status must be open, in_progress, or resolved."
        )

    if priority and priority not in VALID_PRIORITIES:
        raise ValueError(
            "Priority must be critical, high, medium, or low."
        )

    results = []

    # Every supplied filter must match.
    for ticket in tickets:
        if title and title not in ticket["title"].casefold():
            continue

        if (
            category
            and ticket["category"].strip().casefold() != category
        ):
            continue

        if status and ticket["status"] != status:
            continue

        if priority and ticket["priority"] != priority:
            continue

        results.append(ticket)

    # Optional sorting: highest priority first, then lowest ticket ID.
    if sort_by_priority:
        priority_order = {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 3,
        }

        results.sort(
            key=lambda ticket: (
                priority_order[ticket["priority"]],
                int(ticket["id"][1:]),
            )
        )

    return results
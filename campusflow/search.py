"""Search tickets using a title and optional filters."""


def search_tickets(
    tickets,
    title="",
    category="",
    status="",
    priority="",
    sort_by_priority=False,
):
    """Return tickets matching every supplied search filter."""

    # Define the valid filter options.
    valid_categories = {"Network", "Hardware", "Software", "Other"}
    valid_statuses = {"open", "in_progress", "resolved"}
    valid_priorities = {"critical", "high", "medium", "low"}

    # Convert optional filters to clean text.
    title = title.strip().casefold() if isinstance(title, str) else title
    category = category.strip() if isinstance(category, str) else category
    status = status.strip().lower() if isinstance(status, str) else status
    priority = priority.strip().lower() if isinstance(priority, str) else priority

    # Reject invalid filters rather than silently ignoring them.
    if not isinstance(title, str):
        raise ValueError("Title search must be text.")

    if category and category.casefold() not in {
        item.casefold() for item in valid_categories
    }:
        raise ValueError("Invalid category filter.")

    if status and status not in valid_statuses:
        raise ValueError("Invalid status filter.")

    if priority and priority not in valid_priorities:
        raise ValueError("Invalid priority filter.")

    # Find tickets that match ALL supplied filters.
    results = []

    for ticket in tickets:
        # A blank title means no title filtering.
        if title and title not in ticket["title"].casefold():
            continue

        # Category matching ignores capitalization.
        if category and ticket["category"].casefold() != category.casefold():
            continue

        if status and ticket["status"] != status:
            continue

        if priority and ticket["priority"] != priority:
            continue

        results.append(ticket)

    # Optional sorting: priority first, then numeric ticket ID.
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
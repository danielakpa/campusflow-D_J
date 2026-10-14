"""Generate reports about tickets, statuses, priorities, and categories."""


def generate_report(tickets):
    """Summarize ticket totals, current status, priority, and category."""

    # Count tickets by their current status.
    status_counts = {
        "open": 0,
        "in_progress": 0,
        "resolved": 0,
    }

    # Count tickets by priority.
    priority_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    # Count tickets by category.
    category_counts = {
        "Network": 0,
        "Hardware": 0,
        "Software": 0,
        "Other": 0,
    }

    # Examine every ticket and update the counts.
    for ticket in tickets:
        status_counts[ticket["status"]] += 1
        priority_counts[ticket["priority"]] += 1
        category_counts[ticket["category"]] += 1

    # Unresolved tickets are open or currently being worked on.
    unresolved = status_counts["open"] + status_counts["in_progress"]

    # Calculate the percentage of tickets that are resolved.
    total = len(tickets)

    if total == 0:
        resolution_percentage = 0.0
    else:
        resolution_percentage = round(
            (status_counts["resolved"] / total) * 100,
            2,
        )

    # Return all report information together.
    return {
        "total": total,
        "by_status": status_counts,
        "by_priority": priority_counts,
        "by_category": category_counts,
        "unresolved": unresolved,
        "resolved": status_counts["resolved"],
        "resolution_percentage": resolution_percentage,
    }
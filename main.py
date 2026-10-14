"""Main entry point for the CampusFlow helpdesk application."""

import json
from pathlib import Path

from campusflow.tickets import create_ticket
from campusflow.workflow import (
    assign_staff,
    find_ticket,
    get_unresolved_queue,
    get_open_work_queue,
    update_status,
)
from campusflow.search import search_tickets
from campusflow.reports import generate_report
from campusflow.notes import add_note, get_notes
from campusflow.understanding_check import run_quiz
from campusflow.storage import load_tickets, save_tickets


# Store tickets in the data folder inside the project.
DATA_FILE = Path(__file__).parent / "data" / "tickets.json"


def display_ticket(ticket):
    """Display the important information about one ticket."""

    print("-" * 45)
    print(f"Ticket ID:      {ticket['id']}")
    print(f"Title:          {ticket['title']}")
    print(f"Category:       {ticket['category']}")
    print(f"Urgency:        {ticket['urgency']}")
    print(f"Affected users: {ticket['affected_users']}")
    print(f"Priority:       {ticket['priority']}")
    print(f"Status:         {ticket['status']}")
    print(f"Assigned to:    {ticket.get('assigned_to') or 'Not assigned'}")
    print(f"Notes:          {len(ticket.get('notes', []))}")
    print("-" * 45)


def create_new_ticket(tickets):
    """Create a ticket after collecting and validating user input."""

    title = input("\nEnter ticket title: ").strip()

    category_options = {
        "1": "Network",
        "2": "Hardware",
        "3": "Software",
        "4": "Other",
    }

    print("\nChoose a category:")
    print("1. Network")
    print("2. Hardware")
    print("3. Software")
    print("4. Other")

    category_choice = input("Enter your choice (1-4): ").strip()

    if category_choice not in category_options:
        print("Error: Invalid category.")
        return

    category = category_options[category_choice]

    urgency_options = {
        "1": "low",
        "2": "medium",
        "3": "high",
    }

    print("\nChoose urgency:")
    print("1. Low")
    print("2. Medium")
    print("3. High")

    urgency_choice = input("Enter your choice (1-3): ").strip()

    if urgency_choice not in urgency_options:
        print("Error: Invalid urgency.")
        return

    urgency = urgency_options[urgency_choice]

    affected_users_input = input(
        "\nEnter the number of affected users: "
    ).strip()

    try:
        affected_users = int(affected_users_input)

        ticket = create_ticket(
            tickets,
            title,
            category,
            urgency,
            affected_users,
        )

        save_tickets(tickets, DATA_FILE)

        print(f"\nTicket {ticket['id']} created successfully!")
        display_ticket(ticket)

    except (ValueError, OSError) as error:
        print(f"\nError creating ticket: {error}")


def list_tickets(tickets):
    """Display all tickets."""

    if not tickets:
        print("\nNo tickets found.")
        return

    print("\nALL TICKETS")

    for ticket in tickets:
        display_ticket(ticket)


def assign_ticket_to_staff(tickets):
    """Assign a staff member to a selected ticket."""

    if not tickets:
        print("\nThere are no tickets to assign.")
        return

    list_tickets(tickets)

    ticket_id = input(
        "\nEnter ticket ID to assign (or 0 to cancel): "
    ).strip().upper()

    if ticket_id == "0":
        print("Assignment cancelled.")
        return

    staff_name = input("Enter the staff member's name: ").strip()

    try:
        ticket = assign_staff(tickets, ticket_id, staff_name)
        save_tickets(tickets, DATA_FILE)

        print(
            f"\nTicket {ticket['id']} assigned to "
            f"{ticket['assigned_to']}."
        )

    except (ValueError, OSError) as error:
        print(f"\nError assigning staff: {error}")


def change_ticket_status(tickets):
    """Allow a user to update a ticket's status."""

    if not tickets:
        print("\nThere are no tickets to update.")
        return

    list_tickets(tickets)

    ticket_id = input(
        "\nEnter ticket ID to update (or 0 to cancel): "
    ).strip().upper()

    if ticket_id == "0":
        print("Status update cancelled.")
        return

    try:
        ticket = find_ticket(tickets, ticket_id)

        print("\nAvailable status options:")
        print("1. open")
        print("2. in_progress")
        print("3. resolved")

        status_options = {
            "1": "open",
            "2": "in_progress",
            "3": "resolved",
        }

        choice = input("Choose a status (1-3): ").strip()

        if choice not in status_options:
            print("Invalid status choice.")
            return

        ticket = update_status(
            tickets,
            ticket_id,
            status_options[choice],
        )

        save_tickets(tickets, DATA_FILE)

        print(
            f"\nTicket {ticket['id']} status changed to "
            f"{ticket['status']}."
        )

    except (ValueError, OSError) as error:
        print(f"\nError updating status: {error}")


def show_unresolved_queue(tickets):
    """Display open and in-progress tickets by priority."""

    queue = get_unresolved_queue(tickets)

    if not queue:
        print("\nThere are no unresolved tickets.")
        return

    print("\nUNRESOLVED TICKET QUEUE")

    for ticket in queue:
        display_ticket(ticket)


def show_open_work_queue(tickets):
    """Display only tickets that have not started work."""

    queue = get_open_work_queue(tickets)

    if not queue:
        print("\nThere are no open tickets waiting for work.")
        return

    print("\nOPEN WORK QUEUE")
    print("Tickets are ordered by priority.")

    for ticket in queue:
        display_ticket(ticket)


def search_and_filter_tickets(tickets):
    """Search tickets using a title and optional filters."""

    if not tickets:
        print("\nThere are no tickets to search.")
        return

    print("\nSEARCH AND FILTER TICKETS")
    print("Leave a filter blank to ignore it.")

    title = input("Title contains: ").strip()
    category = input(
        "Category (Network/Hardware/Software/Other): "
    ).strip()
    status = input(
        "Status (open/in_progress/resolved): "
    ).strip()
    priority = input(
        "Priority (critical/high/medium/low): "
    ).strip()

    sort_choice = input(
        "Sort by priority? (y/n): "
    ).strip().lower()

    try:
        results = search_tickets(
            tickets,
            title=title,
            category=category,
            status=status,
            priority=priority,
            sort_by_priority=(sort_choice == "y"),
        )

        if not results:
            print("\nNo tickets matched your search.")
            return

        print(f"\nFound {len(results)} matching ticket(s).")

        for ticket in results:
            display_ticket(ticket)

    except ValueError as error:
        print(f"\nSearch error: {error}")


def show_reports(tickets):
    """Display ticket totals and breakdowns."""

    report = generate_report(tickets)

    print("\n========== CAMPUSFLOW REPORT ==========")
    print(f"Total tickets: {report['total']}")
    print(f"Unresolved tickets: {report['unresolved']}")
    print(f"Resolved tickets: {report['resolved']}")
    print(
        f"Resolution percentage: "
        f"{report['resolution_percentage']}%"
    )

    print("\nTickets by status:")

    for status, count in report["by_status"].items():
        print(f"  {status}: {count}")

    print("\nTickets by priority:")

    for priority, count in report["by_priority"].items():
        print(f"  {priority}: {count}")

    print("\nTickets by category:")

    for category, count in report["by_category"].items():
        print(f"  {category}: {count}")

    print("=" * 40)


def add_ticket_note(tickets):
    """Add a note to an open or in-progress ticket."""

    if not tickets:
        print("\nThere are no tickets to add notes to.")
        return

    list_tickets(tickets)

    ticket_id = input(
        "\nEnter ticket ID for the note (or 0 to cancel): "
    ).strip().upper()

    if ticket_id == "0":
        print("Adding note cancelled.")
        return

    author = input("Enter your name: ").strip()
    message = input("Enter your note (5-300 characters): ").strip()

    try:
        note = add_note(
            tickets,
            ticket_id,
            author,
            message,
        )

        save_tickets(tickets, DATA_FILE)

        print(f"\nNote {note['note_id']} added successfully.")

    except (ValueError, OSError) as error:
        print(f"\nError adding note: {error}")


def show_ticket_notes(tickets):
    """Display all notes attached to a selected ticket."""

    if not tickets:
        print("\nThere are no tickets.")
        return

    list_tickets(tickets)

    ticket_id = input(
        "\nEnter ticket ID to view notes (or 0 to cancel): "
    ).strip().upper()

    if ticket_id == "0":
        print("Viewing notes cancelled.")
        return

    try:
        notes = get_notes(tickets, ticket_id)

        if not notes:
            print(f"\nTicket {ticket_id} has no notes.")
            return

        print(f"\nNOTES FOR TICKET {ticket_id}")

        for note in notes:
            print("-" * 40)
            print(f"Note ID: {note['note_id']}")
            print(f"Author:  {note['author']}")
            print(f"Message: {note['message']}")

        print("-" * 40)

    except ValueError as error:
        print(f"\nError viewing notes: {error}")


def take_understanding_check():
    """Run the CampusFlow understanding quiz."""

    score = run_quiz()

    print(f"\nYou scored {score}/6.")

    if score == 6:
        print("Excellent work! You answered every question correctly.")
    elif score >= 4:
        print("Good work! Review the questions you missed.")
    else:
        print("Keep practising. Review the project and try again.")


def show_menu():
    """Display the main menu."""

    print("\n========== CAMPUSFLOW ==========")
    print("1. Create a ticket")
    print("2. List all tickets")
    print("3. Assign staff")
    print("4. Update ticket status")
    print("5. View unresolved queue")
    print("6. View open-work queue")
    print("7. Search and filter tickets")
    print("8. View reports")
    print("9. Add a ticket note")
    print("10. View ticket notes")
    print("11. Take the Understanding Check")
    print("12. Exit")
    print("================================")


def load_tickets_for_application():
    """Load saved tickets safely when the application starts."""

    try:
        return load_tickets(DATA_FILE)

    except (ValueError, OSError) as error:
        print(f"\nCould not load saved tickets: {error}")
        print("Please check the saved ticket file before continuing.")
        return None


def main():
    """Load tickets and run the application menu."""

    try:
        tickets = load_tickets_for_application()

    except OSError as error:
        print(f"Could not access saved tickets: {error}")
        return

    if tickets is None:
        return

    print("Welcome to CampusFlow!")

    while True:
        show_menu()

        choice = input("Choose an option (1-12): ").strip()

        try:
            if choice == "1":
                create_new_ticket(tickets)

            elif choice == "2":
                list_tickets(tickets)

            elif choice == "3":
                assign_ticket_to_staff(tickets)

            elif choice == "4":
                change_ticket_status(tickets)

            elif choice == "5":
                show_unresolved_queue(tickets)

            elif choice == "6":
                show_open_work_queue(tickets)

            elif choice == "7":
                search_and_filter_tickets(tickets)

            elif choice == "8":
                show_reports(tickets)

            elif choice == "9":
                add_ticket_note(tickets)

            elif choice == "10":
                show_ticket_notes(tickets)

            elif choice == "11":
                take_understanding_check()

            elif choice == "12":
                print("Thank you for using CampusFlow!")
                break

            else:
                print("Invalid choice. Enter a number from 1 to 12.")

        except (ValueError, OSError) as error:
            print(f"\nError: {error}")


if __name__ == "__main__":
    main()
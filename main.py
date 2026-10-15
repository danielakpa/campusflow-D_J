"""Main entry point for the CampusFlow helpdesk application."""

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


def ask_text(prompt, allow_blank=False):
    """Ask for text again until the user enters an acceptable value."""

    while True:
        value = input(prompt).strip()

        if allow_blank or value:
            return value

        print("Error: This field cannot be empty. Please try again.")


def ask_choice(prompt, options):
    """Ask until the user enters one of the available choices."""

    while True:
        choice = input(prompt).strip()

        if choice in options:
            return choice

        print(
            f"Error: Invalid choice. "
            f"Choose from {', '.join(options.keys())}."
        )


def ask_ticket_id(prompt):
    """Ask for an existing ticket ID, allowing 0 to cancel."""

    while True:
        ticket_id = input(prompt).strip().upper()

        if ticket_id == "0":
            return None

        try:
            find_ticket(current_tickets, ticket_id)
            return ticket_id
        except ValueError:
            print("Error: Ticket not found. Enter a valid ticket ID or 0 to cancel.")


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
    """Create a ticket, retrying invalid input."""

    category_options = {
        "1": "Network",
        "2": "Hardware",
        "3": "Software",
        "4": "Other",
    }

    urgency_options = {
        "1": "low",
        "2": "medium",
        "3": "high",
    }

    while True:
        title = ask_text("\nEnter ticket title (or 0 to cancel): ")

        if title == "0":
            print("Ticket creation cancelled.")
            return

        print("\nChoose a category:")
        print("1. Network")
        print("2. Hardware")
        print("3. Software")
        print("4. Other")

        category_choice = ask_choice(
            "Enter your choice (1-4): ",
            category_options,
        )

        category = category_options[category_choice]

        # If the user selects Other, ask for a custom category.
        if category == "Other":
            while True:
                custom_category = input(
                    "Enter the specific category: "
                ).strip()

                if custom_category:
                    category = custom_category
                    break

                print("Error: Category cannot be empty. Please try again.")

        print("\nChoose urgency:")
        print("1. Low")
        print("2. Medium")
        print("3. High")

        urgency_choice = ask_choice(
            "Enter your choice (1-3): ",
            urgency_options,
        )

        urgency = urgency_options[urgency_choice]

        # Keep asking until affected_users is a positive integer.
        while True:
            affected_input = input(
                "\nEnter the number of affected users (or 0 to cancel): "
            ).strip()

            if affected_input == "0":
                print("Ticket creation cancelled.")
                return

            try:
                affected_users = int(affected_input)

                if affected_users <= 0:
                    print("Error: The number must be greater than zero.")
                    continue

                break

            except ValueError:
                print("Error: Enter a whole number, such as 5.")

        try:
            ticket = create_ticket(
                tickets,
                title,
                category,
                urgency,
                affected_users,
            )

            # Save before announcing success.
            save_tickets(tickets, DATA_FILE)

            print(f"\nTicket {ticket['id']} created successfully!")
            display_ticket(ticket)
            return

        except ValueError as error:
            print(f"\nError creating ticket: {error}")
            print("Please enter the ticket information again.")

        except OSError as error:
            print(f"\nCould not save the ticket: {error}")
            print("The application will continue running.")
            return

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

    while True:
        ticket_id = input(
            "\nEnter ticket ID to assign (or 0 to cancel): "
        ).strip().upper()

        if ticket_id == "0":
            print("Assignment cancelled.")
            return

        try:
            find_ticket(tickets, ticket_id)
            break
        except ValueError:
            print("Error: Ticket not found. Please try again.")

    while True:
        staff_name = ask_text(
            "Enter the staff member's name (or 0 to cancel): "
        )

        if staff_name == "0":
            print("Assignment cancelled.")
            return

        try:
            ticket = assign_staff(tickets, ticket_id, staff_name)
            save_tickets(tickets, DATA_FILE)

            print(
                f"\nTicket {ticket['id']} assigned to "
                f"{ticket['assigned_to']}."
            )
            return

        except ValueError as error:
            print(f"Error assigning staff: {error}")

            # Do not repeatedly ask for a name if the ticket itself
            # cannot be assigned. Let the user choose another ticket.
            if "resolved" in str(error).lower():
                return

        except OSError as error:
            print(f"Could not save the assignment: {error}")
            return


def change_ticket_status(tickets):
    """Display all tickets, then update or reopen a selected ticket."""

    if not tickets:
        print("\nThere are no tickets to update.")
        return

    # Show every ticket before asking which one to update.
    print("\n========== ALL TICKETS ==========")

    for ticket in tickets:
        display_ticket(ticket)

    # Ask which ticket the user wants to update.
    while True:
        ticket_id = input(
            "\nEnter the ticket ID to update (or 0 to cancel): "
        ).strip().upper()

        if ticket_id == "0":
            print("Status update cancelled.")
            return

        try:
            ticket = find_ticket(tickets, ticket_id)
            break
        except ValueError as error:
            print(f"Error: {error}")
            print("Please enter a valid ticket ID.")

    print(f"\nSelected ticket: {ticket['id']} - {ticket['title']}")
    print(f"Current status: {ticket['status']}")

    # Offer reopening as an explicit menu choice.
    if ticket["status"] == "resolved":
        status_options = {
            "1": "open",
        }

        print("\nChoose an action:")
        print("1. Reopen ticket")
        print("0. Cancel")

        choice = ask_choice(
            "Enter your choice: ",
            {"1": "reopen", "0": "cancel"},
        )

        if choice == "0":
            print("Status update cancelled.")
            return

        new_status = status_options[choice]

    else:
        status_options = {
            "1": "open",
            "2": "in_progress",
            "3": "resolved",
        }

        print("\nChoose the new status:")
        print("1. Open")
        print("2. In progress")
        print("3. Resolved")
        print("0. Cancel")

        status_options["0"] = "cancel"

        choice = ask_choice(
            "Enter your choice: ",
            status_options,
        )

        if choice == "0":
            print("Status update cancelled.")
            return

        new_status = status_options[choice]

    try:
        update_status(tickets, ticket_id, new_status)

        # Save the updated ticket.
        save_tickets(tickets, DATA_FILE)

        print(
            f"\nTicket {ticket_id} status updated to "
            f"{new_status.replace('_', ' ')}."
        )

        display_ticket(ticket)

    except ValueError as error:
        print(f"\nError: {error}")

    except OSError as error:
        print(f"\nCould not save the updated ticket: {error}")

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
    """Search tickets using numbered filter choices."""

    if not tickets:
        print("\nThere are no tickets to search.")
        return

    category_options = {
        "1": "Network",
        "2": "Hardware",
        "3": "Software",
        "4": "Other",
        "5": "",
    }

    status_options = {
        "1": "open",
        "2": "in_progress",
        "3": "resolved",
        "4": "",
    }

    priority_options = {
        "1": "critical",
        "2": "high",
        "3": "medium",
        "4": "low",
        "5": "",
    }

    while True:
        print("\n========== SEARCH TICKETS ==========")
        print("Enter 0 at the title prompt to cancel.")

        title = input("Title contains (or 0 to cancel): ").strip()

        if title == "0":
            print("Search cancelled.")
            return

        print("\nChoose category:")
        print("1. Network")
        print("2. Hardware")
        print("3. Software")
        print("4. Other")
        print("5. Any category")

        category_choice = ask_choice(
            "Enter choice (1-5): ",
            category_options,
        )
        category = category_options[category_choice]

        print("\nChoose status:")
        print("1. Open")
        print("2. In progress")
        print("3. Resolved")
        print("4. Any status")

        status_choice = ask_choice(
            "Enter choice (1-4): ",
            status_options,
        )
        status = status_options[status_choice]

        print("\nChoose priority:")
        print("1. Critical")
        print("2. High")
        print("3. Medium")
        print("4. Low")
        print("5. Any priority")

        priority_choice = ask_choice(
            "Enter choice (1-5): ",
            priority_options,
        )
        priority = priority_options[priority_choice]

        sort_choice = ask_choice(
            "\nSort results by priority? (y/n): ",
            {"y": "yes", "n": "no"},
        )

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

            return

        except ValueError as error:
            print(f"\nSearch error: {error}")
            print("Please try your search again.")


def show_reports(tickets):
    """Display ticket totals and breakdowns."""

    report = generate_report(tickets)

    print("\n========== CAMPUSFLOW REPORT ==========")
    print(f"Total tickets: {report['total']}")
    print(f"Unresolved tickets: {report['unresolved']}")
    print(f"Resolved tickets: {report['resolved']}")
    print(f"Resolution percentage: {report['resolution_percentage']}%")

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

    while True:
        ticket_id = input(
            "\nEnter ticket ID for the note (or 0 to cancel): "
        ).strip().upper()

        if ticket_id == "0":
            print("Adding note cancelled.")
            return

        try:
            find_ticket(tickets, ticket_id)
            break
        except ValueError:
            print("Error: Ticket not found. Please try again.")

    while True:
        author = input("Enter your name (or 0 to cancel): ").strip()

        if author == "0":
            print("Adding note cancelled.")
            return

        message = input(
            "Enter your note (5-300 characters): "
        ).strip()

        if message == "0":
            print("Adding note cancelled.")
            return

        try:
            note = add_note(tickets, ticket_id, author, message)
            save_tickets(tickets, DATA_FILE)

            print(f"\nNote {note['note_id']} added successfully.")
            return

        except ValueError as error:
            print(f"Error adding note: {error}")
            print("Please correct the information and try again.")

        except OSError as error:
            print(f"Could not save the note: {error}")
            return


def show_ticket_notes(tickets):
    """Display all notes attached to a selected ticket."""

    if not tickets:
        print("\nThere are no tickets.")
        return

    list_tickets(tickets)

    while True:
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
            return

        except ValueError as error:
            print(f"Error viewing notes: {error}")
            print("Please enter a valid ticket ID or 0 to cancel.")


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


def main():
    """Load tickets and run the application menu."""

    try:
        tickets = load_tickets(DATA_FILE)

    except (ValueError, OSError) as error:
        print(f"\nCould not load saved tickets: {error}")
        print("The saved data was not loaded.")
        print("Please fix the saved file before starting CampusFlow.")
        return

    print("Welcome to CampusFlow!")

    while True:
        show_menu()

        try:
            choice = input("Choose an option (1-12): ").strip()

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
                print("Error: Enter a number from 1 to 12.")

        except (ValueError, OSError) as error:
            print(f"\nError: {error}")
            print("Please try again.")


if __name__ == "__main__":
    main()
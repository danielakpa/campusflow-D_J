"""Tests for CampusFlow ticket notes."""

import unittest

from campusflow.notes import add_note, get_notes


class TestTicketNotes(unittest.TestCase):

    def setUp(self):
        self.tickets = [
            {
                "id": "T001",
                "title": "Campus WiFi outage",
                "category": "Network",
                "urgency": "high",
                "affected_users": 12,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
                "notes": [],
            }
        ]

    def test_add_note_generates_first_id(self):
        note = add_note(
            self.tickets,
            "T001",
            "Ada",
            "Router needs inspection.",
        )

        self.assertEqual(note["note_id"], "N001")
        self.assertEqual(note["author"], "Ada")

    def test_next_note_gets_next_id(self):
        add_note(self.tickets, "T001", "Ada", "First note here.")
        note = add_note(self.tickets, "T001", "John", "Second note here.")

        self.assertEqual(note["note_id"], "N002")

    def test_note_message_is_trimmed(self):
        note = add_note(
            self.tickets,
            "T001",
            " Ada ",
            "  Check the router now.  ",
        )

        self.assertEqual(note["author"], "Ada")
        self.assertEqual(note["message"], "Check the router now.")

    def test_reject_short_message_without_consuming_id(self):
        with self.assertRaises(ValueError):
            add_note(self.tickets, "T001", "Ada", "Bad")

        note = add_note(
            self.tickets,
            "T001",
            "Ada",
            "This message is valid.",
        )

        self.assertEqual(note["note_id"], "N001")

    def test_resolved_ticket_rejects_note(self):
        self.tickets[0]["status"] = "resolved"

        with self.assertRaises(ValueError):
            add_note(
                self.tickets,
                "T001",
                "Ada",
                "This ticket is already resolved.",
            )

        self.assertEqual(self.tickets[0]["notes"], [])

    def test_reopened_ticket_accepts_note(self):
        self.tickets[0]["status"] = "resolved"

        with self.assertRaises(ValueError):
            add_note(
                self.tickets,
                "T001",
                "Ada",
                "Cannot add this while resolved.",
            )

        self.tickets[0]["status"] = "open"

        note = add_note(
            self.tickets,
            "T001",
            "Ada",
            "The issue has returned.",
        )

        self.assertEqual(note["note_id"], "N001")

    def test_reject_empty_author(self):
        with self.assertRaises(ValueError):
            add_note(
                self.tickets,
                "T001",
                "   ",
                "This message is valid.",
            )

    def test_reject_unknown_ticket(self):
        with self.assertRaises(ValueError):
            add_note(
                self.tickets,
                "T999",
                "Ada",
                "This message is valid.",
            )

    def test_notes_are_returned_in_numeric_order(self):
        self.tickets[0]["notes"] = [
            {
                "note_id": "N010",
                "author": "Ada",
                "message": "Tenth note here.",
            },
            {
                "note_id": "N002",
                "author": "John",
                "message": "Second note here.",
            },
        ]

        notes = get_notes(self.tickets, "T001")

        self.assertEqual(
            [note["note_id"] for note in notes],
            ["N002", "N010"],
        )


if __name__ == "__main__":
    unittest.main()
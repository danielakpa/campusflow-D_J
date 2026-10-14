"""Tests for the open-only work queue."""

import unittest

from campusflow.workflow import get_open_work_queue


class TestOpenWorkQueue(unittest.TestCase):

    def setUp(self):
        self.tickets = [
            {"id": "T003", "priority": "low", "status": "open"},
            {"id": "T010", "priority": "critical", "status": "open"},
            {"id": "T002", "priority": "high", "status": "open"},
            {"id": "T001", "priority": "critical", "status": "open"},
            {
                "id": "T004",
                "priority": "critical",
                "status": "in_progress",
            },
            {"id": "T005", "priority": "critical", "status": "resolved"},
        ]

    def test_only_open_tickets_are_returned(self):
        result = get_open_work_queue(self.tickets)

        self.assertTrue(
            all(ticket["status"] == "open" for ticket in result)
        )

    def test_priority_then_numeric_id_order(self):
        result = get_open_work_queue(self.tickets)

        self.assertEqual(
            [ticket["id"] for ticket in result],
            ["T001", "T010", "T002", "T003"],
        )

    def test_empty_queue(self):
        self.assertEqual(get_open_work_queue([]), [])

    def test_original_tickets_are_not_reordered(self):
        original_ids = [ticket["id"] for ticket in self.tickets]

        get_open_work_queue(self.tickets)

        self.assertEqual(
            [ticket["id"] for ticket in self.tickets],
            original_ids,
        )


if __name__ == "__main__":
    unittest.main()
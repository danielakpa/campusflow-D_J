"""Tests for CampusFlow ticket searching."""

import unittest

from campusflow.search import search_tickets


class TestTicketSearch(unittest.TestCase):

    def setUp(self):
        # Fresh sample tickets for every test.
        self.tickets = [
            {
                "id": "T002",
                "title": "Campus WiFi outage",
                "category": "Network",
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
            },
            {
                "id": "T001",
                "title": "Broken laptop",
                "category": "Hardware",
                "priority": "high",
                "status": "in_progress",
                "assigned_to": "Ada",
            },
            {
                "id": "T003",
                "title": "WiFi password issue",
                "category": "Network",
                "priority": "medium",
                "status": "resolved",
                "assigned_to": "John",
            },
        ]

    def test_title_search_ignores_capitalization(self):
        results = search_tickets(self.tickets, title="WIFI")
        self.assertEqual(len(results), 2)

    def test_category_filter(self):
        results = search_tickets(self.tickets, category="network")
        self.assertEqual(len(results), 2)

    def test_combined_filters_use_and(self):
        results = search_tickets(
            self.tickets,
            title="wifi",
            category="Network",
            status="open",
        )
        self.assertEqual([ticket["id"] for ticket in results], ["T002"])

    def test_no_matches_returns_empty_list(self):
        results = search_tickets(self.tickets, title="printer")
        self.assertEqual(results, [])

    def test_blank_filters_return_all_tickets(self):
        results = search_tickets(self.tickets)
        self.assertEqual(len(results), 3)

    def test_priority_sort_uses_numeric_ticket_id_for_ties(self):
        results = search_tickets(
            self.tickets,
            sort_by_priority=True,
        )
        self.assertEqual(
            [ticket["id"] for ticket in results],
            ["T002", "T001", "T003"],
        )

    def test_invalid_status_filter_is_rejected(self):
        with self.assertRaises(ValueError):
            search_tickets(self.tickets, status="waiting")


if __name__ == "__main__":
    unittest.main()
"""Tests for CampusFlow Next reports."""

import unittest

from campusflow.reports import generate_report


class TestReportsNext(unittest.TestCase):

    def test_empty_report(self):
        report = generate_report([])

        self.assertEqual(report["total"], 0)
        self.assertEqual(report["unresolved"], 0)
        self.assertEqual(report["resolved"], 0)
        self.assertEqual(report["resolution_percentage"], 0.0)

    def test_counts_status_priority_and_category(self):
        tickets = [
            {
                "status": "open",
                "priority": "critical",
                "category": "Network",
            },
            {
                "status": "in_progress",
                "priority": "high",
                "category": "Hardware",
            },
            {
                "status": "resolved",
                "priority": "medium",
                "category": "Software",
            },
            {
                "status": "resolved",
                "priority": "low",
                "category": "Network",
            },
        ]

        report = generate_report(tickets)

        self.assertEqual(report["total"], 4)
        self.assertEqual(report["by_status"]["open"], 1)
        self.assertEqual(report["by_status"]["in_progress"], 1)
        self.assertEqual(report["by_status"]["resolved"], 2)
        self.assertEqual(report["by_priority"]["critical"], 1)
        self.assertEqual(report["by_category"]["Network"], 2)
        self.assertEqual(report["unresolved"], 2)
        self.assertEqual(report["resolved"], 2)
        self.assertEqual(report["resolution_percentage"], 50.0)

    def test_all_resolved(self):
        tickets = [
            {
                "status": "resolved",
                "priority": "high",
                "category": "Hardware",
            },
        ]

        report = generate_report(tickets)

        self.assertEqual(report["resolution_percentage"], 100.0)
        self.assertEqual(report["unresolved"], 0)


if __name__ == "__main__":
    unittest.main()
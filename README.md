# CampusFlow – Helpdesk Ticket Management System

## About the Project

CampusFlow is a Python command-line application for managing support tickets. It helps users create tickets, track their status, assign staff, manage unresolved issues, and generate reports.

The project uses JSON file storage to save ticket information.

## Features

- Create and manage support tickets.
- Set ticket urgency and priority.
- View existing tickets.
- Assign staff members to tickets.
- Update ticket status.
- View unresolved tickets.
- Generate ticket reports.
- Save and load ticket data using JSON.
- Validate ticket data before processing.
- Run automated tests to check the application's functionality.

## Technologies Used

- **Python 3** – Application logic.
- **JSON** – Data storage.
- **unittest** – Automated testing.
- **Git and GitHub** – Version control and collaboration.

## Project Structure

```text
campusflow/
├── campusflow/
│   ├── __init__.py
│   ├── reports.py
│   ├── storage.py
│   ├── tickets.py
│   └── workflow.py
├── data/
│   └── tickets.json
├── tests/
│   ├── test_reports.py
│   ├── test_storage.py
│   ├── test_tickets.py
│   └── test_workflow.py
├── .gitignore
├── main.py
└── README.md

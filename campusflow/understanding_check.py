"""Run a quiz and collect questions for the CampusFlow mentor."""

import json
from pathlib import Path


# Store the mentor questions in the project's data folder.
DATA_FILE = (
    Path(__file__).parent.parent
    / "data"
    / "learning_notes.json"
)


# Keep quiz questions separate from the scoring logic.
QUESTIONS = [
    {
        "question": "1. What is CampusFlow used for?",
        "options": {
            "A": "Managing campus helpdesk tickets",
            "B": "Playing games",
            "C": "Editing pictures",
            "D": "Sending social media messages",
        },
        "answer": "A",
    },
    {
        "question": "2. What does a ticket's priority describe?",
        "options": {
            "A": "Who created the ticket",
            "B": "How urgently the ticket should be handled",
            "C": "The ticket's file name",
            "D": "The staff member's age",
        },
        "answer": "B",
    },
    {
        "question": "3. Which status means work is currently happening?",
        "options": {
            "A": "resolved",
            "B": "closed",
            "C": "in_progress",
            "D": "deleted",
        },
        "answer": "C",
    },
    {
        "question": "4. Why does CampusFlow use JSON storage?",
        "options": {
            "A": "To permanently delete tickets",
            "B": "To save ticket data between program runs",
            "C": "To create computer hardware",
            "D": "To replace Python",
        },
        "answer": "B",
    },
    {
        "question": (
            "5. What should happen if someone tries to resolve "
            "an open ticket directly?"
        ),
        "options": {
            "A": "The ticket should be resolved immediately",
            "B": "The ticket should be deleted",
            "C": "The workflow should reject the invalid transition",
            "D": "All tickets should be reset",
        },
        "answer": "C",
    },
    {
        "question": "6. Why do we write automated tests?",
        "options": {
            "A": "To check that our code behaves as expected",
            "B": "To make every function longer",
            "C": "To avoid running our program",
            "D": "To automatically write documentation",
        },
        "answer": "A",
    },
]


def ask_question(question_data, input_func=input, print_func=print):
    """Ask one question until the user enters a valid answer."""

    print_func("\n" + question_data["question"])

    for letter, option in question_data["options"].items():
        print_func(f"{letter}. {option}")

    while True:
        answer = input_func("Your answer (A-D): ").strip().upper()

        if answer in question_data["options"]:
            return answer

        print_func("Invalid answer. Please enter A, B, C, or D.")


def save_learning_note(note, file_path=DATA_FILE):
    """Save a learning note without deleting existing notes."""

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Keep previously saved learning notes.
    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as file:
                notes = json.load(file)
        except json.JSONDecodeError as error:
            raise ValueError(
                "Cannot save learning note: the existing learning "
                "notes file contains invalid JSON."
            ) from error

        if not isinstance(notes, list):
            raise ValueError(
                "Cannot save learning note: expected a list of notes."
            )
    else:
        notes = []

    notes.append(note)

    # Write to a temporary file before replacing the original.
    temporary_path = path.with_name(path.name + ".tmp")

    try:
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(notes, file, indent=4)

        temporary_path.replace(path)

    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def ask_mentor_questions(input_func=input, print_func=print):
    """Collect two questions the user wants to discuss with a mentor."""

    mentor_questions = []

    print_func("\n=== Questions for Your Mentor ===")
    print_func(
        "Write two things about CampusFlow that you want your "
        "mentor to explain."
    )

    for number in range(1, 3):
        while True:
            question = input_func(
                f"\nMentor question {number}: "
            ).strip()

            if question:
                mentor_questions.append(question)
                break

            print_func("Your question cannot be empty. Please try again.")

    return mentor_questions


def run_quiz(input_func=input, print_func=print):
    """Run the quiz, display the score, and save mentor questions."""

    score = 0
    incorrect_questions = []

    print_func("\n=== CampusFlow Understanding Check ===")

    for question_data in QUESTIONS:
        answer = ask_question(
            question_data,
            input_func,
            print_func,
        )

        if answer == question_data["answer"]:
            print_func("Correct!")
            score += 1
        else:
            correct_answer = question_data["answer"]
            correct_option = question_data["options"][correct_answer]

            print_func(
                f"Not quite. Correct answer: "
                f"{correct_answer}. {correct_option}"
            )

            incorrect_questions.append(question_data)

    print_func(f"\nYour final score: {score}/{len(QUESTIONS)}")

    # Explain at least two questions, or all questions if fewer were missed.
    print_func("\n=== Review and Learn ===")

    questions_to_review = incorrect_questions[:2]

    if len(questions_to_review) < 2:
        for question_data in QUESTIONS:
            if question_data not in questions_to_review:
                questions_to_review.append(question_data)

            if len(questions_to_review) == 2:
                break

    for question_data in questions_to_review:
        correct_answer = question_data["answer"]
        correct_option = question_data["options"][correct_answer]

        print_func(f"\n{question_data['question']}")
        print_func(f"Correct answer: {correct_answer}. {correct_option}")

    # Ask the user to identify what they still want to understand.
    mentor_questions = ask_mentor_questions(
        input_func,
        print_func,
    )

    learning_note = {
        "score": score,
        "total_questions": len(QUESTIONS),
        "mentor_questions": mentor_questions,
    }

    try:
        save_learning_note(learning_note)
        print_func("\nYour learning note has been saved successfully.")
        print_func("Your two mentor questions are:")
        for number, question in enumerate(mentor_questions, start=1):
            print_func(f"{number}. {question}")

    except (OSError, ValueError) as error:
        print_func(f"\nCould not save your learning note: {error}")
        print_func("Please write down your mentor questions for now.")

    return score


if __name__ == "__main__":
    run_quiz()
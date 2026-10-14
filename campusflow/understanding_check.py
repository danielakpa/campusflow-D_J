"""Run a short quiz to check understanding of CampusFlow."""


# Keep the questions separate from the code that calculates the score.
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
        "question": "5. What should happen if someone tries to resolve an open ticket directly?",
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
    """Ask one question and keep asking until the answer is valid."""

    print_func("\n" + question_data["question"])

    for letter, option in question_data["options"].items():
        print_func(f"{letter}. {option}")

    while True:
        answer = input_func("Your answer (A-D): ").strip().upper()

        if answer in question_data["options"]:
            return answer

        print_func("Invalid answer. Please enter A, B, C, or D.")


def run_quiz(input_func=input, print_func=print):
    """Run all questions and return the final score."""

    score = 0

    print_func("\n=== CampusFlow Understanding Check ===")

    for question_data in QUESTIONS:
        answer = ask_question(question_data, input_func, print_func)

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

    print_func(f"\nYour final score: {score}/{len(QUESTIONS)}")

    return score


if __name__ == "__main__":
    run_quiz()
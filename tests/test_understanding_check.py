"""Tests for the CampusFlow understanding quiz."""

import unittest

from campusflow.understanding_check import (
    QUESTIONS,
    ask_question,
    run_quiz,
)


class TestUnderstandingCheck(unittest.TestCase):

    def test_quiz_has_six_questions(self):
        self.assertEqual(len(QUESTIONS), 6)

    def test_each_question_has_four_options(self):
        for question in QUESTIONS:
            self.assertEqual(
                set(question["options"].keys()),
                {"A", "B", "C", "D"},
            )

    def test_correct_answer_is_accepted(self):
        question = QUESTIONS[0]
        answers = iter(["A"])

        answer = ask_question(
            question,
            input_func=lambda _: next(answers),
            print_func=lambda _: None,
        )

        self.assertEqual(answer, "A")

    def test_invalid_answer_is_rejected(self):
        question = QUESTIONS[0]
        answers = iter(["X", "A"])
        messages = []

        answer = ask_question(
            question,
            input_func=lambda _: next(answers),
            print_func=messages.append,
        )

        self.assertEqual(answer, "A")
        self.assertTrue(
            any("Invalid answer" in message for message in messages)
        )

    def test_all_correct_answers_score_six(self):
        answers = iter(["A", "B", "C", "B", "C", "A"])

        score = run_quiz(
            input_func=lambda _: next(answers),
            print_func=lambda _: None,
        )

        self.assertEqual(score, 6)

    def test_all_wrong_answers_score_zero(self):
        answers = iter(["D", "A", "B", "D", "A", "D"])

        score = run_quiz(
            input_func=lambda _: next(answers),
            print_func=lambda _: None,
        )

        self.assertEqual(score, 0)


if __name__ == "__main__":
    unittest.main()
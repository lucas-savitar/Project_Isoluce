from __future__ import annotations

import unittest

from task_engine.parser import parse_request


class ParseRequestTests(unittest.TestCase):
    def test_valid_request_is_normalized(self) -> None:
        parsed = parse_request(
            {
                "id": " REQ-1 ",
                "client": " Atelier   Nova ",
                "action": " Vérifier le formulaire ",
                "message": " Test ",
                "priority": "HIGH",
                "deadline": "2026-09-08",
                "people": ["Julie Martin"],
            }
        )
        self.assertEqual(parsed.request_id, "REQ-1")
        self.assertEqual(parsed.client, "Atelier Nova")
        self.assertEqual(parsed.priority, "high")

    def test_blank_client_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "client is required"):
            parse_request(
                {
                    "id": "REQ-2",
                    "client": "   ",
                    "action": "Tester",
                    "message": "Test",
                }
            )

    def test_people_are_deduplicated_without_reordering(self) -> None:
        parsed = parse_request(
            {
                "id": "REQ-3",
                "client": "Atelier Nova",
                "action": "Tester",
                "message": "Test",
                "people": ["Zoé", "Alice", "Zoé", "Karim"],
            }
        )
        self.assertEqual(parsed.people, ("Zoé", "Alice", "Karim"))

    def test_invalid_deadline_is_reported_not_invented(self) -> None:
        parsed = parse_request(
            {
                "id": "REQ-4",
                "client": "Atelier Nova",
                "action": "Tester",
                "message": "Test",
                "deadline": "vendredi prochain",
            }
        )
        self.assertIsNone(parsed.deadline)
        self.assertIn("deadline_invalid", parsed.missing_information)


if __name__ == "__main__":
    unittest.main()

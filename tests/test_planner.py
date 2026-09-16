from __future__ import annotations

import unittest

from task_engine.planner import build_plan


class BuildPlanTests(unittest.TestCase):
    def test_one_request_creates_one_task(self) -> None:
        result = build_plan(
            [
                {
                    "id": "REQ-1",
                    "client": "Atelier Nova",
                    "action": "Tester le formulaire",
                    "message": "Le formulaire est à vérifier.",
                    "priority": "medium",
                    "deadline": "2026-09-08",
                    "people": ["Julie"],
                }
            ]
        )
        self.assertEqual(result["task_count"], 1)
        self.assertEqual(result["tasks"][0]["source_ids"], ["REQ-1"])

    def test_known_deadline_clears_missing_alert_regardless_of_order(self) -> None:
        request_no_date = {
            "id": "REQ-1",
            "client": "Atelier Nova",
            "action": "Tester",
            "message": "Test",
        }
        request_with_date = {
            "id": "REQ-2",
            "client": "Atelier Nova",
            "action": "Tester",
            "message": "Test",
            "deadline": "2026-09-10",
        }

        result_a = build_plan([request_no_date, request_with_date])
        result_b = build_plan([request_with_date, request_no_date])

        for result in (result_a, result_b):
            task = result["tasks"][0]
            self.assertEqual(task["deadline"], "2026-09-10")
            self.assertNotIn("deadline", task["missing_information"])

    def test_source_ids_are_deduplicated_preserving_first_appearance(self) -> None:
        def make(request_id: str) -> dict:
            return {
                "id": request_id,
                "client": "Atelier Nova",
                "action": "Tester",
                "message": "Test",
        }

        result = build_plan([make("R2"), make("R1"), make("R2")])

        self.assertEqual(result["tasks"][0]["source_ids"], ["R2", "R1"])

    def test_input_payload_is_not_mutated(self) -> None:
        payloads = [
            {
                "id": "REQ-1",
                "client": "Atelier Nova",
                "action": "Tester",
                "message": "Test",
                "people": ["Julie"],
            }
        ]
        before = [dict(payloads[0], people=list(payloads[0]["people"]))]
        build_plan(payloads)
        self.assertEqual(payloads, before)

    def test_requests_differing_by_case_and_spacing_are_merged(self) -> None:
        request_clean = {
            "id": "REQ-1",
            "client": "Atelier Nova",
            "action": "Vérifier le formulaire",
            "message": "Test",
    }
        request_messy = {
            "id": "REQ-2",
            "client": "  atelier   NOVA ",
            "action": " VÉRIFIER LE FORMULAIRE",
            "message": "Test",
    }

        result = build_plan([request_clean, request_messy])

        self.assertEqual(result["task_count"], 1)
        self.assertEqual(result["tasks"][0]["source_ids"], ["REQ-1", "REQ-2"])

    def test_merge_preserves_people_order_without_duplicates(self) -> None:
        request_a = {
            "id": "REQ-1",
            "client": "Atelier Nova",
            "action": "Tester",
            "message": "Test",
            "people": ["Alice", "Bob"],
    }
        request_b = {
            "id": "REQ-2",
            "client": "Atelier Nova",
            "action": "Tester",
            "message": "Test",
            "people": ["Bob", "Charlie"],
    }

        result = build_plan([request_a, request_b])

        self.assertEqual(result["tasks"][0]["people"], ["Alice", "Bob", "Charlie"])


if __name__ == "__main__":
    unittest.main()

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


if __name__ == "__main__":
    unittest.main()

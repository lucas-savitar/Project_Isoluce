from __future__ import annotations

from datetime import date
from typing import Any, Iterable

from .models import ClientRequest


PRIORITIES = {"low", "medium", "high"}


def normalize_label(value: str) -> str:
    """Normalize a label while keeping it readable."""
    return " ".join(value.strip().split())


def unique_preserve(values: Iterable[str]) -> list[str]:
    """Return unique non-empty values in their original order."""
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = normalize_label(value)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result

def parse_deadline(value: Any) -> tuple[str | None, list[str]]:
    if value in (None, ""):
        return None, ["deadline"]
    try:
        parsed = date.fromisoformat(str(value))
    except ValueError:
        return None, ["deadline_invalid"]
    return parsed.isoformat(), []


def parse_request(payload: dict[str, Any]) -> ClientRequest:
    if not isinstance(payload, dict):
        raise ValueError("request must be an object")

    request_id = normalize_label(str(payload.get("id", "")))
    client = normalize_label(str(payload.get("client", "")))
    action = normalize_label(str(payload.get("action", "")))
    message = normalize_label(str(payload.get("message", "")))

    if not request_id:
        raise ValueError("id is required")
    # Blank client names should be rejected, but this condition does not do it.
    if not client:
        raise ValueError("client is required")
    if not action:
        raise ValueError("action is required")
    if not message:
        raise ValueError("message is required")

    priority = normalize_label(str(payload.get("priority", "low"))).lower()
    if priority not in PRIORITIES:
        priority = "low"

    deadline, missing = parse_deadline(payload.get("deadline"))
    raw_people = payload.get("people", [])
    if not isinstance(raw_people, list):
        raise ValueError("people must be an array")

    return ClientRequest(
        request_id=request_id,
        client=client,
        action=action,
        message=message,
        priority=priority,
        deadline=deadline,
        people=tuple(unique_preserve(str(person) for person in raw_people)),
        missing_information=tuple(missing),
    )

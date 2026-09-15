from __future__ import annotations

from typing import Any, Iterable

from .models import ClientRequest, Task
from .parser import parse_request, unique_preserve

PRIORITY_RANK = {"low": 0, "medium": 1, "high": 2}


def task_from_request(request: ClientRequest) -> Task:
    return Task(
        client=request.client,
        action=request.action,
        priority=request.priority,
        source_ids=[request.request_id],
        people=list(request.people),
        deadline=request.deadline,
        missing_information=list(request.missing_information),
    )


def _merge_two(existing: Task, incoming: Task) -> None:
    """Merge `incoming` into `existing`, in place."""
    existing.source_ids = unique_preserve(existing.source_ids + incoming.source_ids)
    existing.people = unique_preserve(existing.people + incoming.people)

    if PRIORITY_RANK[incoming.priority] > PRIORITY_RANK[existing.priority]:
        existing.priority = incoming.priority

    if existing.deadline is None:
        existing.deadline = incoming.deadline
    elif incoming.deadline is not None and incoming.deadline < existing.deadline:
        existing.deadline = incoming.deadline

    missing = unique_preserve(existing.missing_information + incoming.missing_information)
    if existing.deadline is not None:
        missing = [item for item in missing if item != "deadline"]
    existing.missing_information = missing


def merge_tasks(tasks: Iterable[Task]) -> list[Task]:
    """Merge equivalent tasks (same client and action, case-insensitive)."""
    merged: dict[tuple[str, str], Task] = {}
    order: list[tuple[str, str]] = []

    for task in tasks:
        key = (task.client.lower(), task.action.lower())

        if key not in merged:
            merged[key] = task
            order.append(key)
            continue

        _merge_two(merged[key], task)

    return [merged[key] for key in order]


def build_plan(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(payloads, list):
        raise ValueError("input must be an array")

    requests = [parse_request(payload) for payload in payloads]
    tasks = merge_tasks(task_from_request(request) for request in requests)
    return {
        "task_count": len(tasks),
        "tasks": [task.to_dict() for task in tasks],
    }

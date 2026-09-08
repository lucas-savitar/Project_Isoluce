from __future__ import annotations

from typing import Any, Iterable

from .models import ClientRequest, Task
from .parser import parse_request


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


def merge_tasks(tasks: Iterable[Task]) -> list[Task]:
    """Merge equivalent tasks.

    The current implementation is intentionally incomplete.
    """
    return list(tasks)


def build_plan(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(payloads, list):
        raise ValueError("input must be an array")

    requests = [parse_request(payload) for payload in payloads]
    tasks = merge_tasks(task_from_request(request) for request in requests)
    return {
        "task_count": len(tasks),
        "tasks": [task.to_dict() for task in tasks],
    }

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class ClientRequest:
    request_id: str
    client: str
    action: str
    message: str
    priority: str
    deadline: str | None = None
    people: tuple[str, ...] = ()
    missing_information: tuple[str, ...] = ()


@dataclass
class Task:
    client: str
    action: str
    priority: str
    source_ids: list[str] = field(default_factory=list)
    people: list[str] = field(default_factory=list)
    deadline: str | None = None
    missing_information: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

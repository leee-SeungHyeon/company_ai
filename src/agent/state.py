from dataclasses import dataclass, field
from typing import Annotated


def _append_messages(existing: list, update: list) -> list:
    return existing + update


@dataclass
class Config:
    max_execute_tool_count: int = field(default=3)


@dataclass
class State:
    messages: Annotated[list, _append_messages] = field(default_factory=list)
    execute_tool_count: int = field(default=0)

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AccountAdd:
    link: str
    server_answer: str


@dataclass(frozen=True)
class SourcesAdd:
    link: str
    server_answer: str


@dataclass(frozen=True)
class AccountChange:
    res_id: int
    server_answer: str


__all__ = [
    'AccountAdd',
    'AccountChange',
    'SourcesAdd',
]
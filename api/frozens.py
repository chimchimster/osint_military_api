from dataclasses import dataclass


@dataclass(frozen=True)
class FrozenServerResponse:
    link: str
    server_answer: str

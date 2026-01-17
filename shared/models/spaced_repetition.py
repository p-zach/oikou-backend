from typing import Literal, Optional
from dataclasses import dataclass, asdict, fields

Grade = Literal[0, 1, 2, 3]

# SM-2-style scheduling
@dataclass
class UserFactProgress:
    # DB interface dataclass uses non-Python casing
    id: str
    userId: str
    factId: str
    intervalDays: int
    ease: float
    repetitions: int
    dueAt: str
    lastReviewedAt: Optional[str] = None
    
    @staticmethod
    def create_id(user_id: str, fact_id: str) -> str:
        return f"{user_id}|{fact_id}"

    @classmethod
    def from_dict(cls, d: dict) -> "UserFactProgress":
        field_names = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in d.items() if k in field_names}
        return cls(**filtered)

    def to_dict(self) -> dict:
        return asdict(self)
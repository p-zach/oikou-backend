from typing import Literal, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

Grade = Literal[0, 1, 2, 3]

# SM-2-style scheduling
@dataclass
class UserFactProgress:
    id: str
    user_id: str
    fact_id: str
    interval_days: int
    ease: float
    repetitions: int
    due_at: str
    last_reviewed_at: Optional[str] = None
    
    @staticmethod
    def create_id(user_id: str, fact_id: str) -> str:
        return f"{user_id}|{fact_id}"

    @staticmethod
    def from_dict(d: dict) -> "UserFactProgress":
        return UserFactProgress(**d)

    def to_dict(self) -> dict:
        return asdict(self)
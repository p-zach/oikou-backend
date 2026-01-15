from typing import TypedDict, Literal
from shared.models.challenge import Challenge

LessonSubject = Literal[
    "capitals", 
    "flags", 
    "neighbors"
]

class Lesson(TypedDict):
    sessionId: str
    challenges: list[Challenge]

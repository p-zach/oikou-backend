from typing import TypedDict, Literal
from shared.models.challenge import Challenge, ChallengeResult

LessonSubject = Literal[
    "capitals", 
    "flags", 
    "neighbors"
]

class Lesson(TypedDict):
    sessionId: str
    challenges: list[Challenge]

class LessonResult(TypedDict):
    sessionId: str
    results: list[ChallengeResult]
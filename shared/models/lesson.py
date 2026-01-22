from typing import TypedDict, Literal, get_args
from shared.models.challenge import Challenge, ChallengeResult

LessonSubject = Literal[
    "capitals", 
    "flags", 
    "neighbors"
]

LESSON_SUBJECTS: list[LessonSubject] = list(get_args(LessonSubject))

class Lesson(TypedDict):
    sessionId: str
    challenges: list[Challenge]

class LessonResult(TypedDict):
    sessionId: str
    results: list[ChallengeResult]
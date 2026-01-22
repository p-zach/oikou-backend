from typing import TypedDict

from shared.models.lesson import LessonSubject

class MasterySummary(TypedDict):
    region: str | None
    subject: LessonSubject | None
    mastery: float

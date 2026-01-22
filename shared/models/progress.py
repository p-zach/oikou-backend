from typing import TypedDict

from shared.models.lesson import LessonSubject

type MasterySummary = dict[str, dict[LessonSubject, RegionSubjectMastery]]

class RegionSubjectMastery(TypedDict):
    region: str
    subject: LessonSubject
    mastery: float
    total: int

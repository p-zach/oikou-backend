from typing import TypedDict, Literal

ChallengeType = Literal[
    "multiple-choice",
]

class Challenge(TypedDict):
    factId: str
    challengeType: ChallengeType
    question: str

class ChallengeResult(TypedDict):
    factId: str
    correct: bool

class MultipleChoiceChallenge(Challenge):
    options: list[str]
    correctOptionIndex: int
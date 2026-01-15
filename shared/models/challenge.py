from typing import TypedDict, Literal

ChallengeType = Literal[
    "multiple-choice",
]

class Challenge(TypedDict):
    itemId: str
    challengeType: ChallengeType
    question: str

class MultipleChoiceChallenge(Challenge):
    options: list[str]
    correctOptionIndex: int
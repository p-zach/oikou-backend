import random

from shared.models.fact import Fact
from shared.models.challenge import MultipleChoiceChallenge

def create_multiple_choice_challenge(fact: Fact, subject_facts: list[Fact], num_options = 4):
    question = f"What is the capital of {fact['country']}?"

    other_facts = [f["answer"] for f in subject_facts if f["id"] != fact["id"]]
    options = random.sample(other_facts, k=num_options - 1) + [fact["answer"]]
    random.shuffle(options)

    challenge: MultipleChoiceChallenge = {
        "factId": fact["id"],
        "challengeType": "multiple-choice",
        "question": question,
        "correctOptionIndex": options.index(fact["answer"]),
        "options": options,
    }

    return challenge
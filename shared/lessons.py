import random
import uuid

from shared.cosmos_client import get_container
from shared.challenges import create_multiple_choice_challenge

from shared.models.lesson import Lesson
from shared.models.fact import Fact

def start_lesson(userId: str, region: str, subject: str, question_count: int) -> Lesson:
    all_facts = get_container("facts")
    subject_facts: list[Fact] = [
        Fact(**fact_dict) for fact_dict in all_facts.query_items(
            query="SELECT * FROM f WHERE f.subject = @subject",
            parameters=[
                {"name": "@subject", "value": subject},
            ],
        )
    ]

    if len(subject_facts) < question_count:
        raise ValueError("Not enough facts available for the requested subject")
    
    selected_facts = random.sample(subject_facts, question_count)

    challenges = []
    for fact in selected_facts:
        challenge = create_multiple_choice_challenge(fact, subject_facts)        
        challenges.append(challenge)

    lesson: Lesson = {
        "sessionId": str(uuid.uuid4()),
        "challenges": challenges,
    }

    return lesson
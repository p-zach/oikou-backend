import random
import uuid
from datetime import datetime, timezone

from shared.cosmos_client import get_container
from shared.challenges import create_multiple_choice_challenge
from shared.spaced_repetition import schedule, create_initial_progress

from shared.models.lesson import Lesson
from shared.models.fact import Fact, fact_in_subject
from shared.models.spaced_repetition import UserFactProgress

facts_container_name = "facts"
user_fact_progress_container_name = "user_fact_progress"

def start_lesson(user_id: str, region: str, subject: str, question_count: int) -> Lesson:
    subject_facts = get_all_subject_facts(subject)

    if len(subject_facts) < question_count:
        raise ValueError("Not enough facts available for the requested subject")

    user_fact_progress = get_user_fact_progress(user_id, subject)
    review_facts, new_facts = classify_facts(subject_facts, user_fact_progress)
    facts_to_serve = select_facts_to_serve(review_facts, new_facts, question_count)

    upsert_initial_progress_data(facts_to_serve, user_fact_progress, user_id)

    return create_lesson(facts_to_serve, subject_facts)

def get_all_subject_facts(subject: str) -> list[Fact]:
    """Get all facts matching the given subject."""
    all_facts = get_container(facts_container_name)
    subject_facts: list[Fact] = [
        Fact(**fact_dict)
        for fact_dict in all_facts.query_items(
            query="SELECT * FROM f WHERE f.subject = @subject",
            parameters=[
                {"name": "@subject", "value": subject},
            ],
        )
    ]
    return subject_facts

def get_user_fact_progress(user_id: str, subject: str) -> dict[str, UserFactProgress]:
    """Get the given user's progress for all facts in a subject."""
    user_progress_container = get_container(user_fact_progress_container_name)
    all_user_fact_progress = user_progress_container
    user_fact_progress: dict[str, UserFactProgress] = {
        p["factId"]: UserFactProgress.from_dict(p)
        for p in all_user_fact_progress.query_items(
            query="SELECT * FROM p WHERE p.userId = @userId",
            parameters=[
                {"name": "@userId", "value": user_id},
            ]
        ) 
        # Filter to only facts with matching subject
        if fact_in_subject(p["factId"], subject)
    }
    return user_fact_progress

def classify_facts(subject_facts: list[Fact], user_fact_progress: dict[str, UserFactProgress]) -> tuple[list[Fact], list[Fact]]:
    """Classify facts as review facts (which the user has seen before) and new
    facts (which the user hasn't seen before).
    
    Returns: 
        tuple[list[Fact], list[Fact]]: review_facts, new_facts
    """
    review_facts: list[Fact] = []
    new_facts: list[Fact] = []

    now = datetime.now(timezone.utc)

    for fact in subject_facts:
        progress = user_fact_progress.get(fact["id"])

        if progress is None:
            new_facts.append(fact)
        elif datetime.fromisoformat(progress.due_at) <= now:
            review_facts.append(fact)

    return review_facts, new_facts

def select_facts_to_serve(review_facts: list[Fact], new_facts: list[Fact], question_count: int) -> list[Fact]:
    """Select which facts to serve the user. 
    
    Prioritizes serving review facts before showing new facts.
    """
    random.shuffle(review_facts)
    random.shuffle(new_facts)

    # Always prioritize review facts
    facts_to_serve = (review_facts + new_facts)[:question_count]
    random.shuffle(facts_to_serve)

    return facts_to_serve

def upsert_initial_progress_data(facts_to_serve: list[Fact], user_fact_progress: dict[str, UserFactProgress], user_id: str):
    """Create progress data in Cosmos for each fact that the user hasn't reviewed before."""
    now = datetime.now(timezone.utc)
    user_progress_container = get_container(user_fact_progress_container_name)

    for fact in facts_to_serve:
        if fact["id"] not in user_fact_progress:
            progress = create_initial_progress(user_id, fact["id"], now)
            user_progress_container.upsert_item(progress.to_dict())

def create_lesson(facts_to_serve: list[Fact], all_subject_facts: list[Fact]) -> Lesson:
    """Create a lesson from the list of facts to serve the user. 

    Multiple choice options are provided by the list of all subject facts.
    """
    challenges = []
    for fact in facts_to_serve:
        challenge = create_multiple_choice_challenge(fact, all_subject_facts)
        challenges.append(challenge)

    lesson: Lesson = {
        "sessionId": str(uuid.uuid4()),
        "challenges": challenges,
    }

    return lesson
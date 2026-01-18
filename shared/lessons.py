import random
import uuid
from datetime import datetime, timezone
from typing import Callable

from shared.cosmos_client import get_container
from shared.challenges import create_multiple_choice_challenge
from shared.spaced_repetition import schedule, create_initial_progress
from shared.facts import get_all_subject_facts

from shared.models.lesson import Lesson, ChallengeResult
from shared.models.fact import Fact, fact_in_subject
from shared.models.spaced_repetition import UserFactProgress, Grade

# Constants
USER_FACT_PROGRESS_CONTAINER_NAME = "user_fact_progress"

### API interface functions

def start_lesson(user_id: str, region: str, subject: str, question_count: int) -> Lesson:
    """Get a lesson with questions matching specified parameters. Uses spaced
    repetition to decide which facts to show the user.

    Args:
        user_id (str): The user ID.
        region (str): The region requested by the user.
        subject (str): The subject requested by the user.
        question_count (int): The number of questions to return.

    Raises:
        ValueError: If there are not enough facts in the requested subject.

    Returns:
        Lesson: The lesson to send the user.
    """
    subject_facts = get_all_subject_facts(subject)

    if len(subject_facts) < question_count:
        raise ValueError("Not enough facts available for the requested subject")

    # Get user fact progress for all facts in the lesson's subject
    user_fact_progress = get_user_fact_progress(
        user_id, 
        lambda p: fact_in_subject(p["factId"], subject)
    )
    review_facts, new_facts, not_due_facts = classify_facts(
        subject_facts, 
        user_fact_progress
    )
    facts_to_serve = select_facts_to_serve(
        review_facts, 
        new_facts, 
        not_due_facts, 
        user_fact_progress, 
        question_count
    )

    upsert_initial_progress_data(facts_to_serve, user_fact_progress, user_id)

    return create_lesson(facts_to_serve, subject_facts)

def complete_lesson(user_id: str, session_id: str, results: list[ChallengeResult]) -> None:
    """Update user progress based on lesson results.

    Args:
        user_id (str): The user ID.
        lesson_result (LessonResult): The result of the lesson.
    """
    fact_grades = get_fact_grades(results)

    update_progress(user_id, fact_grades)

    # TODO: Keep track of all user lessons in another DB

### Helper functions

def get_user_fact_progress(user_id: str, predicate: Callable[[dict], bool] | None = None) -> dict[str, UserFactProgress]:
    """Get the given user's progress for all facts they have seen.
    
    Optionally filter by a predicate which takes a UserFactProgress dict.
    """
    user_progress_container = get_container(USER_FACT_PROGRESS_CONTAINER_NAME)
    all_user_fact_progress = user_progress_container    
    user_fact_progress: dict[str, UserFactProgress] = {
        p["factId"]: UserFactProgress.from_dict(p)
        for p in all_user_fact_progress.query_items(
            query="SELECT * FROM p WHERE p.userId = @userId",
            parameters=[
                {"name": "@userId", "value": user_id},
            ]
        ) 
        if predicate is not None and predicate(p)
    }
    return user_fact_progress

def classify_facts(subject_facts: list[Fact], user_fact_progress: dict[str, UserFactProgress]) -> tuple[list[Fact], list[Fact], list[Fact]]:
    """Classify facts as review facts (which the user has seen before and are 
    due), new facts (which the user hasn't seen before), and facts not due yet.
    
    Returns: 
        tuple[list[Fact], list[Fact], list[Fact]]: 
            review_facts, 
            new_facts, 
            not_due_yet_facts
    """
    review_facts: list[Fact] = []
    new_facts: list[Fact] = []
    not_due_yet_facts: list[Fact] = []

    now = datetime.now(timezone.utc)

    for fact in subject_facts:
        progress = user_fact_progress.get(fact["id"])

        if progress is None:
            new_facts.append(fact)
        elif datetime.fromisoformat(progress.dueAt) <= now:
            review_facts.append(fact)
        else:
            not_due_yet_facts.append(fact)

    return review_facts, new_facts, not_due_yet_facts

def select_facts_to_serve(
        review_facts: list[Fact], 
        new_facts: list[Fact], 
        not_due_facts: list[Fact], 
        user_fact_progress: dict[str, UserFactProgress],
        question_count: int
    ) -> list[Fact]:
    """Select which facts to serve the user. 
    
    Prioritizes serving review facts before showing new facts. If there are no
    new facts to show and the user has reviewed all their due facts, show facts
    not due yet.
    """
    # Order review facts by due date
    review_facts.sort(key=lambda f: user_fact_progress[f["id"]].dueAt)
    # Shuffle before adding to list so it's not always the same order
    random.shuffle(new_facts)

    # Always prioritize review facts
    facts_to_serve = (review_facts + new_facts)[:question_count]
    # If we need more facts to meet question_count, extend with facts not due,
    # ordered by due date 
    if len(facts_to_serve) < question_count:
        not_due_facts.sort(key=lambda f: user_fact_progress[f["id"]].dueAt)
        facts_to_serve.extend(
            not_due_facts[:question_count - len(facts_to_serve)]
        )

    random.shuffle(facts_to_serve)

    return facts_to_serve

def upsert_initial_progress_data(facts_to_serve: list[Fact], user_fact_progress: dict[str, UserFactProgress], user_id: str):
    """Create progress data in Cosmos for each fact that the user hasn't reviewed before."""
    now = datetime.now(timezone.utc)
    user_progress_container = get_container(USER_FACT_PROGRESS_CONTAINER_NAME)

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

def get_fact_grades(results: list[ChallengeResult]) -> dict[str, Grade]:
    """Get the grade for each fact reviewed by the user."""
    fact_incorrect_count = get_fact_incorrect_count(results)
    fact_grades: dict[str, Grade] = {}
    for fact_id, times_incorrect in fact_incorrect_count.items():
        if times_incorrect == 0:
            # If the user got the answer correct immediately, they receive a
            # grade of 3, which corresponds with 'correct and easy'.
            grade = 3
            # A grade of 2 is 'correct but difficult'; there is not a clear way
            # to distinguish the two in a correct/incorrect dichotomy like we 
            # have here.
        elif times_incorrect == 1:
            # Receive 'wrong but familiar' if the user gets the fact wrong once
            grade = 1
        else:
            # Getting the fact wrong more than once indicates 'complete failure'
            grade = 0
        fact_grades[fact_id] = grade

    return fact_grades

def get_fact_incorrect_count(results: list[ChallengeResult]) -> dict[str, int]:
    """Count the number of times the user got each fact incorrect in a lesson.
    """
    fact_incorrect_count: dict[str, int] = { 
        result["factId"]: 0
        for result in results
    }
    for result in results:
        if not result["correct"]:
            fact_incorrect_count[result["factId"]] += 1

    return fact_incorrect_count

def update_progress(user_id: str, fact_grades: dict[str, Grade]) -> None:
    """Update the user's progress for each fact in fact_grades."""
    # Collect the user fact progress items associated with the lesson's facts
    user_fact_progress = get_user_fact_progress(
        user_id, 
        lambda p: p["factId"] in fact_grades.keys()
    )
    now = datetime.now(timezone.utc)
    user_progress_container = get_container(USER_FACT_PROGRESS_CONTAINER_NAME)

    # Update the progress for each reviewed fact
    for fact_id, progress in user_fact_progress.items():
        grade = fact_grades[fact_id]
        new_progress = schedule(progress, grade, now)
        user_progress_container.upsert_item(new_progress.to_dict())

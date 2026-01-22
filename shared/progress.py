from datetime import datetime, timezone
from typing import Callable

from shared.db import USER_FACT_PROGRESS_CONTAINER_NAME, query_simple, upsert_item
from shared.spaced_repetition import schedule, create_initial_progress, is_mastered
from shared.regions import get_country_codes_in_region

from shared.models.fact import Fact, is_fact_in_subject, get_fact_country_code
from shared.models.spaced_repetition import UserFactProgress, Grade
from shared.models.progress import MasterySummary
from shared.models.lesson import LessonSubject

def get_mastery(user_id: str, region: str | None, subject: LessonSubject | None) -> MasterySummary:
    """Get the mastery percentage for a user.
    
    Optionally narrow to region and/or subject.
    """
    # Create predicate to filter by subject if subject is defined
    predicate = (lambda p: is_fact_in_subject(p["factId"], subject)) if subject is not None else None

    user_fact_progress = list(get_user_fact_progress(user_id, predicate).values())
    
    # Filter by region
    if region is not None:
        country_codes_in_region = get_country_codes_in_region(region)
        user_fact_progress = [
            progress
            for progress in user_fact_progress
            if get_fact_country_code(progress.factId) in country_codes_in_region
        ]

    total_mastered = sum(is_mastered(p) for p in user_fact_progress)
    mastery_percent = total_mastered / len(user_fact_progress)

    return {
        "mastery": mastery_percent,
        "region": region,
        "subject": subject,
    }

def get_user_fact_progress(user_id: str, predicate: Callable[[dict], bool] | None = None) -> dict[str, UserFactProgress]:
    """Get the given user's progress for all facts they have seen.
    
    Optionally filter by a predicate which takes a UserFactProgress dict.

    Returns:
        dict[str, UserFactProgress]: A dictionary mapping fact IDs to the 
            associated UserFactProgress.
    """
    user_fact_progress: dict[str, UserFactProgress] = {
        p["factId"]: UserFactProgress.from_dict(p)
        for p in query_simple(
            container_name=USER_FACT_PROGRESS_CONTAINER_NAME,
            parameters={ "userId": user_id }
        ) 
        if predicate is None or (predicate is not None and predicate(p))
    }
    return user_fact_progress

def upsert_initial_progress_data(facts_to_serve: list[Fact], user_fact_progress: dict[str, UserFactProgress], user_id: str) -> None:
    """Create progress data in Cosmos for each fact that the user hasn't reviewed before."""
    now = datetime.now(timezone.utc)

    for fact in facts_to_serve:
        if fact["id"] not in user_fact_progress:
            progress = create_initial_progress(user_id, fact["id"], now)
            upsert_item(USER_FACT_PROGRESS_CONTAINER_NAME, progress.to_dict())

def update_progress(user_id: str, fact_grades: dict[str, Grade]) -> None:
    """Update the user's progress for each fact in fact_grades."""
    # Collect the user fact progress items associated with the lesson's facts
    user_fact_progress = get_user_fact_progress(
        user_id, 
        lambda p: p["factId"] in fact_grades.keys()
    )
    now = datetime.now(timezone.utc)

    # Update the progress for each reviewed fact
    for fact_id, progress in user_fact_progress.items():
        grade = fact_grades[fact_id]
        new_progress = schedule(progress, grade, now)
        upsert_item(USER_FACT_PROGRESS_CONTAINER_NAME, new_progress.to_dict())

from datetime import datetime, timezone
from typing import Callable

from shared.db import USER_FACT_PROGRESS_CONTAINER_NAME, query_simple, upsert_item
from shared.spaced_repetition import schedule, create_initial_progress, get_mastery_percent
from shared.regions import get_country_codes_in_region
from shared.facts import get_all_facts

from shared.models.fact import Fact, is_fact_in_subject, get_fact_country_code
from shared.models.spaced_repetition import UserFactProgress, Grade
from shared.models.progress import MasterySummary
from shared.models.lesson import LessonSubject, LESSON_SUBJECTS

def get_mastery(user_id: str, regions: list[str], subjects: list[LessonSubject] | None) -> MasterySummary:
    """Get the mastery percentage for a user for a list of regions. Optionally 
    narrow to a specific lesson subject.
    
    Response is of the form:
    ```
    {
        "europe": {
            "capitals": {
                "region": "europe",
                "subject": "capitals",
                "mastery": 0.45,
                "total": 29,
            },
            "flags": {
                ...
            }
        }
        "americas": {
            ...
        }
    }
    ```
    """
    predicate = None
    if subjects is not None:
        # Create predicate to filter by specified subjects
        predicate = lambda p: any(
            is_fact_in_subject(p["factId"], subject) 
            for subject in subjects
        )
    else:
        # Return info for all subjects if none specified
        subjects = LESSON_SUBJECTS

    # Get the user's progress for all facts they have seen in all regions within
    # the specified subjects
    global_subjects_facts_progress = list(get_user_fact_progress(user_id, predicate).values())
    
    # Divide into region buckets
    region_subjects_facts_progress: dict[str, list[UserFactProgress]] = {}
    for region in regions:
        country_codes_in_region = get_country_codes_in_region(region)
        region_subjects_facts_progress[region] = [
            progress
            for progress in global_subjects_facts_progress
            if get_fact_country_code(progress.factId) in country_codes_in_region
        ]

    mastery_summary: MasterySummary = {}

    # Calculate mastery for each subject in each region
    for region, subjects_facts_progress in region_subjects_facts_progress.items():
        mastery_summary[region] = {}
        region_facts = get_all_facts(region=region)
        for subject in subjects:
            num_facts_in_subject = sum(
                is_fact_in_subject(fact["id"], subject)
                for fact in region_facts
            )
            # Avoid division by 0
            if num_facts_in_subject == 0:
                continue
            subject_facts_progress = [
                p
                for p in subjects_facts_progress
                if is_fact_in_subject(p.factId, subject)
            ]
            total_mastered = sum(
                get_mastery_percent(p)
                for p in subject_facts_progress
            )
            mastery_summary[region][subject] = {
                "region": region,
                "subject": subject,
                "mastery": total_mastered / num_facts_in_subject,
                "total": num_facts_in_subject,
            }

    return mastery_summary

def get_user_fact_progress(user_id: str, predicate: Callable[[dict[str, str]], bool] | None = None) -> dict[str, UserFactProgress]:
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

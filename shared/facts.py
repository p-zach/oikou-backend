import random
from datetime import datetime, timezone

from shared.db import FACTS_CONTAINER_NAME, query_simple
from shared.regions import get_country_codes_in_region

from shared.models.fact import Fact, fact_from_dict
from shared.models.challenge import ChallengeResult
from shared.models.spaced_repetition import UserFactProgress, Grade

def get_specific_facts(fact_ids: list[str], subject: str | None) -> list[Fact]:
    """Get fact information for all facts listed in fact_ids."""
    facts = [
        fact_from_dict(fact_dict)
        for fact_dict in query_simple(
            container_name=FACTS_CONTAINER_NAME,
            parameters={ "subject": subject } if subject is not None else {},
            enable_cross_partition_query=subject is None
        )
        if fact_dict["id"] in fact_ids
    ]
    return facts

def get_all_subject_facts(subject: str, region: str | None = None) -> list[Fact]:
    """Get all facts matching the given subject and optional region."""
    subject_facts = [
        fact_from_dict(fact_dict)
        for fact_dict in query_simple(
            container_name=FACTS_CONTAINER_NAME,
            parameters={ "subject": subject }
        )
    ]
    if region is None:
        return subject_facts
    
    country_codes_in_region = get_country_codes_in_region(region)

    region_facts = [
        fact for fact in subject_facts
        if fact["countryCode"] in country_codes_in_region
    ]
    return region_facts

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

import uuid

from shared.challenges import create_multiple_choice_challenge
from shared.facts import get_all_facts, classify_facts, select_facts_to_serve, get_fact_grades
from shared.progress import get_user_fact_progress, upsert_initial_progress_data, update_progress

from shared.models.lesson import Lesson, ChallengeResult
from shared.models.fact import Fact, is_fact_in_subject

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
    subject_facts = get_all_facts(subject, region)

    if len(subject_facts) < question_count:
        raise ValueError("Not enough facts available for the requested subject")

    # Get user fact progress for all facts in the lesson's subject
    user_fact_progress = get_user_fact_progress(
        user_id, 
        lambda p: is_fact_in_subject(p["factId"], subject)
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

from datetime import datetime, timedelta
from shared.models.spaced_repetition import UserFactProgress, Grade

# The minimum `ease` and `repetitions` at or above which a fact is considered to 
# be "mastered" in the UI.
MASTERY_EASE_THRESHOLD = 2.7
MASTERY_REPETITIONS_THRESHOLD = 2

# The percent mastery for facts that have met a mid-level repetitions threshold 
# but do not meet the full mastery thresholds. This is used to give partial 
# credit in the UI for facts that are on their way to being mastered but haven't 
# reached the full mastery thresholds yet.
MOSTLY_MASTERED_PERCENT = 0.50
# The minimum `repetitions` at or above which a fact is considered to be "mostly 
# mastered" in the UI.
MOSTLY_MASTERED_REPETITIONS_THRESHOLD = 2

# The percent mastery for facts that meet the minimum repetitions threshold for 
# being considered "partly mastered" but do not meet the full or mostly mastered 
# thresholds.
PART_MASTERY_PERCENT = 0.25
# The minimum `repetitions` necessary for a fact to be considered partly 
# mastered.
PART_MASTERY_REPETITIONS_THRESHOLD = 1

def schedule(progress: UserFactProgress, grade: Grade, now: datetime) -> UserFactProgress:
    if grade < 2:
        progress.repetitions = 0
        progress.intervalDays = 1
    else:
        progress.repetitions += 1
        if progress.repetitions == 1:
            progress.intervalDays = 1
        elif progress.repetitions == 2:
            progress.intervalDays = 3
        else:
            progress.intervalDays = round(progress.intervalDays * progress.ease)

    # grade 3: +0.10
    # grade 2: +0.00
    # grade 1: -0.14
    # grade 0: -0.32
    progress.ease = max(
        1.3,
        progress.ease + (0.1 - (3 - grade) * (0.08 + (3 - grade) * 0.02))
    )

    progress.lastReviewedAt = now.isoformat()
    progress.dueAt = (now + timedelta(days=progress.intervalDays)).isoformat()

    return progress

def create_initial_progress(user_id: str, fact_id: str, now: datetime) -> UserFactProgress:
    return UserFactProgress(
        id=UserFactProgress.create_id(user_id, fact_id),
        userId=user_id,
        factId=fact_id,
        intervalDays=0,
        ease=2.5,
        repetitions=0,
        dueAt=now.isoformat(),
        lastReviewedAt=None,
    )

def get_mastery_percent(progress: UserFactProgress) -> float:
    if progress.ease >= MASTERY_EASE_THRESHOLD \
       and progress.repetitions >= MASTERY_REPETITIONS_THRESHOLD:
        return 1
    elif progress.repetitions >= MOSTLY_MASTERED_REPETITIONS_THRESHOLD:
        return MOSTLY_MASTERED_PERCENT
    elif progress.repetitions >= PART_MASTERY_REPETITIONS_THRESHOLD:
        return PART_MASTERY_PERCENT
    return 0
    
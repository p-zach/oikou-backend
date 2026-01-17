from datetime import datetime, timedelta
from shared.models.spaced_repetition import UserFactProgress, Grade

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

from datetime import datetime, timedelta
from shared.models.spaced_repetition import UserFactProgress, Grade

def schedule(progress: UserFactProgress, grade: Grade, now: datetime):
    if grade < 2:
        progress.repetitions = 0
        progress.interval_days = 1
    else:
        progress.repetitions += 1
        if progress.repetitions == 1:
            progress.interval_days = 1
        elif progress.repetitions == 2:
            progress.interval_days = 3
        else:
            progress.interval_days = round(
                progress.interval_days * progress.ease
            )

    progress.ease = max(
        1.3,
        progress.ease + (0.1 - (3 - grade) * (0.08 + (3 - grade) * 0.02))
    )

    progress.last_reviewed_at = now.isoformat()
    progress.due_at = (now + timedelta(days=progress.interval_days)).isoformat()

def create_initial_progress(user_id: str, fact_id: str, now: datetime) -> UserFactProgress:
    return UserFactProgress(
        id=UserFactProgress.create_id(user_id, fact_id),
        user_id=user_id,
        fact_id=fact_id,
        interval_days=0,
        ease=2.5,
        repetitions=0,
        due_at=now.isoformat(),
        last_reviewed_at=None,
    )

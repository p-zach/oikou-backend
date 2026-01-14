import random
import uuid
from shared.cosmos_client import get_container

def start_lesson(userId: str, region: str, subject: str, question_count: int) -> dict:
    all_facts = get_container("facts")
    subject_facts = list(
        all_facts.query_items(
            query="SELECT * FROM f WHERE f.subject = @subject",
            parameters=[
                {"name": "@subject", "value": subject},
            ],
        )
    )

    if len(subject_facts) < question_count:
        raise ValueError("Not enough facts available for the requested subject")
    
    selected_facts = random.sample(subject_facts, question_count)

    questions = []
    for fact in selected_facts:
        question = {
            "itemId": fact["id"],
            "prompt": f"What is the capital of {fact['country']}?",
            "correctAnswer": fact["answer"],
            "choices": random.sample(
                [f["answer"] for f in subject_facts if f["id"] != fact["id"]],
                k=3
            ) + [fact["answer"]],
        }
        random.shuffle(question["choices"])
        questions.append(question)

    lesson = {
        "lessonId": str(uuid.uuid4()),
        "questions": questions,
    }

    return lesson
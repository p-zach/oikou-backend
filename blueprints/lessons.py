import json
import logging
import azure.functions as func
from blueprints.utils.router import get_router
from shared.lessons import start_lesson, complete_lesson

lessons_bp = func.Blueprint()
versioned = get_router("v1").route

@lessons_bp.route(route=versioned("lesson/start"), methods=["POST"])
def lesson_start(req: func.HttpRequest) -> func.HttpResponse:
    try:
        user_id = req.headers.get("X-User-Id")
        if not user_id:
            return func.HttpResponse("Missing X-User-Id header", status_code=400)
        
        req_body = req.get_json()
        region = req_body.get("region")
        subject = req_body.get("subject")
        question_count = req_body.get("questionCount")

        if not all([region, subject, question_count]):
            return func.HttpResponse(
                "Missing one or more required fields in request (region, subject, questionCount)", 
                status_code=400
            )
        
        lesson = start_lesson(user_id, region, subject, question_count)

        return func.HttpResponse(json.dumps(lesson), status_code=200, mimetype="application/json")
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse("Error processing request.", status_code=500)

@lessons_bp.route(route=versioned("lesson/complete"), methods=["POST"])
def lesson_complete(req: func.HttpRequest) -> func.HttpResponse:
    try:
        user_id = req.headers.get("X-User-Id")
        if not user_id:
            return func.HttpResponse("Missing X-User-Id header", status_code=400)

        req_body = req.get_json()
        session_id = req_body.get("sessionId")
        results = req_body.get("results")

        if not all([session_id, results]):
            return func.HttpResponse(
                "Missing one or more required fields in request (sessionId, results)", 
                status_code=400
            )

        complete_lesson(user_id, session_id, results)

        return func.HttpResponse(status_code=204)
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse("Error processing request.", status_code=500)

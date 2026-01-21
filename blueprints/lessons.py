import json
import logging
from http import HTTPStatus
import azure.functions as func

from blueprints.utils.router import v1
from shared.lessons import start_lesson, complete_lesson

lessons_bp = func.Blueprint()

@lessons_bp.route(route=v1("lesson/start"), methods=["POST"])
def lesson_start(req: func.HttpRequest) -> func.HttpResponse:
    try:
        user_id = req.headers.get("X-User-Id")
        if not user_id:
            return func.HttpResponse(
                "Missing X-User-Id header", 
                status_code=HTTPStatus.BAD_REQUEST
            )
        
        req_body = req.get_json()
        region = req_body.get("region")
        subject = req_body.get("subject")
        question_count = req_body.get("questionCount")

        if not all([region, subject, question_count]):
            return func.HttpResponse(
                "Missing one or more required fields in request (region, subject, questionCount)", 
                status_code=HTTPStatus.BAD_REQUEST
            )
        
        lesson = start_lesson(user_id, region, subject, question_count)

        return func.HttpResponse(
            json.dumps(lesson), 
            status_code=HTTPStatus.OK, 
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse(
            "Error processing request", 
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )

@lessons_bp.route(route=v1("lesson/complete"), methods=["POST"])
def lesson_complete(req: func.HttpRequest) -> func.HttpResponse:
    try:
        user_id = req.headers.get("X-User-Id")
        if not user_id:
            return func.HttpResponse(
                "Missing X-User-Id header", 
                status_code=HTTPStatus.BAD_REQUEST
            )

        req_body = req.get_json()
        session_id = req_body.get("sessionId")
        results = req_body.get("results")

        if not all([session_id, results]):
            return func.HttpResponse(
                "Missing one or more required fields in request (sessionId, results)", 
                status_code=HTTPStatus.BAD_REQUEST
            )

        complete_lesson(user_id, session_id, results)

        return func.HttpResponse(status_code=HTTPStatus.NO_CONTENT)
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse(
            "Error processing request", 
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )

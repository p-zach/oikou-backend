import json
import logging
from http import HTTPStatus
import azure.functions as func
from typing import cast

from blueprints.utils.router import v1
from shared.progress import get_mastery

from shared.models.lesson import LessonSubject

mastery_bp = func.Blueprint()

@mastery_bp.route(route=v1("mastery/summary"), methods=["GET"])
def get_mastery_summary(req: func.HttpRequest) -> func.HttpResponse:
    try:
        user_id = req.headers.get("X-User-Id") or req.params.get("user")
        if not user_id:
            return func.HttpResponse(
                "Specify X-User-Id header or user parameter", 
                status_code=HTTPStatus.BAD_REQUEST
            )

        region = req.params.get("region")
        subject = cast(LessonSubject | None, req.params.get("subject"))
        
        mastery = get_mastery(user_id, region, subject)

        return func.HttpResponse(
            json.dumps(mastery),
            status_code=HTTPStatus.OK, 
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse(
            "Error processing request", 
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )

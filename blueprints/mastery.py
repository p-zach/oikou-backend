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

        regions = req.params.get("regions")
        subjects = req.params.get("subjects")

        region_list = regions.split(',') if regions is not None else []
        subject_list = cast(
            list[LessonSubject] | None, 
            subjects.split(',') if subjects is not None else None
        )
        
        mastery = get_mastery(user_id, region_list, subject_list)

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

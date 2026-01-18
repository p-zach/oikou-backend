import json
import logging
from http import HTTPStatus
import azure.functions as func

from blueprints.utils.router import get_router
from shared.facts import get_specific_facts

facts_bp = func.Blueprint()
versioned = get_router("v1").route

FACTS_CONTAINER_NAME = "facts"

@facts_bp.route(route=versioned("facts"), methods=["GET"])
def get_facts(req: func.HttpRequest) -> func.HttpResponse:
    try:
        fact_ids_param = req.params.get("fact_ids")
        subject = req.params.get("subject")

        if fact_ids_param is None:
            return func.HttpResponse(
                "Missing required parameter fact_ids", 
                status_code=HTTPStatus.BAD_REQUEST
            )

        fact_ids = fact_ids_param.split(',')

        facts = get_specific_facts(fact_ids, subject)

        return func.HttpResponse(
            json.dumps(facts),
            status_code=HTTPStatus.OK, 
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse(
            "Error processing request", 
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )

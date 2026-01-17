import json
import azure.functions as func
from shared.lessons import start_lesson, complete_lesson

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="lesson/start", methods=["POST"])
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
        return func.HttpResponse(f"Error processing request: {e}", status_code=500)

@app.route(route="lesson/complete", methods=["POST"])
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
        return func.HttpResponse(f"Error processing request: {e}", status_code=500)

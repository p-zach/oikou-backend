import json
import azure.functions as func
from shared.lesson import start_lesson

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="lesson/start", methods=["POST"])
def lesson_start(req: func.HttpRequest) -> func.HttpResponse:
    try:
        userId = req.headers.get("X-User-Id")
        if not userId:
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
        
        lesson = start_lesson(userId, region, subject, question_count)

        return func.HttpResponse(json.dumps(lesson), status_code=200, mimetype="application/json")
    except:
        return func.HttpResponse("Error processing request.", status_code=500)
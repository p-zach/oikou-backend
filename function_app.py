import http
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="test", methods=["GET"])
def test(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Test successful! Request is: " + str(req), status_code=http.HTTPStatus.OK)
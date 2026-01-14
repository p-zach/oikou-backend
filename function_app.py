import azure.functions as func
from shared.cosmos_client import return_5

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="test", methods=["GET"])
def test(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Hello, world! " + str(return_5()), status_code=200)
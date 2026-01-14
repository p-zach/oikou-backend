import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="test", methods=["GET"])
def test(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Hello, world!", status_code=200)
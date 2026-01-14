import azure.functions as func
from shared.cosmos_client import get_container

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="test", methods=["GET"])
def test(req: func.HttpRequest) -> func.HttpResponse:
    try:
        container = get_container("facts")
        items = list(container.query_items(
            query="SELECT * FROM c",
            enable_cross_partition_query=True
        ))
        return func.HttpResponse(items[0]["id"])
    except Exception as e:
        return func.HttpResponse(
            str(e),
            status_code=500
        )
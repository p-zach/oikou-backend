import json
import azure.functions as func
# from shared.cosmos_client import get_container
# import azure.cosmos

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="test", methods=["GET"])
def test(req: func.HttpRequest) -> func.HttpResponse:
    # container = get_container("facts")
    # items = list(
    #     container.query_items(
    #         query="SELECT * FROM c",
    #         enable_cross_partition_query=True
    #     )
    # )

    return func.HttpResponse(
        # json.dumps(items),
        '{"val": "test with importing get_container"}',
        mimetype="application/json"
    )
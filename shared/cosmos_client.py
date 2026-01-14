import os
from azure.cosmos import CosmosClient, DatabaseProxy, ContainerProxy

# Lazy initialization of shared values
_client = None
_database = None

def get_database() -> DatabaseProxy:
    global _client, _database

    if _client is None:
        endpoint = os.environ.get("COSMOS_DB_ENDPOINT")
        key = os.environ.get("COSMOS_DB_KEY")
        database_name = os.environ.get("COSMOS_DB_DATABASE")

        if not all([endpoint, key, database_name]):
            raise RuntimeError("Missing CosmosDB environment variables")

        _client = CosmosClient(endpoint, key)
        _database = _client.get_database_client(database_name)

    return _database

def get_container(container_name: str) -> ContainerProxy:
    return get_database().get_container_client(container_name)

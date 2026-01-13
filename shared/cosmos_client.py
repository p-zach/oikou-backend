import os
from azure.cosmos import CosmosClient, ContainerProxy

endpoint = os.environ["COSMOS_DB_ENDPOINT"]
key = os.environ["COSMOS_DB_KEY"]
database_name = os.environ["COSMOS_DB_DATABASE"]

client = CosmosClient(endpoint, key)
database = client.get_database_client(database_name)

def get_container(container_name: str) -> ContainerProxy:
    return database.get_container_client(container_name)
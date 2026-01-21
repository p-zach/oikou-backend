from azure.cosmos import ContainerProxy

from shared.cosmos_client import get_container as _get_cosmos_container

# Constants
FACTS_CONTAINER_NAME = "facts"
REGIONS_CONTAINER_NAME = "regions"
USER_FACT_PROGRESS_CONTAINER_NAME = "user_fact_progress"

# Initialized globals
_containers: dict[str, ContainerProxy | None] = {
    FACTS_CONTAINER_NAME: None,
    REGIONS_CONTAINER_NAME: None,
    USER_FACT_PROGRESS_CONTAINER_NAME: None,
}

### Public functions

def query_simple(container_name: str, parameters: dict, enable_cross_partition_query: bool | None = None) -> list[dict]:
    """Query items from the specified container with a simple SELECT * query and given parameters.
    Parameters are given in the form {"param_name": param_value, ...}.
    """
    query = "SELECT * FROM c"
    param_list = [
        {"name": f"@{key}", "value": value}
        for key, value in parameters.items()
    ]
    if len(param_list) > 0:
        where_clauses = [f"c.{key} = @{key}" for key in parameters.keys()]
        query += " WHERE " + " AND ".join(where_clauses)
    return query_items(
        container_name=container_name,
        query=query,
        parameters=param_list,
        enable_cross_partition_query=enable_cross_partition_query
    )

def query_items(container_name: str, query: str, parameters: list[dict], enable_cross_partition_query: bool | None = None) -> list[dict]:
    """Query items from the specified container."""
    container = _get_container(container_name)
    return list(container.query_items(query=query, parameters=parameters, enable_cross_partition_query=enable_cross_partition_query))

def upsert_item(container_name: str, item: dict) -> dict:
    """Upsert an item into the specified container."""
    container = _get_container(container_name)
    return container.upsert_item(item)

### Helper functions

def _get_container(container_name: str) -> ContainerProxy:
    """Get the Cosmos DB container with the given name."""
    global _containers
    if _containers[container_name] is None:
        _containers[container_name] = _get_cosmos_container(container_name)
    return _containers[container_name] # type: ignore
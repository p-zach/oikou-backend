from azure.cosmos import ContainerProxy

from shared.cosmos_client import get_container

from shared.models.fact import Fact, fact_from_dict

# Constants
FACTS_CONTAINER_NAME = "facts"

# Initialized globals
_facts_container = None

def get_specific_facts(fact_ids: list[str], subject: str | None) -> list[Fact]:
    """Get fact information for all facts listed in fact_ids."""
    facts_container = _get_facts_container()
    query = "SELECT * FROM f"
    if subject is not None:
        query += " WHERE f.subject = @subject"
    facts: list[Fact] = [
        fact_from_dict(fact_dict)
        for fact_dict in facts_container.query_items(
            query=query,
            parameters=[
                {"name": "@subject", "value": subject},
            ],
            enable_cross_partition_query=subject is None
        )
        if fact_dict["id"] in fact_ids
    ]
    return facts

def get_all_subject_facts(subject: str) -> list[Fact]:
    """Get all facts matching the given subject."""
    facts_container = _get_facts_container()
    subject_facts: list[Fact] = [
        fact_from_dict(fact_dict)
        for fact_dict in facts_container.query_items(
            query="SELECT * FROM f WHERE f.subject = @subject",
            parameters=[
                {"name": "@subject", "value": subject},
            ],
            enable_cross_partition_query=False
        )
    ]
    return subject_facts

# Utilities
def _get_facts_container() -> ContainerProxy:
    global _facts_container

    if _facts_container is None:
        _facts_container = get_container(FACTS_CONTAINER_NAME)
    return _facts_container
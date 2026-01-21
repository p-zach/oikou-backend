from azure.cosmos import ContainerProxy

from shared.cosmos_client import get_container

from shared.models.fact import Fact, fact_from_dict

# Constants
FACTS_CONTAINER_NAME = "facts"
REGIONS_CONTAINER_NAME = "regions"

# Initialized globals
_facts_container = None
_regions_container = None

def get_specific_facts(fact_ids: list[str], subject: str | None) -> list[Fact]:
    """Get fact information for all facts listed in fact_ids."""
    facts_container = _get_facts_container()
    query = "SELECT * FROM f"
    if subject is not None:
        query += " WHERE f.subject = @subject"
    # TODO: Extract all DB queries to a shared utility module
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

def get_all_subject_facts(subject: str, region: str | None = None) -> list[Fact]:
    """Get all facts matching the given subject and optional region."""
    facts_container = _get_facts_container()
    # TODO: Extract all DB queries to a shared utility module
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
    if region is None:
        return subject_facts
    
    regions_container = _get_regions_container()
    # TODO: Extract all DB queries to a shared utility module
    region_items = list(regions_container.query_items(
        query="SELECT * FROM r WHERE r.region = @region",
        parameters=[
            {"name": "@region", "value": region},
        ],
        enable_cross_partition_query=False
    ))
    country_codes_in_region = set(
        region_item["countryCode"] for region_item in region_items
    )

    region_facts: list[Fact] = [
        fact for fact in subject_facts
        if fact["countryCode"] in country_codes_in_region
    ]
    return region_facts

# Utilities
def _get_facts_container() -> ContainerProxy:
    global _facts_container

    if _facts_container is None:
        _facts_container = get_container(FACTS_CONTAINER_NAME)
    return _facts_container

def _get_regions_container() -> ContainerProxy:
    global _regions_container

    if _regions_container is None:
        _regions_container = get_container(REGIONS_CONTAINER_NAME)
    return _regions_container
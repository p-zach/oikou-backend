from shared.db import FACTS_CONTAINER_NAME, REGIONS_CONTAINER_NAME, query_simple

from shared.models.fact import Fact, fact_from_dict

def get_specific_facts(fact_ids: list[str], subject: str | None) -> list[Fact]:
    """Get fact information for all facts listed in fact_ids."""
    facts: list[Fact] = [
        fact_from_dict(fact_dict)
        for fact_dict in query_simple(
            container_name=FACTS_CONTAINER_NAME,
            parameters={ "subject": subject } if subject is not None else {},
            enable_cross_partition_query=subject is None
        )
        if fact_dict["id"] in fact_ids
    ]
    return facts

def get_all_subject_facts(subject: str, region: str | None = None) -> list[Fact]:
    """Get all facts matching the given subject and optional region."""
    subject_facts: list[Fact] = [
        fact_from_dict(fact_dict)
        for fact_dict in query_simple(
            container_name=FACTS_CONTAINER_NAME,
            parameters={ "subject": subject }
        )
    ]
    if region is None:
        return subject_facts
    
    region_items = query_simple(
        container_name=REGIONS_CONTAINER_NAME,
        parameters={ "region": region }
    )
    country_codes_in_region = set(
        region_item["countryCode"] for region_item in region_items
    )

    region_facts: list[Fact] = [
        fact for fact in subject_facts
        if fact["countryCode"] in country_codes_in_region
    ]
    return region_facts

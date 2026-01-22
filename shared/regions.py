from shared.db import REGIONS_CONTAINER_NAME, query_simple

def get_country_codes_in_region(region: str) -> set[str]:
    region_items = query_simple(
        container_name=REGIONS_CONTAINER_NAME,
        parameters={ "region": region }
    )
    return set(region_item["countryCode"] for region_item in region_items)

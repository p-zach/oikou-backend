from typing import TypedDict

class Fact(TypedDict):
    id: str
    subject: str
    countryCode: str
    country: str
    answer: str
    
def fact_from_dict(d: dict) -> Fact:
    field_names = Fact.__annotations__.keys()
    filtered = {k: v for k, v in d.items() if k in field_names}
    return Fact(**filtered)

def is_fact_in_subject(fact_id: str, subject: str) -> bool:
    # Fact IDs are like "subject:COUNTRY_CODE[:rev]"
    return fact_id.split(':')[0] == subject

def get_fact_country_code(fact_id: str) -> str:
    return fact_id.split(':')[1]
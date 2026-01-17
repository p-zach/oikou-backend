from typing import TypedDict

class Fact(TypedDict):
    id: str
    subject: str
    countryCode: str
    country: str
    answer: str

def fact_in_subject(fact_id: str, subject: str) -> bool:
    # Fact IDs are like "subject:COUNTRY_CODE[:rev]"
    return fact_id.split(':')[0] == subject
from pydantic import BaseModel

TARGET_FORMS = [
    "10-K", "10-K/A", "10-Q", "10-Q/A", "20-F", "20-F/A",
    "40-F", "40-F/A", "6-K", "6-K/A",
]

# Chunk sizes in characters.
# Roughly, 1 token is approximately 4 characters. 
# So 2000 chars is ~500 tokens.
CHUNK_SIZES_CHARS = [
    1000, 2000, 3300
]


SectionTypes = {
    "SEGMENT_REVENUE": "This excerpt discloses revenue, sales, or financial performance explicitly broken down by official reportable or operating business segments. Look for tables or text discussing 'Segment Results', 'Operating Segments', or revenue attributed to specific product lines or divisions. Exclude general company-wide consolidated revenue.",
    "GEOGRAPHIC_REVENUE": "This excerpt discloses revenue or sales broken down by customer geography, region, country, or destination (e.g., 'North America', 'EMEA', 'Asia Pacific', 'International'). Look for geographic breakdowns of net sales. Exclude discussions of geographic physical assets or property unless revenue is explicitly tied to them.",
    "SIGNIFICANT_CUSTOMERS": "This excerpt discloses major customer concentration, specifically identifying customers that account for a significant share (often 10% or more) of total consolidated revenue. Look for mentions of 'major customer', 'significant customer', or specific percentages of revenue tied to a single client or group of clients.",
    "OTHER": "Use this category if the text chunk does not contain any specific disclosures about segment revenue, geographic revenue, or significant customers. This includes general business desciprtions, risk factors, general MD&A, or unrelated financial data."
}

class ExtractedSections(BaseModel):
    types: list = list(SectionTypes.keys())
    version: str = "1"

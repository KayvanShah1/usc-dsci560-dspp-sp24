from typing import List, Optional
from pydantic import BaseModel


class CleanWellData(BaseModel):
    api_no: str
    closest_city: Optional[str]
    county: str
    latest_barrels_of_oil_produced: Optional[str]
    latest_mcf_of_gas_produced: Optional[str]
    latitude: float
    link: str
    longitude: float
    operator: str
    well_name: Optional[str]
    well_status: Optional[str]
    well_type: Optional[str]


class WellsData(BaseModel):
    data: List[CleanWellData]

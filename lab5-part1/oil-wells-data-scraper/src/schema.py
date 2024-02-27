from typing import Optional
from pydantic import BaseModel


class RawWellData(BaseModel):
    api_no: str
    county: str
    date_simulated: str
    datum: str
    filename: str
    formation: str
    job_id: int
    job_type: str
    latitude: str
    lbs: str
    longitude: str
    max_treatment_rate: str
    operator: str
    psi: str
    top_bottom_stimulation_stages: str
    type_treatment: str
    volume: str
    well_file_no: int
    well_name: str


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

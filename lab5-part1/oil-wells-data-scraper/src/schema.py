from datetime import datetime
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


class WellTreatment(BaseModel):
    file_id: str
    api_no: str
    date_stimulated: Optional[datetime]
    stimulated_formation: Optional[str]
    top_ft: Optional[float]
    bottom_ft: Optional[float]
    stimulation_stages: Optional[float]
    volume: Optional[float]
    volume_units: Optional[str]
    type_treatment: Optional[str]
    lbs_proppant: Optional[float]
    maximum_treatment_pressure_psi: Optional[float]
    maximum_treatment_rate_bbls_per_min: Optional[float]


class WellDetails(BaseModel):
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
    date_stimulated: Optional[datetime]
    stimulated_formation: Optional[str]
    top_ft: Optional[float]
    bottom_ft: Optional[float]
    stimulation_stages: Optional[float]
    volume: Optional[float]
    volume_units: Optional[str]
    type_treatment: Optional[str]
    lbs_proppant: Optional[float]
    maximum_treatment_pressure_psi: Optional[float]
    maximum_treatment_rate_bbls_per_min: Optional[float]

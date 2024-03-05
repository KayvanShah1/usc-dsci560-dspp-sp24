from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


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


class WellsData(BaseModel):
    data: List[WellDetails]

    def convert_to_geojson(self) -> dict:
        """
        Convert the WellsData object to GeoJSON format.

        Args:
            wells_data (WellsData): Input data containing well information.

        Returns:
            Dict: GeoJSON representation of the well data.
        """
        features = []
        for well in self.data:
            feature = {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [well.longitude, well.latitude]},
                "properties": {
                    "api_no": well.api_no,
                    "location": {
                        "closest_city": well.closest_city,
                        "county": well.county,
                        "latitude": well.latitude,
                        "longitude": well.longitude,
                    },
                    "production": {
                        "latest_barrels_of_oil_produced": well.latest_barrels_of_oil_produced,
                        "latest_mcf_of_gas_produced": well.latest_mcf_of_gas_produced,
                    },
                    "details": {
                        "link": well.link,
                        "operator": well.operator,
                        "well_name": well.well_name,
                        "well_status": well.well_status,
                        "well_type": well.well_type,
                    },
                    "stimulation_details": {
                        "date_stimulated": well.date_stimulated,
                        "stimulated_formation": well.stimulated_formation,
                        "top_ft": well.top_ft,
                        "bottom_ft": well.bottom_ft,
                        "stimulation_stages": well.stimulation_stages,
                        "volume": well.volume,
                        "volume_units": well.volume_units,
                        "type_treatment": well.type_treatment,
                        "lbs_proppant": well.lbs_proppant,
                        "maximum_treatment_pressure_psi": well.maximum_treatment_pressure_psi,
                        "maximum_treatment_rate_bbls_per_min": well.maximum_treatment_rate_bbls_per_min,
                    },
                },
            }

            # Replace None values with "N/A" in stimulation_details
            for key, value in feature["properties"]["stimulation_details"].items():
                if value is None:
                    feature["properties"]["stimulation_details"][key] = "N/A"

            features.append(feature)

        return {"type": "FeatureCollection", "features": features}

    def compute_center(self) -> List[float]:
        """
        Compute the center of the map based on the latitude and longitude values.

        Args:
            wells_data (WellsData): Input data containing well information.

        Returns:
            List[float]: Latitude and longitude values of the center.
        """
        total_lat = sum(well.latitude for well in self.data)
        total_lon = sum(well.longitude for well in self.data)
        num_wells = len(self.data)
        center_lat = total_lat / num_wells
        center_lon = total_lon / num_wells
        return [center_lat, center_lon]

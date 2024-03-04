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
                    "closest_city": well.closest_city,
                    "county": well.county,
                    "latest_barrels_of_oil_produced": well.latest_barrels_of_oil_produced,
                    "latest_mcf_of_gas_produced": well.latest_mcf_of_gas_produced,
                    "link": well.link,
                    "operator": well.operator,
                    "well_name": well.well_name,
                    "well_status": well.well_status,
                    "well_type": well.well_type,
                },
            }
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

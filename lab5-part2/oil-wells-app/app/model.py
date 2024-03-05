from app.database import Base, engine
from sqlalchemy import Column, DateTime, Float, String, Text


# Define the CleanWellData table model
class CleanWellDataModel(Base):
    __tablename__ = "clean_well_data"

    api_no = Column(String(12), primary_key=True)
    closest_city = Column(Text)
    county = Column(Text)
    latest_barrels_of_oil_produced = Column(Text)
    latest_mcf_of_gas_produced = Column(Text)
    latitude = Column(Float)
    link = Column(Text)
    longitude = Column(Float)
    operator = Column(Text)
    well_name = Column(Text, nullable=False)
    well_status = Column(Text)
    well_type = Column(Text)


class WellTreatmentSQLModel(Base):
    __tablename__ = "well_treatments"

    file_id = Column(Text)
    api_no = Column(String(12), primary_key=True)
    date_stimulated = Column(DateTime)
    stimulated_formation = Column(Text)
    top_ft = Column(Float)
    bottom_ft = Column(Float)
    stimulation_stages = Column(Float)
    volume = Column(Float)
    volume_units = Column(Text)
    type_treatment = Column(Text)
    lbs_proppant = Column(Float)
    maximum_treatment_pressure_psi = Column(Float)
    maximum_treatment_rate_bbls_per_min = Column(Float)


Base.metadata.create_all(engine)

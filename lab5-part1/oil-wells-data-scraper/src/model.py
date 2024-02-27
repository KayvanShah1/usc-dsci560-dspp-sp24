from database import Base, engine
from sqlalchemy import Column, Float, Integer, String, Text
from sqlalchemy.dialects.mysql import JSON


class RawWellDataModel(Base):
    __tablename__ = "raw_well_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_no = Column(JSON)
    county = Column(Text)
    date_simulated = Column(Text)
    datum = Column(Text)
    filename = Column(Text)
    formation = Column(Text)
    job_id = Column(Integer)
    job_type = Column(Text)
    latitude = Column(Text)
    lbs = Column(Text)
    longitude = Column(Text)
    max_treatment_rate = Column(Text)
    operator = Column(Text)
    psi = Column(Text)
    top_bottom_stimulation_stages = Column(Text)
    type_treatment = Column(Text)
    volume = Column(Text)
    well_file_no = Column(Integer)
    well_name = Column(Text)


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


Base.metadata.create_all(engine)

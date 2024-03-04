from database import Base, engine
from sqlalchemy import Column, Float, String, Text


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

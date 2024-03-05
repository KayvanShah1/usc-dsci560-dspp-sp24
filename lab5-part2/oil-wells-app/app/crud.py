from app.model import CleanWellDataModel, WellTreatmentSQLModel
import app.schema as schema
from app.settings import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__file__)


def get_well_data(db: Session):
    """
    Retrieve all oil wells data from clean table

    Args:
        db (Session): SQLAlchemy database session.
    """
    # posts = db.query(CleanWellDataModel).all()
    posts = (
        db.query(
            CleanWellDataModel,
            WellTreatmentSQLModel.date_stimulated,
            WellTreatmentSQLModel.stimulated_formation,
            WellTreatmentSQLModel.top_ft,
            WellTreatmentSQLModel.bottom_ft,
            WellTreatmentSQLModel.stimulation_stages,
            WellTreatmentSQLModel.volume,
            WellTreatmentSQLModel.volume_units,
            WellTreatmentSQLModel.type_treatment,
            WellTreatmentSQLModel.lbs_proppant,
            WellTreatmentSQLModel.maximum_treatment_pressure_psi,
            WellTreatmentSQLModel.maximum_treatment_rate_bbls_per_min,
        )
        .outerjoin(WellTreatmentSQLModel, CleanWellDataModel.api_no == WellTreatmentSQLModel.api_no)
        .all()
    )

    result_dicts = []
    for row in posts:
        clean_well_data_dict = row[0].__dict__
        treatment_data_dict = {
            "date_stimulated": row[1],
            "stimulated_formation": row[2],
            "top_ft": row[3],
            "bottom_ft": row[4],
            "stimulation_stages": row[5],
            "volume": row[6],
            "volume_units": row[7],
            "type_treatment": row[8],
            "lbs_proppant": row[9],
            "maximum_treatment_pressure_psi": row[10],
            "maximum_treatment_rate_bbls_per_min": row[11],
        }
        result_dicts.append({**clean_well_data_dict, **treatment_data_dict})

    posts = schema.WellsData(data=[schema.WellDetails(**post) for post in result_dicts])
    return posts

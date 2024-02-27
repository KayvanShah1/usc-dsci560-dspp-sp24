import glob
import os

import schema
from crud import bulk_ingest_clean, bulk_ingest_raw, document_exists, get_all_ids
from database import get_db
from extract import extract_data_from_text_file, get_well_details
from settings import Path
from tqdm import tqdm

db = get_db()


def ingest_raw_data():
    docs = []

    text_file_paths = glob.glob(os.path.join(Path.data_text_dir, "*.txt"))
    for i in tqdm(text_file_paths):
        res = extract_data_from_text_file(i)
        res = schema.RawWellData(**res)
        docs.append(res)

    bulk_ingest_raw(docs, db)


def fetch_and_ingest_clean_data():
    clean_documents = []

    unique_ids = get_all_ids(db)
    for api_id in tqdm(unique_ids):
        if not document_exists(api_id, db):
            well_details = get_well_details(api_no=api_id)
            well_details = schema.CleanWellData(**well_details)
            if well_details.well_name is not None:
                clean_documents.append(well_details)
    bulk_ingest_clean(clean_documents, db)


if __name__ == "__main__":
    ingest_raw_data()
    fetch_and_ingest_clean_data()

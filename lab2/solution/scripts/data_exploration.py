import logging
import os
import re
import shutil
from typing import List
from urllib.parse import urljoin, urlsplit

import fitz
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)


class Path:
    file_dir = os.path.dirname(__file__)
    root_dir = os.path.dirname(file_dir)

    data_dir = os.path.join(root_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    COURSE_DATA_SAVE_PATH = os.path.join(data_dir, "ml_course.csv")
    PDF_FILE_DIR = os.path.join(data_dir, "pdfs")
    os.makedirs(PDF_FILE_DIR, exist_ok=True)


class Settings:
    SITE_URL: str = "https://www.cs.cmu.edu/~ninamf/courses/601sp15/lectures.shtml"
    BASE_URL: str = "https://www.cs.cmu.edu/~ninamf/courses/601sp15/"


class Topic(BaseModel):
    name: str | None


class ReadingUsefulLinks(BaseModel):
    name: str
    link: str | None


class CourseItem(BaseModel):
    lecture: str
    topics: List[Topic]
    readings: List[ReadingUsefulLinks]
    handouts: List[ReadingUsefulLinks]

    class Config:
        arbitrary_types_allowed = True


def is_relative_url(link):
    parsed_url = urlsplit(link)
    return not parsed_url.scheme and not parsed_url.netloc


def get_lecture_info(columns):
    lecture = re.sub(r"\s+", " ", columns[1].get_text(separator=" ")).strip()
    topics = columns[2].find_all("li")
    topics_list = [Topic(name=re.sub(r"\s+", " ", detail.text).strip()) for detail in topics]
    return lecture, topics_list


def get_handouts(columns):
    slides_video_links = columns[4].find_all("a")
    handouts = [
        ReadingUsefulLinks(
            name=link.text.strip(),
            link=(
                urljoin(Settings.BASE_URL, link["href"])
                if is_relative_url(link["href"])
                else link["href"]
            ),
        )
        for link in slides_video_links
    ]
    return handouts


def get_readings(columns):
    readings_links = columns[3].find_all("a")
    readings = [
        ReadingUsefulLinks(name=re.sub(r"\s+", " ", link.text).strip(), link=link["href"])
        for link in readings_links
    ]

    other_readings = re.sub(r"\s+", " ", columns[3].get_text(separator=" ")).strip()
    if len(readings) > 0:
        for r in readings:
            other_readings = other_readings.replace(r.name, "").strip()
    if other_readings != "":
        readings.append(ReadingUsefulLinks(name=other_readings, link=None))
    return readings


def scrape_course_page():
    try:
        resp = requests.get(Settings.SITE_URL)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        table = soup.find("table", class_="schedule")
        if table:
            table_body = table.find("tbody")
            if table_body:
                items = table_body.find_all("tr")[1:]

                course_items = []
                for item in items:
                    columns = item.find_all("td")

                    if len(columns) == 5:
                        lecture, topics_list = get_lecture_info(columns)
                        handouts = get_handouts(columns)
                        readings = get_readings(columns)

                        course_item = CourseItem(
                            lecture=lecture,
                            topics=topics_list,
                            readings=readings,
                            handouts=handouts,
                        )
                        course_items.append(course_item.model_dump())

                return course_items
            else:
                logging.warning("No tbody found in the table.")
        else:
            logging.warning("No schedule table found on the page.")
    except requests.exceptions.RequestException as e:
        logging.exception(f"Error during HTTP request: {e}")
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")


def read_pdf_from_url(url, output_folder):
    try:
        # Create the output folder if it doesn't exist
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)

        os.makedirs(output_folder, exist_ok=True)

        # Download the PDF file
        pdf_data = requests.get(url).content

        # Open the PDF document
        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")

        # Iterate through pages
        for page_number in range(pdf_document.page_count):
            # Get text content of the page
            page = pdf_document[page_number]
            text = page.get_text()

            # Create a text file for each page
            output_file_path = os.path.join(output_folder, f"page_{page_number + 1}.txt")
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                output_file.write(text)

        logging.info(f"Text files for each page created in `{os.path.relpath(output_folder)}`")

        # Close the PDF document
        pdf_document.close()

    except Exception as e:
        logging.exception(f"Error: {e}")


def extract_text_from_pdfs(data):
    for row in tqdm(data.to_dict(orient="records")):
        title = row["lecture"].replace(" ", "_").lower()
        handouts = [item for item in eval(row["handouts"]) if item["name"] == "Slides"]

        output_dir = os.path.join(Path.PDF_FILE_DIR, title)
        for h in handouts:
            read_pdf_from_url(h["link"], output_dir)


def main():
    course_page_content = scrape_course_page()
    logging.info(f"Sample Course Items:\n{course_page_content[:2]}")
    course_page_content_df = pd.DataFrame(course_page_content)

    logging.info(course_page_content_df.head())
    logging.info(course_page_content_df.info())

    logging.info(f"Saving course details files to '{os.path.relpath(Path.COURSE_DATA_SAVE_PATH)}'")
    course_page_content_df.to_csv(Path.COURSE_DATA_SAVE_PATH, index=False)

    df = pd.read_csv(Path.COURSE_DATA_SAVE_PATH, usecols=["lecture", "handouts"])
    logging.info("Extracting data from PDF files...")
    extract_text_from_pdfs(df)


if __name__ == "__main__":
    main()

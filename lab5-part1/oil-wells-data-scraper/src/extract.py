import json
import os
import re

import requests
from bs4 import BeautifulSoup
from settings import config, get_logger

logger = get_logger(__file__)


class Patterns:
    api_no: str = (
        r"(?:\b\d{2}-\d{3}-\d{5}\b)|(?:\b\d{2} - \d{3} - \d{5}\b)|(?:^API(?:\s)?#:(?:\s)?\d{10}$)|(?:API(?:\s+)?\d{10})"
    )
    operator = r"Well Operator : (.*?)\n"
    well_name = r"Well Name\s*:\s*(.*)\n"
    job_id = r"\bJob (\d+)\b"
    job_type = r"Type of Incident : (.*?)\n"
    county = r"County : (.*?)\n"
    latitude = r"(\d+°\d+\'\d+\.\d+\"[NS])"
    longitude = r"(\d+°\d+\'\d+\.\d+\"[EW])"
    datum = r"Vertical Datum to DDZ\s+([\d.]+ ft)"

    date_simulated = r"Date Stimulated\s*\n\s*(\d{1,2}/\d{1,2}/\d{4})"
    formation = r"Stimulated Formation\s*\n\s*([^\n]+)"
    top_bottom_stimulation_stages = r"Top \(Ft\)\s*Bottom \(Ft\)\s*Stimulation Stages\n\s*(\d+)\s+(\d+)\s+(\d+)"
    psi = r"Maximum Treatment Pressure \(PSI\)\s*\n\s*(\d+)"
    lbs = r"Lbs Proppant\s*\n\s*(\d+)"
    type_treatment = r"Type Treatment\s*\n\s*([^\n]+)"
    volume = r"Volume Units\s*\n(\d+)\s*(\w+)"
    max_treatment_rate = r"Maximum Treatment Rate \(BBLS/Min\)\s*\n\s*(\d+(?:\.\d+)?)"


def get_data_by_th(soup, th_text):
    th = soup.find("th", string=th_text)
    if th and th.next_sibling:
        return th.next_sibling.get_text(strip=True)
    return None


def get_well_details(well_name=None, api_no=None):
    # Construct the first URL with parameters
    params = {
        "type": "wells",
    }
    if well_name:
        params["well_name"] = well_name
    if api_no:
        params["api_no"] = api_no

    results = {
        "api_no": api_no,
        "closest_city": None,
        "county": "",
        "latest_barrels_of_oil_produced": None,
        "latest_mcf_of_gas_produced": None,
        "latitude": 0.0,
        "link": "",
        "longitude": 0.0,
        "operator": "",
        "well_name": well_name,
        "well_status": None,
        "well_type": None,
    }

    response = requests.get(config.DRILLING_EDGE_BASE_SEARCH_URL, params=params)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the first href
        well_page_links = soup.find("table", class_="table wide-table interest_table").find("a")
        if well_page_links:
            well_page_link = well_page_links["href"]
            results["link"] = well_page_link
            response = requests.get(well_page_link)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")

                meta_info = soup.find("section", class_="meta_info")
                results["operator"] = meta_info.find_all("div")[2].find("span").text

                block_stats = meta_info.find_all("p", class_="block_stat")
                for stat in block_stats:
                    text = stat.get_text()
                    span_text = stat.find("span").text

                    text = text.replace(span_text, "").strip().split(" ")[:4]
                    text = " ".join(text).lower().replace(" ", "_")

                    results[f"latest_{text}"] = span_text.strip()

                well_table = soup.find("article", class_="well_table")
                if well_table:
                    results["well_status"] = get_data_by_th(well_table, "Well Status").strip()
                    results["well_type"] = get_data_by_th(well_table, "Well Type").strip()
                    results["closest_city"] = get_data_by_th(well_table, "Closest City").strip()
                    results["county"] = get_data_by_th(well_table, "County").strip()
                    results["well_name"] = get_data_by_th(well_table, "Well Name").strip()

            json_data_url = f"{well_page_link}?json"
            response = requests.get(json_data_url).json()
            results["latitude"] = float(response["data"][0]["lat"])
            results["longitude"] = float(response["data"][0]["lon"])
    return results


def find_api_no(text):
    api_id = set(re.findall(Patterns.api_no, text))
    api_id = [re.sub(r"[^\d-]", "", id) for id in api_id]

    api_id_final_pattern = r"(\d{2})(\d{3})(\d{5})"
    for i in range(len(api_id)):
        # Find all matches of the pattern in the string
        if len(api_id[i]) != 12:
            match = re.search(api_id_final_pattern, api_id[i])
            if match:
                # Format the match into 'XX-XXX-XXXXX' format
                api_id[i] = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

    return list(set(api_id))


def extract_data_from_text_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    filename = os.path.basename(filepath)
    well_file_no = int(re.sub("[a-zA-Z]", "", filename.split(".")[0]))
    results = {"filename": filename, "api_no": json.dumps(find_api_no(text)), "well_file_no": well_file_no}

    keys_encountered = set(results.keys())
    for key, pattern in dict(Patterns.__dict__).items():
        if "__" not in key:
            if key not in keys_encountered:
                results[key] = ""
                match = re.search(pattern, text)
                if match:
                    results[key] = match.group(1)
                    keys_encountered.add(key)
    if results["job_id"] == "":
        results["job_id"] = results["well_file_no"]
    return results

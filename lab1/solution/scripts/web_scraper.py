import logging
import os

import requests
from bs4 import BeautifulSoup
from chromedriver_py import binary_path
from pydantic_settings import BaseSettings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Path:
    file_dir = os.path.dirname(__file__)
    root_dir = os.path.dirname(file_dir)

    data_dir = os.path.join(root_dir, "data")


class Settings(BaseSettings):
    BASE_URL: str = "https://www.cnbc.com/world/?region=world"


def add_driver_options(options):
    """
    Add configurable options
    """
    chrome_options = Options()
    for opt in options:
        chrome_options.add_argument(opt)
    return chrome_options


def initialize_driver():
    """
    Initialize the web driver
    """
    driver_config = {
        "executable_path": binary_path,
        "options": [
            "--headless",
            "--no-sandbox",
            "--start-fullscreen",
            "--allow-insecure-localhost",
            "--disable-dev-shm-usage",
            "--log-level=3",
        ],
    }
    options = add_driver_options(driver_config["options"])
    driver = webdriver.Chrome(options=options)
    return driver


def save_html_page(page: BeautifulSoup, save_to: str):
    logging.info("Saving HTML page...")
    market_banner = page.find("div", class_="MarketsBanner-marketData").prettify()

    response = requests.get(Settings().BASE_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    latest_news = soup.find("ul", class_="LatestNews-list").prettify()

    # Save the collected data in the raw_data folder
    with open(save_to, "w", encoding="utf-8") as file:
        file.write(str(market_banner))
        file.write("\n\n")
        file.write(str(latest_news))

    logging.info("Successfully saved the HTML file to %s", save_to)


if __name__ == "__main__":
    settings = Settings()
    try:
        logging.info("Initializing the Chrome WebDriver...")
        driver = initialize_driver()
        logging.info("Getting the CNBC Web Page...")
        driver.get(settings.BASE_URL)

        logging.info("Waiting for the Market Cards rows to be populated...")
        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "MarketCard-row"))
        )
        page = BeautifulSoup(driver.page_source, "html.parser")

        EXTRACTED_HTML_PATH = os.path.join(Path.data_dir, "raw_data", "web_data.html")
        save_html_page(page, EXTRACTED_HTML_PATH)

        with open(EXTRACTED_HTML_PATH, "r", encoding="utf-8") as f:
            for _ in range(10):
                print(f.readline().strip())

    except Exception as e:
        logging.error("Unable to fetch data from page: %s", e)
    finally:
        driver.quit()

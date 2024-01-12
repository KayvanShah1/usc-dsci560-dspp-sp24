import logging
import os

from bs4 import BeautifulSoup
from pydantic_settings import BaseSettings

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from chromedriver_py import binary_path


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
    latest_news = page.find("ul", class_="LatestNews-list")
    market_banner = page.find("div", class_="MarketsBanner-marketData")

    # Save the collected data in the raw_data folder
    with open(save_to, "w", encoding="utf-8") as file:
        file.write(str(market_banner))
        file.write("\n\n")
        file.write(str(latest_news))


if __name__ == "__main__":
    settings = Settings()
    try:
        driver = initialize_driver()
        driver.get(settings.BASE_URL)

        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "MarketCard-row"))
        )
        page = BeautifulSoup(driver.page_source, "lxml")
        save_html_page(page.text, os.path.join(Path.data_dir, "raw_data", "web_data.html"))
    except Exception as e:
        logging.error("Unable to fetch data from page: %s", e)
    finally:
        driver.quit()

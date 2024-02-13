import re
import unicodedata
import warnings

import contractions
import nltk
import requests
from bs4 import BeautifulSoup
from chromedriver_py import binary_path
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from rake_nltk import Rake
from requests.exceptions import RequestException
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from settings import get_logger

warnings.filterwarnings("ignore")
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("averaged_perceptron_tagger", quiet=True)
logger = get_logger(__file__)


class TextCleaner:
    @staticmethod
    def unicode_to_ascii(s):
        return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

    @staticmethod
    def expand_contractions(text):
        return contractions.fix(text)

    @staticmethod
    def remove_email_addresses(text):
        return re.sub(r"[a-zA-Z0-9_\-\.]+@[a-zA-Z0-9_\-\.]+\.[a-zA-Z]{2,5}", " ", text)

    @staticmethod
    def remove_urls(text):
        return re.sub(r"\bhttps?:\/\/\S+|www\.\S+", " ", text)

    @staticmethod
    def remove_html_tags(text):
        return re.sub(r"<.*?>", "", text)

    @staticmethod
    def clean_text(text):
        text = TextCleaner.unicode_to_ascii(text.lower().strip())
        # replacing email addresses with empty string
        text = TextCleaner.remove_email_addresses(text)
        # replacing urls with empty string
        text = TextCleaner.remove_urls(text)
        # Remove HTML tags
        text = TextCleaner.remove_html_tags(text)
        # Expand contraction for eg., wouldn't => would not
        text = TextCleaner.expand_contractions(text)
        # creating a space between a word and the punctuation following it
        text = re.sub(r"([?.!,¿])", r" \1 ", text)
        text = re.sub(r'[" "]+', " ", text)
        # removes all non-alphabetical characters
        text = re.sub(r"[^a-zA-Z\s]+", "", text)
        # remove extra spaces
        text = re.sub(" +", " ", text)
        text = text.strip()
        return text


class TextPreprocessor:
    lemmatizer = WordNetLemmatizer()

    @staticmethod
    def get_stopwords_pattern():
        # Stopword list
        og_stopwords = set(stopwords.words("english"))

        # Define a list of negative words to remove
        neg_words = ["no", "not", "nor", "neither", "none", "never", "nobody", "nowhere"]
        custom_stopwords = [word for word in og_stopwords if word not in neg_words]
        pattern = re.compile(r"\b(" + r"|".join(custom_stopwords) + r")\b\s*")
        return pattern

    @staticmethod
    def pos_tagger(tag):
        if tag.startswith("J"):
            return wordnet.ADJ
        elif tag.startswith("V"):
            return wordnet.VERB
        elif tag.startswith("N"):
            return wordnet.NOUN
        elif tag.startswith("R"):
            return wordnet.ADV
        else:
            return None

    @staticmethod
    def lemmatize_text_using_pos_tags(text):
        words = nltk.pos_tag(word_tokenize(text))
        words = map(lambda x: (x[0], TextPreprocessor.pos_tagger(x[1])), words)
        lemmatized_words = [TextPreprocessor.lemmatizer.lemmatize(word, tag) if tag else word for word, tag in words]
        return " ".join(lemmatized_words)

    @staticmethod
    def lemmatize_text(text):
        words = word_tokenize(text)
        lemmatized_words = [TextPreprocessor.lemmatizer.lemmatize(word) for word in words]
        return " ".join(lemmatized_words)

    pattern = get_stopwords_pattern()

    @staticmethod
    def preprocess_text(text):
        # replacing all the stopwords
        text = TextPreprocessor.pattern.sub("", text)
        # text = TextPreprocessor.lemmatize_text(text)
        return text


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


def get_text(url, driver):
    headers = {"User-Agent": "DSCI560-Lab4"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

    except RequestException as e:
        logger.error(f"Failed to fetch URL: '{url}', Error: {e}. Trying with Selenium...")

        try:
            driver.get(url)
            WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.TAG_NAME, "p")))
            soup = BeautifulSoup(driver.page_source, "lxml")

        except WebDriverException:
            logger.error(f"Failed to fetch URL: '{url}'")
            return ""

    elements = soup.find_all("p")
    all_text = [element.get_text() for element in elements]
    text = " ".join(all_text)
    return text


def extract_keywords(text, topn: int = 10):
    keyword_extracter = Rake()
    keyword_extracter.extract_keywords_from_text(text)
    keyword_extracted = keyword_extracter.get_ranked_phrases()
    return keyword_extracted[:topn]

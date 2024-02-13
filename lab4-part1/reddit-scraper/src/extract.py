import re
import unicodedata
import warnings

import contractions
import nltk
import requests

from bs4 import BeautifulSoup
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from settings import get_logger

from rake_nltk import Rake

warnings.filterwarnings("ignore")
nltk.download("stopwords", quiet=True)
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


def get_text(url):
    headers = {"User-Agent": "DSCI560-Lab4"}

    # Create a session
    with requests.Session() as session:
        # Set headers for the session
        session.headers.update(headers)

        # Send a GET request using the session
        response = session.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            elements = soup.find_all("p")
            all_text = [element.get_text() for element in elements]

            # Concatenate all text elements
            text = " ".join(all_text)
            return text
        else:
            logger.error(f"Failed to fetch URL: {url}, Status code: {response.status_code}")
            return ""


def extract_keywords(text, topn: int = 10):
    keyword_extracter = Rake()
    keyword_extracter.extract_keywords_from_text(text)
    keyword_extracted = keyword_extracter.get_ranked_phrases()
    return keyword_extracted[:topn]

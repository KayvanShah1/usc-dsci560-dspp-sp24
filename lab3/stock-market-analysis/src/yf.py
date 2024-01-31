import pandas as pd
import yfinance as yf
from models import TickerSummaryModel
from pandas_datareader import data as pdr
from pyrate_limiter import Duration, Limiter, RequestRate
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from settings import config, get_logger

yf.pdr_override()

logger = get_logger(__name__)


class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    def __init__(self, timeout=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout = timeout

    def request(self, *args, **kwargs):
        # Pass the stored timeout to the request method
        kwargs["timeout"] = self.timeout
        return super().request(*args, **kwargs)


session = CachedLimiterSession(
    limiter=Limiter(RequestRate(2, Duration.SECOND * 5)),  # max 2 requests per 5 seconds
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache(config.YFINANCE_CACHE_FILE),
    timeout=15,
)


def get_ticker_info(ticker_code: str):
    # Create a Ticker object using yfinance with the provided ticker code and session
    ticker_info = yf.Ticker(ticker_code)

    # Retrieve information about the ticker
    ticker_info = ticker_info.info
    if "symbol" in ticker_info:
        ticker_info = TickerSummaryModel(
            ticker_code=ticker_info["symbol"],
            name=ticker_info["shortName"],
            exchange=ticker_info["exchange"],
        )
        return ticker_info.model_dump()
    else:
        logger.error("Invalid Ticker code '%s'", ticker_code)
        raise ValueError("Invalid Ticker code '%s'", ticker_code)


def get_ticker_data(ticker_dict: dict, start_date, end_date):
    ticker = ticker_dict["ticker_code"]
    data = pdr.get_data_yahoo(ticker, start=start_date, end=end_date, session=session)
    return data


def clean_ticker_data(df):
    df = df.reset_index()
    df.columns = [col.lower().replace(" ", "_") for col in df.columns]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.sort_values(by="date", ascending=True)
    return df


def resample(df):
    df = df.set_index("date")
    df = df.resample("D").asfreq()
    return df


def basic_preprocess(df):
    df = df.astype("float64")
    df = df.interpolate(method="time")
    df = df.fillna("bfill")
    return df.reset_index()

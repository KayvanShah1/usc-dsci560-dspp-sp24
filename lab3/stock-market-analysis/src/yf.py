import pandas as pd
import yfinance as yf
from pandas_datareader import data as pdr
from pyrate_limiter import Duration, Limiter, RequestRate
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket

yf.pdr_override()


class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass


session = CachedLimiterSession(
    limiter=Limiter(RequestRate(2, Duration.SECOND * 5)),  # max 2 requests per 5 seconds
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache("yfinance.cache"),
)


def get_ticker_data(ticker_dict: dict, start_date, end_date):
    ticker = ticker_dict["ticker_code"]
    start_date = 0
    end_date = 0
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

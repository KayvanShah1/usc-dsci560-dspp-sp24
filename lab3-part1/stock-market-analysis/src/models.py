from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, RootModel

from db import PyObjectId
from settings import config


class Name(BaseModel):
    first_name: str
    last_name: str


class UserBase(BaseModel):
    username: str
    name: Name
    password: str = Field(default_factory=lambda: config.pwd_context.hash("password"))
    created_at: datetime


class UserDetailsModel(BaseModel):
    username: str
    name: Name
    created_at: datetime


class TickerBase(BaseModel):
    name: str
    ticker_code: str
    created_at: datetime
    exchange: Optional[str] | None = None


TickerBaseListModel = RootModel[List[TickerBase]]


class TickerInfoUpdateModel(BaseModel):
    updated_at: datetime


class TickerSummaryModel(BaseModel):
    name: str
    ticker_code: str
    exchange: Optional[str] | None = None


TickerSummaryListModel = RootModel[List[TickerSummaryModel]]


class OHLCModel(BaseModel):
    datetime: datetime
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: float


class TickerDataModel(BaseModel):
    data: List[OHLCModel]


class PortfolioModel(BaseModel):
    username: str
    portfolio_name: str
    tickers: Optional[List[TickerSummaryModel]] = None
    created_at: datetime
    updated_at: Optional[datetime | None] = None


class PortfolioPreviewModel(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    portfolio_name: str
    tickers: Optional[List[TickerSummaryModel]]
    created_at: datetime
    updated_at: Optional[datetime | None] = None


PortfolioListModel = RootModel[List[PortfolioPreviewModel]]

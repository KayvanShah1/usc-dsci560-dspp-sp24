from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Name(BaseModel):
    first_name: str
    last_name: str


class UserBase(BaseModel):
    username: str
    name: Name
    created_at: datetime


class UserSummaryModel(BaseModel):
    username: str
    name: Name


class TickerBase(BaseModel):
    name: str
    code: str
    created_at: datetime
    updated_at: Optional[datetime | None] = None


class TickerModel(TickerBase):
    exchange: str


class TickerSummaryModel(BaseModel):
    name: str
    code: str


class OHLCModel(BaseModel):
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
    tickers: List[TickerSummaryModel]
    created_at: datetime
    updated_at: Optional[datetime]

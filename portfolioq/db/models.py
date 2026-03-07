from datetime import datetime
from pydantic import BaseModel

class Dividend(BaseModel):
    "An event of dividend transaction"
    id: int
    "Unique identifier"
    ticker: str
    payoutDate: datetime
    "The date when transaction was processed"
    amount: float
    marketValue: float
    "The value of the holdings which generated the dividend"
    currency: str
    "The currency in which `amount` and `marketValue` are represented"

class Trade(BaseModel):
    "A trade position which is completed and cashed in"
    id: int
    "Unique identifier"
    ticker: str
    buyDate: datetime
    sellDate: datetime
    "The date when this position closure was processed"
    buyValue: float
    "The date when this position opening was processed"
    sellValue: float
    currency: str
    "The currency in which `buyValue` and `sellValue` are represented"

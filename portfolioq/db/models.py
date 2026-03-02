from datetime import datetime
from pydantic import BaseModel

class Dividend(BaseModel):
    id: int
    ticker: str
    payoutDate: datetime
    amount: float
    currency: str

class Trade(BaseModel):
    id: int
    ticker: str
    buyDate: datetime
    sellDate: datetime
    buyValue: float
    sellValue: float
    currency: str

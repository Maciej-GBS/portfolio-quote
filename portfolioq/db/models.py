from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class Dividend(BaseModel):
    "An event of dividend transaction"
    id: int # TODO checksum for identifying duplicate data
    "Unique identifier"
    ticker: str
    payoutDate: datetime
    "The date when transaction was processed"
    amount: float
    marketValue: float
    "The value of the holdings which generated the dividend"
    withholdingTax: float
    "The tax paid at source"
    currency: str
    "The currency in which `amount`, `marketValue` and `withholdingTax` are represented"
    # clientId: int # TODO

class Trade(BaseModel):
    "A trade position which is completed and cashed in"
    id: int # TODO checksum for identifying duplicate data
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
    quantity: Optional[float] = None
    "Quantity of the underlying asset"
    # clientId: int # TODO

class Client(BaseModel):
    "Client information for grouping portfolio views"
    id: int
    "Unique identifier"
    name: str

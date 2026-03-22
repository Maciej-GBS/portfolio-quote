"Generate random data in extracted view for loading"
import random
from datetime import datetime, timedelta
from portfolioq.db import Dividend, Trade

def inf_int_generator():
    g = 0
    while True:
        yield g
        g += 1

class MockData:
    def __init__(self):
        self.tickers = [
            "NYSE",
            "ARCH",
            "NVDA",
            "ALPH",
            "PGFW",
            "KGHM",
            "PPPP"
        ]
        self.currencies = [
            "USD",
            "JPY",
            "PLN",
            "EUR"
        ]
        self.id_generator = inf_int_generator()

    def random_ticker(self) -> str:
        return random.choice(self.tickers)

    def random_currency(self) -> str:
        return random.choice(self.currencies)

    def random_day(self) -> datetime:
        y = random.randint(2023, 2026)
        m = random.randint(1, 12)
        d = random.randint(1, 30)
        if m == 2:
            d = (d % 27) + 1
        return datetime(year=y, month=m, day=d, hour=12)

    def random_dividend(self) -> Dividend:
        value = random.random() * 100
        return Dividend(
            id=next(self.id_generator),
            ticker=self.random_ticker(),
            payoutDate=self.random_day(),
            amount=value,
            marketValue=random.randint(10, 40) * value,
            withholdingTax=value * 0.1,
            currency=self.random_currency()
        )

    def random_trade(self) -> Trade:
        openDate = self.random_day()
        closeDate = openDate + timedelta(days=random.randint(1, 365 * 10))
        return Trade(
            id=next(self.id_generator),
            ticker=self.random_ticker(),
            buyDate=openDate,
            sellDate=closeDate,
            buyValue=random.random() * 2000,
            sellValue=random.random() * 3000,
            currency=self.random_currency()
        )

class MockDividendStream(MockData):
    def __init__(self):
        super().__init__()

    def __iter__(self):
        return self

    def __next__(self) -> Dividend:
        return self.random_dividend()

class MockTradeStream(MockData):
    def __init__(self):
        super().__init__()

    def __iter__(self):
        return self

    def __next__(self) -> Trade:
        return self.random_trade()

from abc import ABCMeta, abstractmethod
from .connector import get_connector
from .models import Dividend, Trade


class Table(metaclass=ABCMeta):
    def __init__(self):
        self.conn = get_connector()
        self.create()

    def __hash__(self):
        return hash(id(self))

    def close(self):
        self.conn.close()

    def query(self, q: str):
        cursor = self.conn.get_cursor()
        cursor.execute(q)
        return cursor.fetchall()

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def all(self):
        return []

    @abstractmethod
    def insert(self, values):
        pass


class DividendsTable(Table):
    NAME = "dividends"

    def __init__(self):
        super().__init__()

    def __hash__(self):
        return hash(self.NAME)

    def create(self):
        with self.conn as c:
            c.get_cursor().execute(f"""
            CREATE TABLE IF NOT EXISTS {self.NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                payoutDate DATE NOT NULL,
                amount REAL NOT NULL,
                marketValue REAL NOT NULL,
                withholdingTax REAL NOT NULL,
                currency VARCHAR NOT NULL
            )""")

    def all(self) -> list[Dividend]:
        return [
            Dividend(**{k:v for k,v in zip(Dividend.model_fields, kw)})
            for kw in self.query(f"SELECT * FROM {self.NAME}")
        ]

    def insert(self, values: list[Dividend]):
        if len(values) < 1:
            return
        values = [obj.model_dump() for obj in values]
        s_keys = [str(k) for k in values[0].keys() if k != "id"]
        columns = ",".join(s_keys)
        value_keys = ",".join(f":{k}" for k in s_keys)
        with self.conn as c:
            c.get_cursor().executemany(f"""
            INSERT INTO {self.NAME} ({columns})
            VALUES ({value_keys})
            """, values)


class TradeTable(Table):
    NAME = "trades"

    def __init__(self):
        super().__init__()

    def __hash__(self):
        return hash(self.NAME)

    def create(self):
        with self.conn as c:
            c.get_cursor().execute(f"""
            CREATE TABLE IF NOT EXISTS {self.NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                buyDate DATE NOT NULL,
                sellDate DATE NOT NULL,
                buyValue REAL NOT NULL,
                sellValue REAL NOT NULL,
                currency VARCHAR NOT NULL
            )""")

    def all(self) -> list[Trade]:
        return [
            Trade(**{k:v for k,v in zip(Trade.model_fields, kw)})
            for kw in self.query(f"SELECT * FROM {self.NAME}")
        ]

    def insert(self, values: list[Trade]):
        if len(values) < 1:
            return
        values = [obj.model_dump() for obj in values]
        s_keys = [str(k) for k in values[0].keys() if k != "id"]
        columns = ",".join(s_keys)
        value_keys = ",".join(f":{k}" for k in s_keys)
        with self.conn as c:
            c.get_cursor().executemany(f"""
            INSERT INTO {self.NAME} ({columns})
            VALUES ({value_keys})
            """, values)

from abc import ABCMeta, abstractmethod
from .connector import get_connector
from .models import Dividend, Trade


class Table(metaclass=ABCMeta):
    def __init__(self):
        self.conn = get_connector()
        self.create()

    def close(self):
        self.conn.close()

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

    def create(self):
        with self.conn as c:
            c.get_cursor().execute(f"""
            CREATE TABLE IF NOT EXISTS {self.NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                payoutDate DATE NOT NULL,
                amount REAL NOT NULL,
                currency VARCHAR NOT NULL
            )""")

    def all(self) -> list[Dividend]:
        cursor = self.conn.get_cursor()
        cursor.execute(f"SELECT * FROM {self.NAME}")
        return [Dividend(**kw) for kw in cursor.fetchall()]

    def insert(self, values: list[Dividend]):
        if len(values) < 1:
            return
        values = [obj.model_dump() for obj in values]
        s_keys = [str(k) for k in values[0].keys()]
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
        cursor = self.conn.get_cursor()
        cursor.execute(f"SELECT * FROM {self.NAME}")
        return [Trade(**kw) for kw in cursor.fetchall()]

    def insert(self, values: list[Trade]):
        if len(values) < 1:
            return
        values = [obj.model_dump() for obj in values]
        s_keys = [str(k) for k in values[0].keys()]
        columns = ",".join(s_keys)
        value_keys = ",".join(f":{k}" for k in s_keys)
        with self.conn as c:
            c.get_cursor().executemany(f"""
            INSERT INTO {self.NAME} ({columns})
            VALUES ({value_keys})
            """, values)

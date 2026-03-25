"""
This is a special middleware layer used to load NBP currency conversions.
Unlike the others, it does not expose any Stream but a Converter tool directly.

Sources of data:
- https://nbp.pl/statystyka-i-sprawozdawczosc/kursy/archiwum-tabela-a-csv-xls/ (.csv)
- https://nbp.pl/statystyka-i-sprawozdawczosc/kursy/archiwum-tabela-b-csv-xls/ (.csv)
"""
import pandas as pd
from datetime import datetime, timedelta

SATURDAY = 5

def str_to_float(s: str) -> float:
    return float(s.replace(',', '.')) if isinstance(s, str) else float(s)

class NbpConverter:
    def __init__(self):
        self._scales = {}
        self._df = pd.DataFrame()

    def __call__(self, value: float, foreign_currency: str, day: datetime) -> float:
        "Converts foreign to home currency at a given day"
        while day.weekday() >= SATURDAY:
            day += timedelta(days=1)
        day = day.date()
        return value * self._loc_closest(foreign_currency, day) / self._scales[foreign_currency]

    def _loc_closest(self, currency: str, day: datetime) -> float:
        if len(self._df) == 0:
            raise ValueError("No data available for currency conversion!")
        idx = self._df.index
        closest_day = idx[idx >= pd.to_datetime(day)].min()
        if closest_day is not pd.NaT:
            return self._df.loc[closest_day, currency]
        raise ValueError(f"Day {day} is out of range!")

    def load_nbp_table(self, nbp_table_path: str):
        df = pd.read_csv(nbp_table_path, header=0, index_col=0, sep=';', encoding='cp1250')
        df = df.dropna(axis=1, how='any').dropna(axis=0, how='any')

        currencies = df.loc['kod ISO']
        scale = df.loc['liczba jednostek']
        assert len(scale) == len(currencies)
        scale.index = currencies

        data = df[df.index.map(lambda i: isinstance(i, str) and i.isdecimal())]
        data = data.map(str_to_float)
        data.index = data.index.map(lambda i: datetime.strptime(i, r'%Y%m%d'))
        assert data.shape[1] == len(currencies)
        data.columns = currencies

        self._df = pd.concat((self._df, data), axis=1)
        self._scales.update(scale.map(str_to_float).to_dict())

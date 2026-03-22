"""
Sources of data:
- IBKR account activity statement (.csv)

The Activity Statement from IBKR is the most easy to use,
since it provides prices and dividends in source currency.

Other reports, like transaction history, fx or dividends
use the account base currency which makes it difficult to
calculate tax.
"""
import pandas as pd
from datetime import datetime
from portfolioq.db import Dividend, Trade

def line_filter(file: str, filter_func):
    early_stop_active = False
    with open(file, 'r') as f:
        for line in f:
            if filter_func(line):
                early_stop_active = True
                yield line
            elif early_stop_active:
                return

def combined_iterator(*iterators):
    for it in iterators:
        for e in it:
            yield e
    return

def safe_split(s: str, sep: str = ',', escape: str = '"') -> tuple:
    s = s.replace('\n', '')
    result = []
    escape_flag = False
    for elem in s.split(sep):
        if elem.startswith(escape):
            result.append(elem)
            escape_flag = True
        elif elem.endswith(escape):
            result[-1] = result[-1] + elem
            escape_flag = False
        elif escape_flag:
            result[-1] = result[-1] + elem
        else:
            result.append(elem)
    return tuple(result)

def lines_to_dataframe(iterable) -> pd.DataFrame:
    header = safe_split(next(iterable))
    return pd.DataFrame(data=[safe_split(line) for line in iterable], columns=header)

class IbkrDividendStream:
    def __init__(self, file: str):
        self.dividends = lines_to_dataframe(
            line_filter(file, lambda l: l.startswith("Dividends")))
        self.tax = lines_to_dataframe(
            line_filter(file, lambda l: l.startswith("Withholding Tax")))
        self._drop_nondata_rows()
        self._infer_symbol_column()
        self._queryable_tax()

    def _drop_nondata_rows(self):
        self.dividends.drop(
            self.dividends.index[self.dividends["Currency"].map(lambda c: "Total" in c)],
            inplace=True
        )
        self.tax.drop(self.tax.index[self.tax["Currency"].map(lambda c: "Total" in c)], inplace=True)

    def _infer_symbol_column(self):
        extract_symbol = lambda desc: desc[:min(desc.find(" "), desc.find("("))]
        self.dividends["Symbol"] = self.dividends["Description"].map(extract_symbol)
        self.tax["Symbol"] = self.tax["Description"].map(extract_symbol)

    def _queryable_tax(self):
        self.tax["Q"] = self.tax["Currency"] + ";" + self.tax["Symbol"] + ";" + self.tax["Date"]
        self.tax.set_index("Q", inplace=True)
        self.tax = self.tax["Amount"].to_dict()

    def __iter__(self):
        self.ptr_ = iter(range(len(self.dividends)))
        return self

    def __next__(self) -> Dividend:
        row = self.dividends.iloc[next(self.ptr_)]
        tax = self.tax.get(row["Currency"] + ";" + row["Symbol"] + ";" + row["Date"], 0.0)
        return Dividend(
            id=-1,
            ticker=row["Symbol"],
            payoutDate=datetime.strptime(row["Date"], r"%Y-%m-%d"),
            amount=row["Amount"],
            marketValue=1e9, # TODO replace placeholder
            withholdingTax=tax,
            currency=row["Currency"]
        )

class IbkrTradeStream:
    def __init__(self):
        self._criteria = lambda l: all([
            l.startswith("Trades,Header"),
            "Comm/Fee" in l
        ]) or l.startswith("Trades,Data,Order")
        self.files = []
        self.open_trades = []

    def add_file(self, file: str):
        self.files.append(file)
        return self

    def __iter__(self):
        trade_history = combined_iterator(*[
            line_filter(f, self._criteria) for f in self.files
        ])
        self.data_ = lines_to_dataframe(trade_history)
        return self

    def __next__(self) -> Trade:
        Trade(
            id=-1,
            ticker="Symbol",
            currency="Currency",
            buyDate="Date/Time;O",
            sellDate="Date/Time;C",
            buyValue="- Proceeds - Comm/Fee",
            sellValue="Proceeds + Comm/Fee"
        )
        raise StopIteration()

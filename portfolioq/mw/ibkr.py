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

CODE_OPEN = "O"
CODE_CLOSE = "C"

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
            result.append(elem[1:])
            escape_flag = True
        elif elem.endswith(escape):
            result[-1] = result[-1] + elem[:-1]
            escape_flag = False
        elif escape_flag:
            result[-1] = result[-1] + elem
        else:
            num_test = elem.replace('.', '', 1)
            if num_test.isnumeric() or (num_test.startswith('-') and num_test[1:].isnumeric()):
                result.append(float(elem))
            else:
                result.append(elem)
    return tuple(result)

def lines_to_dataframe(iterable) -> pd.DataFrame:
    header = safe_split(next(iterable))
    return pd.DataFrame(data=[safe_split(line) for line in iterable], columns=header)

class IbkrDividendStream:
    def __init__(self, file: str):
        self.dividends = lines_to_dataframe(
            line_filter(file, lambda l: l.startswith("Dividends"))).sort_values("Date", ascending=True)
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
    def __init__(self, files: list | None = None):
        self._criteria = lambda l: all([
            l.startswith("Trades,Header"),
            "Comm/Fee" in l
        ]) or l.startswith("Trades,Data,Order")
        self.files = []

        for f in (files or []):
            self.add_file(f)

    def add_file(self, file: str):
        self.files.append(file)
        return self

    def __iter__(self):
        trade_history = combined_iterator(*[line_filter(f, self._criteria) for f in self.files])
        self.data_ = iter(lines_to_dataframe(trade_history)
                          .sort_values("Date/Time", ascending=True)
                          .iterrows())
        self.open_trades_ = {}
        self.pending_ = []
        return self

    def __next__(self) -> Trade:
        if self.pending_:
            return self.pending_.pop(0)
        _, row = next(self.data_)
        trade_key = row["Currency"] + " " + row["Symbol"]
        codes = row["Code"].split(";")
        if CODE_OPEN in codes:
            active_trades = self.open_trades_.get(trade_key, None)
            new_trade = Trade(
                id=-1,
                ticker=row["Symbol"],
                currency=row["Currency"],
                buyDate=row["Date/Time"],
                sellDate=datetime.min,
                buyValue=-(row["Proceeds"] + row["Comm/Fee"]),
                sellValue=0.0,
                quantity=row["Quantity"]
            )
            if active_trades is None:
                self.open_trades_.update({trade_key: [new_trade]})
            else:
                active_trades.append(new_trade)
        elif CODE_CLOSE in codes:
            closed_trades: list[Trade] = self._pop_by_quantity(trade_key, row["Quantity"])
            if closed_trades:
                self.pending_ = [
                    Trade(
                        id=-1,
                        ticker=row["Symbol"],
                        currency=row["Currency"],
                        buyDate=t.buyDate,
                        sellDate=row["Date/Time"],
                        buyValue=t.buyValue,
                        sellValue=row["Proceeds"] + row["Comm/Fee"],
                        quantity=t.quantity
                    )
                    for t in closed_trades
                ]
                return self.pending_.pop(0)
            else:
                print(f"Warning: discarding Trade, not found in active : {row}")
        # Trade is active, cannot produce until closed
        return next(self)

    def _pop_by_quantity(self, key, quantity: float):
        "Pop open trades in FIFO mode by given quantity and adjust for partial operations."
        active_trades: list[Trade] = self.open_trades_.get(key, None)
        if active_trades is None:
            return None
        closed = []
        while len(active_trades) > 0 and quantity > 1e-5:
            t = active_trades.pop(0)
            quantity -= t.quantity
            closed.append(t)
        if len(closed) > 0 and quantity < 0.0:
            adjusted_t: Trade = closed[-1]
            remaining_active_q = -quantity
            remaining_factor = remaining_active_q / adjusted_t.quantity
            active_trades.insert(0, Trade(
                id=-1,
                ticker=adjusted_t.ticker,
                currency=adjusted_t.currency,
                buyDate=adjusted_t.buyDate,
                sellDate=adjusted_t.sellDate,
                buyValue=adjusted_t.buyValue * remaining_factor,
                sellValue=adjusted_t.sellValue * remaining_factor,
                quantity=remaining_active_q
            ))
            adjusted_t.buyValue *= (1 - remaining_factor)
            adjusted_t.sellValue *= (1 - remaining_factor)
            adjusted_t.quantity -= remaining_active_q
        return closed

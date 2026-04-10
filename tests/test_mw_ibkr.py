import pytest
from portfolioq.db import Dividend, Trade
from portfolioq.mw.ibkr import combined_iterator, IbkrDividendStream, IbkrTradeStream

@pytest.fixture
def fixture_ibkr_archives():
    # TODO create a temp file and cleanup
    return [
        "sample_data/U12345678_20240528_20250528.csv",
        "sample_data/U12345678_20250529_20260320.csv"
    ]

def test_combined_iterator():
    l1 = [1, 2, 3]
    l2 = ["a", "b", 4]
    l3 = []
    ci = combined_iterator(iter(l1), iter(l2), iter(l3))
    assert (l1 + l2 + l3) == list(ci)
    assert [] == list(combined_iterator(*[]))

def test_dividend_stream(fixture_ibkr_archives):
    for archive in fixture_ibkr_archives:
        s = IbkrDividendStream(archive)
        value_produced = False
        for d in s:
            value_produced = True
            print(d)
            assert type(d) is Dividend
        assert value_produced

def test_trade_stream(fixture_ibkr_archives):
    s = IbkrTradeStream(fixture_ibkr_archives)
    value_produced = False
    for t in s:
        value_produced = True
        print(t)
        assert type(t) is Trade
    assert value_produced

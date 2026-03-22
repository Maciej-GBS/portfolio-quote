import pytest
from portfolioq.db import Dividend, Trade
from portfolioq.mw import MockDividendStream, MockTradeStream

@pytest.fixture
def fixture_dividend_stream():
    return MockDividendStream()

@pytest.fixture
def fixture_trade_stream():
    return MockTradeStream()

def test_generate_data(
        fixture_dividend_stream,
        fixture_trade_stream
):
    div_obj = next(fixture_dividend_stream)
    assert type(div_obj) is Dividend
    print(div_obj.model_dump())

    trade_obj = next(fixture_trade_stream)
    assert type(trade_obj) is Trade
    print(trade_obj.model_dump())

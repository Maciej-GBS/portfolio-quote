import pytest
from datetime import datetime
from portfolioq.mw import NbpConverter

@pytest.fixture
def fixture_nbp_archives():
    # TODO create a temp file and cleanup
    return [
        "sample_data/archiwum_tab_a_2025.csv",
        "sample_data/archiwum_tab_b_2025.csv"
    ]

def test_load_archive(fixture_nbp_archives):
    converter = NbpConverter()
    for path in fixture_nbp_archives:
        converter.load_nbp_table(path)
    print(converter(1.0, "EUR", datetime(year=2025, month=6, day=13, hour=11)))
    with pytest.raises(ValueError):
        converter(1.0, "USD", datetime(year=2000, month=1, day=2))

import os
import pytest
from datetime import datetime
from portfolioq.mw import NbpConverter

@pytest.fixture
def fixture_nbp_archives():
    archives = [
        ".pytmp.A.csv",
        ".pytmp.B.csv"
    ]
    content_list = [
        """data;1THB;1USD;1AUD;1HKD;1CAD;1NZD;1SGD;1EUR;100HUF;1CHF;1GBP;1UAH;100JPY;1CZK;1DKK;100ISK;1NOK;1SEK;1RON;1BGN;1TRY;1ILS;100CLP;1PHP;1MXN;1ZAR;1BRL;1MYR;10000IDR;100INR;100KRW;1CNY;1XDR;nr tabeli;pełny numer tabeli;
;bat (Tajlandia);dolar amerykański;dolar australijski;dolar Hongkongu;dolar kanadyjski;dolar nowozelandzki;dolar singapurski;euro;forint (Węgry);frank szwajcarski;funt szterling;hrywna (Ukraina);jen (Japonia);korona czeska;korona duńska;korona islandzka;korona norweska;korona szwedzka;lej rumuński;lew (Bułgaria);lira turecka;nowy izraelski szekel;peso chilijskie;peso filipińskie;peso meksykańskie;rand (Republika Południowej Afryki);real (Brazylia);ringgit (Malezja);rupia indonezyjska;rupia indyjska;won południowokoreański;yuan renminbi (Chiny);SDR (MFW);
20250107;0,1182;4,0770;2,5619;0,5245;2,8506;2,3183;2,9984;4,2515;1,0226;4,5097;5,1217;0,0964;2,5866;0,1690;0,5699;2,9300;0,3617;0,3706;0,8547;2,1737;0,1154;1,1258;0,4033;0,0702;0,2008;0,2200;0,6667;0,9085;2,5276;4,7561;0,2818;0,5564;5,3207;3;003/A/NBP/2025;
20250224;0,1186;3,9734;2,5291;0,5111;2,7958;2,2829;2,9702;4,1609;1,0334;4,4187;5,0216;0,0953;2,6565;0,1658;0,5578;2,8558;0,3571;0,3732;0,8359;2,1274;0,1089;1,1119;0,4214;0,0687;0,1947;0,2157;0,6934;0,9009;2,4414;4,5826;0,2784;0,5482;5,2197;37;037/A/NBP/2025;
20250225;0,1171;3,9470;2,4995;0,5078;2,7666;2,2558;2,9461;4,1339;1,0315;4,4041;4,9830;0,0946;2,6385;0,1656;0,5542;2,8451;0,3547;0,3709;0,8307;2,1136;0,1081;1,1002;0,4183;0,0681;0,1927;0,2146;0,6830;0,8925;2,4148;4,5263;0,2753;0,5433;5,1866;38;038/A/NBP/2025;

kod ISO;THB;USD;AUD;HKD;CAD;NZD;SGD;EUR;HUF;CHF;GBP;UAH;JPY;CZK;DKK;ISK;NOK;SEK;RON;BGN;TRY;ILS;CLP;PHP;MXN;ZAR;BRL;MYR;IDR;INR;KRW;CNY;XDR;
nazwa waluty;bat (Tajlandia);dolar amerykański;dolar australijski;dolar Hongkongu;dolar kanadyjski;dolar nowozelandzki;dolar singapurski;euro;forint (Węgry);frank szwajcarski;funt szterling;hrywna (Ukraina);jen (Japonia);korona czeska;korona duńska;korona islandzka;korona norweska;korona szwedzka;lej rumuński;lew (Bułgaria);lira turecka;nowy izraelski szekel;peso chilijskie;peso filipińskie;peso meksykańskie;rand (Republika Południowej Afryki);real (Brazylia);ringgit (Malezja);rupia indonezyjska;rupia indyjska;won południowokoreański;yuan renminbi (Chiny);SDR (MFW);
liczba jednostek;1;1;1;1;1;1;1;1;100;1;1;1;100;1;1;100;1;1;1;1;1;1;100;1;1;1;1;1;10000;100;100;1;1;
""",

        """data;1THB;1USD;1AUD;1HKD;1CAD;1NZD;1SGD;1EUR;100HUF;1CHF;1GBP;1UAH;100JPY;1CZK;1DKK;100ISK;1NOK;1SEK;1RON;1BGN;1TRY;1ILS;100CLP;1PHP;1MXN;1ZAR;1BRL;1MYR;10000IDR;100INR;100KRW;1CNY;1XDR;nr tabeli;pełny numer tabeli;
;bat (Tajlandia);dolar amerykański;dolar australijski;dolar Hongkongu;dolar kanadyjski;dolar nowozelandzki;dolar singapurski;euro;forint (Węgry);frank szwajcarski;funt szterling;hrywna (Ukraina);jen (Japonia);korona czeska;korona duńska;korona islandzka;korona norweska;korona szwedzka;lej rumuński;lew (Bułgaria);lira turecka;nowy izraelski szekel;peso chilijskie;peso filipińskie;peso meksykańskie;rand (Republika Południowej Afryki);real (Brazylia);ringgit (Malezja);rupia indonezyjska;rupia indyjska;won południowokoreański;yuan renminbi (Chiny);SDR (MFW);
20250303;0,1202;4,1219;2,5630;0,5300;2,8597;2,3159;3,0260;4,2668;1,0368;4,5554;5,1448;0,0980;2,6287;0,1693;0,5721;2,9651;0,3633;0,3732;0,8578;2,1816;0,1167;1,1301;0,4136;0,0713;0,1984;0,2199;0,6665;0,9204;2,5453;4,8059;0,2815;0,5646;5,3541;1;001/A/NBP/2025;
20250304;0,1205;4,1512;2,5794;0,5337;2,8849;2,3252;3,0299;4,2718;1,0299;4,5658;5,1498;0,0986;2,6398;0,1697;0,5727;2,9769;0,3644;0,3726;0,8588;2,1841;0,1173;1,1365;0,4129;0,0714;0,2023;0,2210;0,6747;0,9225;2,5641;4,8407;0,2823;0,5672;5,3801;2;002/A/NBP/2025;

kod ISO;THB;USD;AUD;HKD;CAD;NZD;SGD;EUR;HUF;CHF;GBP;UAH;JPY;CZK;DKK;ISK;NOK;SEK;RON;BGN;TRY;ILS;CLP;PHP;MXN;ZAR;BRL;MYR;IDR;INR;KRW;CNY;XDR;
nazwa waluty;bat (Tajlandia);dolar amerykański;dolar australijski;dolar Hongkongu;dolar kanadyjski;dolar nowozelandzki;dolar singapurski;euro;forint (Węgry);frank szwajcarski;funt szterling;hrywna (Ukraina);jen (Japonia);korona czeska;korona duńska;korona islandzka;korona norweska;korona szwedzka;lej rumuński;lew (Bułgaria);lira turecka;nowy izraelski szekel;peso chilijskie;peso filipińskie;peso meksykańskie;rand (Republika Południowej Afryki);real (Brazylia);ringgit (Malezja);rupia indonezyjska;rupia indyjska;won południowokoreański;yuan renminbi (Chiny);SDR (MFW);
liczba jednostek;1;1;1;1;1;1;1;1;100;1;1;1;100;1;1;100;1;1;1;1;1;1;100;1;1;1;1;1;10000;100;100;1;1;
"""
    ]
    for fn, content in zip(archives, content_list):
        with open(fn, 'wb') as f:
            f.write(content.encode('cp1250'))
    yield archives
    for fn in archives:
        os.remove(fn)

@pytest.fixture
def fixture_nbp_converter(fixture_nbp_archives):
    converter = NbpConverter()
    for path in fixture_nbp_archives:
        converter.load_nbp_table(path)
    return converter

def test_load_archive(fixture_nbp_archives):
    converter = NbpConverter()
    for path in fixture_nbp_archives:
        converter.load_nbp_table(path)

def test_conversion(fixture_nbp_converter):
    converter = fixture_nbp_converter
    assert (converter(1.0, "EUR", datetime(year=2025, month=2, day=25, hour=11)) - 4.1609) < 0.0001
    assert (converter(2.0, "THB", datetime(year=2025, month=3, day=4, hour=17)) - 0.1202 * 2) < 0.0001
    assert (converter(1.0, "THB", datetime(year=2025, month=3, day=15, hour=19)) - 0.1205) < 0.0001
    with pytest.raises(ValueError):
        converter(1.5, "USD", datetime(year=2025, month=1, day=7))

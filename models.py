import datetime
from dataclasses import dataclass

@dataclass
class EtfInfo:
    ticker: str
    company: str
    name: str

@dataclass
class StockCompanyInfo:
    ticker: str
    market_type: str
    corp_name : str
    corp_code: str

@dataclass
class CorporationInfo:
    crno: str
    sic_name: str
    enp_rpr_fnm: str
    address: str
    homepage: str
    enp_main_biz_name: str
    corp_name: str

@dataclass
class EtfOHLCV:
    ticker: str
    nav: float
    close: int
    trade_date: datetime.date
    volume: int
    change_rate: float
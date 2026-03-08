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
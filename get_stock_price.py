import datetime
import logging
from pprint import pprint
import os
from dotenv import load_dotenv
from models import dataclass, EtfInfo
from pykrx.website.comm import webio
from pykrx import stock
from login import KrxSessionManager

load_dotenv()

KRX_ID = os.getenv("KRX_ID")
KRX_PASSWORD = os.getenv("KRX_PASSWORD")
ASSET_MANAGER = {"TIGER", "KODEX"}

# 1. 인프라스트럭처(통신) 객체 생성
krx_session = KrxSessionManager(login_id=KRX_ID, login_pw=KRX_PASSWORD)

# 2. pykrx에 세션 주입
krx_session.patch_pykrx(webio)

if krx_session.login():
    etf_tickers = stock.get_etf_ticker_list(datetime.date.today().strftime("%Y%m%d"))
    etfs = []
    for etf_ticker in etf_tickers:
        etf_info = stock.get_etf_ticker_name(etf_ticker).split()
        # 회사 및 이름 분리
        etf_company = etf_info[0]
        etf_name = ""

        for etf in etf_info[1:]:
            etf_name += etf + " "

        if etf_company not in ASSET_MANAGER:
            continue
        etfs.append(
            EtfInfo(
                etf_ticker,
                etf_company,
                etf_name)
        )
    pprint(etfs)

else:
    logging.error("로그인 실패")

import datetime
import logging
from pprint import pprint

from pykrx.website.comm import webio
from login import _session_post_read, _session_get_read, start_session, login_krx
from pykrx import stock
from dotenv import load_dotenv
import os
load_dotenv()

KRX_ID = os.getenv("KRX_ID")
KRX_PASSWORD = os.getenv("KRX_PASSWORD")
start_session()

webio.Post.read = _session_post_read
webio.Get.read = _session_get_read

ASSET_MANAGER = {"TIGER", "KODEX"}

if login_krx(KRX_ID, KRX_PASSWORD):
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
        etfs.append({
            "ticker": etf_ticker,
            "company": etf_company,
            "name": etf_name
        })
    pprint(etfs)

else:
    logging.error("로그인 실패")

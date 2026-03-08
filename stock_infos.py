import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from json import JSONDecodeError
from time import sleep
import requests
import dotenv

from get_etf_pdf import load_etf_tickers
from models import StockCompanyInfo
dotenv.load_dotenv()
STOCK_INFO_URL = "https://apis.data.go.kr/1160100/service/GetKrxListedInfoService/getItemInfo"
SERVICE_KEY = os.getenv("DATA_PORTAL_COMPANY_SERVICE_KEY")
MAX_WORKERS = 5

# 주식 종목 코드
global stock_tickers
stock_tickers = set()

# 상장주식 종목 코드
global listed_stock_tickers
listed_stock_tickers = set()

# 상장주식에서 제외된 코드
global not_listed_tickers
not_listed_tickers = list()

# 주식 정보들
global stock_infos
stock_infos = list()

# api 조회 실패 코드들 (api 토큰 이슈로 인한 에러)
api_failed_tickers = list()

# 조회 실패 (api 호출은 정상이나, 내부가 비어있음)코드들
global read_failed_tickers
read_failed_tickers = list()

def get_stock_tickers(tickers: list[str]):
    for stock in tickers:
        if stock and stock in listed_stock_tickers:
            stock_tickers.add(stock)
        else:
            not_listed_tickers.append(stock)
    return stock_tickers

def load_stock_tickers(etf_ticker:str) -> list[str]:
    path = f"pdf_datas/{etf_ticker}.csv"
    tickers = []

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # header skip

        for row in reader:
            if row:
                tickers.append(row[0])

    return tickers

def get_stock_info(ticker):
    sleep(0.3)
    response = requests.get(STOCK_INFO_URL, params={
        "ServiceKey" : SERVICE_KEY,
        "likeSrtnCd" : ticker,
        "resultType" : "json",
        "basDt" : "20260305"
    })

    try:
        response = response.json()
        item = response.get("response", {}).get("body", {}).get("items", {}).get("item", [])[0]
        srtn_cd = item.get("srtnCd")
        market_category = item.get("mrktCtg")
        corp_name = item.get("corpNm")
        corp_number = item.get("crno")

        if not srtn_cd:
            raise ValueError("회사 조회 실패")

        return StockCompanyInfo(srtn_cd, market_category, corp_name, corp_number)

    except JSONDecodeError:
        api_failed_tickers.append(ticker)

    except IndexError or ValueError:
        read_failed_tickers.append(ticker)

    return response

def get_listed_stock_tickers():
    with open("listed_stocks.csv", "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)
        for row in reader:
            if not row:
                continue
            listed_stock_ticker = row[1].strip()
            if listed_stock_ticker:
                listed_stock_tickers.add(listed_stock_ticker)

def main():
    etf_tickers = load_etf_tickers("processed_etf_data.csv")

    results = []
    completed = 0

    get_listed_stock_tickers()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(get_stock_tickers, load_stock_tickers(ticker)): ticker for ticker in etf_tickers}

    total = len(stock_tickers)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(get_stock_info, ticker): ticker for ticker in stock_tickers}
        for future in as_completed(futures):
            completed += 1
            result = future.result()
            stock_infos.append(result)
            print(f"{completed}/{total} {result}")
            results.append(result)

    stock_info_df = [stock_info.__dict__ for stock_info in stock_infos]
    keys = stock_info_df[0].keys()

    with open("stock_info.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(stock_info_df)

    print(read_failed_tickers)
    print(api_failed_tickers)

    success_count = sum(1 for r in results if r.startswith("[OK]"))
    error_count = sum(1 for r in results if r.startswith("[ERROR]"))
    skip_count = sum(1 for r in results if r.startswith("[SKIP]"))
    print(len(stock_tickers))
    print("==== DONE ====")
    print(f"success: {success_count}")
    print(f"skip   : {skip_count}")
    print(f"error  : {error_count}")


if __name__ == "__main__":
    main()
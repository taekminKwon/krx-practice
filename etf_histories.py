import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

from pathlib import Path

from pandas import DataFrame

from get_etf_pdf import load_etf_tickers
from pykrx import stock

MAX_WORKERS = 5

# api 조회 실패 코드들 (api 토큰 이슈로 인한 에러)
api_failed_tickers = list()

# 조회 실패 (api 호출은 정상이나, 내부가 비어있음)코드들
read_failed_tickers = list()

def fetch_etf(ticker):
    df = stock.get_etf_ohlcv_by_date("20230302", "20260308", ticker)
    return ticker, df

def main():
    etf_tickers = load_etf_tickers("processed_etf_data.csv")
    total = len(etf_tickers)
    results = []
    completed = 0
    output_dir = Path("./etf_ohlcv")
    output_dir.mkdir(exist_ok=True)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_etf, ticker): ticker for ticker in etf_tickers}
        for future in as_completed(futures):
            ticker = futures[future]
            completed += 1

            try:
                ticker, df = future.result()

                if df is None or df.empty:
                    print(f"[{completed}/{total}] {ticker} -> empty")
                    read_failed_tickers.append(ticker)
                    continue

                df = df.reset_index()
                df["ticker"] = ticker

                output_path = output_dir / f"{ticker}.csv"
                df.to_csv(output_path, index=False, encoding="utf-8-sig")

                print(f"[{completed}/{total}] {ticker} saved ({len(df)} rows)")

            except Exception as e:
                api_failed_tickers.append(ticker)
                print(f"[{completed}/{total}] {ticker} failed: {e}")

    print(api_failed_tickers)
    print(read_failed_tickers)

    success_count = sum(1 for r in results if r.startswith("[OK]"))
    error_count = sum(1 for r in results if r.startswith("[ERROR]"))
    skip_count = sum(1 for r in results if r.startswith("[SKIP]"))
    print("==== DONE ====")
    print(f"success: {success_count}")
    print(f"skip   : {skip_count}")
    print(f"error  : {error_count}")


if __name__ == "__main__":
    main()
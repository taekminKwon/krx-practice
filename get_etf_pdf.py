import csv
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from pykrx import stock

from get_etf_list import krx_session

OUTPUT_DIR = Path("pdf_datas")
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_WORKERS = 5   # 처음엔 3~5 정도로 보수적으로 시작
SLEEP_SEC = 0.2   # 너무 몰아치지 않게 약간 텀

def fetch_and_save(etf_ticker: str) -> str:
    try:
        # KRX 쪽 차단 방지를 위해 약간 쉬어주기
        time.sleep(SLEEP_SEC)

        pdf = stock.get_etf_portfolio_deposit_file(etf_ticker)

        # 빈 데이터 방어
        if pdf is None or pdf.empty:
            return f"[SKIP] {etf_ticker}: empty"

        output_path = OUTPUT_DIR / f"{etf_ticker}.csv"
        pdf.to_csv(output_path, encoding="utf-8-sig")
        return f"[OK] {etf_ticker}"

    except Exception as e:
        return f"[ERROR] {etf_ticker}: {e}"


def load_tickers(csv_path: str) -> list[str]:
    tickers = []
    with open(csv_path, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # 헤더 스킵
        for row in reader:
            if not row:
                continue
            etf_ticker = row[0].strip()
            if etf_ticker:
                tickers.append(etf_ticker)
    return tickers


def main():
    tickers = load_tickers("processed_etf_data.csv")
    total = len(tickers)
    print(f"total: {total}")

    results = []
    completed = 0
    if krx_session.login():
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(fetch_and_save, ticker): ticker for ticker in tickers}

            for future in as_completed(futures):
                completed += 1
                result = future.result()
                print(f"{completed}/{total} {result}")
                results.append(result)

    success_count = sum(1 for r in results if r.startswith("[OK]"))
    error_count = sum(1 for r in results if r.startswith("[ERROR]"))
    skip_count = sum(1 for r in results if r.startswith("[SKIP]"))

    print("==== DONE ====")
    print(f"success: {success_count}")
    print(f"skip   : {skip_count}")
    print(f"error  : {error_count}")


if __name__ == "__main__":
    main()
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

from stock_infos import get_stock_info

stock_tickers = ['000815', '005945', '003545', '00088K', '051905', '071055', '005387', '097955', '00104K', '010955', '006405', '00680K', '005385', '02826K', '090435', '051915', '066575', '011785', '003555', '009155', '005935', '000155']

completed = 0
total = len(stock_tickers)
results = []
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(get_stock_info, ticker): ticker for ticker in stock_tickers}
    for future in as_completed(futures):
        completed += 1
        result = future.result()
        print(f"{completed}/{total} {result}")
        results.append(result)

print(results)

stock_info_df = [stock_info.__dict__ for stock_info in results]
print(stock_info_df)
# keys = stock_info_df[0].keys()
#
# with open("stock_info.csv", "a", newline="", encoding="utf-8-sig") as f:
#     writer = csv.DictWriter(f, fieldnames=keys)
#     writer.writerows(stock_info_df)
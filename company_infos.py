import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from json import JSONDecodeError
from time import sleep
import requests
import dotenv

from models import StockCompanyInfo, CorporationInfo

dotenv.load_dotenv()
STOCK_INFO_URL = "https://apis.data.go.kr/1160100/service/GetCorpBasicInfoService_V2/getCorpOutline_V2"
SERVICE_KEY = os.getenv("DATA_PORTAL_COMPANY_SERVICE_KEY")
MAX_WORKERS = 5
read_failed_codes = []
api_failed_codes = []
def load_corp_infos() -> list[StockCompanyInfo]:
    path = "stock_info.csv"
    corp_infos = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # header skip

        for row in reader:
            if row:
                corp_infos.append(StockCompanyInfo(row[0], row[1], row[2], row[3]))

    return corp_infos

def get_corp_number(corp_info: StockCompanyInfo):
    return StockCompanyInfo.corp_code

global size
size = 0
def get_company_info(corp_number):
    sleep(0.2)
    response = requests.get(STOCK_INFO_URL, params={
        "ServiceKey" : SERVICE_KEY,
        "pageNo" : 1,
        "numOfRows" : 1,
        "resultType" : "json",
        "crno" : corp_number
    })

    try:
        response = response.json()
        item = response.get("response", {}).get("body", {}).get("items", {}).get("item", [])[0]

        crno = corp_number

        sic_name = item.get("sicNm")

        enp_rpr_fnm = item.get("enpRprFnm")

        address = item.get("enpBsadr")

        homepage = item.get("enpHmpgUrl")

        enp_main_biz_name = item.get("enpMainBizNm")

        corp_name = item.get("enpPbanCmpyNm")

        return CorporationInfo(crno, sic_name, enp_rpr_fnm, address, homepage, enp_main_biz_name, corp_name)
    except JSONDecodeError:
        api_failed_codes.append(corp_number)
    except (IndexError, ValueError):
        read_failed_codes.append(corp_number)

    return response

def main():
    results = []
    completed = 0

    infos = load_corp_infos()
    total = len(infos)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(get_company_info, info.corp_code): info for info in infos}
        for future in as_completed(futures):
            completed += 1
            result = future.result()
            results.append(result)
            print(f"{completed}/{total} {result}")

    with open("results_raw.txt", "w", encoding="utf-8") as f:
        for r in results:
            f.write(repr(r) + "\n")

    results_df = [company_info.__dict__ for company_info in results]
    keys = results_df[0].keys()

    with open("company_infos.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results_df)

    print(read_failed_codes)
    print(api_failed_codes)

    print("==== DONE ====")

if __name__ == "__main__":
    main()
import csv
import re

INPUT_FILE = "results_raw.txt"
OUTPUT_FILE = "company_infos.csv"

line_pattern = re.compile(r"^\s*CorporationInfo\((.*)\)\s*$")
field_pattern = re.compile(r"(\w+)=('(?:\\'|[^'])*'|None)")

rows = []

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line_no, line in enumerate(f, start=1):
        raw_line = line.rstrip("\n")
        line = raw_line.strip()

        if not line:
            continue

        match = line_pattern.match(line)
        if not match:
            print(f"[SKIP] line {line_no}: 형식 불일치")
            print(raw_line)
            continue

        inner = match.group(1)

        try:
            fields = dict()
            for key, value in field_pattern.findall(inner):
                if value == "None":
                    fields[key] = None
                else:
                    # 앞뒤 따옴표 제거
                    fields[key] = value[1:-1]

            # 최소 필드 검증
            required_keys = {
                "crno",
                "sic_name",
                "enp_rpr_fnm",
                "address",
                "homepage",
                "enp_main_biz_name",
                "corp_name",
            }

            if not required_keys.issubset(fields.keys()):
                print(f"[SKIP] line {line_no}: 필드 누락")
                print(raw_line)
                continue

            rows.append(fields)

        except Exception as e:
            print(f"[ERROR] line {line_no}: {e}")
            print(raw_line)

if not rows:
    raise ValueError("복구된 데이터가 없습니다.")

fieldnames = [
    "crno",
    "sic_name",
    "enp_rpr_fnm",
    "address",
    "homepage",
    "enp_main_biz_name",
    "corp_name",
]

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"복구 완료: {len(rows)}건 -> {OUTPUT_FILE}")
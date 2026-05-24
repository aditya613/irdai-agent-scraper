import requests
import time
import random
import json
import os
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# =========================================================

# CONFIG

# =========================================================

BASE_URL = "https://agencyportal.irdai.gov.in"

LOCATE_URL = (
f"{BASE_URL}/_WebService/PublicAccess/AgentLocator.asmx/LocateAgent"
)

HEADERS = {
"X-Requested-With": "XMLHttpRequest",
"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
"Referer": f"{BASE_URL}/PublicAccess/AgentLocator.aspx",
"User-Agent": "Mozilla/5.0"
}

INSURANCE_TYPE = 1
STATE_ID = 19

REQUEST_DELAY_MIN = 1
REQUEST_DELAY_MAX = 2

TIMEOUT = 60

# =========================================================

# CREATE DIRECTORIES

# =========================================================

os.makedirs("raw", exist_ok=True)
os.makedirs("exports", exist_ok=True)

# =========================================================

# LOAD DATA FILES

# =========================================================

with open("data/insurers.json", "r", encoding="utf-8") as f:
    insurers = json.load(f)

with open("data/districts/punjab.json", "r", encoding="utf-8") as f:
    districts = json.load(f)

# =========================================================

# ROBUST SESSION

# =========================================================

session = requests.Session()

retries = Retry(
total=5,
backoff_factor=2,
status_forcelist=[429, 500, 502, 503, 504]
)

adapter = HTTPAdapter(max_retries=retries)

session.mount("http://", adapter)
session.mount("https://", adapter)

# =========================================================

# PINCODE RANGE EXPANDER

# =========================================================

def expand_pincode_range(range_str):


    try:

        start_pin, end_pin = range_str.split("-")

        start_pin = int(start_pin.strip())
        end_pin = int(end_pin.strip())

        return [str(pin) for pin in range(start_pin, end_pin + 1)]

    except Exception as e:

        print("Pincode range error:", range_str)
        return []


# =========================================================

# RESPONSE PARSER

# =========================================================

def parse_response(response_text):

    agents = []

    try:

        soup = BeautifulSoup(response_text, "xml")

        rows = soup.find_all("row")

        print("Rows found:", len(rows))

        for row in rows:

            cells = row.find_all("cell")

            values = []

            for cell in cells:
                values.append(cell.get_text(strip=True))

            print("Cells found:", len(values))

            if not values:
                continue

            agent = {
                "internal_id": values[0] if len(values) > 0 else "",
                "agent_name": values[1] if len(values) > 1 else "",
                "license_no": values[2] if len(values) > 2 else "",
                "agent_code": values[3] if len(values) > 3 else "",
                "urn": values[4] if len(values) > 4 else "",
                "insurance_type": values[5] if len(values) > 5 else "",
                "insurer_name": values[6] if len(values) > 6 else "",
                "extra": values[7] if len(values) > 7 else "",
                "state": values[8] if len(values) > 8 else "",
                "district": values[9] if len(values) > 9 else "",
                "pincode": values[10] if len(values) > 10 else "",
                "license_start_date": values[11] if len(values) > 11 else "",
                "license_end_date": values[12] if len(values) > 12 else "",
                "active": values[13] if len(values) > 13 else "",
                "mobile_1": values[14] if len(values) > 14 else "",
                "mobile_2": values[15] if len(values) > 15 else "",
            }

            agents.append(agent)

    except Exception as e:

        print("Parse error:", e)

    return agents


# =========================================================

# PROGRESS TRACKING

# =========================================================

PROGRESS_FILE = "progress.txt"

completed = set()

if os.path.exists(PROGRESS_FILE):


    with open(PROGRESS_FILE, "r") as f:

        for line in f:
            completed.add(line.strip())


# =========================================================

# DEDUPLICATION

# =========================================================

seen_agents = set()

all_agents = []

# =========================================================

# MAIN LOOP

# =========================================================

for district in districts[11:12]:


    district_id = district["district_id"]
    district_name = district["district_name"]
    pincode_range = district["pincode_range"]

    pincodes = expand_pincode_range(pincode_range)

    print("\n=================================================")
    print("DISTRICT:", district_name)
    print("TOTAL PINCODES:", len(pincodes))

    for pincode in pincodes:

        for insurer in insurers:

            insurer_id = insurer["insurer_id"]
            insurer_name = insurer["insurer_name"]

            progress_key = (
                f"{district_id}|{pincode}|{insurer_id}"
            )

            if progress_key in completed:
                continue

            customquery = (
                f",,,{INSURANCE_TYPE},"
                f"{insurer_id},"
                f"{STATE_ID},"
                f"{district_id},"
                f"{pincode}"
            )

            payload = {
                "page": 1,
                "rp": 9999,
                "sortname": "AgentName",
                "sortorder": "asc",
                "query": "",
                "qtype": "",
                "customquery": customquery
            }

            print("\n-------------------------------------")
            print("District :", district_name)
            print("Pincode  :", pincode)
            print("Insurer  :", insurer_name)

            try:

                response = session.post(
                    LOCATE_URL,
                    headers=HEADERS,
                    data=payload,
                    timeout=TIMEOUT
                )

                print("Status:", response.status_code)

                # =========================================
                # SAVE RAW RESPONSE
                # =========================================

                filename = (
                    f"raw/"
                    f"{district_name}_"
                    f"{pincode}_"
                    f"{insurer_id}.xml"
                )

                with open(filename, "w", encoding="utf-8") as f:
                    f.write(response.text)

                # =========================================
                # PARSE
                # =========================================
             
                agents = parse_response(response.text)

                print("Agents found:", len(agents))

                # =========================================
                # DEDUPLICATE
                # =========================================

                for agent in agents:

                    unique_key = agent["internal_id"]

                    if unique_key in seen_agents:
                        continue

                    seen_agents.add(unique_key)

                    all_agents.append(agent)

                # =========================================
                # SAVE PROGRESS
                # =========================================

                with open(PROGRESS_FILE, "a") as f:
                    f.write(progress_key + "\n")

                # =========================================
                # EXPORT INTERMEDIATE RESULTS
                # =========================================

                with open(
                    "exports/agents.json",
                    "w",
                    encoding="utf-8"
                ) as f:

                    json.dump(
                        all_agents,
                        f,
                        indent=2,
                        ensure_ascii=False
                    )

                # =========================================
                # DELAY
                # =========================================

                # time.sleep(
                #     random.uniform(
                #         REQUEST_DELAY_MIN,
                #         REQUEST_DELAY_MAX
                #     )
                # )

            except Exception as e:

                print("REQUEST FAILED:", e)


# =========================================================

# DONE

# =========================================================

print("\n=================================================")
print("CRAWL COMPLETE")
print("TOTAL UNIQUE AGENTS:", len(all_agents))

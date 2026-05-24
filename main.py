import requests
import time
import random
import json
import os
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://agencyportal.irdai.gov.in"

LOCATE_URL = f"{BASE_URL}/_WebService/PublicAccess/AgentLocator.asmx/LocateAgent"

HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Referer": f"{BASE_URL}/PublicAccess/AgentLocator.aspx",
    "User-Agent": "Mozilla/5.0"
}

# -------------------------
# Robust session
# -------------------------

session = requests.Session()

retries = Retry(
    total=5,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504]
)

adapter = HTTPAdapter(max_retries=retries)

session.mount("http://", adapter)
session.mount("https://", adapter)

# -------------------------
# Config
# -------------------------

insurance_type = 1
insurer_id = 24
state_id = 19

districts = [
    {"district_id": 602, "pincode": "148025"},
]

# -------------------------
# Output folders
# -------------------------

os.makedirs("raw", exist_ok=True)

# -------------------------
# Parse LocateAgent response
# -------------------------

def parse_response(text):

    agents = []

    try:
        soup = BeautifulSoup(text, "xml")

        raw_text = soup.get_text()

        # Sometimes XML wraps HTML
        html_soup = BeautifulSoup(raw_text, "html.parser")

        rows = html_soup.find_all("tr")

        for row in rows:

            cols = row.find_all("td")

            if len(cols) < 8:
                continue

            agent = {
                "agent_name": cols[0].get_text(strip=True),
                "license_no": cols[1].get_text(strip=True),
                "irda_urn": cols[2].get_text(strip=True),
                "agent_id": cols[3].get_text(strip=True),
                "insurance_type": cols[4].get_text(strip=True),
                "insurer": cols[5].get_text(strip=True),
                "dp_id": cols[6].get_text(strip=True),
                "state": cols[7].get_text(strip=True),
                "district": cols[8].get_text(strip=True)
                if len(cols) > 8 else ""
            }

            agents.append(agent)

    except Exception as e:
        print("Parse error:", e)

    return agents

# -------------------------
# Main crawler
# -------------------------

all_agents = []

for item in districts:

    district_id = item["district_id"]
    pincode = item["pincode"]

    customquery = f",,,{insurance_type},{insurer_id},{state_id},{district_id},{pincode}"

    payload = {
        "page": 1,
        "rp": 9999,
        "sortname": "AgentName",
        "sortorder": "asc",
        "query": "",
        "qtype": "",
        "customquery": customquery
    }

    print("Fetching:", customquery)

    try:

        response = session.post(
            LOCATE_URL,
            headers=HEADERS,
            data=payload,
            timeout=60
        )

        print("Status:", response.status_code)

        # Save raw response
        raw_file = f"raw/{district_id}_{pincode}.xml"

        with open(raw_file, "w", encoding="utf-8") as f:
            f.write(response.text)

        agents = parse_response(response.text)

        print(f"Found {len(agents)} agents")

        all_agents.extend(agents)

        time.sleep(random.uniform(1, 3))

    except Exception as e:
        print("Request failed:", e)

# -------------------------
# Save JSON
# -------------------------

with open("agents.json", "w", encoding="utf-8") as f:
    json.dump(all_agents, f, indent=2, ensure_ascii=False)

print(f"\nTotal agents scraped: {len(all_agents)}")
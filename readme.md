# IRDAI Agent Locator Scraper

A reverse-engineered Python client and scraper for the public IRDAI Agent Locator portal.

This project provides:

* structured access to IRDAI public agent locator APIs
* insurer/state/district enumeration
* automated agent discovery
* XML/HTML response parsing
* rate-limited crawling utilities

The scraper targets publicly accessible endpoints exposed by the IRDAI Agency Portal.

---

# Features

* Reverse engineered `.asmx` AJAX APIs
* No Selenium/browser automation required
* Session-based requests
* XML dataset parsing
* Retry + backoff handling
* State → district discovery
* Insurance type → insurer discovery
* Agent search automation
* Raw response archival
* JSON export
* Extensible architecture

---

# Endpoints Discovered

## Get Insurers

```http
POST /_WebService/General/DataLoader.asmx/GetInsurer
```

Payload:

```json
{InsuranceType:'1'}
```

Returns:

* insurer IDs
* insurer names
* insurer codes

---

## Get Districts

```http
POST /_WebService/General/DataLoader.asmx/GetDistrict
```

Payload:

```json
{StateID:'19'}
```

Returns:

* district IDs
* district names

---

## Locate Agents

```http
POST /_WebService/PublicAccess/AgentLocator.asmx/LocateAgent
```

Payload:

```txt
page=1
&rp=9999
&sortname=AgentName
&sortorder=asc
&query=
&qtype=
&customquery=,,,1,24,19,602,148025
```

---

# customquery Structure

The `customquery` parameter maps to:

```txt
[name],[license_no],[agent_id],[insurance_type],[insurer],[state],[district],[pincode]
```

Example:

```txt
,,,1,24,19,602,148025
```

Meaning:

| Field          | Value  |
| -------------- | ------ |
| name           | empty  |
| license_no     | empty  |
| agent_id       | empty  |
| insurance_type | 1      |
| insurer        | 24     |
| state          | 19     |
| district       | 602    |
| pincode        | 148025 |

---

# Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/irdai-agent-locator-scraper.git

cd irdai-agent-locator-scraper
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Requirements

```txt
requests
beautifulsoup4
lxml
xmltodict
pandas
```

---

# Quick Start

## Basic Agent Search

```python
from client import locate_agents

agents = locate_agents(
    insurance_type=1,
    insurer_id=24,
    state_id=19,
    district_id=602,
    pincode="148025"
)

print(agents)
```

---

# Example Response

```json
[
  {
    "agent_name": "John Doe",
    "license_no": "LIC12345",
    "irda_urn": "IRDA123456",
    "agent_id": "AGT001",
    "insurance_type": "General",
    "insurer": "ICICI Lombard",
    "dp_id": "DP123",
    "state": "Punjab",
    "district": "Sangrur"
  }
]
```

---

# Project Structure

```txt
.
├── client/
│   ├── api.py
│   ├── parser.py
│   ├── models.py
│   └── utils.py
│
├── data/
│   ├── states.json
│   ├── insurers.json
│   └── districts/
│
├── raw/
│   └── responses/
│
├── scripts/
│   ├── crawl_all.py
│   ├── export_json.py
│   └── export_csv.py
│
├── tests/
│
├── requirements.txt
└── README.md
```

---

# Parsing Notes

The portal uses:

* ASP.NET `.asmx` services
* AJAX POST requests
* XML DataSet responses
* occasional HTML-wrapped XML payloads

The parser supports:

* XML datasets
* HTML table extraction
* malformed government responses
* mixed payloads

---

# Rate Limiting

Government infrastructure is fragile.

Please avoid:

* excessive concurrency
* aggressive crawling
* request flooding

Recommended:

```python
time.sleep(random.uniform(1, 3))
```

Default crawler settings are intentionally conservative.

---

# Pagination

The API accepts:

```txt
page
rp
sortname
sortorder
```

Example:

```txt
page=1
rp=9999
```

However:

* some combinations may silently truncate results
* large districts should be tested carefully
* pagination behavior may vary

---

# Data Quality Notes

The public dataset may contain:

* duplicate agents
* expired licenses
* stale mappings
* incomplete records
* inconsistent insurer naming

Consumers should validate data independently before operational use.

---

# Recommended Usage

Useful for:

* insurance distribution research
* intermediary network analysis
* geography-wise insurer mapping
* public regulatory data access
* academic analysis
* CRM enrichment pipelines
* insurance-tech experimentation

---

# Ethical Usage

This repository accesses publicly exposed endpoints.

Users should:

* comply with applicable laws
* avoid abusive traffic patterns
* respect public infrastructure
* avoid redistributing sensitive personal data irresponsibly

This repository is intended for:

* interoperability
* public information access
* research
* automation tooling

---

# Legal Disclaimer

This project is an independent reverse-engineering effort and is not affiliated with:

* IRDAI
* Insurance Information Bureau (IIB)
* Government of India

All trademarks and platform ownership belong to their respective owners.

Users are solely responsible for their usage of this software.

---

# Future Improvements

Planned:

* async crawler
* SQLite/Postgres backend
* incremental crawling
* deduplication engine
* checkpoint recovery
* district auto-discovery
* insurer auto-discovery
* CLI interface
* Docker support

---

# Contributing

Pull requests are welcome.

Suggested areas:

* parser improvements
* response normalization
* pagination handling
* retry strategies
* export formats
* testing

---

# Research Notes

The portal appears to use:

* Microsoft IIS
* ASP.NET 4.x
* legacy Flexigrid-style responses
* XML DataSet serialization

The architecture allows lightweight programmatic access without browser automation.

---

# License

MIT License

Use responsibly.

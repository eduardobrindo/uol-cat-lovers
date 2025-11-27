# 🐱 UOLCatLovers - Data Extraction (ETL)

This directory contains the data extraction and transformation module of the UOLCatLovers pipeline. The objective of this script is to prepare the raw data (Raw Layer) to be ingested into the Data Warehouse (BigQuery).

## 📄 About the Script (`extract_cat_facts.py`)

This script executes the first stage of the ELT (Extract, Load, Transform) pipeline. Due to the occasional instability of the public *Cat Facts* API, this module was configured to read from a local simulated data source (`mock`), ensuring development stability and testing consistency.

### Key Features:
1.  **Extraction:** Reads raw data in JSON format from a local source (`mock_cat_facts.json`).
2.  **Transformation:** Normalizes column names from *camelCase* (JSON/Javascript standard) to *snake_case* (SQL/BigQuery standard).
3.  **Output:** Generates a CSV file with a *timestamp* in the filename, ensuring historical tracking and preventing file overwrites.

## 🛠️ Prerequisites

* **Python 3.6+** installed.
* Standard Python libraries (no external `pip` packages required for this specific script):
    * `json`, `csv`, `logging`, `os`, `datetime`

## 🚀 How to Run

1.  Ensure the mock data file **`mock_cat_facts.json`** is present in the same directory as the script.
2.  Execute the following command in your terminal or PowerShell:

```bash
python extract_cat_facts.py
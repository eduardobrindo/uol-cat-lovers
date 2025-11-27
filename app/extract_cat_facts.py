import json
import csv
import logging
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
from typing import List, Dict, Any, Optional

# Professional Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def generate_output_filename() -> str:
    """
    Generates a CSV filename with a timestamp in YYYYMMDDHH24MISS format.
    Example: cat_facts_20251127093000.csv
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"cat_facts_{timestamp}.csv"

def fetch_data_from_api(url: str, amount: int = 500) -> Optional[List[Dict[str, Any]]]:
    """
    Attempts to fetch data from the API with a retry mechanism (3 attempts).
    Returns None if all attempts fail.
    """
    # Configuration for Retries
    retry_strategy = Retry(
        total=3,  # Total number of retries
        backoff_factor=1,  # Wait 1s, 2s, 4s between retries
        status_forcelist=[429, 500, 502, 503, 504],  # Retry on these errors
        allowed_methods=["GET"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    params = {
        'animal_type': 'cat',
        'amount': amount
    }

    try:
        logging.info(f"Attempting to fetch data from API: {url}")
        response = http.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Ensure we return a list
        if isinstance(data, list):
            logging.info(f"✅ Success! {len(data)} records fetched from API.")
            return data
        elif isinstance(data, dict):
            return [data]
        
    except requests.exceptions.RequestException as e:
        logging.warning(f"⚠️ API request failed after 3 attempts: {e}")
        return None
        
    return None

def load_json_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Loads data from the local JSON file (Mock/Simulation).
    """
    if not os.path.exists(file_path):
        logging.error(f"Input file not found: {file_path}")
        return []

    try:
        logging.info(f"🔄 Fallback: Loading data from local file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logging.info(f"✅ Success! {len(data)} records loaded from local file.")
            return data
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error reading file: {e}")
        return []

def transform_data(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforms/Normalizes data to match the BigQuery Schema.
    Ensures keys are in snake_case format.
    """
    transformed_data = []
    
    for item in raw_data:
        # Handling potential missing keys safely
        new_item = {
            'fact_id': item.get('_id'),
            'version': item.get('__v'),
            'text': item.get('text'),
            'created_at': item.get('updatedAt'),
            'updated_at': item.get('updatedAt'),
            'deleted': item.get('deleted'),
            'source': item.get('source'),
            'sent_count': item.get('sentCount')
        }
        transformed_data.append(new_item)
        
    return transformed_data

def save_csv(data: List[Dict[str, Any]]) -> None:
    """
    Saves the transformed data into a timestamped CSV file.
    """
    if not data:
        logging.warning("No data available to save.")
        return

    filename = generate_output_filename()

    try:
        # Columns header - MUST match the SQL Create Table definition
        columns = ['fact_id', 'version', 'text', 'created_at', 'updated_at', 'deleted', 'source', 'sent_count']
        
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(data)
            
        logging.info(f"✅ CSV file generated successfully: {filename}")
        
    except Exception as e:
        logging.error(f"Error saving CSV: {e}")

if __name__ == "__main__":
    # Configuration
    API_URL = "https://cat-fact.herokuapp.com/facts/random"
    MOCK_FILE = "mock_cat_facts.json"
    
    # 1. Extraction Strategy (API First -> Fallback to Mock)
    raw_data = fetch_data_from_api(API_URL, amount=500)
    
    if not raw_data:
        logging.warning("⚠️ API is unavailable. Switching to local mock data.")
        raw_data = load_json_data(MOCK_FILE)
    
    # 2. Process Data if available
    if raw_data:
        # Transformation (Map fields to Schema)
        clean_data = transform_data(raw_data)
        
        # Load (Save to CSV with timestamp)
        save_csv(clean_data)
    else:
        logging.error("❌ Critical Failure: Could not load data from API or Mock file.")
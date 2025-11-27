import json
import csv
import logging
import os
from datetime import datetime
from typing import List, Dict, Any

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
    # %Y=Year, %m=Month, %d=Day, %H=Hour(24h), %M=Minute, %S=Second
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"cat_facts_{timestamp}.csv"

def load_json_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Loads data from the local JSON file (Mock/Simulation).
    """
    if not os.path.exists(file_path):
        logging.error(f"Input file not found: {file_path}")
        return []

    try:
        logging.info(f"Loading data from file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logging.info(f"Success! {len(data)} records loaded.")
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
        # Mapping: SQL Column Name <- API/JSON Key
        new_item = {
            'fact_id': item.get('_id'),
            'version': item.get('__v'),
            'text': item.get('text'),
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
        columns = ['fact_id', 'version', 'text', 'updated_at', 'deleted', 'source', 'sent_count']
        
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(data)
            
        logging.info(f"✅ CSV file generated successfully: {filename}")
        
    except Exception as e:
        logging.error(f"Error saving CSV: {e}")

if __name__ == "__main__":
    # Configuration
    INPUT_FILE = "mock_cat_facts.json"
    
    # 1. Extraction (Load from local JSON)
    raw_data = load_json_data(INPUT_FILE)
    
    if raw_data:
        # 2. Transformation (Map fields to Schema)
        clean_data = transform_data(raw_data)
        
        # 3. Load (Save to CSV with timestamp)
        save_csv(clean_data)
"""
Configuration loading for the RFQ Dashboard.
"""
import os
import json
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """Load configuration from config.json or environment variables."""
    config = {}

    # Try to load from config.json
    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)

    # Override with environment variables if present
    config['mongo_uri'] = os.getenv('MONGO_URI', config.get('mongo_uri', 'mongodb://mongodb:27017'))
    config['mongo_db'] = os.getenv('MONGO_DB', config.get('mongo_db', 'rfq_tracker'))

    return config
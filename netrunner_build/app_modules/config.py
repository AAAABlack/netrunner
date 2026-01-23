from shodan import Shodan
from dotenv import load_dotenv
import os
import csv
from pymongo import MongoClient
from datetime import datetime, timezone

env_path = os.path.join(os.path.dirname(__file__), '..', '..', 'secret', '.env')
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("api_key")

if api_key:
    api_key = api_key.strip()

try:
    api = Shodan(api_key) if api_key else None
    if api:
        api.info()
        print("✓ Shodan API initialized")
    else:
        print("⚠ Shodan API key not configured")
        api = None
except Exception as e:
    print(f"⚠ Shodan API unavailable: {e}")
    api = None

# MongoDB connection
try:
    mongo_client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    # Test the connection
    mongo_client.server_info()
    mongo_db = mongo_client["netrunner"]
    scans_collection = mongo_db["scans"]
    print("✓ MongoDB connection established")
except Exception as e:
    print(f"⚠ Warning: MongoDB not available - {e}")
    print("  The app will work without caching. To enable caching:")
    print("  1. Install MongoDB from https://www.mongodb.com/try/download/community")
    print("  2. Start MongoDB service")
    mongo_client = None
    mongo_db = None
    scans_collection = None

# here we load the official service ports CSV for protocol and service name lookup, got from IANA
port_service_map = {}
csv_path = os.path.join(os.path.dirname(__file__), '..', 'react', 'src', 'assets', 'datasets', 'service_ports.csv')
try:
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                port_str = row.get('Port Number', '').strip()
                # skipping port ranges if applicable
                if not port_str or '-' in port_str:
                    continue
                port = int(port_str)
                protocol = row.get('Transport Protocol', '').lower().strip()
                service_name = row.get('Service Name', '').lower().strip()
                if port and service_name:  # add if we have both port and service name
                    port_service_map[port] = {
                        'protocol': protocol,
                        'service': service_name
                    }
            except (ValueError, KeyError):
                continue
    print(f"Loaded {len(port_service_map)} port/service mappings from CSV")
except Exception as e:
    print(f"Error loading service ports CSV: {e}")
    port_service_map = {}
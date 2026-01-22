from shodan import Shodan
from dotenv import load_dotenv
import os
import csv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', 'secret', '.env'))
try:
    api = Shodan(os.getenv("api_key"))  # initializing Shodan API
except Exception as e:
    print(f"Error initializing Shodan API: {e}")
    api = None

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
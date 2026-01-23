from fastapi import APIRouter, HTTPException, Request
import json
from datetime import datetime, timezone
from .config import api, port_service_map, scans_collection
import socket
import time

router = APIRouter()

@router.post('/api/scan')
async def scan(request: Request):
    """Endpoint to scan an IP address or hostname using Shodan API"""

    # in-app rate limitting
    if not hasattr(scan, "last_call"):
        scan.last_call = 0.0

    now = time.time()
    if now - scan.last_call < 5:
        raise HTTPException(status_code=429, detail="You're scanning too fast!")

    scan.last_call = now

    if api is None:
        raise HTTPException(status_code=500, detail='Shodan API not initialized')

    try:
        data = await request.json()
        address = data.get('host')
        force_rescan = data.get('force_rescan', False)

        if not address:
            raise HTTPException(status_code=400, detail='No host provided')

        # DNS resolution
        try:
            socket.inet_aton(address)
            resolved_ip = address
        except socket.error:
            try:
                resolved_ip = socket.gethostbyname(address)
            except socket.gaierror:
                raise HTTPException(
                    status_code=400,
                    detail=f'Could not resolve hostname: {address}'
                )

        # checking MongoDB for cached scan if not forcing rescan
        if not force_rescan and scans_collection is not None:
            cached_scan = scans_collection.find_one({"target.ip": resolved_ip})
            if cached_scan:
                cached_scan.pop('_id', None)
                cached_scan['cached'] = True
                return cached_scan

        # query Shodan API
        answer = api.host(resolved_ip)

            # look up protocol and service from the official IANA CSV.
        services = {}
        for entry in answer.get("data", []):
            port = entry.get("port")
            transport = entry.get("transport", "tcp")
            service_name = entry.get("service", "unknown")

            if port in port_service_map:
                csv_data = port_service_map[port]
                transport = csv_data['protocol']
                if csv_data['service']:
                    service_name = csv_data['service']

            key = f"{port}/{transport}"
            if key not in services:
                services[key] = {
                    "port": port,
                    "transport": transport,
                    "service": service_name,
                    "product": entry.get("product", "Unknown"),
                    "version": entry.get("version", "Unknown"),
                    "banner": entry.get("banner", "")[:150]
                }

        # extract vulnerabilities
        vulns_raw = answer.get("vulns", {})
        vulnerabilities = []

        if isinstance(vulns_raw, dict):
            for cve_id, details in vulns_raw.items():
                vulnerabilities.append({
                    "cve": cve_id,
                    "cvss": details.get("cvss"),
                    "verified": details.get("verified", False),
                    "summary": details.get("summary", "")
                })
        elif isinstance(vulns_raw, list):
            for cve_id in vulns_raw:
                vulnerabilities.append({
                    "cve": cve_id,
                    "cvss": None,
                    "verified": False,
                    "summary": ""
                })
        # cleaning and return response, important for formatting later
        cleaned = {
            "target": {
                "ip": answer.get("ip_str"),
                "hostnames": answer.get("hostnames", [])
            },
            "attribution": {
                "organization": answer.get("org", "Unknown"),
                "isp": answer.get("isp", "Unknown"),
                "asn": answer.get("asn", "Unknown")
            },
            "geolocation": {
                "country": answer.get("country_name", "Unknown"),
                "region": answer.get("region_code", "Unknown"),
                "city": answer.get("city", "Unknown")
            },
            "system": {
                "os": answer.get("os", "Unknown")
            },
            "network_exposure": {
                "ports": sorted(answer.get("ports", [])),
                "services": list(services.values())
            },
            "security_context": {
                "tags": answer.get("tags", []),
                "vulns_present": len(vulnerabilities) > 0,
                "vulnerabilities": vulnerabilities
            },
            "scan_metadata": {
                "data_source": "Shodan",
                "scan_timestamp": datetime.now(timezone.utc).isoformat()
            },
            "summary": {
                "total_ports": len(answer.get("ports", [])),
                "total_services": len(services),
                "identified_products": len(
                    {s["product"] for s in services.values() if s["product"] != "Unknown"}
                ),
                "vulnerability_count": len(vulnerabilities)
            },
            "cached": False
        }

        if scans_collection is not None:
            try:
                scans_collection.update_one(
                    {"target.ip": cleaned["target"]["ip"]},
                    {"$set": cleaned},
                    upsert=True
                )
            except Exception as e:
                print(f"Error saving to MongoDB: {e}")

        return cleaned

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in scan endpoint: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal error")

import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
import sys
import os
from mainapp import app
from app_modules import routes


class TestScanEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

        # reset rate limiter between tests to avoid false 429s
        if hasattr(routes.scan, "last_call"):
            routes.scan.last_call = 0.0

        # disabling MongoDB caching for most tests
        self.mongo_patcher = patch("app_modules.routes.scans_collection")
        self.mock_collection = self.mongo_patcher.start()
        self.mock_collection.find_one.return_value = None

    def tearDown(self):
        self.mongo_patcher.stop()

    def test_successful_scan_structure(self):
        """Happy path: valid scan returns expected formnat"""
        mock_response = {
            "ip_str": "8.8.8.8",
            "hostnames": ["dns.google"],
            "org": "Google",
            "isp": "Google",
            "asn": "AS15169",
            "country_name": "United States",
            "region_code": "CA",
            "city": "Mountain View",
            "ports": [53, 443],
            "tags": [],
            "vulns": {},
            "data": []
        }

        with patch("app_modules.routes.api") as mock_api:
            mock_api.host.return_value = mock_response

            res = self.client.post("/api/scan", json={"host": "8.8.8.8"})
            self.assertEqual(res.status_code, 200)

            body = res.json()
            for key in (
                "target",
                "attribution",
                "geolocation",
                "system",
                "network_exposure",
                "security_context",
                "scan_metadata",
                "summary",
            ):
                self.assertIn(key, body)

    def test_vulnerability_processing(self):
        """vulns are normalized from Shodan response"""
        mock_response = {
            "ip_str": "1.1.1.1",
            "hostnames": [],
            "org": "Test",
            "ports": [],
            "tags": [],
            "vulns": {
                "CVE-2021-1234": {
                    "cvss": 7.5,
                    "verified": True,
                    "summary": "Test vulnerability"
                }
            },
            "data": []
        }

        with patch("app_modules.routes.api") as mock_api:
            mock_api.host.return_value = mock_response

            res = self.client.post("/api/scan", json={"host": "1.1.1.1"})
            body = res.json()

            self.assertTrue(body["security_context"]["vulns_present"])
            self.assertEqual(len(body["security_context"]["vulnerabilities"]), 1)

    def test_cached_result_is_returned(self):
        """Cached MongoDB result should mess up shodan call"""
        cached = {
            "target": {"ip": "1.1.1.1", "hostnames": []},
            "attribution": {"organization": "Test", "isp": "Test", "asn": "AS123"},
            "geolocation": {"country": "US", "region": "CA", "city": "Test"},
            "system": {"os": "Unknown"},
            "network_exposure": {"ports": [80], "services": []},
            "security_context": {
                "tags": [],
                "vulns_present": False,
                "vulnerabilities": []
            },
            "scan_metadata": {"data_source": "Shodan", "scan_timestamp": "2026-01-01"},
            "summary": {
                "total_ports": 1,
                "total_services": 0,
                "identified_products": 0,
                "vulnerability_count": 0
            }
        }

        self.mock_collection.find_one.return_value = cached.copy()

        res = self.client.post("/api/scan", json={"host": "1.1.1.1"})
        body = res.json()

        self.assertTrue(body["cached"])
        self.assertEqual(body["target"]["ip"], "1.1.1.1")

    def test_missing_host_returns_400(self):
        """Request without host should fail quick"""
        res = self.client.post("/api/scan", json={})
        self.assertEqual(res.status_code, 400)

    def test_missing_shodan_api(self):
        """Endpoint returns 500 if API not configured"""
        with patch("app_modules.routes.api", None):
            res = self.client.post("/api/scan", json={"host": "8.8.8.8"})
            self.assertEqual(res.status_code, 500)


if __name__ == "__main__":
    unittest.main()

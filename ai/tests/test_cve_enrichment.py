"""
Tests for CVE enrichment module
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest  # noqa: E402

from api.cve_enrichment import (  # noqa: E402
    extract_cves,
    fetch_cve_from_nvd,
    enrich_log_with_cves,
    get_cve_info,
    CVECache,
)


class TestCVEExtraction:
    """Test CVE extraction from text"""

    def test_extract_single_cve(self):
        """Test extracting a single CVE ID"""
        text = "This exploit uses CVE-2021-44228"
        cves = extract_cves(text)
        assert len(cves) == 1
        assert "CVE-2021-44228" in cves

    def test_extract_multiple_cves(self):
        """Test extracting multiple CVE IDs"""
        text = "Exploits CVE-2021-44228 and CVE-2020-1234 were detected"
        cves = extract_cves(text)
        assert len(cves) == 2
        assert "CVE-2021-44228" in cves
        assert "CVE-2020-1234" in cves

    def test_extract_no_cves(self):
        """Test text with no CVE IDs"""
        text = "No vulnerabilities here"
        cves = extract_cves(text)
        assert len(cves) == 0

    def test_extract_duplicate_cves(self):
        """Test deduplication of CVE IDs"""
        text = "CVE-2021-44228 and CVE-2021-44228 again"
        cves = extract_cves(text)
        assert len(cves) == 1

    def test_extract_from_empty_string(self):
        """Test extraction from empty string"""
        cves = extract_cves("")
        assert len(cves) == 0

    def test_extract_from_none(self):
        """Test extraction from None"""
        cves = extract_cves(None)
        assert len(cves) == 0


class TestCVECache:
    """Test CVE caching functionality"""

    def test_cache_set_and_get(self, tmp_path):
        """Test setting and getting cache entries"""
        cache_file = tmp_path / "test_cache.json"
        cache = CVECache(cache_file)

        test_data = {"cve_id": "CVE-2021-44228", "cvss_base_score": 10.0}
        cache.set("CVE-2021-44228", test_data)

        retrieved = cache.get("CVE-2021-44228")
        assert retrieved is not None
        assert retrieved["cve_id"] == "CVE-2021-44228"

    def test_cache_miss(self, tmp_path):
        """Test cache miss"""
        cache_file = tmp_path / "test_cache.json"
        cache = CVECache(cache_file)

        retrieved = cache.get("CVE-9999-9999")
        assert retrieved is None

    def test_cache_persistence(self, tmp_path):
        """Test cache persistence to disk"""
        cache_file = tmp_path / "test_cache.json"

        # Create cache and add entry
        cache1 = CVECache(cache_file)
        test_data = {"cve_id": "CVE-2021-44228", "cvss_base_score": 10.0}
        cache1.set("CVE-2021-44228", test_data)

        # Create new cache instance and verify data persists
        cache2 = CVECache(cache_file)
        retrieved = cache2.get("CVE-2021-44228")
        assert retrieved is not None
        assert retrieved["cve_id"] == "CVE-2021-44228"


class TestNVDFetch:
    """Test NVD API interaction"""

    @patch("api.cve_enrichment.requests.get")
    def test_fetch_cve_success(self, mock_get):
        """Test successful CVE fetch from NVD"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "vulnerabilities": [
                {
                    "cve": {
                        "id": "CVE-2021-44228",
                        "descriptions": [{"lang": "en", "value": "Apache Log4j2 vulnerability"}],
                        "metrics": {
                            "cvssMetricV31": [
                                {
                                    "cvssData": {
                                        "baseScore": 10.0,
                                        "baseSeverity": "CRITICAL",
                                        "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
                                        "attackVector": "NETWORK",
                                        "attackComplexity": "LOW",
                                        "privilegesRequired": "NONE",
                                        "userInteraction": "NONE",
                                        "scope": "CHANGED",
                                        "confidentialityImpact": "HIGH",
                                        "integrityImpact": "HIGH",
                                        "availabilityImpact": "HIGH",
                                    },
                                    "exploitabilityScore": 3.9,
                                    "impactScore": 6.0,
                                }
                            ]
                        },
                        "published": "2021-12-10T10:15:09.000",
                        "lastModified": "2021-12-14T01:15:00.000",
                    }
                }
            ]
        }
        mock_get.return_value = mock_response

        result = fetch_cve_from_nvd("CVE-2021-44228")

        assert result is not None
        assert result["cve_id"] == "CVE-2021-44228"
        assert result["cvss_base_score"] == 10.0
        assert result["cvss_severity"] == "CRITICAL"
        assert result["enrichment_status"] == "success"

    @patch("api.cve_enrichment.requests.get")
    def test_fetch_cve_not_found(self, mock_get):
        """Test CVE not found"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"vulnerabilities": []}
        mock_get.return_value = mock_response

        result = fetch_cve_from_nvd("CVE-9999-9999")

        assert result is None

    @patch("api.cve_enrichment.requests.get")
    @patch("api.cve_enrichment._cache")
    def test_fetch_cve_timeout(self, mock_cache, mock_get):
        """Test API timeout"""
        import requests

        mock_cache.get.return_value = None  # Ensure cache miss
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")

        result = fetch_cve_from_nvd("CVE-2021-44228")

        assert result is not None
        assert result["enrichment_status"] == "timeout"


class TestLogEnrichment:
    """Test log enrichment functionality"""

    @patch("api.cve_enrichment.fetch_cve_from_nvd")
    def test_enrich_log_with_cve(self, mock_fetch):
        """Test enriching log with CVE data"""
        mock_fetch.return_value = {
            "cve_id": "CVE-2021-44228",
            "cvss_base_score": 10.0,
            "cvss_severity": "CRITICAL",
            "enrichment_status": "success",
        }

        log_entry = {"message": "Exploit attempt using CVE-2021-44228", "src_ip": "192.168.1.1"}

        enriched = enrich_log_with_cves(log_entry)

        assert enriched["cve_detected"] is True
        assert "CVE-2021-44228" in enriched["cve_ids"]
        assert enriched["max_cvss_score"] == 10.0
        assert enriched["cve_severity"] == "CRITICAL"

    def test_enrich_log_without_cve(self):
        """Test log without CVE"""
        log_entry = {"message": "Normal login attempt", "src_ip": "192.168.1.1"}

        enriched = enrich_log_with_cves(log_entry)

        assert "cve_detected" not in enriched
        assert "cve_ids" not in enriched

    @patch("api.cve_enrichment.fetch_cve_from_nvd")
    def test_enrich_log_severity_high(self, mock_fetch):
        """Test severity classification for HIGH"""
        mock_fetch.return_value = {
            "cve_id": "CVE-2020-1234",
            "cvss_base_score": 7.5,
            "cvss_severity": "HIGH",
            "enrichment_status": "success",
        }

        log_entry = {"command": "exploit -u CVE-2020-1234"}

        enriched = enrich_log_with_cves(log_entry)

        assert enriched["cve_severity"] == "HIGH"


class TestGetCVEInfo:
    """Test public API function"""

    def test_get_cve_info_invalid_format(self):
        """Test invalid CVE ID format"""
        result = get_cve_info("INVALID-ID")

        assert "error" in result
        assert result["status"] == "invalid"

    @patch("api.cve_enrichment.fetch_cve_from_nvd")
    def test_get_cve_info_not_found(self, mock_fetch):
        """Test CVE not found"""
        mock_fetch.return_value = None

        result = get_cve_info("CVE-9999-9999")

        assert "error" in result
        assert result["status"] == "not_found"

    @patch("api.cve_enrichment.fetch_cve_from_nvd")
    def test_get_cve_info_success(self, mock_fetch):
        """Test successful CVE info retrieval"""
        mock_data = {
            "cve_id": "CVE-2021-44228",
            "cvss_base_score": 10.0,
            "cvss_severity": "CRITICAL",
            "enrichment_status": "success",
        }
        mock_fetch.return_value = mock_data

        result = get_cve_info("CVE-2021-44228")

        assert result == mock_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

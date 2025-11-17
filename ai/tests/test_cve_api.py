"""
Tests for CVE API endpoints (integration-style tests)
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest  # noqa: E402


class TestCVEEndpointsLogic:
    """Test CVE API endpoint logic without full app dependencies"""

    @patch("api.cve_enrichment.get_cve_info")
    def test_cveinfo_endpoint_logic_success(self, mock_get_cve_info):
        """Test successful CVE info retrieval logic"""
        from api.cve_enrichment import get_cve_info

        mock_data = {
            "cve_id": "CVE-2021-44228",
            "cvss_base_score": 10.0,
            "cvss_severity": "CRITICAL",
            "cve_description": "Apache Log4j2 vulnerability",
            "enrichment_status": "success",
        }
        mock_get_cve_info.return_value = mock_data

        result = get_cve_info("CVE-2021-44228")

        assert result["cve_id"] == "CVE-2021-44228"
        assert result["cvss_base_score"] == 10.0
        assert result["cvss_severity"] == "CRITICAL"

    def test_cveinfo_endpoint_logic_invalid(self):
        """Test invalid CVE ID format logic"""
        from api.cve_enrichment import get_cve_info

        result = get_cve_info("INVALID")

        assert "error" in result
        assert result["status"] == "invalid"

    def test_cve_detect_endpoint_logic(self):
        """Test CVE detection logic"""
        from api.cve_enrichment import extract_cves

        cves = extract_cves("Exploiting CVE-2021-44228 and CVE-2020-1234")

        assert len(cves) == 2
        assert "CVE-2021-44228" in cves
        assert "CVE-2020-1234" in cves

    @patch("api.cve_enrichment.fetch_cve_from_nvd")
    def test_cve_enrich_endpoint_logic(self, mock_fetch):
        """Test log enrichment logic"""
        from api.cve_enrichment import enrich_log_with_cves

        mock_fetch.return_value = {
            "cve_id": "CVE-2021-44228",
            "cvss_base_score": 10.0,
            "cvss_severity": "CRITICAL",
            "enrichment_status": "success",
        }

        log_entry = {"message": "Exploit CVE-2021-44228 detected"}
        enriched = enrich_log_with_cves(log_entry)

        assert enriched["cve_detected"] is True
        assert "CVE-2021-44228" in enriched["cve_ids"]
        assert enriched["max_cvss_score"] == 10.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

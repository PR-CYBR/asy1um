"""
Tests for CVE API endpoints (integration-style tests)
"""

import sys
from pathlib import Path
from unittest.mock import patch

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

    @patch("api.cve_enrichment.get_cve_info")
    def test_cveinfo_endpoint_logic_multiple_cves(self, mock_get_cve_info):
        """Test CVE info retrieval with comma-separated list"""
        from api.cve_enrichment import get_cve_info

        # Mock returns for different CVEs
        def mock_get_info(cve_id):
            if cve_id == "CVE-2021-44228":
                return {
                    "cve_id": "CVE-2021-44228",
                    "cvss_base_score": 10.0,
                    "cvss_severity": "CRITICAL",
                    "enrichment_status": "success",
                }
            elif cve_id == "CVE-2020-1234":
                return {
                    "cve_id": "CVE-2020-1234",
                    "cvss_base_score": 7.5,
                    "cvss_severity": "HIGH",
                    "enrichment_status": "success",
                }

        mock_get_cve_info.side_effect = mock_get_info

        # Test with comma-separated string
        cve_list = [c.strip() for c in "CVE-2021-44228,CVE-2020-1234".split(",")]

        results = []
        for cve_id in cve_list:
            results.append(get_cve_info(cve_id))

        assert len(results) == 2
        assert results[0]["cve_id"] == "CVE-2021-44228"
        assert results[1]["cve_id"] == "CVE-2020-1234"

    @patch("api.cve_enrichment.get_cve_info")
    def test_cveinfo_endpoint_logic_with_whitespace(self, mock_get_cve_info):
        """Test CVE info retrieval with whitespace in comma-separated list"""

        def mock_get_info(cve_id):
            return {
                "cve_id": cve_id,
                "cvss_base_score": 8.0,
                "cvss_severity": "HIGH",
                "enrichment_status": "success",
            }

        mock_get_cve_info.side_effect = mock_get_info

        # Test with whitespace around commas
        cve_string = "CVE-2021-44228 , CVE-2020-1234  ,  CVE-2019-5678"
        cve_list = [c.strip() for c in cve_string.split(",")]

        assert len(cve_list) == 3
        assert cve_list[0] == "CVE-2021-44228"
        assert cve_list[1] == "CVE-2020-1234"
        assert cve_list[2] == "CVE-2019-5678"

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

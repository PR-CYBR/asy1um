"""
CVE and CVSS enrichment module for asy1um honeypot system.
Integrates with NIST NVD API to fetch CVE details and CVSS scores.
"""

import re
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import requests
from functools import lru_cache

# CVE pattern regex as specified in requirements
CVE_PATTERN = re.compile(r'\bCVE-\d{4}-\d+\b')

# NVD API configuration
NVD_API_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NVD_REQUEST_TIMEOUT = 10  # seconds
NVD_RATE_LIMIT_DELAY = 0.6  # seconds between requests (public API limit)

# Cache configuration
CACHE_FILE = Path(__file__).parent.parent / "data" / "cve_cache.json"
CACHE_EXPIRY_DAYS = 7


class CVECache:
    """Lightweight caching system for CVE data."""

    def __init__(self, cache_file: Path = CACHE_FILE):
        self.cache_file = cache_file
        self.cache_file.parent.mkdir(exist_ok=True, parents=True)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._last_request_time = 0
        self._load_cache()

    def _load_cache(self):
        """Load cache from disk."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    self._cache = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._cache = {}

    def _save_cache(self):
        """Save cache to disk."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self._cache, f, indent=2)
        except IOError:
            pass  # Fail silently, cache is not critical

    def get(self, cve_id: str) -> Optional[Dict[str, Any]]:
        """Get CVE data from cache if available and not expired."""
        if cve_id not in self._cache:
            return None

        entry = self._cache[cve_id]
        cached_time = datetime.fromisoformat(entry.get("cached_at", "2000-01-01"))
        expiry_time = cached_time + timedelta(days=CACHE_EXPIRY_DAYS)

        if datetime.now() > expiry_time:
            # Cache expired
            del self._cache[cve_id]
            self._save_cache()
            return None

        return entry.get("data")

    def set(self, cve_id: str, data: Dict[str, Any]):
        """Store CVE data in cache."""
        self._cache[cve_id] = {"cached_at": datetime.now().isoformat(), "data": data}
        self._save_cache()

    def rate_limit_wait(self):
        """Enforce rate limiting for NVD API requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < NVD_RATE_LIMIT_DELAY:
            time.sleep(NVD_RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = time.time()


# Global cache instance
_cache = CVECache()


def extract_cves(text: str) -> List[str]:
    """
    Extract CVE identifiers from text using regex pattern.

    Args:
        text: Input text to search for CVE identifiers

    Returns:
        List of unique CVE identifiers found
    """
    if not text:
        return []

    matches = CVE_PATTERN.findall(text)
    return list(set(matches))  # Return unique CVEs


def fetch_cve_from_nvd(cve_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch CVE details from NVD API.

    Args:
        cve_id: CVE identifier (e.g., "CVE-2021-44228")

    Returns:
        CVE data dictionary or None if fetch fails
    """
    # Check cache first
    cached_data = _cache.get(cve_id)
    if cached_data:
        return cached_data

    # Apply rate limiting
    _cache.rate_limit_wait()

    try:
        url = f"{NVD_API_BASE_URL}?cveId={cve_id}"
        response = requests.get(url, timeout=NVD_REQUEST_TIMEOUT)

        if response.status_code != 200:
            return None

        data = response.json()
        vulnerabilities = data.get("vulnerabilities", [])

        if not vulnerabilities:
            return None

        # Extract the first vulnerability (should only be one for exact CVE ID match)
        vuln_data = vulnerabilities[0]
        cve_data = vuln_data.get("cve", {})

        # Extract CVSS scores (prefer v3.1, fallback to v3.0, then v2.0)
        metrics = cve_data.get("metrics", {})
        cvss_data = {}

        if "cvssMetricV31" in metrics:
            cvss_v31 = metrics["cvssMetricV31"][0]["cvssData"]
            cvss_data = {
                "version": "3.1",
                "base_score": cvss_v31.get("baseScore", 0.0),
                "severity": cvss_v31.get("baseSeverity", "NONE"),
                "vector_string": cvss_v31.get("vectorString", ""),
                "attack_vector": cvss_v31.get("attackVector", ""),
                "attack_complexity": cvss_v31.get("attackComplexity", ""),
                "privileges_required": cvss_v31.get("privilegesRequired", ""),
                "user_interaction": cvss_v31.get("userInteraction", ""),
                "scope": cvss_v31.get("scope", ""),
                "confidentiality_impact": cvss_v31.get("confidentialityImpact", ""),
                "integrity_impact": cvss_v31.get("integrityImpact", ""),
                "availability_impact": cvss_v31.get("availabilityImpact", ""),
                "exploitability_score": metrics["cvssMetricV31"][0].get("exploitabilityScore", 0.0),
                "impact_score": metrics["cvssMetricV31"][0].get("impactScore", 0.0),
            }
        elif "cvssMetricV30" in metrics:
            cvss_v30 = metrics["cvssMetricV30"][0]["cvssData"]
            cvss_data = {
                "version": "3.0",
                "base_score": cvss_v30.get("baseScore", 0.0),
                "severity": cvss_v30.get("baseSeverity", "NONE"),
                "vector_string": cvss_v30.get("vectorString", ""),
                "exploitability_score": metrics["cvssMetricV30"][0].get("exploitabilityScore", 0.0),
                "impact_score": metrics["cvssMetricV30"][0].get("impactScore", 0.0),
            }
        elif "cvssMetricV2" in metrics:
            cvss_v2 = metrics["cvssMetricV2"][0]["cvssData"]
            cvss_data = {
                "version": "2.0",
                "base_score": cvss_v2.get("baseScore", 0.0),
                "severity": _cvss_v2_to_severity(cvss_v2.get("baseScore", 0.0)),
                "vector_string": cvss_v2.get("vectorString", ""),
                "exploitability_score": metrics["cvssMetricV2"][0].get("exploitabilityScore", 0.0),
                "impact_score": metrics["cvssMetricV2"][0].get("impactScore", 0.0),
            }

        # Extract description
        descriptions = cve_data.get("descriptions", [])
        description = ""
        for desc in descriptions:
            if desc.get("lang") == "en":
                description = desc.get("value", "")
                break

        enriched_data = {
            "cve_id": cve_id,
            "cvss_base_score": cvss_data.get("base_score", 0.0),
            "cvss_severity": cvss_data.get("severity", "NONE"),
            "cvss_version": cvss_data.get("version", ""),
            "cvss_vector": cvss_data.get("vector_string", ""),
            "cve_description": description[:500] if description else "",  # Limit description length
            "published_date": cve_data.get("published", ""),
            "last_modified": cve_data.get("lastModified", ""),
            "cvss_details": cvss_data,
            "enrichment_timestamp": datetime.now().isoformat(),
            "enrichment_status": "success",
        }

        # Cache the result
        _cache.set(cve_id, enriched_data)

        return enriched_data

    except requests.exceptions.Timeout:
        return {"cve_id": cve_id, "enrichment_status": "timeout", "error": "NVD API request timeout"}
    except requests.exceptions.RequestException as e:
        return {"cve_id": cve_id, "enrichment_status": "failed", "error": str(e)}
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        return {"cve_id": cve_id, "enrichment_status": "parse_error", "error": str(e)}


def _cvss_v2_to_severity(score: float) -> str:
    """Convert CVSS v2.0 score to severity rating."""
    if score >= 9.0:
        return "CRITICAL"
    elif score >= 7.0:
        return "HIGH"
    elif score >= 4.0:
        return "MEDIUM"
    elif score > 0.0:
        return "LOW"
    else:
        return "NONE"


def enrich_log_with_cves(log_entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enrich a log entry with CVE data by detecting CVE IDs in the log message.

    Args:
        log_entry: Log entry dictionary (from honeypot/monitoring)

    Returns:
        Enriched log entry with CVE data
    """
    # Extract text from common log fields
    text_fields = ["message", "input", "command", "data", "payload"]
    combined_text = ""

    for field in text_fields:
        if field in log_entry and log_entry[field]:
            combined_text += " " + str(log_entry[field])

    # Find CVE IDs
    cve_ids = extract_cves(combined_text)

    if not cve_ids:
        return log_entry

    # Fetch enrichment data for each CVE
    cve_enrichments = []
    for cve_id in cve_ids:
        enrichment = fetch_cve_from_nvd(cve_id)
        if enrichment:
            cve_enrichments.append(enrichment)

    # Add enrichment to log entry
    if cve_enrichments:
        log_entry["cve_detected"] = True
        log_entry["cve_ids"] = cve_ids
        log_entry["cve_enrichments"] = cve_enrichments

        # Add highest CVSS score for easy filtering
        scores = [e.get("cvss_base_score", 0.0) for e in cve_enrichments if e.get("cvss_base_score")]
        if scores:
            log_entry["max_cvss_score"] = max(scores)

            # Determine overall severity
            max_score = log_entry["max_cvss_score"]
            if max_score >= 9.0:
                log_entry["cve_severity"] = "CRITICAL"
            elif max_score >= 7.0:
                log_entry["cve_severity"] = "HIGH"
            elif max_score >= 4.0:
                log_entry["cve_severity"] = "MEDIUM"
            elif max_score > 0.0:
                log_entry["cve_severity"] = "LOW"
            else:
                log_entry["cve_severity"] = "NONE"

    return log_entry


def get_cve_info(cve_id: str) -> Dict[str, Any]:
    """
    Public API function to get CVE information.
    Used by the /cveinfo endpoint.

    Args:
        cve_id: CVE identifier

    Returns:
        CVE information dictionary
    """
    if not CVE_PATTERN.match(cve_id):
        return {"error": "Invalid CVE ID format", "status": "invalid"}

    result = fetch_cve_from_nvd(cve_id)

    if result is None:
        return {"error": "CVE not found", "status": "not_found", "cve_id": cve_id}

    return result

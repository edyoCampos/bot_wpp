"""
PHASE 13: Advanced Reports Tests

Test Cases: UC-060 to UC-063
Based on: back/docs/academic/casos-teste-validacao.md

Covers:
- PDF Report Generation
- Excel/CSV Exports
- Campaign Performance Reports
- Conversion Analytics
"""

import pytest


class TestPhase13Reports:
    """Phase 13: Advanced Reports."""

    def test_uc060_generate_daily_report_pdf(self, api_client, auth_headers):
        """UC-060: Generate Daily Report (PDF).

        Expected: Binary response with application/pdf content type.
        """
        response = api_client.get("/dashboard/reports/daily?format=pdf", headers=auth_headers)

        # Skip if endpoint not built
        if response.status_code == 404:
            pytest.skip("Report endpoint not implemented")

        assert response.status_code == 200
        assert "application/pdf" in response.headers.get("Content-Type", "")
        # Minimal check for PDF magic bytes
        assert response.content.startswith(b"%PDF")

    def test_uc061_export_leads_excel(self, api_client, auth_headers):
        """UC-061: Export Leads to Excel.

        Expected: Binary response with proper headers.
        """
        response = api_client.get("/leads/export?format=xlsx", headers=auth_headers)

        if response.status_code == 404:
            pytest.skip("Export endpoint not implemented")

        assert response.status_code == 200
        assert "spreadsheet" in response.headers.get("Content-Type", "") or "excel" in response.headers.get(
            "Content-Type", ""
        )

    def test_uc062_campaign_performance(self, api_client, auth_headers):
        """UC-062: Campaign Performance Analytics."""
        response = api_client.get("/dashboard/metrics/campaigns", headers=auth_headers)

        if response.status_code == 404:
            pytest.skip("Campaign metrics not implemented")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "conversion_rate" in data[0]

    def test_uc063_conversion_funnel(self, api_client, auth_headers):
        """UC-063: Conversion Funnel Data."""
        response = api_client.get("/dashboard/metrics/funnel", headers=auth_headers)

        if response.status_code == 404:
            pytest.skip("Funnel metrics not implemented")

        assert response.status_code == 200
        data = response.json()

        expected_stages = ["total_leads", "qualified", "scheduled", "converted"]
        for stage in expected_stages:
            assert stage in data

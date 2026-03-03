"""
PHASE 9: Metrics and Analytics Tests

Test Cases: UC-036 to UC-038
"""


class TestPhase9Metrics:
    """Phase 9: Metrics and Analytics."""

    def test_uc036_get_general_metrics(self, api_client):
        """UC-036: Get General Metrics (Admin)."""
        response = api_client.get("/metrics/overview")

        assert response.status_code == 200
        data = response.json()

        assert "total_conversations" in data
        assert "conversion_rate" in data
        assert data["period"] == "all_time"

    def test_uc037_get_metrics_by_period(self, api_client):
        """UC-037: Get Metrics by Period."""
        from datetime import date

        today = str(date.today())

        response = api_client.get("/metrics/overview", params={"start_date": today, "end_date": today})

        assert response.status_code == 200
        data = response.json()
        assert today in data["period"]

    def test_uc038_get_campaign_metrics(self, api_client):
        """UC-038: Get Metrics by Campaign."""
        response = api_client.get("/metrics/campaigns")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)

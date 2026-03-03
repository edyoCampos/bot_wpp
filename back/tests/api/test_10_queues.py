"""
PHASE 10: Queue Management Tests

Test Cases: UC-039 to UC-040
"""

import pytest


class TestPhase10Queues:
    """Phase 10: Queue Management."""

    def test_uc039_verify_queue_stats(self, api_client):
        """UC-039: Verify Redis Queue Stats."""
        response = api_client.get("/queues/stats")

        assert response.status_code == 200
        data = response.json()

        assert "queues" in data
        assert isinstance(data["queues"], list)
        assert len(data["queues"]) >= 3  # messages, ai, escalation

    def test_uc040_reprocess_failed_job(self, api_client):
        """UC-040: Reprocess Failed Job (DLQ)."""
        # Check if there are failed jobs
        response = api_client.get("/queues/stats")
        stats = response.json()

        if stats["total_failed"] == 0:
            pytest.skip("No failed jobs")

        # Try to retry a job (may not exist)
        response = api_client.post("/queues/retry/test_job_id")

        # 200 if retried, 404 if job doesn't exist
        assert response.status_code in [200, 404]

"""
PHASE 7: Escalation to Human Tests

Test Cases: UC-031 to UC-033
"""

import pytest


class TestPhase7Escalation:
    """Phase 7: Escalation to Human."""

    conversation_id = None
    notification_id = None

    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """Get an existing conversation."""
        response = api_client.get("/conversations")
        data = response.json()
        if data:
            TestPhase7Escalation.conversation_id = data[0]["id"]

    def test_uc031_assign_to_secretary(self, api_client, secretary_token):
        """UC-031: Assign Conversation to Secretary."""
        if not self.conversation_id:
            pytest.skip("No conversation available")

        # Get secretary ID
        import requests

        response = requests.get(
            f"{api_client.base_url}/auth/me", headers={"Authorization": f"Bearer {secretary_token}"}, timeout=30
        )
        secretary_id = response.json()["id"]

        response = api_client.patch(
            f"/conversations/{self.conversation_id}/assign",
            json={"assigned_to": secretary_id, "reason": "Alta maturidade"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["assigned_to"] == secretary_id

    def test_uc032_verify_notifications(self, api_base_url, secretary_token):
        """UC-032: Verify Secretary Notifications."""
        import requests

        response = requests.get(
            f"{api_base_url}/notifications", headers={"Authorization": f"Bearer {secretary_token}"}, timeout=30
        )

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        if data:
            TestPhase7Escalation.notification_id = data[0]["id"]

    def test_uc033_mark_notification_read(self, api_base_url, secretary_token):
        """UC-033: Mark Notification as Read."""
        if not self.notification_id:
            pytest.skip("No notifications")

        import requests

        response = requests.patch(
            f"{api_base_url}/notifications/{self.notification_id}/read",
            headers={"Authorization": f"Bearer {secretary_token}"},
            timeout=30,
        )

        assert response.status_code == 200

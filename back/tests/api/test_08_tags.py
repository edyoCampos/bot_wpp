"""
PHASE 8: Tags and Filters Tests

Test Cases: UC-034 to UC-035
"""

import pytest


class TestPhase8Tags:
    """Phase 8: Tags and Filters."""

    conversation_id = None

    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """Get an existing conversation."""
        response = api_client.get("/conversations")
        data = response.json()
        if data:
            TestPhase8Tags.conversation_id = data[0]["id"]

    def test_uc034_add_tags(self, api_client):
        """UC-034: Add Tags to Conversation."""
        if not self.conversation_id:
            pytest.skip("No conversation available")

        response = api_client.post(
            f"/conversations/{self.conversation_id}/tags", json={"tags": ["agendamento", "emagrecimento", "urgente"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["tags"]) >= 3

    def test_uc035_filter_by_tag(self, api_client):
        """UC-035: Filter Conversations by Tag."""
        response = api_client.get("/conversations", params={"tags": "urgente"})

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)

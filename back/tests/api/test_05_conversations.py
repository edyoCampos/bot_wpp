"""
PHASE 5: Conversations and Leads Tests
Test Cases: UC-021 to UC-025
"""

import time

import requests


class TestPhase5Conversations:
    """Phase 5: Conversations and Leads tests."""

    test_phone = "5551999887766"

    # Class attributes to persist data between test methods
    conversation_id = None
    lead_id = None

    def test_uc021_simulate_webhook_inbound(self, api_base_url):
        """UC-021: Simulate WAHA Webhook (Inbound Message)."""
        response = requests.post(
            f"{api_base_url}/webhooks/waha",
            headers={"X-WAHA-Event": "message"},
            json={
                "event": "message",
                "session": "test",
                "payload": {
                    "id": f"msg_{int(time.time())}",
                    "timestamp": int(time.time()),
                    "from": f"{self.test_phone}@c.us",
                    "body": "I would like information about weight loss",
                    "hasMedia": False,
                },
            },
            timeout=10,
        )

        assert response.status_code == 202
        # Give the worker a small head start
        time.sleep(2)

    def test_uc022_verify_conversation_created(self, api_client):
        """UC-022: Verify Conversation Created with Polling."""
        max_retries = 20
        data = {}
        found = False

        # Polling loop to wait for asynchronous AI processing and DB insertion
        for _i in range(max_retries):
            response = api_client.get("/conversations", params={"phone_number": self.test_phone})
            assert response.status_code == 200
            data = response.json()

            if "conversations" in data and len(data["conversations"]) > 0:
                found = True
                break

            time.sleep(3)

        assert found is True, f"Conversation not found for phone {self.test_phone} after timeout."

        conv = data["conversations"][0]
        assert conv["phone_number"] == self.test_phone
        assert conv["status"] == "active"

        # Store IDs in class attributes for subsequent tests
        TestPhase5Conversations.conversation_id = conv["id"]
        TestPhase5Conversations.lead_id = conv["lead_id"]

    def test_uc023_get_conversation_messages(self, api_client):
        """UC-023: Get Conversation Messages."""
        cid = TestPhase5Conversations.conversation_id
        assert cid is not None, "conversation_id was not captured in UC-022"

        response = api_client.get(f"/conversations/{cid}/messages")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        # Should contain at least the inbound message simulated in UC-021
        assert len(data) >= 1

    def test_uc024_get_lead_data(self, api_client):
        """UC-024: Get Lead Data."""
        response = api_client.get("/leads", params={"phone_number": self.test_phone})

        # If this returns 500, check API logs for SQLAlchemy or Pydantic errors
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, dict)
        assert "leads" in data
        assert len(data["leads"]) > 0

        lead = data["leads"][0]
        assert lead["id"] == TestPhase5Conversations.lead_id
        assert lead["phone_number"] == self.test_phone

    def test_uc025_verify_lead_interactions(self, api_client):
        """UC-025: Verify Lead Interactions."""
        lid = TestPhase5Conversations.lead_id
        assert lid is not None, "lead_id was not captured in UC-022"

        response = api_client.get(f"/leads/{lid}/interactions")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) > 0

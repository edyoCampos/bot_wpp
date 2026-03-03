"""
PHASE 6: Gemini AI and Context Tests

Test Cases: UC-026 to UC-030
"""

import time

import pytest


class TestPhase6Gemini:
    """Phase 6: Gemini AI and Context."""

    test_phone = "5551999887799"
    conversation_id = None

    @pytest.fixture(autouse=True)
    def setup(self, api_base_url, api_client):
        """Setup: create initial conversation."""
        import requests

        requests.post(
            f"{api_base_url}/webhooks/waha",
            headers={"X-WAHA-Event": "message"},
            json={
                "event": "message",
                "session": "test",
                "payload": {
                    "id": f"msg_{int(time.time())}",
                    "timestamp": int(time.time()),
                    "from": f"{self.test_phone}@c.us",
                    "body": "Quero emagrecer",
                    "hasMedia": False,
                },
            },
        )
        time.sleep(8)

        response = api_client.get("/conversations", params={"phone_number": self.test_phone})
        data = response.json()
        if data and "conversations" in data and data["conversations"]:
            TestPhase6Gemini.conversation_id = data["conversations"][0]["id"]

    def test_uc026_problem_phase(self, api_base_url):
        """UC-026: Simulate Continued Conversation (PROBLEM phase)."""
        import requests

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
                    "body": "Já tentei várias dietas mas não funciona",
                    "hasMedia": False,
                },
            },
        )

        assert response.status_code == 202
        time.sleep(10)

    def test_uc027_implication_phase(self, api_base_url):
        """UC-027: Simulate Advanced Conversation (IMPLICATION phase)."""
        import requests

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
                    "body": "Isso afeta minha autoestima",
                    "hasMedia": False,
                },
            },
        )

        assert response.status_code == 202
        time.sleep(10)

    def test_uc028_scheduling_intent(self, api_base_url):
        """UC-028: Detect Scheduling Intent (NEED-PAYOFF)."""
        import requests

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
                    "body": "Como faço para agendar?",
                    "hasMedia": False,
                },
            },
        )

        assert response.status_code == 202
        time.sleep(10)

    def test_uc029_location_question(self, api_base_url):
        """UC-029: Simulate Location Question (Gemini Tool)."""
        import requests

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
                    "body": "Onde fica a clínica?",
                    "hasMedia": False,
                },
            },
        )

        assert response.status_code == 202
        time.sleep(10)

    def test_uc030_verify_llm_logs(self, api_client):
        """UC-030: Verify LLM Interaction Logs."""
        if not self.conversation_id:
            pytest.skip("No conversation ID")

        response = api_client.get("/llm-interactions", params={"conversation_id": self.conversation_id})

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)

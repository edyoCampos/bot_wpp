"""
PHASE 2: WAHA Integration Tests

Test Cases: UC-006 to UC-009

Note: WAHA CORE edition only supports 'default' session name.
Multiple session support requires WAHA PLUS.
"""


class TestPhase2WAHA:
    """Phase 2: WAHA Integration (WhatsApp)."""

    # WAHA CORE only allows 'default' session name
    session_name = "default"

    def test_uc006_create_whatsapp_session(self, api_client):
        """UC-006: Create WhatsApp Session.

        Note: WAHA CORE may have already created 'default' session.
        If session exists, test passes (idempotent).
        """
        response = api_client.post(
            "/waha/sessions",
            json={
                "name": self.session_name,
                "config": {
                    "webhooks": [
                        {"url": "http://api:3333/api/v1/webhooks/waha", "events": ["message", "session.status"]}
                    ]
                },
            },
        )

        # Session may already exist (WAHA CORE creates 'default' at startup)
        # or may be in DB from previous test run
        # Accept: 201 (created), 409/422 (WAHA conflict), 400 (DB conflict)
        assert response.status_code in [201, 400, 409, 422], f"Got {response.status_code}: {response.text}"

        # If session was created (201), validate response
        if response.status_code == 201:
            data = response.json()
            assert data["name"] == self.session_name
            assert data["status"] == "STOPPED"

    def test_uc007_start_session_get_qr(self, api_client):
        """UC-007: Start Session (Get QR Code).

        Note: Session may already be started from previous test run.
        If already started, test passes (idempotent).
        """
        response = api_client.post(f"/waha/sessions/{self.session_name}/start")

        # Session may already be started; accept both success and conflict
        # Accept: 200 (started), 409 (conflict/already started)
        assert response.status_code in [200, 409], f"Got {response.status_code}: {response.text}"

        # If successfully started (200), validate response
        if response.status_code == 200:
            data = response.json()
            assert data["name"] == self.session_name
            assert data["status"] in ["SCAN_QR_CODE", "STARTING", "WORKING"]

    def test_uc008_verify_session_status(self, api_client):
        """UC-008: Verify Session Status."""
        response = api_client.get(f"/waha/sessions/{self.session_name}")

        assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
        data = response.json()

        assert data["name"] == self.session_name
        assert data["status"] in ["SCAN_QR_CODE", "WORKING", "STOPPED", "STARTING"]

    def test_uc009_list_all_sessions(self, api_client):
        """UC-009: List All Sessions."""
        response = api_client.get("/waha/sessions")

        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) > 0

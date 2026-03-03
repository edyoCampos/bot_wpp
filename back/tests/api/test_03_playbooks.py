"""
PHASE 3: Playbooks Tests

Test Cases: UC-010 to UC-015

Architecture:
- Messages: Reusable content items (text, media, location)
- Topics: Categories for playbooks
- Playbooks: Sequences of messages for specific topics
- Playbook Steps: Link messages to playbooks in order
"""

import time


class TestPhase3Playbooks:
    """Phase 3: Playbooks (Pre-Approved Messages)."""

    def test_uc010_create_topic(self, api_client):
        """UC-010: Create Topic 'Emagrecimento'."""
        topic_name = f"Emagrecimento_{int(time.time())}"
        response = api_client.post(
            "/topics", json={"name": topic_name, "description": "Tratamentos para emagrecimento saudável"}
        )

        assert response.status_code == 201, f"Got {response.status_code}: {response.text}"
        data = response.json()

        assert data["name"] == topic_name
        # Store for next tests
        self.topic_id = data["id"]

    def test_uc011_create_playbook(self, api_client):
        """UC-011: Create Playbook 'Consulta Inicial'."""
        # Get existing topic or create one
        topics_response = api_client.get("/topics")
        if topics_response.status_code == 200:
            topics_payload = topics_response.json()
            if isinstance(topics_payload, dict):
                topics = topics_payload.get("topics", [])
            else:
                topics = topics_payload
            if topics:
                topic_id = topics[0]["id"]  # Use first available topic
            else:
                # Create topic if none exist
                self.test_uc010_create_topic(api_client)
                topic_id = self.topic_id
        else:
            # Fallback to creating topic
            self.test_uc010_create_topic(api_client)
            topic_id = self.topic_id

        playbook_name = f"Consulta_Inicial_{int(time.time())}"
        response = api_client.post(
            "/playbooks",
            json={
                "name": playbook_name,
                "description": "Fluxo de agendamento",
                "topic_id": topic_id,
                "active": True,
            },
        )

        assert response.status_code == 201, f"Got {response.status_code}: {response.text}"
        data = response.json()

        assert playbook_name in data["name"]
        assert data["topic_id"] == topic_id

        # Store for next tests
        self.playbook_id = data["id"]

    def test_uc012_add_text_message(self, api_client):
        """UC-012: Create text message and add to playbook.

        Architecture: First create reusable message, then link to playbook via step.
        """
        # Ensure we have a playbook
        if not hasattr(self, "playbook_id"):
            self.test_uc011_create_playbook(api_client)

        # Step 1: Create reusable text message
        response = api_client.post(
            "/messages",
            json={
                "type": "text",
                "title": "Greeting Message",
                "description": "Initial greeting for consultation",
                "text": "Olá! Posso ajudar com agendamento?",
            },
        )

        assert response.status_code == 201, f"Message creation failed {response.status_code}: {response.text}"
        message_data = response.json()
        text_message_id = message_data["id"]
        print(f"Created message: {text_message_id}")

        # Step 2: Add message to playbook as a step
        payload = {
            "playbook_id": self.playbook_id,
            "message_id": str(text_message_id),  # Ensure it's a string
            "step_order": 1,
            "context_hint": "Use this when patient asks about consultation",
        }
        print(f"Playbook step payload: {payload}")

        response = api_client.post("/playbook-steps", json=payload)

        assert response.status_code == 201, f"Step creation failed {response.status_code}: {response.text}"
        step_data = response.json()

        assert step_data["playbook_id"] == self.playbook_id
        assert step_data["message_id"] == str(text_message_id)
        assert step_data["step_order"] == 1

    def test_uc013_add_image_message(self, api_client):
        """UC-013: Create image message and add to playbook."""
        # Ensure we have a playbook and at least one message
        if not hasattr(self, "playbook_id"):
            self.test_uc012_add_text_message(api_client)

        # Step 1: Create image message
        response = api_client.post(
            "/messages",
            json={
                "type": "image",
                "title": "Consultation Info",
                "description": "Image explaining consultation process",
                "file": {
                    "url": "https://example.com/consultation.jpg",
                    "mimetype": "image/jpeg",
                    "filename": "consultation.jpg",
                },
                "caption": "Nossa consulta inclui avaliação completa...",
                "tags": "consultation,info",  # Comma-separated string
            },
        )

        assert response.status_code == 201, f"Got {response.status_code}: {response.text}"
        message_data = response.json()
        image_message_id = message_data["id"]

        # Step 2: Add to playbook
        response = api_client.post(
            "/playbook-steps",
            json={
                "playbook_id": self.playbook_id,
                "message_id": image_message_id,
                "step_order": 2,
                "context_hint": "Show this image when explaining consultation details",
            },
        )

        assert response.status_code == 201, f"Got {response.status_code}: {response.text}"
        step_data = response.json()

        assert step_data["playbook_id"] == self.playbook_id
        assert step_data["step_order"] == 2

    def test_uc014_search_playbooks(self, api_client):
        """UC-014: Search Playbooks by Semantic Query."""
        # Ensure we have at least one playbook
        if not hasattr(self, "playbook_id"):
            self.test_uc011_create_playbook(api_client)

        response = api_client.get("/playbooks/search", params={"query": "consulta agendamento", "top_k": 5})

        assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
        data = response.json()

        assert "results" in data
        assert isinstance(data["results"], list)

    def test_uc015_get_playbook_steps(self, api_client):
        """UC-015: Get Playbook Steps."""
        # Ensure we have playbook with steps
        if not hasattr(self, "playbook_id"):
            self.test_uc013_add_image_message(api_client)

        response = api_client.get(f"/playbook-steps/playbook/{self.playbook_id}")

        assert response.status_code == 200, f"Got {response.status_code}: {response.text}"
        data = response.json()

        assert "steps" in data
        assert isinstance(data["steps"], list)
        assert len(data["steps"]) >= 1  # At least the messages we added

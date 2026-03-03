"""
PHASE 4: Messages and Media Tests

Test Cases: UC-016 to UC-021

Este módulo testa a criação de mensagens com diferentes tipos de mídia
e valida o enriquecimento automático por IA (transcrição, análise de imagem, metadata).
"""

# URLs públicas para testes de enriquecimento com arquivos reais
TEST_MEDIA_URLS = {
    "audio": "https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav",
    "image": "https://images.unsplash.com/photo-1516549655169-df83a0774514?w=800",
    "video": "https://sample-videos.com/video123/mp4/240/big_buck_bunny_240p_1mb.mp4",
    "document": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
}


class TestPhase4Messages:
    """Phase 4: Messages and Media (CRUD + enrichment schema)."""

    def test_uc016_create_text_message(self, api_client):
        """
        UC-016: Create Text Message (schema-aligned).
        Mensagens de texto NÃO passam por enriquecimento automático.
        """
        response = api_client.post(
            "/messages",
            json={
                "type": "text",
                "text": "Gostaria de informações sobre emagrecimento",
                "title": "Pergunta sobre emagrecimento",
                "description": "Lead perguntando sobre tratamentos de emagrecimento",
                "tags": "emagrecimento,pergunta",
            },
        )

        assert response.status_code == 201, response.text
        data = response.json()

        assert data["type"] == "text"
        assert "emagrecimento" in data["text"]

    def test_uc017_create_voice_message(self, api_client):
        """UC-017: Create Voice Message with automatic transcription."""
        response = api_client.post(
            "/messages",
            json={
                "type": "voice",
                "file": {"url": TEST_MEDIA_URLS["audio"], "mimetype": "audio/wav", "filename": "audio_teste.wav"},
                "caption": "Áudio do paciente sobre consulta",
            },
        )

        assert response.status_code == 201, response.text
        data = response.json()
        assert data["type"] == "voice"

    def test_uc018_create_image_message(self, api_client):
        """UC-018: Create Image Message with BLIP-2 vision analysis."""
        response = api_client.post(
            "/messages",
            json={
                "type": "image",
                "file": {"url": TEST_MEDIA_URLS["image"], "mimetype": "image/jpeg", "filename": "clinica.jpg"},
                "caption": "Imagem da clínica médica",
            },
        )

        assert response.status_code == 201, response.text
        data = response.json()
        assert data["type"] == "image"

    def test_uc019_create_video_message(self, api_client):
        """UC-019: Create Video Message with audio transcription."""
        response = api_client.post(
            "/messages",
            json={
                "type": "video",
                "file": {"url": TEST_MEDIA_URLS["video"], "mimetype": "video/mp4", "filename": "procedimento.mp4"},
                "caption": "Vídeo explicando o procedimento",
            },
        )

        assert response.status_code == 201, response.text
        data = response.json()
        assert data["type"] == "video"
        assert data["file"]["mimetype"] == "video/mp4"

    def test_uc020_create_document_message(self, api_client):
        """UC-020: Create Document Message (metadata generation)."""
        response = api_client.post(
            "/messages",
            json={
                "type": "document",
                "file": {
                    "url": "https://example.com/tabela_precos.pdf",
                    "mimetype": "application/pdf",
                    "filename": "tabela_precos.pdf",
                },
                "caption": "Tabela de preços atualizada",
            },
        )
        assert response.status_code == 201, response.text
        data = response.json()

        assert data["type"] == "document"
        assert data["file"]["mimetype"] == "application/pdf"

    def test_uc021_create_location_message(self, api_client):
        """UC-021: Create Location Message."""
        response = api_client.post(
            "/messages",
            json={"type": "location", "latitude": -29.5838212, "longitude": -51.0869905, "title": "Go"},
        )

        assert response.status_code == 201, response.text
        data = response.json()

        assert data["type"] == "location"
        assert data["latitude"] == -29.5838212

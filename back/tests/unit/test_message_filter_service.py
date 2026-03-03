"""
Testes unitários para MessageFilterService.
Verifica todos os cenários de rejeição/aceitação de mensagens.
"""
import pytest
from unittest.mock import MagicMock, patch


class TestMessageFilterService:
    """Test suite for MessageFilterService.should_process()."""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client."""
        with patch("robbot.services.communication.message_filter_service.get_redis_client") as mock_get:
            mock_client = MagicMock()
            mock_get.return_value = mock_client
            # Default: no messages are processed yet
            mock_client.get.return_value = None
            yield mock_client

    @pytest.fixture
    def filter_service(self, mock_redis):
        """Create MessageFilterService with mocked Redis."""
        with patch("robbot.services.communication.message_filter_service.settings") as mock_settings:
            mock_settings.DEV_MODE = False
            from robbot.services.communication.message_filter_service import MessageFilterService
            service = MessageFilterService()
            service._mock_settings = mock_settings
            yield service

    # =========================================================================
    # BUG 1: fromMe default value
    # =========================================================================
    def test_fromMe_true_should_reject(self, filter_service):
        """Mensagem com fromMe=True DEVE ser rejeitada."""
        msg = {"id": "msg_001", "from": "5511999@c.us", "fromMe": True}
        assert filter_service.should_process(msg) is False

    def test_fromMe_false_should_accept(self, filter_service):
        """Mensagem com fromMe=False DEVE ser aceita."""
        msg = {"id": "msg_002", "from": "5511999@c.us", "fromMe": False}
        assert filter_service.should_process(msg) is True

    def test_fromMe_absent_should_accept(self, filter_service):
        """
        CRITICAL: Mensagem SEM campo fromMe DEVE ser aceita (default False).
        Este é o Bug 1 — o default anterior era True, rejeitando silenciosamente.
        """
        msg = {"id": "msg_003", "from": "5511999@c.us"}
        # fromMe não existe no dict!
        assert "fromMe" not in msg
        assert filter_service.should_process(msg) is True

    # =========================================================================
    # BUG 2: allowed_senders format matching
    # =========================================================================
    def test_dev_mode_raw_phone_matches_cus_sender(self, filter_service):
        """
        DEV Mode: allowed_senders com raw phone '555191628223' DEVE dar match
        contra sender '555191628223@c.us' via sender_base.
        """
        filter_service._mock_settings.DEV_MODE = True
        msg = {
            "id": "msg_004",
            "from": "555191628223@c.us",
            "fromMe": False,
        }
        allowed = {"555191628223"}
        assert filter_service.should_process(msg, allowed_senders=allowed) is True

    def test_dev_mode_lid_in_allowed_should_NOT_match_cus_sender(self, filter_service):
        """
        DEV Mode: allowed_senders com LID '189485451100193@lid' NÃO deve dar match
        contra sender '555191628223@c.us'. Isso era o Bug 2.
        """
        filter_service._mock_settings.DEV_MODE = True
        msg = {
            "id": "msg_005",
            "from": "555191628223@c.us",
            "fromMe": False,
        }
        allowed = {"189485451100193@lid"}  # LID — formato errado para allowlist!
        assert filter_service.should_process(msg, allowed_senders=allowed) is False

    def test_dev_mode_exact_match_sender(self, filter_service):
        """DEV Mode: exact match sender funciona."""
        filter_service._mock_settings.DEV_MODE = True
        msg = {
            "id": "msg_006",
            "from": "555191628223@c.us",
            "fromMe": False,
        }
        allowed = {"555191628223@c.us"}
        assert filter_service.should_process(msg, allowed_senders=allowed) is True

    def test_dev_mode_unauthorized_sender_rejected(self, filter_service):
        """DEV Mode: sender não autorizado DEVE ser rejeitado."""
        filter_service._mock_settings.DEV_MODE = True
        msg = {
            "id": "msg_007",
            "from": "5511888888888@c.us",
            "fromMe": False,
        }
        allowed = {"555191628223"}  # Apenas este número
        assert filter_service.should_process(msg, allowed_senders=allowed) is False

    def test_dev_mode_no_sender_rejected(self, filter_service):
        """DEV Mode: mensagem sem remetente DEVE ser rejeitada."""
        filter_service._mock_settings.DEV_MODE = True
        msg = {
            "id": "msg_008",
            "fromMe": False,
        }
        allowed = {"555191628223"}
        assert filter_service.should_process(msg, allowed_senders=allowed) is False

    def test_prod_mode_no_allowlist_accepts_all_senders(self, filter_service):
        """PROD Mode: sem allowlist, qualquer sender é aceito."""
        filter_service._mock_settings.DEV_MODE = False
        msg = {
            "id": "msg_009",
            "from": "anyphone@c.us",
            "fromMe": False,
        }
        # allowed_senders=None bypasses DEV mode check
        assert filter_service.should_process(msg, allowed_senders=None) is True

    # =========================================================================
    # Deduplication
    # =========================================================================
    def test_already_processed_message_rejected(self, filter_service, mock_redis):
        """Mensagem já processada DEVE ser rejeitada (deduplicação)."""
        mock_redis.get.return_value = b"1"  # Simula: já existe no Redis
        msg = {
            "id": "msg_010",
            "from": "555191628223@c.us",
            "fromMe": False,
        }
        assert filter_service.should_process(msg) is False

    def test_no_message_id_rejected(self, filter_service):
        """Mensagem sem ID DEVE ser rejeitada."""
        msg = {
            "from": "555191628223@c.us",
            "fromMe": False,
        }
        assert filter_service.should_process(msg) is False

    def test_new_message_accepted(self, filter_service, mock_redis):
        """Mensagem nova (não processada, ID válido) DEVE ser aceita."""
        mock_redis.get.return_value = None  # Não existe no Redis
        msg = {
            "id": "msg_011",
            "from": "555191628223@c.us",
            "fromMe": False,
        }
        assert filter_service.should_process(msg) is True

    # =========================================================================
    # mark_as_processed
    # =========================================================================
    def test_mark_as_processed_sets_redis_key(self, filter_service, mock_redis):
        """mark_as_processed DEVE criar chave no Redis com TTL de 24h."""
        filter_service.mark_as_processed("msg_012")
        mock_redis.set.assert_called_once_with("waha:processed:msg_012", "1", ex=86400)

    def test_mark_as_processed_ignores_none(self, filter_service, mock_redis):
        """mark_as_processed DEVE ignorar message_id None."""
        filter_service.mark_as_processed(None)
        mock_redis.set.assert_not_called()

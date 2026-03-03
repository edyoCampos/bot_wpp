
import pytest
from unittest.mock import MagicMock, patch
from robbot.infra.jobs.message_polling_job import poll_waha_messages
from robbot.config.settings import Settings

class TestPollingLogic:
    """
    Integration test for Polling Logic ensuring DEV mode restrictions work correctly.
    """

    @pytest.fixture
    def mock_dependencies(self):
        with patch("robbot.infra.jobs.message_polling_job.get_settings") as mock_get_settings, \
             patch("robbot.infra.jobs.message_polling_job.WahaMetadataService") as mock_metadata_cls, \
             patch("robbot.infra.jobs.message_polling_job.get_polling_strategy") as mock_get_strategy, \
             patch("robbot.infra.jobs.message_polling_job.MessageFilterService") as mock_filter_cls, \
             patch("robbot.infra.jobs.message_polling_job.get_queue_service") as mock_get_queue:
            
            # Setup Mocks
            mock_settings = MagicMock(spec=Settings)
            mock_settings.DEV_MODE = True
            mock_settings.dev_phone_list = ["5511999999999"]
            mock_get_settings.return_value = mock_settings

            mock_metadata = mock_metadata_cls.return_value
            mock_strategy = mock_get_strategy.return_value
            mock_filter = mock_filter_cls.return_value
            mock_queue = mock_get_queue.return_value

            yield {
                "settings": mock_settings,
                "metadata": mock_metadata,
                "strategy": mock_strategy,
                "filter": mock_filter,
                "queue": mock_queue
            }

    def test_polling_accepts_valid_phone_in_dev_mode(self, mock_dependencies):
        """
        Verifies that a message from a valid phone number is accepted even if
        the polling target uses an LID format (e.g., target '123@lid', msg from '123@c.us').
        """
        mocks = mock_dependencies
        
        # Scenario: 
        # - Target is LID: 5511999999999@lid
        # - Message is from: 5511999999999@c.us
        # - Config allows: 5511999999999
        
        mocks["strategy"].get_target_chats.return_value = ["5511999999999@lid"]
        
        msg_payload = {
            "id": "msg_123",
            "from": "5511999999999@c.us",
            "body": "Hello", 
            "fromMe": False,
            "timestamp": 1234567890
        }
        mocks["metadata"].get_messages_from_chat.return_value = [msg_payload]
        
        # Mock filter to behave like real service (partial logic reproduction for test validity)
        # But wait, we patched the class, so we need to mock the method behavior OR spy on arguments.
        # Since we modified the CALLER to pass the correct allowed_senders, we just need to verify
        # that 'should_process' is called with the settings list, NOT the target list.
        
        poll_waha_messages()
        
        # Verify allowlist passed to filter
        expected_allowlist = {"5511999999999"}
        
        # Get the call args
        call_args = mocks["filter"].should_process.call_args
        assert call_args is not None
        
        _, kwargs = call_args
        passed_allowlist = kwargs.get("allowed_senders")
        
        # Verify the allowlist contains the raw phone number
        assert passed_allowlist == expected_allowlist
        
        # Verify message was enqueued (assuming filter returned True by default mock)
        mocks["filter"].should_process.return_value = True
        
        # Re-run to trigger enqueue
        poll_waha_messages()
        mocks["queue"].enqueue_message_processing_debounced.assert_called()


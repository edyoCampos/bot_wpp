"""
Unit tests for QueueService.

Tests core business logic for queue management and job processing.
Note: These tests mock RQ and Redis to avoid external dependencies.
"""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from robbot.core.custom_exceptions import QueueError
from robbot.services.infrastructure.queue_service import QueueService


@pytest.fixture()
def mock_queue_manager():
    """Mock QueueManager and its queues."""
    with patch("robbot.services.queue_service.get_queue_manager") as mock_get_manager:
        mock_manager = MagicMock()

        # Mock individual queues
        mock_messages_queue = MagicMock()
        mock_ai_queue = MagicMock()
        mock_escalation_queue = MagicMock()
        mock_failed_queue = MagicMock()

        mock_manager.queue_messages = mock_messages_queue
        mock_manager.queue_ai = mock_ai_queue
        mock_manager.queue_escalation = mock_escalation_queue
        mock_manager.queue_failed = mock_failed_queue

        # Mock get_all_queues
        mock_manager.get_all_queues.return_value = {
            "messages": mock_messages_queue,
            "ai": mock_ai_queue,
            "escalation": mock_escalation_queue,
        }

        # Mock queue stats
        mock_manager.get_queue_stats.return_value = {
            "messages": {"queued": 5, "started": 2, "finished": 10},
            "ai": {"queued": 3, "started": 1, "finished": 7},
            "escalation": {"queued": 1, "started": 0, "finished": 2},
        }

        mock_get_manager.return_value = mock_manager

        yield {
            "manager": mock_manager,
            "messages": mock_messages_queue,
            "ai": mock_ai_queue,
            "escalation": mock_escalation_queue,
            "failed": mock_failed_queue,
        }


@pytest.fixture()
def queue_service(mock_queue_manager):
    """Create QueueService instance with mocked queues."""
    return QueueService()


# =====================================================================
# ENQUEUE JOBS TESTS
# =====================================================================
def test_enqueue_message_processing(queue_service, mock_queue_manager):
    """Test enqueuing message processing job."""
    message_data = {"phone": "+5511999999999", "text": "Hello", "type": "text"}
    conversation_id = "conv-123"

    job_id = queue_service.enqueue_message_processing(
        message_data=message_data, conversation_id=conversation_id, message_direction="inbound"
    )

    assert job_id is not None
    assert isinstance(job_id, str)

    # Verify enqueue was called
    mock_queue_manager["messages"].enqueue.assert_called_once()


def test_enqueue_message_processing_without_conversation(queue_service, mock_queue_manager):
    """Test enqueuing message without conversation ID."""
    message_data = {"phone": "+5511888888888", "text": "Test message"}

    job_id = queue_service.enqueue_message_processing(message_data=message_data)

    assert job_id is not None


def test_enqueue_ai_processing(queue_service, mock_queue_manager):
    """Test enqueuing AI processing job."""
    job_id = queue_service.enqueue_ai_processing(
        conversation_id="conv-456",
        message_id="msg-789",
        user_input="I want to schedule an appointment",
        phone="+5511777777777",
    )

    assert job_id is not None

    # Verify AI queue was used
    mock_queue_manager["ai"].enqueue.assert_called_once()


def test_enqueue_escalation(queue_service, mock_queue_manager):
    """Test enqueuing escalation job."""
    job_id = queue_service.enqueue_escalation(
        conversation_id="conv-999",
        reason="Customer requested human agent",
        phone="+5511666666666",
        user_name="John Doe",
    )

    assert job_id is not None

    # Verify escalation queue was used
    mock_queue_manager["escalation"].enqueue.assert_called_once()


def test_enqueue_escalation_without_user_name(queue_service, mock_queue_manager):
    """Test enqueuing escalation without user name."""
    job_id = queue_service.enqueue_escalation(
        conversation_id="conv-888", reason="Complex query", phone="+5511555555555"
    )

    assert job_id is not None


# =====================================================================
# GET JOB STATUS TESTS
# =====================================================================
@patch("robbot.services.queue_service.Job")
def test_get_job_status_queued(mock_job_class, queue_service, mock_queue_manager):
    """Test getting status of queued job."""
    job_id = "job-123"

    # Mock RQ Job
    mock_job = MagicMock()
    mock_job.get_status.return_value = "queued"
    mock_job.is_started = False
    mock_job.is_finished = False
    mock_job.is_failed = False
    mock_job.result = None
    mock_job.exc_info = None
    mock_job.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    mock_job.started_at = None
    mock_job.ended_at = None

    mock_job_class.fetch.return_value = mock_job

    status = queue_service.get_job_status(job_id)

    assert status["job_id"] == job_id
    assert status["status"] == "queued"
    assert status["is_started"] is False
    assert status["is_finished"] is False


@patch("robbot.services.queue_service.Job")
def test_get_job_status_finished(mock_job_class, queue_service, mock_queue_manager):
    """Test getting status of finished job."""
    job_id = "job-456"

    mock_job = MagicMock()
    mock_job.get_status.return_value = "finished"
    mock_job.is_started = True
    mock_job.is_finished = True
    mock_job.is_failed = False
    mock_job.result = {"success": True, "data": "processed"}
    mock_job.exc_info = None
    mock_job.created_at = datetime(2025, 1, 1, 10, 0, tzinfo=UTC)
    mock_job.started_at = datetime(2025, 1, 1, 10, 1, tzinfo=UTC)
    mock_job.ended_at = datetime(2025, 1, 1, 10, 2, tzinfo=UTC)

    mock_job_class.fetch.return_value = mock_job

    status = queue_service.get_job_status(job_id)

    assert status["status"] == "finished"
    assert status["is_finished"] is True
    assert status["result"] == {"success": True, "data": "processed"}


@patch("robbot.services.queue_service.Job")
def test_get_job_status_failed(mock_job_class, queue_service, mock_queue_manager):
    """Test getting status of failed job."""
    job_id = "job-789"

    mock_job = MagicMock()
    mock_job.get_status.return_value = "failed"
    mock_job.is_started = True
    mock_job.is_finished = True
    mock_job.is_failed = True
    mock_job.result = None
    mock_job.exc_info = "ValueError: Invalid input"
    mock_job.created_at = datetime(2025, 1, 1, tzinfo=UTC)
    mock_job.started_at = datetime(2025, 1, 1, tzinfo=UTC)
    mock_job.ended_at = datetime(2025, 1, 1, tzinfo=UTC)

    mock_job_class.fetch.return_value = mock_job

    status = queue_service.get_job_status(job_id)

    assert status["status"] == "failed"
    assert status["is_failed"] is True
    assert "ValueError" in status["exc_info"]


@patch("robbot.services.queue_service.Job")
def test_get_job_status_not_found(mock_job_class, queue_service, mock_queue_manager):
    """Test getting status of non-existent job."""
    job_id = "nonexistent-job"

    # Make Job.fetch raise exception for all queues
    mock_job_class.fetch.side_effect = ValueError("Job not found")

    status = queue_service.get_job_status(job_id)

    assert status["status"] == "not_found"
    # Accept both English and Portuguese error messages
    error_lower = status["error"].lower()
    assert "not found" in error_lower or "não encontrado" in error_lower


# =====================================================================
# QUEUE STATS TESTS
# =====================================================================
def test_get_queue_stats(queue_service, mock_queue_manager):
    """Test getting queue statistics."""
    stats = queue_service.get_queue_stats()

    assert "timestamp" in stats
    assert "queues" in stats
    assert isinstance(stats["queues"], dict)


# =====================================================================
# FAILED JOBS TESTS
# =====================================================================
# TODO: Implement or import FailedJobRegistry in queue_service
@patch("robbot.services.queue_service.FailedJobRegistry")
@patch("robbot.services.queue_service.Job")
def test_get_failed_jobs(mock_job_class, mock_registry_class, queue_service, mock_queue_manager):
    """Test retrieving failed jobs."""
    # Mock failed job registry
    mock_registry = MagicMock()
    mock_registry.get_job_ids.return_value = ["failed-1", "failed-2"]
    mock_registry_class.return_value = mock_registry

    # Mock failed jobs
    mock_job1 = MagicMock()
    mock_job1.func_name = "MessageProcessingJob"
    mock_job1.ended_at = datetime(2025, 1, 1, tzinfo=UTC)
    mock_job1.exc_info = "Error: Connection failed"

    mock_job2 = MagicMock()
    mock_job2.func_name = "GeminiAIProcessingJob"
    mock_job2.ended_at = datetime(2025, 1, 2, tzinfo=UTC)
    mock_job2.exc_info = "Error: Timeout"

    mock_job_class.fetch.side_effect = [mock_job1, mock_job2]

    failed_jobs = queue_service.get_failed_jobs(limit=10)

    assert len(failed_jobs) == 2
    assert failed_jobs[0]["job_id"] == "failed-1"
    assert failed_jobs[1]["job_id"] == "failed-2"
    assert "error" in failed_jobs[0]


@patch("robbot.services.queue_service.FailedJobRegistry")
@patch("robbot.services.queue_service.Job")
def test_get_failed_jobs_with_limit(mock_job_class, mock_registry_class, queue_service, mock_queue_manager):
    """Test getting failed jobs respects limit."""
    mock_registry = MagicMock()
    # Return more job IDs than limit
    mock_registry.get_job_ids.return_value = [f"job-{i}" for i in range(20)]
    mock_registry_class.return_value = mock_registry

    # Mock jobs
    def mock_fetch(job_id, connection):
        mock_job = MagicMock()
        mock_job.func_name = "TestJob"
        mock_job.ended_at = None
        mock_job.exc_info = "Error"
        return mock_job

    mock_job_class.fetch.side_effect = mock_fetch

    failed_jobs = queue_service.get_failed_jobs(limit=5)

    assert len(failed_jobs) <= 5


@patch("robbot.services.queue_service.FailedJobRegistry")
def test_get_failed_jobs_empty(mock_registry_class, queue_service, mock_queue_manager):
    """Test getting failed jobs when queue is empty."""
    mock_registry = MagicMock()
    mock_registry.get_job_ids.return_value = []
    mock_registry_class.return_value = mock_registry

    failed_jobs = queue_service.get_failed_jobs()

    assert failed_jobs == []


# =====================================================================
# RETRY JOB TESTS
# =====================================================================
@patch("robbot.services.queue_service.Job")
def test_retry_job_success(mock_job_class, queue_service, mock_queue_manager):
    """Test retrying a failed job successfully."""
    job_id = "failed-job-123"

    mock_job = MagicMock()
    mock_job_class.fetch.return_value = mock_job

    result = queue_service.retry_job(job_id)

    assert result is True
    mock_job.requeue.assert_called_once()


@patch("robbot.services.queue_service.Job")
def test_retry_job_not_found(mock_job_class, queue_service, mock_queue_manager):
    """Test retrying non-existent job returns False."""
    job_id = "nonexistent-job"

    mock_job_class.fetch.side_effect = ValueError("Job not found")

    result = queue_service.retry_job(job_id)

    assert result is False


@patch("robbot.services.queue_service.Job")
def test_retry_job_error_handling(mock_job_class, queue_service, mock_queue_manager):
    """Test retry job handles errors gracefully."""
    job_id = "error-job"

    mock_job = MagicMock()
    mock_job.requeue.side_effect = Exception("Requeue failed")
    mock_job_class.fetch.return_value = mock_job

    with pytest.raises(QueueError) as exc_info:
        queue_service.retry_job(job_id)

    assert "Failed to retry" in str(exc_info.value)


# =====================================================================
# HEALTH CHECK TESTS
# =====================================================================
def test_health_check(queue_service, mock_queue_manager):
    """Test queue service health check."""
    health = queue_service.health_check()

    assert health is not None
    assert "status" in health


# =====================================================================
# INTEGRATION-LIKE TESTS
# =====================================================================
def test_enqueue_multiple_jobs_different_queues(queue_service, mock_queue_manager):
    """Test enqueuing jobs to different queues."""
    # Enqueue to messages queue
    job1 = queue_service.enqueue_message_processing(message_data={"text": "Hello", "phone": "+5511999999999"})

    # Enqueue to AI queue
    job2 = queue_service.enqueue_ai_processing(
        conversation_id="conv-1", message_id="msg-1", user_input="Test", phone="+5511111111111"
    )

    # Enqueue to escalation queue
    job3 = queue_service.enqueue_escalation(conversation_id="conv-2", reason="Test", phone="+5511222222222")

    # All should return job IDs
    assert job1 is not None
    assert job2 is not None
    assert job3 is not None

    # Verify different queues were used
    assert mock_queue_manager["messages"].enqueue.called
    assert mock_queue_manager["ai"].enqueue.called
    assert mock_queue_manager["escalation"].enqueue.called


# =====================================================================
# EDGE CASE TESTS
# =====================================================================
def test_get_job_status_with_none_timestamps(queue_service, mock_queue_manager):
    """Test getting job status when timestamps are None."""
    with patch("robbot.services.queue_service.Job") as mock_job_class:
        mock_job = MagicMock()
        mock_job.get_status.return_value = "queued"
        mock_job.is_started = False
        mock_job.is_finished = False
        mock_job.is_failed = False
        mock_job.result = None
        mock_job.exc_info = None
        mock_job.created_at = None
        mock_job.started_at = None
        mock_job.ended_at = None

        mock_job_class.fetch.return_value = mock_job

        status = queue_service.get_job_status("job-123")

        assert status["created_at"] is None
        assert status["started_at"] is None
        assert status["ended_at"] is None

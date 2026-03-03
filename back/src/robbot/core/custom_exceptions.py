"""Custom exceptions para melhor error handling."""
# ===== Base Exceptions =====


class RobbotError(Exception):
    """Base exception para todas exceções do sistema."""


class AuthException(RobbotError):  # noqa: N818 (nomenclatura estabelecida no projeto)
    """Exceções relacionadas a autenticação e autorização."""


class NotFoundException(RobbotError):  # noqa: N818 (nomenclatura estabelecida no projeto)
    """Recurso não encontrado."""


class BusinessRuleError(RobbotError):
    """Violação de regra de negócio."""


class DatabaseError(RobbotError):
    """Erros de banco de dados."""


# ===== Service Exceptions =====


class ExternalServiceError(RobbotError):
    """Erro em serviço externo (WAHA, Gemini, etc)."""

    status_code: int | None

    def __init__(
        self,
        service_name: str = "ExternalService",
        message: str = "",
        original_error: Exception | None = None,
        status_code: int | None = None,
    ):
        self.service_name = service_name
        self.original_error = original_error
        self.status_code = status_code
        super().__init__(message)


class QueueError(RobbotError):
    """Erros no sistema de filas."""


class LLMError(ExternalServiceError):
    """Erros específicos de LLM (Gemini, Groq, etc)."""

    def __init__(self, service: str = "LLM", message: str = "", original_error: Exception | None = None):
        super().__init__(service, message, original_error)


class WAHAError(ExternalServiceError):
    """Erros específicos do WAHA."""

    def __init__(self, message: str, original_error: Exception | None = None, status_code: int | None = None):
        super().__init__("WAHA", message, original_error, status_code=status_code)


class VectorDBError(ExternalServiceError):
    """Erros no ChromaDB."""

    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__("ChromaDB", message, original_error)


# ===== Data Exceptions =====


class ValidationError(RobbotError):
    """Erro de validação de dados."""


class ExportError(RobbotError):
    """Erro durante exportação de relatórios (PDF/Excel)."""


class ConfigurationError(RobbotError):
    """Erro de configuração do sistema."""


class JobError(RobbotError):
    """Erro durante execução de job background."""

    def __init__(self, job_name: str, message: str, original_error: Exception | None = None):
        self.job_name = job_name
        self.original_error = original_error
        super().__init__(f"Job '{job_name}': {message}")

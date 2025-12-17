"""Custom exceptions para melhor error handling."""

from typing import Optional


# ===== Base Exceptions =====

class RobbotException(Exception):
    """Base exception para todas exceções do sistema."""


class AuthException(RobbotException):
    """Exceções relacionadas a autenticação e autorização."""


class NotFoundException(RobbotException):
    """Recurso não encontrado."""


class BusinessRuleError(RobbotException):
    """Violação de regra de negócio."""


class DatabaseError(RobbotException):
    """Erros de banco de dados."""


# ===== Service Exceptions =====

class ExternalServiceError(RobbotException):
    """Erro em serviço externo (WAHA, Gemini, etc)."""
    
    def __init__(self, service_name: str, message: str, original_error: Optional[Exception] = None):
        self.service_name = service_name
        self.original_error = original_error
        super().__init__(f"{service_name}: {message}")


class QueueError(RobbotException):
    """Erros no sistema de filas."""


class LLMError(ExternalServiceError):
    """Erros específicos de LLM (Gemini, OpenAI, etc)."""
    
    def __init__(self, service: str = "LLM", message: str = "", original_error: Optional[Exception] = None):
        super().__init__(service, message, original_error)


class WAHAError(ExternalServiceError):
    """Erros específicos do WAHA."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__("WAHA", message, original_error)


class VectorDBError(ExternalServiceError):
    """Erros no ChromaDB."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__("ChromaDB", message, original_error)


# ===== Data Exceptions =====

class ValidationError(RobbotException):
    """Erro de validação de dados."""


class ConfigurationError(RobbotException):
    """Erro de configuração do sistema."""


class JobError(RobbotException):
    """Erro durante execução de job background."""
    
    def __init__(self, job_name: str, message: str, original_error: Optional[Exception] = None):
        self.job_name = job_name
        self.original_error = original_error
        super().__init__(f"Job '{job_name}': {message}")

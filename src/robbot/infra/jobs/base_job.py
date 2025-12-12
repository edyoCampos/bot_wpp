"""
Base job class com retry policy, logging e error handling.
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Optional

from robbot.config.settings import settings

logger = logging.getLogger(__name__)


class JobFailureError(Exception):
    """Exceção para falhas não-recuperáveis em jobs."""
    pass


class JobRetryableError(Exception):
    """Exceção para falhas recuperáveis (serão retentadas)."""
    pass


class BaseJob(ABC):
    """
    Classe base para todos os jobs assíncronos.
    
    Responsabilidades:
    - Implementar retry com backoff exponencial
    - Logging estruturado de eventos
    - Tratamento de exceções
    - Persistência de estado (quando necessário)
    
    Subclasses devem implementar: execute()
    """

    # Retry config
    MAX_RETRIES = settings.RQ_MAX_RETRIES
    RETRY_BACKOFF = [1, 2, 4]  # segundos (exponencial)

    def __init__(
        self,
        job_id: Optional[str] = None,
        attempt: int = 0,
        metadata: Optional[dict[str, Any]] = None,
    ):
        """
        Inicializar job.
        
        Args:
            job_id: ID único do job (gerado pelo RQ se não fornecido)
            attempt: Número da tentativa atual (0 = primeira tentativa)
            metadata: Dados adicionais para rastreamento
        """
        self.job_id = job_id or self._generate_job_id()
        self.attempt = attempt
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    @staticmethod
    def _generate_job_id() -> str:
        """Gerar ID único para o job."""
        return f"{datetime.utcnow().timestamp()}"

    @abstractmethod
    def execute(self) -> Any:
        """
        Executar lógica do job.
        
        Este método DEVE ser implementado pelas subclasses.
        
        Pode lançar:
        - JobRetryableError: Será retentado com backoff
        - JobFailureError: Falha definitiva, vai para DLQ
        - Exception: Tratado como erro não-previsto, retentado
        
        Returns:
            Resultado do processamento
        """
        raise NotImplementedError("Subclasses devem implementar execute()")

    def run(self) -> Any:
        """
        Executar job com tratamento de erros e logging.
        
        Esta é a função que RQ vai chamar diretamente.
        
        Returns:
            Resultado do execute() ou None se falhar
        """
        self.started_at = datetime.utcnow()
        
        try:
            logger.info(
                f"[JOB:{self.job_id}] Iniciando execução (tentativa {self.attempt + 1}/{self.MAX_RETRIES + 1})",
                extra=self._log_context(),
            )
            
            result = self.execute()
            
            self.completed_at = datetime.utcnow()
            duration = (self.completed_at - self.started_at).total_seconds()
            
            logger.info(
                f"[JOB:{self.job_id}] ✓ Concluído com sucesso ({duration:.2f}s)",
                extra=self._log_context(),
            )
            
            return result

        except JobRetryableError as e:
            return self._handle_retryable_error(e)
        except JobFailureError as e:
            return self._handle_failure_error(e)
        except Exception as e:
            return self._handle_unexpected_error(e)

    def _handle_retryable_error(self, error: JobRetryableError) -> None:
        """Tratar erro recuperável (retentável)."""
        self.attempt += 1
        
        if self.attempt < self.MAX_RETRIES:
            wait_seconds = self.RETRY_BACKOFF[self.attempt - 1]
            logger.warning(
                f"[JOB:{self.job_id}] ⚠ Erro retentável: {error}. "
                f"Retentando em {wait_seconds}s (tentativa {self.attempt + 1}/{self.MAX_RETRIES + 1})",
                extra=self._log_context(),
            )
            
            # Aguardar e relançar para RQ reprocessar
            time.sleep(wait_seconds)
            raise error
        else:
            logger.error(
                f"[JOB:{self.job_id}] ✗ Falha após {self.MAX_RETRIES} tentativas. "
                f"Movendo para DLQ. Erro: {error}",
                extra=self._log_context(),
            )
            raise JobFailureError(str(error))

    def _handle_failure_error(self, error: JobFailureError) -> None:
        """Tratar erro não-recuperável (vai para DLQ)."""
        logger.error(
            f"[JOB:{self.job_id}] ✗ Falha definitiva (não-recuperável): {error}",
            extra=self._log_context(),
        )
        raise error

    def _handle_unexpected_error(self, error: Exception) -> None:
        """Tratar erro inesperado (tentar retryar)."""
        self.attempt += 1
        
        if self.attempt < self.MAX_RETRIES:
            wait_seconds = self.RETRY_BACKOFF[self.attempt - 1]
            logger.warning(
                f"[JOB:{self.job_id}] ⚠ Erro inesperado: {type(error).__name__}: {error}. "
                f"Retentando em {wait_seconds}s (tentativa {self.attempt + 1}/{self.MAX_RETRIES + 1})",
                extra=self._log_context(),
            )
            
            time.sleep(wait_seconds)
            raise JobRetryableError(str(error))
        else:
            logger.error(
                f"[JOB:{self.job_id}] ✗ Falha após {self.MAX_RETRIES} tentativas. "
                f"Erro: {type(error).__name__}: {error}",
                extra=self._log_context(),
            )
            raise JobFailureError(str(error))

    def _log_context(self) -> dict[str, Any]:
        """Retornar contexto estruturado para logging."""
        return {
            "job_id": self.job_id,
            "job_type": self.__class__.__name__,
            "attempt": self.attempt,
            "metadata": json.dumps(self.metadata, default=str),
        }

    def get_status(self) -> dict[str, Any]:
        """Retornar status atual do job."""
        status = "pending"
        if self.started_at:
            status = "running"
        if self.completed_at:
            status = "completed"
        
        return {
            "job_id": self.job_id,
            "type": self.__class__.__name__,
            "status": status,
            "attempt": self.attempt,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
        }

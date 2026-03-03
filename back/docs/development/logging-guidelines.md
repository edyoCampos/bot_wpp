# Logging Guidelines - Clinica Go Backend

> **Versão:** 1.0  
> **Data:** 05/01/2026  
> **Status:** ✅ Implementado

## 📋 Visão Geral

Este documento define os padrões de logging para o backend da Clinica Go, seguindo o modelo do WAHA (WhatsApp HTTP API) para logs profissionais, estruturados e sem emojis.

## 🎯 Formato Padrão

### Estrutura

```
[YYYY-MM-DD HH:MM:SS.mmm] LEVEL (ModuleName/ProcessID): Message
```

### Exemplos

```log
[2026-01-05 12:13:58.177] INFO (Bootstrap/48): Application started successfully
[2026-01-05 12:13:51.061] INFO (rq.worker): Worker worker-9be3c0bbe0ce: started with PID 1
[2026-01-05 12:42:09.492] INFO (AutoscalerService/1): Current state: Workers=1, PendingJobs=0
[2026-01-05 12:30:45.123] ERROR (AuthService/42): Authentication failed user_id=123 reason=invalid_password
```

## 🚫 O Que NÃO Fazer

### ❌ Não usar emojis

```python
# ERRADO
logger.info("🟢 Usuário autenticado com sucesso")
logger.error("🔴 Falha na autenticação")
logger.warning("⚠️ Cache quase cheio")

# CORRETO
logger.info("User authenticated successfully")
logger.error("Authentication failed")
logger.warning("Cache usage at 85% capacity")
```

### ❌ Não usar logs sem contexto

```python
# ERRADO
logger.info("Processing message")
logger.error("Failed")

# CORRETO
logger.info(f"Processing message: chat_id={chat_id}, message_id={message_id}")
logger.error(f"Message processing failed: chat_id={chat_id}, error={error}")
```

### ❌ Não logar informações sensíveis

```python
# ERRADO
logger.info(f"User logged in: password={password}")
logger.debug(f"API key: {api_key}")

# CORRETO
logger.info(f"User logged in: user_id={user_id}")
logger.debug(f"API key configured: length={len(api_key)}")
```

## ✅ Boas Práticas

### 1. Use Níveis Apropriados

```python
import logging

logger = logging.getLogger(__name__)

# DEBUG: Informações detalhadas para debugging
logger.debug(f"Query executed: {query} rows={rows_returned}")

# INFO: Eventos normais de negócio
logger.info(f"User authenticated: user_id={user_id}")
logger.info(f"Conversation created: conv_id={conv_id}, chat_id={chat_id}")

# WARNING: Situações inesperadas mas recuperáveis
logger.warning(f"Cache miss: key={cache_key}, fetching from database")
logger.warning(f"Retry attempt {attempt}/3 for request_id={request_id}")

# ERROR: Erros que precisam atenção
logger.error(f"Database connection failed: {error}", exc_info=True)
logger.error(f"External API timeout: service={service_name} timeout={timeout}s")

# CRITICAL: Falhas graves do sistema
logger.critical(f"Redis connection lost, application cannot continue")
```

### 2. Adicione Contexto Relevante

```python
# Contexto de usuário/sessão
logger.info(
    f"Message processed: "
    f"user_id={user_id}, "
    f"session_id={session_id}, "
    f"duration_ms={duration}"
)

# Contexto de operação
logger.info(
    f"Database query completed: "
    f"table={table_name}, "
    f"operation={operation}, "
    f"rows_affected={rows}, "
    f"duration_ms={duration}"
)

# Contexto de erro
logger.error(
    f"API request failed: "
    f"endpoint={endpoint}, "
    f"status_code={status_code}, "
    f"retry_count={retry_count}, "
    f"error={error_message}"
)
```

### 3. Use Timestamps Automaticamente

```python
# NÃO faça manualmente
logger.info(f"[{datetime.now()}] Message processed")

# FAÇA: deixe o logging_setup.py adicionar automaticamente
logger.info("Message processed")
# Resultado: [2026-01-05 12:30:45.123] INFO (ServiceName/42): Message processed
```

### 4. Logs em Operações Críticas

```python
# Início e fim de operações importantes
logger.info(f"Starting message processing: message_id={message_id}")
try:
    # ... processamento ...
    logger.info(
        f"Message processing completed: "
        f"message_id={message_id}, "
        f"duration_ms={duration}"
    )
except Exception as e:
    logger.error(
        f"Message processing failed: "
        f"message_id={message_id}, "
        f"error={str(e)}",
        exc_info=True  # Inclui stack trace
    )
    raise
```

## 📚 Configuração

### Uso Básico

```python
from robbot.core.logging_setup import configure_logging
import logging

# Configurar no início da aplicação (main.py, worker.py, etc)
configure_logging()

# Usar em módulos
logger = logging.getLogger(__name__)
logger.info("Module initialized")
```

### Configuração Customizada

```python
from robbot.core.logging_setup import configure_logging

# Custom log file e rotation
configure_logging(
    log_file="custom_service.log",
    max_bytes=20 * 1024 * 1024,  # 20MB
    backup_count=10,
    console_output=True,  # False para disable console em prod
)
```

### Níveis por Ambiente

```bash
# Development (default: DEBUG)
export ENVIRONMENT=development
export LOG_LEVEL=DEBUG

# Staging (default: INFO)
export ENVIRONMENT=staging
export LOG_LEVEL=INFO

# Production (default: INFO)
export ENVIRONMENT=production
export LOG_LEVEL=INFO

# Custom override
export LOG_LEVEL=WARNING  # Sobrescreve o default do ambiente
```

## 🔧 Exemplos Práticos

### Services

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ConversationService:
    def create_conversation(self, chat_id: str, phone: str) -> Conversation:
        logger.info(f"Creating conversation: chat_id={chat_id}, phone={phone}")
        
        try:
            conversation = self.repository.create(chat_id, phone)
            
            logger.info(
                f"Conversation created successfully: "
                f"conv_id={conversation.id}, "
                f"chat_id={chat_id}"
            )
            
            return conversation
            
        except DatabaseError as e:
            logger.error(
                f"Failed to create conversation: "
                f"chat_id={chat_id}, "
                f"error={str(e)}",
                exc_info=True
            )
            raise
```

### Workers

```python
import logging
from rq import Worker

logger = logging.getLogger(__name__)

def process_message_job(message_id: int):
    logger.info(f"Job started: process_message message_id={message_id}")
    
    try:
        # ... processamento ...
        logger.info(f"Job completed: process_message message_id={message_id}")
        
    except Exception as e:
        logger.error(
            f"Job failed: process_message "
            f"message_id={message_id}, "
            f"error={str(e)}",
            exc_info=True
        )
        raise

# Início do worker
logger.info(f"Worker starting: queues={queues}, name={worker_name}")
worker = Worker(queues, connection=redis_conn)
worker.work()
```

### Scripts

```python
import logging
from robbot.core.logging_setup import configure_logging

# Configurar logging no início do script
configure_logging()
logger = logging.getLogger(__name__)

def main():
    logger.info("Script started: autoscale_workers")
    
    try:
        current_workers = get_worker_count()
        pending_jobs = get_pending_jobs_count()
        
        logger.info(
            f"Current state: "
            f"workers={current_workers}, "
            f"pending_jobs={pending_jobs}"
        )
        
        # ... lógica de autoscaling ...
        
        logger.info("Script completed successfully")
        
    except Exception as e:
        logger.error(f"Script failed: error={str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
```

## 📊 Log Rotation

### Configuração

- **Tamanho máximo por arquivo:** 10MB (default)
- **Número de backups:** 5 arquivos (default)
- **Formato de arquivos:** `robbot.log`, `robbot.log.1`, `robbot.log.2`, etc.
- **Encoding:** UTF-8

### Estrutura de Diretórios

```
back/
├── logs/
│   ├── robbot.log          # Arquivo atual
│   ├── robbot.log.1        # Backup mais recente
│   ├── robbot.log.2
│   ├── robbot.log.3
│   ├── robbot.log.4
│   └── robbot.log.5        # Backup mais antigo
```

## 🔍 Debugging

### Ativar DEBUG Temporariamente

```python
import logging

# Ativar DEBUG para módulo específico
logging.getLogger("robbot.services.auth").setLevel(logging.DEBUG)

# Ativar DEBUG para todos os módulos
logging.getLogger("robbot").setLevel(logging.DEBUG)
```

### Análise de Logs

```bash
# Filtrar logs por nível
grep "ERROR" logs/robbot.log

# Filtrar por módulo
grep "(AuthService/" logs/robbot.log

# Últimas 100 linhas
tail -n 100 logs/robbot.log

# Follow em tempo real
tail -f logs/robbot.log

# Contar erros
grep -c "ERROR" logs/robbot.log
```

## ✅ Checklist de Validação

Antes de fazer commit, verifique:

- [ ] Logs não contêm emojis
- [ ] Logs têm contexto suficiente (IDs, valores relevantes)
- [ ] Não há informações sensíveis (passwords, tokens, API keys)
- [ ] Níveis de log apropriados (INFO para eventos normais, ERROR para falhas)
- [ ] Stack traces incluídos em erros (`exc_info=True`)
- [ ] Timestamps não são adicionados manualmente
- [ ] Formato consistente com exemplos acima

## 🔗 Referências

- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [Logging Best Practices](https://docs.python-guide.org/writing/logging/)
- WAHA Logs (modelo de referência): Ver logs do container `waha`

---

**Última Atualização:** 05/01/2026  
**Mantido por:** Equipe Backend Clinica Go

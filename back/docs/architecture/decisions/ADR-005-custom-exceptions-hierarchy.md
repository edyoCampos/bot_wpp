# ADR-003: Custom Exceptions com Hierarquia RobbotException

**Status:** ✅ Aceito e Implementado  
**Data:** 30/12/2025 (Migração FASE 3 completa)  
**Decisão Por:** Time de Desenvolvimento  
**Contexto:** Eliminação de duplicações e padronização

---

## Contexto

O projeto tinha **dois arquivos de exceptions** com duplicação:

1. `core/exceptions.py` - Versão simples (exceptions genéricas)
2. `core/custom_exceptions.py` - Versão completa com hierarquia

Código usava ambos arquivos de forma inconsistente:
- Controllers usavam `exceptions.py`
- Workers/Jobs usavam `custom_exceptions.py`
- Confusão sobre qual importar

---

## Decisão

**Padronizar em `custom_exceptions.py`** com hierarquia completa:

```python
class RobbotException(Exception):
    """Base exception para todas exceções do sistema."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

# Especializações
class AuthException(RobbotException):
    """Autenticação/Autorização"""

class ExternalServiceError(RobbotException):
    """Serviços externos (Gemini, WAHA, ChromaDB)"""
    
    def __init__(self, service_name: str, message: str, original_error: Optional[Exception] = None):
        self.service_name = service_name
        self.original_error = original_error
        super().__init__(f"{service_name}: {message}")

class LLMError(ExternalServiceError):
    """Específico para LLMs (Gemini)"""

class WAHAError(ExternalServiceError):
    """Específico para WAHA API"""

class VectorDBError(ExternalServiceError):
    """Específico para ChromaDB"""
```

**Deletar** `core/exceptions.py` após migração.

---

## Consequências

### Positivas ✅

1. **Hierarquia Clara**
   - `RobbotException` como base
   - Especializações por categoria
   - Possível fazer `except RobbotException` para catch-all

2. **Contexto Adicional**
   - `details` dict para metadata
   - `service_name` em ExternalServiceError
   - `original_error` para debugging

3. **Rastreabilidade em Logs**
   ```python
   try:
       gemini_client.generate()
   except LLMError as e:
       logger.error(f"LLM falhou: {e.service_name} - {e.message}", 
                    extra={"original_error": str(e.original_error)})
   ```

4. **Tratamento Específico**
   ```python
   # Retry apenas para external services
   except ExternalServiceError as e:
       if e.service_name == "Gemini":
           retry()
   ```

### Negativas ❌

1. **Migração Necessária**
   - 36 arquivos precisaram ser atualizados
   - Overhead de 2-3 horas de refactoring

2. **Mais Código**
   - Hierarquia adiciona complexidade inicial
   - Compensado por melhor debugging

---

## Implementação

### FASE 3: Migração de Exceptions (30/12/2025)

**Estatísticas:**
- ✅ 36 arquivos migrados
- ✅ 0 imports antigos remanescentes
- ✅ `exceptions.py` deletado
- ✅ Todos os testes passando

**Arquivos Migrados:**
- 18 Controllers
- 10 Services
- 5 Workers/Jobs
- 3 External Adapters

### Padrão de Import

```python
# Antes (inconsistente)
from robbot.core.exceptions import AuthException  # Versão simples
from robbot.core.custom_exceptions import LLMError  # Versão completa

# Depois (padronizado)
from robbot.core.custom_exceptions import AuthException, LLMError
```

---

## Casos de Uso

### 1. External Services com Retry

```python
from robbot.core.custom_exceptions import LLMError

try:
    response = gemini_client.generate_response(prompt)
except LLMError as e:
    logger.error(f"Gemini falhou: {e.message}", extra=e.details)
    # Retry com backoff exponencial
    retry_with_backoff()
```

### 2. Catch-All de Sistema

```python
from robbot.core.custom_exceptions import RobbotException

try:
    process_webhook()
except RobbotException as e:
    # Log estruturado
    logger.error(f"Erro interno: {e.message}", extra=e.details)
    return {"error": "Internal error", "code": type(e).__name__}
except Exception as e:
    # Erro desconhecido (não esperado)
    logger.critical(f"Erro não tratado: {str(e)}")
    raise
```

### 3. Validação de Negócio

```python
from robbot.core.custom_exceptions import BusinessRuleError

def create_lead(data):
    if Lead.exists(data["phone"]):
        raise BusinessRuleError(
            "Lead já existe",
            details={"phone": data["phone"], "existing_id": lead.id}
        )
```

---

## Alternativas Consideradas

### Alternativa 1: Manter exceptions.py simples ❌
- **Problema:** Sem contexto adicional, debugging difícil
- **Decisão:** Rejeitado

### Alternativa 2: Usar apenas Exception nativa ❌
- **Problema:** Impossível distinguir erros do sistema vs. bugs
- **Decisão:** Rejeitado

### Alternativa 3: Exceptions genéricas + códigos ❌
```python
raise AppException("AUTH_001", "Invalid token")
```
- **Problema:** Códigos magic numbers, menos type-safe
- **Decisão:** Rejeitado - hierarquia é mais Pythonic

---

## Exceções Disponíveis

| Classe | Uso | Parent |
|--------|-----|--------|
| `RobbotException` | Base (catch-all) | `Exception` |
| `AuthException` | Login, JWT, MFA | `RobbotException` |
| `NotFoundException` | Resource não existe | `RobbotException` |
| `BusinessRuleError` | Validação negócio | `RobbotException` |
| `DatabaseError` | SQLAlchemy errors | `RobbotException` |
| `ExternalServiceError` | APIs externas | `RobbotException` |
| `LLMError` | Gemini AI | `ExternalServiceError` |
| `WAHAError` | WhatsApp API | `ExternalServiceError` |
| `VectorDBError` | ChromaDB | `ExternalServiceError` |
| `QueueError` | Redis Queue | `RobbotException` |
| `ValidationError` | Pydantic, schema | `RobbotException` |
| `ConfigurationError` | Settings, env | `RobbotException` |
| `JobError` | Background jobs | `RobbotException` |

---

## Referências

- [Python Exception Hierarchy](https://docs.python.org/3/library/exceptions.html)
- [Custom Exceptions Best Practices](https://realpython.com/python-exceptions/)
- Refatoração FASE 3 - 30/12/2025

---

**Última Atualização:** 03/01/2026  
**Arquivos Migrados:** 36/36 (100%)  
**Status:** ✅ Produção

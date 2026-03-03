# Guia de Correção de Erros de Linting

**Data:** 16 de Janeiro de 2026  
**Total de Warnings:** 196  
**Status:** 🔧 Em correção

---

## 📊 Resumo por Categoria

| Categoria | Quantidade | Prioridade | Status |
|-----------|-----------|-----------|---------|
| **raise-missing-from** | 14 | 🔴 ALTA | ⏳ Pendente |
| **logging-fstring-interpolation** | 7 | 🔴 ALTA | ⏳ Pendente |
| **missing-timeout** | 26 | 🔴 ALTA | ⏳ Pendente |
| **redefined-outer-name** | 67 | 🟢 BAIXA | ✅ Aceitável (pytest) |
| **broad-exception-caught** | 12 | 🟡 MÉDIA | 🔍 Revisar |
| **unused-import** | 5 | 🟡 MÉDIA | ⏳ Pendente |
| **unused-variable** | 4 | 🟡 MÉDIA | ⏳ Pendente |
| **fixme/TODO** | 1 | 🟢 BAIXA | ✅ Documentado |
| **Outros** | 60 | 🟢 BAIXA | 🔍 Avaliar |

---

## 🔴 PRIORIDADE ALTA: Correções Críticas

### 1. `W0707: raise-missing-from` (14 ocorrências)

**Problema:** Ao capturar e re-lançar exceções, não usar `from e` perde o stack trace original.

**Impacto:** Debugging difícil, perda de contexto de erro.

**Arquivos afetados:**
- `auth_services.py:440`
- `context_builder.py:64, 86`
- `message_pipeline.py:150, 193`
- `message_processor.py:135, 165`
- `response_generator.py:103, 217`
- `transcription_service.py:50, 52, 113`
- `conftest.py:299`

**Solução:**
```python
# ❌ ERRADO
except Exception as e:
    raise CustomError(f"Failed: {e}")

# ✅ CORRETO
except Exception as e:
    raise CustomError(f"Failed: {e}") from e
```

**Correção automática:** Executar `python fix_linting.py`

---

### 2. `W1203: logging-fstring-interpolation` (7 ocorrências)

**Problema:** Usar f-strings em logs causa avaliação desnecessária mesmo quando o log não será exibido.

**Impacto:** Performance degradada, overhead desnecessário.

**Arquivos afetados:**
- `filter_service.py:99, 164, 216, 246`
- `transcription_service.py:112, 180`
- `waha_service.py:269, 289`

**Solução:**
```python
# ❌ ERRADO
logger.error(f"Failed to process {item_id}: {error}")

# ✅ CORRETO
logger.error("Failed to process %s: %s", item_id, error)
```

**Benefício:** Lazy evaluation - variáveis só são formatadas se o log for realmente exibido.

---

### 3. `W3101: missing-timeout` (26 ocorrências nos testes)

**Problema:** Chamadas HTTP sem timeout podem travar indefinidamente.

**Impacto:** Testes pendurados, CI/CD travado, timeout de 30 minutos.

**Arquivos afetados:**
- `conftest.py:70, 115, 137, 178, 198, 282, 302`
- `test_01_auth.py:22, 35, 37, 59, 65, 81, 117, 120, 128, 154, 157, 165, 197`
- `test_05_conversations.py:21`
- `test_06_gemini.py:21, 47, 70, 93, 116`
- `test_07_escalation.py:30, 52, 71`
- `test_message_debug.py:18, 27, 32`

**Solução:**
```python
# ❌ ERRADO
response = requests.get(url)

# ✅ CORRETO
response = requests.get(url, timeout=30)
```

---

## 🟡 PRIORIDADE MÉDIA: Limpeza de Código

### 4. `W0611: unused-import` (5 ocorrências)

**Arquivos:**
- `test_01_auth.py:10` - `import pytest`
- `test_02_waha.py:9` - `import pytest`
- `test_03_playbooks.py:12` - `import pytest`
- `test_05_conversations.py:6` - `import pytest`
- `test_09_metrics.py:6` - `import pytest`

**Solução:** Remover imports ou adicionar `# noqa: F401` se necessário para fixtures.

---

### 5. `W0612: unused-variable` (4 ocorrências)

**Arquivos:**
- `waha_service.py:90` - `unused variable 'e'`
- `conftest.py:246` - `unused variable 'email'`
- `test_conversation_orchestrator_new.py:333` - `unused variable 'status'`

**Solução:**
```python
# ❌ ERRADO
except Exception as e:
    raise

# ✅ CORRETO (usar underscore se não for usar)
except Exception as _e:
    raise
```

---

### 6. `W0718: broad-exception-caught` (12 ocorrências)

**Análise:**

**✅ ACEITÁVEL (health checks):**
- `health_service.py:40, 46, 58, 67, 75` - Health checks devem capturar qualquer erro

**🔍 REVISAR:**
- `message_processor.py:87, 103` - Pode especificar exceções específicas
- `response_generator.py:155` - Pode especificar LLMError, DatabaseError
- `transcription_service.py:179` - Já tem LLMError no except acima
- `waha_service.py:78, 299` - Pode especificar httpx.HTTPError, requests.RequestException

**Solução (onde aplicável):**
```python
# ❌ GENÉRICO
except Exception:
    handle_error()

# ✅ ESPECÍFICO
except (HTTPError, Timeout, ConnectionError) as e:
    handle_error(e)
```

---

## 🟢 PRIORIDADE BAIXA: Aceitáveis ou Documentados

### 7. `W0621: redefined-outer-name` (67 ocorrências)

**Status:** ✅ **ACEITÁVEL**

**Razão:** Padrão esperado em pytest fixtures. Fixtures são definidas no escopo externo e redefinidas como parâmetros nos testes.

**Exemplo:**
```python
@pytest.fixture
def admin_token():
    return "token123"

def test_something(admin_token):  # Redefined-outer-name é esperado
    assert admin_token == "token123"
```

**Ação:** Nenhuma - é o comportamento correto do pytest.

---

### 8. `W0511: fixme` (1 ocorrência)

**Arquivo:** `message_processor.py:83` - `TODO: Implementar descrição assíncrona`

**Status:** ✅ **DOCUMENTADO**

**Razão:** TODO está no épico de melhorias futuras (docs/epic/messages/README.md).

**Ação:** Manter como está - é um lembrete válido.

---

## 🔧 Como Corrigir

### Opção 1: Script Automático (Recomendado)

```bash
cd back

# Executar script de correção
python fix_linting.py

# Verificar mudanças
ruff check .

# Review manual
git diff
```

**O que o script corrige:**
- ✅ Adiciona `from e` em 14 raises
- ✅ Converte 7 f-strings para lazy %
- ✅ Adiciona timeout=30 em 26 requests
- ✅ Remove 5 imports não usados

---

### Opção 2: Correção Manual

#### Passo 1: Corrigir raise-missing-from

```bash
# Buscar todos os casos
ruff check --select W0707 .

# Exemplo de correção
# Antes:
except Exception as e:
    raise CustomError(f"Error: {e}")

# Depois:
except Exception as e:
    raise CustomError(f"Error: {e}") from e
```

#### Passo 2: Corrigir logging

```bash
# Buscar todos os casos
ruff check --select W1203 .

# Exemplo de correção
# Antes:
logger.error(f"Failed: {var1}, {var2}")

# Depois:
logger.error("Failed: %s, %s", var1, var2)
```

#### Passo 3: Adicionar timeouts

```bash
# Buscar todos os casos
ruff check --select W3101 .

# Exemplo de correção
# Antes:
requests.get(url)

# Depois:
requests.get(url, timeout=30)
```

---

## 📈 Progresso

### Antes da Correção
```
Total de warnings: 196
Críticos (ALTA): 47
Médios: 21
Baixos (Aceitáveis): 128
```

### Após Correção Automática (Estimativa)
```
Total de warnings: 149
Críticos (ALTA): 0  ✅
Médios: 21
Baixos (Aceitáveis): 128
```

### Meta Final
```
Total de warnings: < 130
Críticos: 0
Médios: < 10
Baixos: < 130 (pytest fixtures aceitáveis)
```

---

## 🧪 Validação

Após correções, executar:

```bash
# Linting completo
ruff check .

# Formatação
ruff format .

# Testes unitários
pytest tests/unit/ -v

# Testes de integração
pytest tests/integration/ -v

# Testes de API (se containers rodando)
pytest tests/api/ -v
```

---

## 📝 Regras de Linting (ruff.toml)

Para evitar erros futuros, considerar adicionar ao `ruff.toml`:

```toml
[lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]

ignore = [
    "W0621",  # redefined-outer-name (pytest fixtures)
    "W0511",  # fixme (allow TODOs)
]

[lint.per-file-ignores]
"tests/**/*.py" = [
    "W0621",  # pytest fixtures
]

"*/health_service.py" = [
    "W0718",  # broad-exception-caught (health checks)
]
```

---

## ✅ Checklist de Correção

- [ ] Executar `python fix_linting.py`
- [ ] Revisar mudanças com `git diff`
- [ ] Executar `ruff check .` para verificar
- [ ] Executar `pytest` para garantir que não quebrou nada
- [ ] Commit: `fix: resolve 47 critical linting warnings`
- [ ] Push e verificar CI

---

## 📚 Referências

- [PEP 3134 - Exception Chaining](https://peps.python.org/pep-3134/) - raise from
- [Python Logging Performance](https://docs.python.org/3/howto/logging.html#optimization) - lazy %
- [Requests Timeouts](https://requests.readthedocs.io/en/latest/user/advanced/#timeouts) - best practices
- [Pytest Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) - redefined-outer-name

---

**Última atualização:** 16 de Janeiro de 2026  
**Status:** 🔧 Pronto para correção automática

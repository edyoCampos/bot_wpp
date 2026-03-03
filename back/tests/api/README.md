# API Integration Tests

Testes de integração da API GO. usando **pytest + requests** em Python puro.

## 📊 Cobertura

| Fase | Testes | Arquivo | Casos (UC) |
|------|--------|---------|-----------|
| 1 | 5 | `test_01_auth.py` | UC-001 a UC-005: Autenticação |
| 2 | 4 | `test_02_waha.py` | UC-006 a UC-009: WAHA/WhatsApp |
| 3 | 6 | `test_03_playbooks.py` | UC-010 a UC-015: Playbooks |
| 4 | 5 | `test_04_messages.py` | UC-016 a UC-020: Mensagens |
| 5 | 5 | `test_05_conversations.py` | UC-021 a UC-025: Conversas |
| 6 | 5 | `test_06_gemini.py` | UC-026 a UC-030: Gemini AI |
| 7 | 3 | `test_07_escalation.py` | UC-031 a UC-033: Escalação |
| 8 | 2 | `test_08_tags.py` | UC-034 a UC-035: Tags |
| 9 | 3 | `test_09_metrics.py` | UC-036 a UC-038: Métricas |
| 10 | 2 | `test_10_queues.py` | UC-039 a UC-040: Filas |

**Total: 40 testes automatizados**

## 🚀 Executar Testes

### Todos os testes

```bash
# Via script (Windows)
./run-api-tests.bat all

# Via script (Linux/Mac)
./run-api-tests.sh all

# Via uv direto
uv run pytest tests/api/ -v
```

### Fase específica

```bash
# Autenticação
uv run pytest tests/api/test_01_auth.py -v

# WAHA
uv run pytest tests/api/test_02_waha.py -v

# Playbooks
uv run pytest tests/api/test_03_playbooks.py -v

# ... e assim por diante
```

### Scripts auxiliares

```bash
# Coletar testes (sem rodar)
uv run pytest tests/api/ --collect-only -q

# Com output resumido
uv run pytest tests/api/ -q

# Com traceback completo
uv run pytest tests/api/ -v --tb=long

# Parar no primeiro erro
uv run pytest tests/api/ -x

# Com logs (print statements)
uv run pytest tests/api/ -v -s
```

## 📁 Estrutura

```
tests/api/
├── __init__.py              # Package init
├── conftest.py              # Fixtures pytest
├── README.md                # Este arquivo
├── test_01_auth.py          # Phase 1
├── test_02_waha.py          # Phase 2
├── test_03_playbooks.py     # Phase 3
├── test_04_messages.py      # Phase 4
├── test_05_conversations.py # Phase 5
├── test_06_gemini.py        # Phase 6
├── test_07_escalation.py    # Phase 7
├── test_08_tags.py          # Phase 8
├── test_09_metrics.py       # Phase 9
└── test_10_queues.py        # Phase 10
```

## 🔧 Fixtures Disponíveis

- `api_base_url`: URL base da API (`http://localhost:3333/api/v1`)
- `admin_token`: Token de autenticação do admin
- `secretary_token`: Token de autenticação da secretária
- `auth_headers`: Headers com autenticação
- `api_client`: Cliente HTTP com autenticação automática

### Uso em testes

```python
def test_example(api_client, api_base_url, admin_token):
    # api_client: APIClient com headers de auth automáticos
    response = api_client.get("/conversations")
    
    # api_base_url: string com URL base
    import requests
    response = requests.get(f"{api_base_url}/health")
    
    # admin_token: token JWT do admin
    headers = {"Authorization": f"Bearer {admin_token}"}
```

## 📝 Referência Documentação

- Casos de teste: [back/docs/academic/casos-teste-validacao.md](../../docs/academic/casos-teste-validacao.md)
- API docs: `http://localhost:3333/docs` (quando API está rodando)
- Pytest docs: https://docs.pytest.org/

## ⚙️ Requisitos

- Python 3.12+
- uv (gerenciador de pacotes)
- API rodando em `http://localhost:3333`

Dependências já estão no `pyproject.toml`:
- pytest
- requests
- pytest-asyncio (para testes async se necessário)

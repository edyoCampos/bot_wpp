# Backlog de Desenvolvimento - Bot WhatsApp Clínica

> **Projeto:** Sistema de atendimento automatizado com IA para clínica  
> **Stack:** FastAPI + PostgreSQL + Redis + Gemini AI + WAHA + LangChain + ChromaDB  
> **Priorização:** Por dependência técnica e valor de negócio

---

## 📊 Status Atual do Projeto

### ✅ Implementado

- Estrutura base FastAPI com Clean Architecture
- Sistema de autenticação JWT (signup, login, refresh, logout)
- Tabelas: users, revoked_tokens, alerts, messages, message_media, message_location
- CRUD completo de mensagens (texto, mídia, localização)
- Migrations Alembic
- Docker Compose (api, db, adminer, waha)
- Logging e tratamento de exceções

### 🔄 Em Desenvolvimento

- Nenhum card em andamento

### ⏳ Backlog Priorizado

167 cards divididos em 8 épicos

---

## 🔐 Autenticação e Permissões

**Importante:** Todas as APIs REST (exceto webhooks do WAHA) devem ser protegidas com autenticação JWT.

### Roles e Permissões:

- **ADMIN:** Acesso total a todas as APIs e dados de todos os usuários
- **USER (Secretária):** Acesso apenas aos próprios dados (conversas, leads, métricas)

### Implementação:

- Use o decorator `@require_auth` em todos os endpoints protegidos
- Use `@require_role(Role.ADMIN)` para endpoints exclusivos de admin
- Extraia `user_id` do token JWT para filtrar dados por usuário
- Endpoints de métricas e dashboard devem respeitar o role do usuário autenticado

### Gerenciador de Pacotes:

- **UV:** Este projeto usa `uv` como gerenciador de pacotes Python
- Adicionar dependências: `uv add <package>`
- Adicionar dev dependencies: `uv add --dev <package>`
- Sincronizar ambiente: `uv sync`
- **NÃO USE:** `pip install` ou `poetry add`

---

## 🎯 Épicos e Priorização

### **ÉPICO 1: Infraestrutura Base** (Cards 1-15)

Configuração de serviços essenciais para suportar o sistema.

### **ÉPICO 2: Integração WAHA** (Cards 16-35)

Client WhatsApp, gerenciamento de sessões e webhooks.

### **ÉPICO 3: Sistema de Filas** (Cards 36-45)

Redis Queue para processamento assíncrono.

### **ÉPICO 4: Banco de Dados Core** (Cards 46-75)

Tabelas para conversas, leads, sessões, interações LLM.

### **ÉPICO 5: Integração Gemini AI** (Cards 76-95)

LangChain, ChromaDB, orquestração de conversas.

### **ÉPICO 6: Lógica de Negócio** (Cards 96-125)

Detecção de intenção, maturidade de leads, transferência.

### **ÉPICO 7: Dashboard e Métricas** (Cards 126-155)

Endpoints REST, KPIs, visualizações por role.

### **ÉPICO 8: Melhorias e Testes** (Cards 156-167)

Testes, documentação, otimizações.

---

# ÉPICO 1: INFRAESTRUTURA BASE

## Card 001: Adicionar dependências Redis ao projeto

**Labels:** `infra`, `redis`, `backend`

**Descrição:**  
Instalar bibliotecas Python para integração com Redis (cache e fila).

**Checklist Desenvolvimento:**

- [ ] Adicionar `redis` com `uv add redis`
- [ ] Adicionar `redis-om` com `uv add redis-om`
- [ ] Adicionar `rq` com `uv add rq`
- [ ] Sincronizar dependências com `uv sync`
- [ ] Verificar compatibilidade com Python 3.11

**Checklist Validação:**

- [ ] `uv pip list | grep redis` exibe versões instaladas
- [ ] Importação `import redis` funciona sem erros
- [ ] Importação `from rq import Queue` funciona

---

## Card 002: Adicionar dependências LangChain e ChromaDB

**Labels:** `infra`, `ai`, `backend`

**Descrição:**  
Instalar bibliotecas para orquestração LLM e armazenamento vetorial.

**Checklist Desenvolvimento:**

- [ ] Adicionar `langchain` com `uv add langchain`
- [ ] Adicionar `langchain-google-genai` com `uv add langchain-google-genai`
- [ ] Adicionar `chromadb` com `uv add chromadb`
- [ ] Adicionar `tiktoken` com `uv add tiktoken`
- [ ] Sincronizar com `uv sync`

**Checklist Validação:**

- [ ] `import langchain` funciona
- [ ] `import chromadb` funciona
- [ ] `from langchain_google_genai import ChatGoogleGenerativeAI` funciona

---

## Card 003: Adicionar dependências Google Generative AI

**Labels:** `infra`, `ai`, `backend`

**Descrição:**  
Instalar SDK oficial do Google para Gemini API.

**Checklist Desenvolvimento:**

- [ ] Adicionar `google-generativeai` com `uv add google-generativeai`
- [ ] Sincronizar com `uv sync`
- [ ] Criar `.env.example` com `GOOGLE_API_KEY=your-key-here`

**Checklist Validação:**

- [ ] `import google.generativeai as genai` funciona
- [ ] Conexão com API pode ser testada com key válida

---

## Card 004: Configurar Redis no Docker Compose

**Labels:** `infra`, `redis`, `docker`

**Descrição:**  
Adicionar serviço Redis ao `docker-compose.yml` para cache e filas.

**Checklist Desenvolvimento:**

- [ ] Adicionar serviço `redis` no `docker/docker-compose.yml`
- [ ] Usar imagem `redis:7-alpine`
- [ ] Expor porta `127.0.0.1:6379:6379`
- [ ] Configurar volume `redis_data:/data`
- [ ] Adicionar healthcheck `redis-cli ping`
- [ ] Configurar restart policy `unless-stopped`

**Checklist Validação:**

- [ ] `docker compose up -d` inicia Redis sem erros
- [ ] `docker exec docker-redis-1 redis-cli ping` retorna `PONG`
- [ ] Container permanece healthy após 30s

---

## Card 005: Adicionar configurações Redis ao settings.py

**Labels:** `backend`, `config`, `redis`

**Descrição:**  
Estender `Settings` com variáveis de ambiente para Redis.

**Checklist Desenvolvimento:**

- [ ] Adicionar `REDIS_URL: str` com default `redis://redis:6379/0`
- [ ] Adicionar `REDIS_CACHE_TTL: int` com default `3600`
- [ ] Adicionar `REDIS_MAX_CONNECTIONS: int` com default `10`
- [ ] Documentar no `.env.example`

**Checklist Validação:**

- [ ] `settings.REDIS_URL` retorna string válida
- [ ] Conexão com Redis usando URL funciona
- [ ] Variáveis podem ser sobrescritas via `.env`

---

## Card 006: Adicionar configurações Gemini AI ao settings.py

**Labels:** `backend`, `config`, `ai`

**Descrição:**  
Adicionar variáveis para integração com Google Gemini.

**Checklist Desenvolvimento:**

- [ ] Adicionar `GOOGLE_API_KEY: str` (obrigatório)
- [ ] Adicionar `GEMINI_MODEL: str` com default `gemini-1.5-flash`
- [ ] Adicionar `GEMINI_MAX_TOKENS: int` com default `2048`
- [ ] Adicionar `GEMINI_TEMPERATURE: float` com default `0.7`
- [ ] Documentar no `.env.example`

**Checklist Validação:**

- [ ] `settings.GOOGLE_API_KEY` exige valor (validation error se vazio)
- [ ] Valores podem ser customizados via `.env`

---

## Card 007: Adicionar configurações WAHA ao settings.py

**Labels:** `backend`, `config`, `waha`

**Descrição:**  
Configurar URL e credenciais do serviço WAHA.

**Checklist Desenvolvimento:**

- [ ] Adicionar `WAHA_URL: str` com default `http://waha:3000`
- [ ] Adicionar `WAHA_API_KEY: str | None` com default `None`
- [ ] Adicionar `WAHA_SESSION_NAME: str` com default `default`
- [ ] Adicionar `WAHA_WEBHOOK_URL: str` (URL do nosso webhook)
- [ ] Documentar no `.env.example`

**Checklist Validação:**

- [ ] `settings.WAHA_URL` retorna URL válida
- [ ] Pode conectar com WAHA usando configurações

---

## Card 008: Adicionar configurações ChromaDB ao settings.py

**Labels:** `backend`, `config`, `ai`

**Descrição:**  
Configurar path de persistência do ChromaDB.

**Checklist Desenvolvimento:**

- [ ] Adicionar `CHROMA_PERSIST_DIR: str` com default `./data/chroma`
- [ ] Adicionar `CHROMA_COLLECTION_NAME: str` com default `conversations`
- [ ] Documentar no `.env.example`

**Checklist Validação:**

- [ ] Path pode ser criado automaticamente
- [ ] ChromaDB pode inicializar com configurações

---

## Card 009: Criar enum ConversationStatus

**Labels:** `backend`, `domain`, `enum`

**Descrição:**  
Enum para status de conversas no sistema.

**Checklist Desenvolvimento:**

- [ ] Adicionar ao `src/robbot/domain/enums.py`
- [ ] Valores: `ACTIVE`, `WAITING_SECRETARY`, `TRANSFERRED`, `CLOSED`
- [ ] Herdar de `str, Enum`

**Checklist Validação:**

- [ ] Enum pode ser importado em outros módulos
- [ ] Valores são strings válidas
- [ ] Pode ser usado em SQLAlchemy models

---

## Card 010: Criar enum LeadStatus

**Labels:** `backend`, `domain`, `enum`

**Descrição:**  
Enum para status de leads (maturidade).

**Checklist Desenvolvimento:**

- [ ] Adicionar ao `src/robbot/domain/enums.py`
- [ ] Valores: `NEW`, `ENGAGED`, `INTERESTED`, `READY`, `SCHEDULED`, `LOST`
- [ ] Herdar de `str, Enum`

**Checklist Validação:**

- [ ] Enum pode ser importado
- [ ] Representa jornada do lead corretamente

---

## Card 011: Criar enum MessageDirection

**Labels:** `backend`, `domain`, `enum`

**Descrição:**  
Enum para direção de mensagens (entrada/saída).

**Checklist Desenvolvimento:**

- [ ] Adicionar ao `src/robbot/domain/enums.py`
- [ ] Valores: `INBOUND`, `OUTBOUND`
- [ ] Herdar de `str, Enum`

**Checklist Validação:**

- [ ] Usado para identificar origem da mensagem

---

## Card 012: Criar enum SessionStatus

**Labels:** `backend`, `domain`, `enum`

**Descrição:**  
Enum para status de sessões WAHA.

**Checklist Desenvolvimento:**

- [ ] Adicionar ao `src/robbot/domain/enums.py`
- [ ] Valores: `STOPPED`, `STARTING`, `SCAN_QR_CODE`, `WORKING`, `FAILED`
- [ ] Herdar de `str, Enum`

**Checklist Validação:**

- [ ] Representa estados do WAHA corretamente

---

## Card 013: Criar enum LLMProvider

**Labels:** `backend`, `domain`, `enum`

**Descrição:**  
Enum para provedores de LLM (futuro: suportar múltiplos).

**Checklist Desenvolvimento:**

- [ ] Adicionar ao `src/robbot/domain/enums.py`
- [ ] Valores: `GEMINI`, `OPENAI`, `ANTHROPIC`
- [ ] Herdar de `str, Enum`

**Checklist Validação:**

- [ ] Permite extensão futura

---

## Card 014: Criar health check para Redis

**Labels:** `backend`, `health`, `redis`

**Descrição:**  
Adicionar verificação de Redis ao endpoint `/health`.

**Checklist Desenvolvimento:**

- [ ] Modificar `src/robbot/services/health_service.py`
- [ ] Adicionar método `check_redis_connection()`
- [ ] Tentar `redis.ping()` com timeout de 2s
- [ ] Incluir no response do endpoint `/api/v1/health`

**Checklist Validação:**

- [ ] GET `/api/v1/health` retorna `redis: {"ok": true}` quando conectado
- [ ] Retorna `redis: {"ok": false, "error": "..."}` quando desconectado
- [ ] Status 200 se DB OK, 503 se Redis ou DB falhar

---

## Card 015: Criar factory para conexão Redis

**Labels:** `backend`, `infra`, `redis`

**Descrição:**  
Singleton para gerenciar pool de conexões Redis.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/infra/redis/client.py`
- [ ] Implementar `get_redis_client()` com pool
- [ ] Usar `redis.ConnectionPool` com `max_connections` do settings
- [ ] Implementar `close_redis_client()` para cleanup

**Checklist Validação:**

- [ ] Cliente pode ser importado: `from robbot.infra.redis.client import get_redis_client`
- [ ] Pool é reutilizado entre chamadas
- [ ] Conexões são liberadas corretamente

---

# ÉPICO 2: INTEGRAÇÃO WAHA

## Card 016: Criar client HTTP para WAHA

**Labels:** `backend`, `waha`, `integration`

**Descrição:**  
Classe cliente para consumir API REST do WAHA.

**Payload:** N/A (client interno)  
**Response:** N/A (métodos retornam objetos Python)

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/adapters/external/waha_client.py`
- [ ] Classe `WAHAClient` com `__init__(base_url, api_key)`
- [ ] Usar `httpx.AsyncClient` para requests HTTP
- [ ] Implementar método `_request(method, endpoint, **kwargs)`
- [ ] Adicionar tratamento de erros e timeout padrão 30s
- [ ] Adicionar logging de requisições

**Checklist Validação:**

- [ ] Cliente pode ser instanciado com settings
- [ ] Timeout funciona corretamente
- [ ] Erros HTTP são capturados e re-raised como exceções customizadas

---

## Card 017: Implementar WAHAClient.create_session()

**Labels:** `backend`, `waha`, `session`

**Descrição:**  
Método para criar nova sessão WhatsApp no WAHA.

**Payload:**

```json
{
	"name": "default",
	"config": {
		"webhooks": [
			{
				"url": "http://api:3333/api/v1/webhooks/waha",
				"events": ["message"]
			}
		]
	}
}
```

**Response:** `201 Created` - Session object

**Checklist Desenvolvimento:**

- [ ] Método `async def create_session(name: str, webhook_url: str)`
- [ ] POST para `/api/sessions`
- [ ] Retornar dict com session data
- [ ] Validar response status 201

**Checklist Validação:**

- [ ] Sessão é criada no WAHA
- [ ] Webhook é registrado corretamente
- [ ] Exceção é lançada se sessão já existe

---

## Card 018: Implementar WAHAClient.start_session()

**Labels:** `backend`, `waha`, `session`

**Descrição:**  
Iniciar sessão WhatsApp (gera QR code).

**Payload:** N/A (POST vazio)  
**Response:** `200 OK`

**Checklist Desenvolvimento:**

- [ ] Método `async def start_session(name: str)`
- [ ] POST para `/api/sessions/{name}/start`
- [ ] Retornar True se sucesso

**Checklist Validação:**

- [ ] Sessão muda status para `STARTING`
- [ ] QR code fica disponível via endpoint

---

## Card 019: Implementar WAHAClient.stop_session()

**Labels:** `backend`, `waha`, `session`

**Descrição:**  
Parar sessão WhatsApp.

**Payload:** N/A  
**Response:** `200 OK`

**Checklist Desenvolvimento:**

- [ ] Método `async def stop_session(name: str)`
- [ ] POST para `/api/sessions/{name}/stop`
- [ ] Retornar True se sucesso

**Checklist Validação:**

- [ ] Sessão muda status para `STOPPED`
- [ ] Conexão WhatsApp é encerrada

---

## Card 020: Implementar WAHAClient.restart_session()

**Labels:** `backend`, `waha`, `session`

**Descrição:**  
Reiniciar sessão (útil em caso de falhas).

**Payload:** N/A  
**Response:** `200 OK`

**Checklist Desenvolvimento:**

- [ ] Método `async def restart_session(name: str)`
- [ ] POST para `/api/sessions/{name}/restart`
- [ ] Retornar True se sucesso

**Checklist Validação:**

- [ ] Sessão é parada e reiniciada
- [ ] Status volta para `STARTING` → `WORKING`

---

## Card 021: Implementar WAHAClient.get_session_status()

**Labels:** `backend`, `waha`, `session`

**Descrição:**  
Obter status atual da sessão.

**Payload:** N/A  
**Response:** `200 OK` - Session status object

**Checklist Desenvolvimento:**

- [ ] Método `async def get_session_status(name: str)`
- [ ] GET para `/api/sessions/{name}`
- [ ] Retornar dict com `status`, `qr`, etc.

**Checklist Validação:**

- [ ] Retorna status atualizado
- [ ] Campo `qr` contém imagem base64 quando em `SCAN_QR_CODE`

---

## Card 022: Implementar WAHAClient.get_qr_code()

**Labels:** `backend`, `waha`, `session`

**Descrição:**  
Obter QR code para autenticação.

**Payload:** N/A  
**Response:** `200 OK` - QR code image (base64)

**Checklist Desenvolvimento:**

- [ ] Método `async def get_qr_code(name: str)`
- [ ] GET para `/api/sessions/{name}/qr`
- [ ] Retornar string base64 da imagem

**Checklist Validação:**

- [ ] QR code é válido e pode ser escaneado
- [ ] Retorna None se sessão já autenticada

---

## Card 023: Implementar WAHAClient.send_text_message()

**Labels:** `backend`, `waha`, `message`

**Descrição:**  
Enviar mensagem de texto para contato.

**Payload:**

```json
{
	"chatId": "5511999999999@c.us",
	"text": "Olá! Como posso ajudar?"
}
```

**Response:** `200 OK` - Message ID

**Checklist Desenvolvimento:**

- [ ] Método `async def send_text_message(session: str, chat_id: str, text: str)`
- [ ] POST para `/api/{session}/sendText`
- [ ] Retornar message_id da resposta

**Checklist Validação:**

- [ ] Mensagem é enviada e aparece no WhatsApp
- [ ] Message ID pode ser usado para tracking

---

## Card 024: Implementar WAHAClient.send_image()

**Labels:** `backend`, `waha`, `message`

**Descrição:**  
Enviar imagem com legenda opcional.

**Payload:**

```json
{
	"chatId": "5511999999999@c.us",
	"file": {
		"url": "https://example.com/image.jpg",
		"mimetype": "image/jpeg",
		"filename": "image.jpg"
	},
	"caption": "Veja esta imagem"
}
```

**Response:** `200 OK` - Message ID

**Checklist Desenvolvimento:**

- [ ] Método `async def send_image(session, chat_id, image_url, caption, mimetype, filename)`
- [ ] POST para `/api/{session}/sendImage`
- [ ] Retornar message_id

**Checklist Validação:**

- [ ] Imagem é enviada corretamente
- [ ] Caption aparece abaixo da imagem

---

## Card 025: Implementar WAHAClient.send_audio()

**Labels:** `backend`, `waha`, `message`

**Descrição:**  
Enviar arquivo de áudio.

**Payload:**

```json
{
	"chatId": "5511999999999@c.us",
	"file": {
		"url": "https://example.com/audio.mp3",
		"mimetype": "audio/mpeg",
		"filename": "audio.mp3"
	}
}
```

**Response:** `200 OK` - Message ID

**Checklist Desenvolvimento:**

- [ ] Método `async def send_audio(session, chat_id, audio_url, mimetype, filename)`
- [ ] POST para `/api/{session}/sendAudio`

**Checklist Validação:**

- [ ] Áudio é enviado e pode ser reproduzido no WhatsApp

---

## Card 026: Implementar WAHAClient.send_video()

**Labels:** `backend`, `waha`, `message`

**Descrição:**  
Enviar arquivo de vídeo.

**Payload:**

```json
{
	"chatId": "5511999999999@c.us",
	"file": {
		"url": "https://example.com/video.mp4",
		"mimetype": "video/mp4",
		"filename": "video.mp4"
	},
	"caption": "Assista este vídeo"
}
```

**Response:** `200 OK` - Message ID

**Checklist Desenvolvimento:**

- [ ] Método `async def send_video(session, chat_id, video_url, caption, mimetype, filename)`
- [ ] POST para `/api/{session}/sendVideo`

**Checklist Validação:**

- [ ] Vídeo é enviado e reproduz no WhatsApp

---

## Card 027: Implementar WAHAClient.send_document()

**Labels:** `backend`, `waha`, `message`

**Descrição:**  
Enviar documento/arquivo genérico.

**Payload:**

```json
{
	"chatId": "5511999999999@c.us",
	"file": {
		"url": "https://example.com/doc.pdf",
		"mimetype": "application/pdf",
		"filename": "documento.pdf"
	}
}
```

**Response:** `200 OK` - Message ID

**Checklist Desenvolvimento:**

- [ ] Método `async def send_document(session, chat_id, file_url, mimetype, filename)`
- [ ] POST para `/api/{session}/sendFile`

**Checklist Validação:**

- [ ] Documento é enviado e pode ser baixado

---

## Card 028: Implementar WAHAClient.send_location()

**Labels:** `backend`, `waha`, `message`

**Descrição:**  
Enviar localização geográfica.

**Payload:**

```json
{
	"chatId": "5511999999999@c.us",
	"latitude": -23.55052,
	"longitude": -46.633308,
	"title": "Clínica Exemplo"
}
```

**Response:** `200 OK` - Message ID

**Checklist Desenvolvimento:**

- [ ] Método `async def send_location(session, chat_id, lat, lon, title)`
- [ ] POST para `/api/{session}/sendLocation`

**Checklist Validação:**

- [ ] Localização aparece como pin no WhatsApp
- [ ] Título é exibido corretamente

---

## Card 029: Implementar WAHAClient.download_media()

**Labels:** `backend`, `waha`, `message`

**Descrição:**  
Baixar mídia recebida em mensagem.

**Payload:**

```json
{
	"mediaId": "true_5511999999999@c.us_3EB0XXXXX"
}
```

**Response:** `200 OK` - Binary file

**Checklist Desenvolvimento:**

- [ ] Método `async def download_media(session, media_id)`
- [ ] GET para `/api/{session}/messages/{media_id}/media`
- [ ] Retornar bytes do arquivo

**Checklist Validação:**

- [ ] Arquivo é baixado corretamente
- [ ] MIME type é preservado

---

## Card 030: Criar schema WAHAWebhookPayload

**Labels:** `backend`, `schema`, `waha`

**Descrição:**  
Pydantic schema para validar webhooks do WAHA.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/schemas/waha.py`
- [ ] Classe `WAHAMessage` com campos: `id`, `from`, `body`, `hasMedia`, `mediaUrl`
- [ ] Classe `WAHAWebhookPayload` com `event`, `session`, `payload`

**Checklist Validação:**

- [ ] Schema valida webhook real do WAHA sem erros
- [ ] Campos opcionais funcionam corretamente

---

## Card 031: Criar endpoint POST /api/v1/webhooks/waha

**Labels:** `backend`, `webhook`, `waha`

**Descrição:**  
Endpoint para receber webhooks do WAHA.

**Payload:** `WAHAWebhookPayload` (varia por evento)  
**Response:** `200 OK` - `{"status": "received"}`

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/adapters/controllers/webhook_controller.py`
- [ ] Endpoint aceita POST **SEM autenticação JWT** (webhook externo do WAHA)
- [ ] Validar origem do webhook (verificar IP ou usar webhook secret se disponível)
- [ ] Validar payload com schema Pydantic
- [ ] Logar evento recebido
- [ ] Enfileirar mensagem no Redis para processamento

**Checklist Validação:**

- [ ] WAHA consegue enviar webhook com sucesso
- [ ] Payload inválido retorna 422
- [ ] Mensagem entra na fila Redis

---

## Card 032: Criar service WAHASessionService

**Labels:** `backend`, `service`, `waha`

**Descrição:**  
Orquestrar operações de sessão WAHA.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/services/waha_session_service.py`
- [ ] Classe `WAHASessionService` com dependency `WAHAClient`
- [ ] Métodos: `create_and_start()`, `restart_if_failed()`, `check_health()`
- [ ] Integrar com repository de sessões (Card 065)

**Checklist Validação:**

- [ ] Service pode criar e iniciar sessão end-to-end
- [ ] Detecta falhas e reinicia automaticamente

---

## Card 033: Criar repository WAHASessionRepository

**Labels:** `backend`, `repository`, `database`

**Descrição:**  
Persistir informações de sessões WAHA no PostgreSQL.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/adapters/repositories/waha_session_repository.py`
- [ ] Métodos: `create()`, `get_by_name()`, `update_status()`, `get_active()`
- [ ] Usar model `WAHASessionModel` (Card 065)

**Checklist Validação:**

- [ ] CRUD completo de sessões funciona
- [ ] Status é atualizado corretamente

---

## Card 034: Criar endpoint GET /api/v1/waha/sessions/{name}/qr

**Labels:** `backend`, `api`, `waha`

**Descrição:**  
Retornar QR code para autenticação da sessão.

**Payload:** N/A  
**Response:** `200 OK` - `{"qr": "data:image/png;base64,..."}`

**Checklist Desenvolvimento:**

- [ ] Endpoint em `webhook_controller.py` ou novo controller
- [ ] Chamar `WAHAClient.get_qr_code()`
- [ ] Retornar base64 image

**Checklist Validação:**

- [ ] QR code pode ser exibido em frontend
- [ ] Retorna 404 se sessão não existe
- [ ] Retorna 400 se sessão já autenticada

---

## Card 035: Criar endpoint POST /api/v1/waha/sessions/{name}/restart

**Labels:** `backend`, `api`, `waha`

**Descrição:**  
Permitir restart manual de sessão.

**Payload:** N/A  
**Response:** `200 OK` - `{"status": "restarting"}`

**Checklist Desenvolvimento:**

- [ ] Endpoint protegido (requer auth admin)
- [ ] Chamar `WAHASessionService.restart_if_failed()`
- [ ] Atualizar status no banco

**Checklist Validação:**

- [ ] Sessão é reiniciada com sucesso
- [ ] Apenas admin pode executar

---

# ÉPICO 3: SISTEMA DE FILAS

## Card 036: Criar RedisQueue client

**Labels:** `backend`, `redis`, `queue`

**Descrição:**  
Abstração para gerenciar filas Redis.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/infra/redis/queue.py`
- [ ] Classe `RedisQueue` usando `rq.Queue`
- [ ] Métodos: `enqueue()`, `get_job()`, `get_failed()`, `clear()`
- [ ] Configurar default queue `messages`

**Checklist Validação:**

- [ ] Jobs podem ser enfileirados
- [ ] Worker pode processar jobs
- [ ] Falhas são registradas

---

## Card 037: Criar worker para processar mensagens

**Labels:** `backend`, `redis`, `worker`

**Descrição:**  
Script worker RQ para processar fila de mensagens.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/workers/message_worker.py`
- [ ] Função `process_inbound_message(message_data)`
- [ ] Importar e executar lógica de conversação
- [ ] Configurar retry em caso de falha (3 tentativas)
- [ ] Adicionar logging detalhado

**Checklist Validação:**

- [ ] Worker pode ser iniciado: `rq worker messages`
- [ ] Processa mensagens da fila
- [ ] Retries funcionam corretamente

---

## Card 038: Criar Dockerfile para worker

**Labels:** `infra`, `docker`, `worker`

**Descrição:**  
Container separado para workers Redis.

**Checklist Desenvolvimento:**

- [ ] Criar `docker/Dockerfile.worker` (baseado no Dockerfile da API)
- [ ] CMD: `rq worker messages --url $REDIS_URL`
- [ ] Adicionar serviço `worker` no `docker-compose.yml`
- [ ] Configurar escalabilidade (replicas: 2)

**Checklist Validação:**

- [ ] Workers iniciam com `docker compose up -d`
- [ ] Múltiplos workers processam em paralelo
- [ ] Logs aparecem em `docker logs`

---

## Card 039: Criar função enqueue_message()

**Labels:** `backend`, `redis`, `helper`

**Descrição:**  
Helper para enfileirar mensagens facilmente.

**Checklist Desenvolvimento:**

- [ ] Criar em `src/robbot/common/utils.py`
- [ ] Função `async def enqueue_message(message_data: dict)`
- [ ] Usar `RedisQueue().enqueue('process_inbound_message', message_data)`
- [ ] Retornar job_id

**Checklist Validação:**

- [ ] Mensagem entra na fila
- [ ] Job ID é válido
- [ ] Pode ser usado no webhook controller

---

## Card 040: Modificar webhook para enfileirar mensagens

**Labels:** `backend`, `webhook`, `integration`

**Descrição:**  
Webhook não processa diretamente, apenas enfileira.

**Checklist Desenvolvimento:**

- [ ] Modificar `webhook_controller.py` endpoint
- [ ] Chamar `enqueue_message()` com payload
- [ ] Retornar imediatamente `202 Accepted`
- [ ] Não aguardar processamento

**Checklist Validação:**

- [ ] Webhook responde em < 100ms
- [ ] Mensagem é processada assincronamente
- [ ] Alta taxa de mensagens não trava sistema

---

## Card 041: Criar endpoint GET /api/v1/queue/stats

**Labels:** `backend`, `api`, `queue`

**Descrição:**  
Estatísticas da fila de mensagens.

**Payload:** N/A  
**Response:** `200 OK`

```json
{
	"pending": 5,
	"processing": 2,
	"failed": 1,
	"completed": 120
}
```

**Checklist Desenvolvimento:**

- [ ] Criar endpoint protegido (auth admin)
- [ ] Consultar Redis Queue stats
- [ ] Retornar contadores

**Checklist Validação:**

- [ ] Stats refletem estado real da fila
- [ ] Apenas admin acessa

---

## Card 042: Criar endpoint POST /api/v1/queue/retry-failed

**Labels:** `backend`, `api`, `queue`

**Descrição:**  
Reprocessar jobs que falharam.

**Payload:**

```json
{
	"job_ids": ["uuid1", "uuid2"]
}
```

**Response:** `200 OK` - `{"retried": 2}`

**Checklist Desenvolvimento:**

- [ ] Endpoint protegido (admin)
- [ ] Buscar jobs failed no Redis
- [ ] Re-enfileirar jobs
- [ ] Retornar contador

**Checklist Validação:**

- [ ] Jobs são reprocessados
- [ ] Apenas admin pode executar

---

## Card 043: Criar endpoint DELETE /api/v1/queue/clear-failed

**Labels:** `backend`, `api`, `queue`

**Descrição:**  
Limpar fila de jobs falhados.

**Payload:** N/A  
**Response:** `204 No Content`

**Checklist Desenvolvimento:**

- [ ] Endpoint protegido (admin)
- [ ] Chamar `RedisQueue().clear_failed()`

**Checklist Validação:**

- [ ] Fila failed é limpa
- [ ] Não afeta jobs em processamento

---

## Card 044: Implementar rate limiting no webhook

**Labels:** `backend`, `security`, `webhook`

**Descrição:**  
Proteger webhook contra spam.

**Checklist Desenvolvimento:**

- [ ] Usar Redis para contador de requests
- [ ] Limitar: 100 msgs/min por chatId
- [ ] Retornar `429 Too Many Requests` se exceder
- [ ] Adicionar header `X-RateLimit-Remaining`

**Checklist Validação:**

- [ ] Limite funciona corretamente
- [ ] Requests legítimos não são bloqueados
- [ ] Ataques são mitigados

---

## Card 045: Criar monitoramento de fila

**Labels:** `backend`, `monitoring`, `queue`

**Descrição:**  
Alertar quando fila cresce muito.

**Checklist Desenvolvimento:**

- [ ] Job periódico (a cada 5 min) verifica tamanho da fila
- [ ] Se > 100 mensagens pendentes, criar alerta
- [ ] Registrar em `alerts` table
- [ ] Notificar via log

**Checklist Validação:**

- [ ] Alerta é criado quando fila cresce
- [ ] Sistema se recupera automaticamente

---

# ÉPICO 4: BANCO DE DADOS CORE

> **⚠️ IMPORTANTE:** Todas as APIs REST de CRUD (Conversas, Leads, Sessões, etc) **REQUEREM autenticação JWT**.
>
> - Use `user_id` do token para filtrar dados
> - Admin pode acessar todos os dados
> - Secretária acessa apenas conversas/leads atribuídos a ela

## Card 046: Criar model ConversationModel

**Labels:** `backend`, `database`, `model`

**Descrição:**  
Tabela para armazenar conversas completas.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/infra/db/models/conversation_model.py`
- [ ] Campos: `id` (UUID), `chat_id` (str, unique), `phone_number` (str)
- [ ] `name` (str, nullable), `status` (enum), `lead_id` (FK nullable)
- [ ] `created_at`, `updated_at`, `last_message_at`
- [ ] Relationship: `messages` (one-to-many)

**Checklist Validação:**

- [ ] Model pode ser importado
- [ ] Migrations podem ser geradas

---

## Card 047: Criar migration para conversations

**Labels:** `backend`, `database`, `migration`

**Descrição:**  
Alembic migration para tabela conversations.

**Checklist Desenvolvimento:**

- [ ] Executar `alembic revision -m "add conversations table"`
- [ ] Adicionar enum `conversation_status`
- [ ] Criar tabela `conversations`
- [ ] Criar índices: `chat_id`, `status`, `last_message_at`

**Checklist Validação:**

- [ ] `alembic upgrade head` executa sem erros
- [ ] Tabela aparece em `\dt` no PostgreSQL
- [ ] Índices foram criados

---

## Card 048: Criar model ConversationMessageModel

**Labels:** `backend`, `database`, `model`

**Descrição:**  
Tabela para mensagens de conversação (diferente de `messages` que é script).

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/infra/db/models/conversation_message_model.py`
- [ ] Campos: `id` (UUID), `conversation_id` (FK), `direction` (enum)
- [ ] `from_phone`, `to_phone`, `body` (text), `media_url` (nullable)
- [ ] `waha_message_id` (str, unique, nullable)
- [ ] `created_at`
- [ ] Relationship: `conversation` (many-to-one)

**Checklist Validação:**

- [ ] FK constraint funciona
- [ ] Cascade delete: apagar conversation apaga mensagens

---

## Card 049: Criar migration para conversation_messages

**Labels:** `backend`, `database`, `migration`

**Descrição:**  
Migration para tabela conversation_messages.

**Checklist Desenvolvimento:**

- [ ] `alembic revision -m "add conversation_messages table"`
- [ ] Criar enum `message_direction`
- [ ] Criar tabela com FK para `conversations(id)` ON DELETE CASCADE
- [ ] Índices: `conversation_id`, `created_at`, `waha_message_id`

**Checklist Validação:**

- [ ] Migration executa
- [ ] CASCADE funciona
- [ ] Queries rápidas por conversation_id

---

## Card 050: Criar model LeadModel

**Labels:** `backend`, `database`, `model`

**Descrição:**  
Tabela para leads (prospects prontos para agendamento).

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/infra/db/models/lead_model.py`
- [ ] Campos: `id` (UUID), `conversation_id` (FK unique)
- [ ] `name` (str), `phone_number` (str), `email` (nullable)
- [ ] `status` (enum LeadStatus), `maturity_score` (int, 0-100)
- [ ] `notes` (text, nullable), `assigned_to_user_id` (FK nullable)
- [ ] `created_at`, `updated_at`, `converted_at` (nullable)
- [ ] Relationships: `conversation`, `assigned_to`

**Checklist Validação:**

- [ ] FK constraints funcionam
- [ ] Score range é validado (0-100)

---

## Card 051: Criar migration para leads

**Labels:** `backend`, `database`, `migration`

**Descrição:**  
Migration para tabela leads.

**Checklist Desenvolvimento:**

- [ ] `alembic revision -m "add leads table"`
- [ ] Criar enum `lead_status`
- [ ] Criar tabela com FKs para `conversations` e `users`
- [ ] Índices: `status`, `assigned_to_user_id`, `created_at`
- [ ] CHECK constraint: `maturity_score BETWEEN 0 AND 100`

**Checklist Validação:**

- [ ] Migration executa
- [ ] Score inválido é rejeitado
- [ ] Queries por status são rápidas

---

## Card 052: Criar model LeadInteractionModel

**Labels:** `backend`, `database`, `model`

**Descrição:**  
Registro de interações da secretária com lead.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/infra/db/models/lead_interaction_model.py`
- [ ] Campos: `id` (UUID), `lead_id` (FK), `user_id` (FK)
- [ ] `interaction_type` (enum: NOTE, STATUS_CHANGE, CALL, EMAIL)
- [ ] `notes` (text), `created_at`

**Checklist Validação:**

- [ ] Histórico de interações pode ser consultado

---

## Card 053: Criar migration para lead_interactions

**Labels:** `backend`, `database`, `migration`

**Descrição:**  
Migration para lead_interactions.

**Checklist Desenvolvimento:**

- [ ] `alembic revision -m "add lead_interactions table"`
- [ ] Criar enum `interaction_type`
- [ ] Criar tabela com FKs para `leads` e `users`
- [ ] Índice: `lead_id`, `created_at`

**Checklist Validação:**

- [ ] Migration executa
- [ ] Auditoria de ações funciona

---

## Card 054: Criar model WAHASessionModel

**Labels:** `backend`, `database`, `model`

**Descrição:**  
Persistir sessões WAHA.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/infra/db/models/waha_session_model.py`
- [ ] Campos: `id` (UUID), `name` (str, unique), `status` (enum)
- [ ] `qr_code` (text, nullable), `phone_number` (str, nullable)
- [ ] `webhook_url` (str), `last_ping_at` (timestamp nullable)
- [ ] `created_at`, `updated_at`

**Checklist Validação:**

- [ ] Sessões podem ser persistidas
- [ ] Status é atualizado corretamente

---

## Card 055: Criar migration para waha_sessions

**Labels:** `backend`, `database`, `migration`

**Descrição:**  
Migration para waha_sessions.

**Checklist Desenvolvimento:**

- [ ] `alembic revision -m "add waha_sessions table"`
- [ ] Criar enum `session_status`
- [ ] Criar tabela com unique constraint em `name`
- [ ] Índices: `status`, `phone_number`

**Checklist Validação:**

- [ ] Migration executa
- [ ] Unique constraint funciona

---

## Card 056: Criar model LLMInteractionModel

**Labels:** `backend`, `database`, `model`

**Descrição:**  
Log de interações com LLM para auditoria.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/infra/db/models/llm_interaction_model.py`
- [ ] Campos: `id` (UUID), `conversation_id` (FK)
- [ ] `provider` (enum LLMProvider), `model_name` (str)
- [ ] `prompt_tokens` (int), `completion_tokens` (int), `total_tokens` (int)
- [ ] `prompt` (text), `response` (text), `latency_ms` (int)
- [ ] `created_at`

**Checklist Validação:**

- [ ] Logs são criados automaticamente
- [ ] Queries por conversation são rápidas

---

## Card 057: Criar migration para llm_interactions

**Labels:** `backend`, `database`, `migration`

**Descrição:**  
Migration para llm_interactions.

**Checklist Desenvolvimento:**

- [ ] `alembic revision -m "add llm_interactions table"`
- [ ] Criar tabela com FK para `conversations`
- [ ] Índices: `conversation_id`, `created_at`

**Checklist Validação:**

- [ ] Migration executa
- [ ] Auditoria de LLM funciona

---

## Card 058: Criar model ConversationContextModel

**Labels:** `backend`, `database`, `model`

**Descrição:**  
Armazenar contexto estruturado da conversa (extraído pelo LLM).

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/infra/db/models/conversation_context_model.py`
- [ ] Campos: `id` (UUID), `conversation_id` (FK unique)
- [ ] `patient_name` (str, nullable), `symptoms` (JSONB)
- [ ] `concerns` (JSONB), `preferences` (JSONB)
- [ ] `intent_detected` (bool), `intent_type` (str, nullable)
- [ ] `updated_at`

**Checklist Validação:**

- [ ] JSONB permite queries flexíveis
- [ ] Contexto é atualizado conforme conversa evolui

---

## Card 059: Criar migration para conversation_contexts

**Labels:** `backend`, `database`, `migration`

**Descrição:**  
Migration para conversation_contexts.

**Checklist Desenvolvimento:**

- [ ] `alembic revision -m "add conversation_contexts table"`
- [ ] Criar tabela com unique FK para `conversations`
- [ ] Índice: `intent_detected`

**Checklist Validação:**

- [ ] Migration executa
- [ ] JSONB funciona corretamente

---

## Card 060: Criar repository ConversationRepository

**Labels:** `backend`, `repository`, `database`

**Descrição:**  
CRUD para conversas.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/adapters/repositories/conversation_repository.py`
- [ ] Métodos: `create()`, `get_by_chat_id()`, `get_by_id()`
- [ ] `update_status()`, `update_last_message_at()`, `get_active()`
- [ ] Eager load relationships quando necessário

**Checklist Validação:**

- [ ] CRUD completo funciona
- [ ] Queries são otimizadas

---

## Card 061: Criar repository ConversationMessageRepository

**Labels:** `backend`, `repository`, `database`

**Descrição:**  
CRUD para mensagens de conversa.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/adapters/repositories/conversation_message_repository.py`
- [ ] Métodos: `create()`, `get_by_conversation()`
- [ ] `get_last_n_messages()`, `count_by_conversation()`

**Checklist Validação:**

- [ ] Mensagens podem ser salvas e recuperadas
- [ ] Histórico completo acessível

---

## Card 062: Criar repository LeadRepository

**Labels:** `backend`, `repository`, `database`

**Descrição:**  
CRUD para leads.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/adapters/repositories/lead_repository.py`
- [ ] Métodos: `create()`, `get_by_id()`, `get_by_conversation_id()`
- [ ] `update_status()`, `update_maturity_score()`, `assign_to_user()`
- [ ] `get_unassigned()`, `get_by_status()`, `get_by_assigned_user()`

**Checklist Validação:**

- [ ] CRUD completo
- [ ] Queries por status são eficientes

---

## Card 063: Criar repository LLMInteractionRepository

**Labels:** `backend`, `repository`, `database`

**Descrição:**  
CRUD para logs LLM.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/adapters/repositories/llm_interaction_repository.py`
- [ ] Métodos: `create()`, `get_by_conversation()`
- [ ] `get_total_tokens_by_conversation()`, `get_total_cost()`

**Checklist Validação:**

- [ ] Logs são salvos automaticamente
- [ ] Custos podem ser calculados

---

## Card 064: Criar repository ConversationContextRepository

**Labels:** `backend`, `repository`, `database`

**Descrição:**  
CRUD para contexto de conversa.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/adapters/repositories/conversation_context_repository.py`
- [ ] Métodos: `create()`, `get_by_conversation()`, `update()`
- [ ] `mark_intent_detected()`, `update_patient_info()`

**Checklist Validação:**

- [ ] Contexto é atualizado incrementalmente
- [ ] JSONB queries funcionam

---

## Card 065: Criar repository WAHASessionRepository

**Labels:** `backend`, `repository`, `database`

**Descrição:**  
CRUD para sessões WAHA (já mencionado no Card 033).

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/adapters/repositories/waha_session_repository.py`
- [ ] Métodos: `create()`, `get_by_name()`, `update_status()`
- [ ] `update_qr_code()`, `update_phone_number()`, `get_active()`

**Checklist Validação:**

- [ ] Sessões podem ser gerenciadas
- [ ] Status é sincronizado com WAHA

---

## Card 066: Criar schemas de Conversation

**Labels:** `backend`, `schema`, `pydantic`

**Descrição:**  
Schemas Pydantic para API.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/schemas/conversation.py`
- [ ] Classes: `ConversationCreate`, `ConversationOut`, `ConversationUpdate`
- [ ] `ConversationWithMessages` (nested)
- [ ] Usar `ConfigDict(from_attributes=True)`

**Checklist Validação:**

- [ ] Schemas validam inputs corretamente
- [ ] ORM models convertidos para schemas

---

## Card 067: Criar schemas de Lead

**Labels:** `backend`, `schema`, `pydantic`

**Descrição:**  
Schemas para leads.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/schemas/lead.py`
- [ ] Classes: `LeadCreate`, `LeadOut`, `LeadUpdate`
- [ ] `LeadWithConversation`, `LeadListOut`

**Checklist Validação:**

- [ ] Validação de email opcional
- [ ] Score 0-100 é validado

---

## Card 068: Criar schemas de ConversationContext

**Labels:** `backend`, `schema`, `pydantic`

**Descrição:**  
Schemas para contexto de conversa.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/schemas/conversation_context.py`
- [ ] Classe `ConversationContextOut` com campos JSONB tipados
- [ ] `IntentDetection` nested model

**Checklist Validação:**

- [ ] JSONB é validado corretamente
- [ ] Schema reflete estrutura do contexto

---

## Card 069: Criar endpoint GET /api/v1/conversations

**Labels:** `backend`, `api`, `conversation`

**Descrição:**  
Listar conversas com filtros.

**Payload:** Query params: `status`, `limit`, `offset`  
**Response:** `200 OK`

```json
{
	"total": 50,
	"items": [
		{
			"id": "uuid",
			"chat_id": "5511999999999@c.us",
			"status": "active",
			"last_message_at": "2025-12-05T10:00:00Z"
		}
	]
}
```

**Checklist Desenvolvimento:**

- [ ] Criar endpoint em `conversation_controller.py`
- [ ] Proteger com auth (user/admin)
- [ ] Filtrar por status, ordenar por last_message_at DESC
- [ ] Paginação

**Checklist Validação:**

- [ ] User vê apenas suas conversas (se houver atribuição)
- [ ] Admin vê todas
- [ ] Paginação funciona

---

## Card 070: Criar endpoint GET /api/v1/conversations/{id}

**Labels:** `backend`, `api`, `conversation`

**Descrição:**  
Detalhes de uma conversa com histórico completo.

**Payload:** N/A  
**Response:** `200 OK` - `ConversationWithMessages`

**Checklist Desenvolvimento:**

- [ ] Retornar conversa + mensagens nested
- [ ] Eager load messages
- [ ] Proteger com auth

**Checklist Validação:**

- [ ] Histórico completo é retornado
- [ ] Performance OK mesmo com muitas mensagens

---

## Card 071: Criar endpoint PATCH /api/v1/conversations/{id}/status

**Labels:** `backend`, `api`, `conversation`

**Descrição:**  
Mudar status da conversa (ex: transferir para secretária).

**Payload:**

```json
{
	"status": "WAITING_SECRETARY",
	"reason": "Cliente solicitou agendamento"
}
```

**Response:** `200 OK` - `ConversationOut`

**Checklist Desenvolvimento:**

- [ ] Validar transição de status
- [ ] Registrar reason em log/auditoria
- [ ] Proteger com auth

**Checklist Validação:**

- [ ] Status é atualizado
- [ ] Notificação é enviada (futuramente)

---

## Card 072: Criar endpoint GET /api/v1/leads

**Labels:** `backend`, `api`, `lead`

**Descrição:**  
Listar leads com filtros.

**Payload:** Query: `status`, `assigned_to`, `limit`, `offset`  
**Response:** `200 OK` - Lista de `LeadListOut`

**Checklist Desenvolvimento:**

- [ ] Filtrar por status, assigned_to
- [ ] User vê apenas seus leads
- [ ] Admin vê todos
- [ ] Ordenar por created_at DESC

**Checklist Validação:**

- [ ] Filtros funcionam
- [ ] Paginação OK

---

## Card 073: Criar endpoint GET /api/v1/leads/{id}

**Labels:** `backend`, `api`, `lead`

**Descrição:**  
Detalhes do lead com conversa e interações.

**Payload:** N/A  
**Response:** `200 OK` - `LeadWithConversation`

**Checklist Desenvolvimento:**

- [ ] Eager load conversation + interactions
- [ ] Proteger com auth

**Checklist Validação:**

- [ ] Dados completos retornados

---

## Card 074: Criar endpoint PATCH /api/v1/leads/{id}

**Labels:** `backend`, `api`, `lead`

**Descrição:**  
Atualizar lead (status, notas, atribuição).

**Payload:**

```json
{
	"status": "SCHEDULED",
	"notes": "Agendado para 10/12",
	"assigned_to_user_id": "uuid"
}
```

**Response:** `200 OK` - `LeadOut`

**Checklist Desenvolvimento:**

- [ ] Validar campos
- [ ] Atualizar timestamps
- [ ] Registrar interação automaticamente

**Checklist Validação:**

- [ ] Lead é atualizado
- [ ] Histórico preservado

---

## Card 075: Criar endpoint POST /api/v1/leads/{id}/interactions

**Labels:** `backend`, `api`, `lead`

**Descrição:**  
Adicionar nota/interação ao lead.

**Payload:**

```json
{
	"interaction_type": "NOTE",
	"notes": "Cliente pediu ligar depois das 14h"
}
```

**Response:** `201 Created` - Interaction object

**Checklist Desenvolvimento:**

- [ ] Criar registro em lead_interactions
- [ ] Associar com user autenticado
- [ ] Proteger com auth

**Checklist Validação:**

- [ ] Interação é salva
- [ ] Aparece no histórico

---

# ÉPICO 5: INTEGRAÇÃO GEMINI AI

## Card 076: Criar client Gemini

**Labels:** `backend`, `ai`, `gemini`

**Descrição:**  
Cliente para Google Gemini API.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/adapters/external/gemini_client.py`
- [ ] Classe `GeminiClient` usando `google.generativeai`
- [ ] Método `generate_response(prompt, context)`
- [ ] Configurar model, temperature, max_tokens do settings
- [ ] Adicionar retry logic (3 tentativas)
- [ ] Logging de requests

**Checklist Validação:**

- [ ] Cliente conecta com API
- [ ] Respostas são geradas corretamente
- [ ] Erros são tratados

---

## Card 077: Criar ChromaDB client

**Labels:** `backend`, `ai`, `vectordb`

**Descrição:**  
Cliente para armazenamento vetorial.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/infra/vectordb/chroma_client.py`
- [ ] Classe `ChromaClient` usando `chromadb`
- [ ] Métodos: `add_conversation()`, `search_similar()`, `get_context()`
- [ ] Configurar persist_directory do settings

**Checklist Validação:**

- [ ] Conversas podem ser adicionadas
- [ ] Busca semântica funciona
- [ ] Persistência funciona entre restarts

---

## Card 078: Criar LangChain chain para conversação

**Labels:** `backend`, `ai`, `langchain`

**Descrição:**  
Orquestrar conversação com LangChain.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/services/langchain_conversation_service.py`
- [ ] Usar `ConversationChain` com memory
- [ ] Integrar `ChatGoogleGenerativeAI`
- [ ] Configurar `ConversationBufferMemory`

**Checklist Validação:**

- [ ] Histórico é mantido na memória
- [ ] Respostas são contextualizadas

---

## Card 079: Criar prompt template base

**Labels:** `backend`, `ai`, `prompt`

**Descrição:**  
Template de prompt para o LLM.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/ai/prompts/base_prompt.py`
- [ ] Definir system prompt com personalidade da clínica
- [ ] Instruções: ser empático, identificar intenções, usar linguagem natural
- [ ] Placeholder para contexto dinâmico

**Checklist Validação:**

- [ ] Prompt gera respostas consistentes
- [ ] Tom de voz adequado

---

## Card 080: Criar prompt template para detecção de intenção

**Labels:** `backend`, `ai`, `prompt`

**Descrição:**  
Prompt específico para detectar intenção de agendamento.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/ai/prompts/intent_detection_prompt.py`
- [ ] Pedir ao LLM analisar se há intenção clara
- [ ] Retornar JSON estruturado: `{"intent_detected": bool, "confidence": float, "intent_type": str}`

**Checklist Validação:**

- [ ] Intenções são detectadas corretamente
- [ ] False positives são raros

---

## Card 081: Criar prompt template para scoring de maturidade

**Labels:** `backend`, `ai`, `prompt`

**Descrição:**  
Prompt para calcular maturidade do lead.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/ai/prompts/maturity_scoring_prompt.py`
- [ ] Analisar: engajamento, clareza de interesse, objeções
- [ ] Retornar score 0-100
- [ ] Critérios claros no prompt

**Checklist Validação:**

- [ ] Score reflete realidade da conversa
- [ ] Pode ser usado para priorização

---

## Card 082: Criar service ConversationOrchestrator

**Labels:** `backend`, `service`, `ai`

**Descrição:**  
Orquestrar todo fluxo de conversação.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/services/conversation_orchestrator_service.py`
- [ ] Métodos: `process_inbound_message()`, `generate_response()`
- [ ] Integrar: ConversationRepository, ChromaDB, LangChain, Gemini
- [ ] Fluxo:
  1. Buscar ou criar conversation
  2. Salvar mensagem inbound
  3. Recuperar contexto (ChromaDB + últimas N msgs)
  4. Gerar resposta com LLM
  5. Detectar intenção
  6. Atualizar contexto
  7. Enviar resposta via WAHA
  8. Salvar mensagem outbound

**Checklist Validação:**

- [ ] Fluxo completo funciona end-to-end
- [ ] Contexto é preservado
- [ ] Respostas são enviadas

---

## Card 083: Integrar ChromaDB no fluxo

**Labels:** `backend`, `ai`, `integration`

**Descrição:**  
Adicionar conversas ao ChromaDB para retrieval.

**Checklist Desenvolvimento:**

- [ ] No `ConversationOrchestrator`, após salvar mensagem:
  - [ ] Adicionar ao ChromaDB com embedding
  - [ ] Usar chat_id como ID
- [ ] Ao gerar resposta:
  - [ ] Buscar conversas similares
  - [ ] Incluir no contexto do prompt

**Checklist Validação:**

- [ ] Embeddings são gerados
- [ ] Busca semântica retorna contexto relevante

---

## Card 084: Implementar detecção de intenção no orchestrator

**Labels:** `backend`, `ai`, `logic`

**Descrição:**  
Detectar intenção de agendamento automaticamente.

**Checklist Desenvolvimento:**

- [ ] Após gerar resposta, chamar LLM com prompt de detecção
- [ ] Se intenção detectada:
  - [ ] Atualizar `conversation_context.intent_detected = true`
  - [ ] Criar lead se não existe
  - [ ] Mudar status conversa para `WAITING_SECRETARY`
  - [ ] Notificar secretária (log por enquanto)

**Checklist Validação:**

- [ ] Intenção é detectada corretamente
- [ ] Lead é criado automaticamente
- [ ] Status muda

---

## Card 085: Implementar cálculo de maturidade

**Labels:** `backend`, `ai`, `logic`

**Descrição:**  
Calcular score de maturidade periodicamente.

**Checklist Desenvolvimento:**

- [ ] Após N mensagens (ex: 5), chamar LLM com prompt de scoring
- [ ] Atualizar `lead.maturity_score`
- [ ] Usar score para priorização

**Checklist Validação:**

- [ ] Score é atualizado conforme conversa evolui
- [ ] Leads com score alto são priorizados

---

## Card 086: Criar sistema de templates de resposta

**Labels:** `backend`, `message`, `template`

**Descrição:**  
Usar tabela `messages` existente como scripts multimídia.

**Checklist Desenvolvimento:**

- [ ] Criar service `MessageTemplateService`
- [ ] Métodos: `get_by_type()`, `get_random()`
- [ ] LLM pode referenciar templates: "usar template de boas-vindas"
- [ ] Expandir para suportar variáveis: `{{name}}`, `{{clinic_name}}`

**Checklist Validação:**

- [ ] Templates podem ser usados em respostas
- [ ] Variáveis são substituídas

---

## Card 087: Implementar envio de mensagens multimídia

**Labels:** `backend`, `waha`, `message`

**Descrição:**  
Orquestrar envio de texto, imagem, áudio, vídeo.

**Checklist Desenvolvimento:**

- [ ] Modificar `ConversationOrchestrator.send_response()`
- [ ] Detectar tipo de mídia no template
- [ ] Chamar método correto do WAHAClient (`send_text`, `send_image`, etc.)
- [ ] Salvar mensagem outbound com tipo correto

**Checklist Validação:**

- [ ] Mensagens multimídia são enviadas
- [ ] Tipos são detectados automaticamente

---

## Card 088: Criar estratégia de fallback

**Labels:** `backend`, `ai`, `resilience`

**Descrição:**  
O que fazer quando LLM falha ou está lento.

**Checklist Desenvolvimento:**

- [ ] Se Gemini timeout ou erro:
  - [ ] Enviar mensagem padrão: "Desculpe, tive um problema. Por favor aguarde."
  - [ ] Re-enfileirar job para retry
  - [ ] Criar alerta
- [ ] Se múltiplas falhas consecutivas:
  - [ ] Transferir para secretária automaticamente

**Checklist Validação:**

- [ ] Sistema não trava em caso de falha LLM
- [ ] Experiência do usuário é degradada gracefully

---

## Card 089: Criar rate limiting para LLM

**Labels:** `backend`, `ai`, `cost`

**Descrição:**  
Evitar custos excessivos com LLM.

**Checklist Desenvolvimento:**

- [ ] Limitar chamadas por conversation: max 50/dia
- [ ] Usar Redis para counter
- [ ] Se exceder, transferir para secretária
- [ ] Registrar no log

**Checklist Validação:**

- [ ] Limite funciona
- [ ] Custos são controlados

---

## Card 090: Implementar log de custos LLM

**Labels:** `backend`, `ai`, `monitoring`

**Descrição:**  
Calcular custo de cada interação.

**Checklist Desenvolvimento:**

- [ ] Ao salvar `LLMInteractionModel`:
  - [ ] Calcular custo baseado em tokens
  - [ ] Usar tabela de preços (input/output token)
  - [ ] Adicionar campo `cost_usd` (decimal)
- [ ] Endpoint para total de custos

**Checklist Validação:**

- [ ] Custos são calculados corretamente
- [ ] Podem ser auditados

---

## Card 091: Criar endpoint GET /api/v1/ai/stats

**Labels:** `backend`, `api`, `ai`

**Descrição:**  
Estatísticas de uso do LLM.

**Payload:** N/A  
**Response:** `200 OK`

```json
{
	"total_interactions": 1500,
	"total_tokens": 45000,
	"total_cost_usd": 12.5,
	"avg_latency_ms": 850
}
```

**Checklist Desenvolvimento:**

- [ ] Proteger com auth admin
- [ ] Consultar `llm_interactions` table
- [ ] Agregar métricas

**Checklist Validação:**

- [ ] Stats refletem realidade
- [ ] Query é otimizada

---

## Card 092: Criar testes unitários para prompt templates

**Labels:** `test`, `ai`, `prompt`

**Descrição:**  
Garantir prompts geram outputs esperados.

**Checklist Desenvolvimento:**

- [ ] Criar `tests/unit/ai/test_prompts.py`
- [ ] Mockar LLM com respostas fixas
- [ ] Testar cada template
- [ ] Validar estrutura do output

**Checklist Validação:**

- [ ] Prompts são consistentes
- [ ] Mudanças em prompts não quebram sistema

---

## Card 093: Criar testes de integração Gemini

**Labels:** `test`, `ai`, `integration`

**Descrição:**  
Testar integração real com Gemini API.

**Checklist Desenvolvimento:**

- [ ] Criar `tests/integration/test_gemini_client.py`
- [ ] Usar API key de teste
- [ ] Testar geração de resposta simples
- [ ] Testar retry em caso de falha

**Checklist Validação:**

- [ ] Cliente funciona em ambiente real
- [ ] Erros são tratados

---

## Card 094: Criar documentação de prompts

**Labels:** `docs`, `ai`, `prompt`

**Descrição:**  
Documentar estratégia de prompts.

**Checklist Desenvolvimento:**

- [ ] Criar `docs/AI_PROMPTS.md`
- [ ] Explicar cada template
- [ ] Incluir exemplos de input/output
- [ ] Guia de customização

**Checklist Validação:**

- [ ] Documentação está clara
- [ ] Time pode customizar prompts

---

## Card 095: Implementar versionamento de prompts

**Labels:** `backend`, `ai`, `versioning`

**Descrição:**  
Permitir A/B testing de prompts.

**Checklist Desenvolvimento:**

- [ ] Adicionar campo `prompt_version` em `llm_interactions`
- [ ] Carregar prompt de arquivo versionado
- [ ] Endpoint para comparar performance entre versões

**Checklist Validação:**

- [ ] Versões podem ser comparadas
- [ ] Rollback é possível

---

# ÉPICO 6: LÓGICA DE NEGÓCIO

## Card 096: Criar service ConversationService

**Labels:** `backend`, `service`, `business`

**Descrição:**  
Orquestrar operações de conversação (separado do AI orchestrator).

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/services/conversation_service.py`
- [ ] Métodos: `get_or_create()`, `update_status()`, `close()`
- [ ] `get_active_conversations()`, `transfer_to_secretary()`
- [ ] Integrar com ConversationRepository

**Checklist Validação:**

- [ ] CRUD de conversas funciona
- [ ] Lógica de negócio centralizada

---

## Card 097: Criar service LeadService

**Labels:** `backend`, `service`, `business`

**Descrição:**  
Orquestrar operações de leads.

**Checklist Desenvolvimento:**

- [ ] Criar `src/robbot/services/lead_service.py`
- [ ] Métodos: `create_from_conversation()`, `update_maturity()`
- [ ] `assign_to_user()`, `convert()`, `mark_lost()`
- [ ] `get_leads_by_status()`, `get_unassigned_leads()`

**Checklist Validação:**

- [ ] Lógica de leads centralizada
- [ ] Transições de status validadas

---

## Card 098: Implementar atribuição automática de leads

**Labels:** `backend`, `service`, `business`

**Descrição:**  
Auto-assign leads para secretárias com base em disponibilidade.

**Checklist Desenvolvimento:**

- [ ] Lógica de round-robin ou carga de trabalho
- [ ] Verificar secretárias ativas (`UserStatus.ACTIVE`)
- [ ] Atualizar `Lead.assigned_to` automaticamente
- [ ] Adicionar evento de atribuição

**Checklist Validação:**

- [ ] Leads distribuídos uniformemente
- [ ] Apenas secretárias ativas recebem leads

---

## Card 099: Implementar sistema de notificações in-app

**Labels:** `backend`, `service`, `notifications`

**Descrição:**  
Notificações para secretárias sobre novos leads/mensagens.

**Checklist Desenvolvimento:**

- [ ] Criar tabela `notifications`
- [ ] Campos: `user_id`, `type`, `title`, `message`, `read`, `created_at`
- [ ] Service `NotificationService`
- [ ] Método `create_notification()`, `mark_as_read()`
- [ ] API GET `/api/v1/notifications` (listar) - Requer autenticação JWT
- [ ] API PUT `/api/v1/notifications/{id}/read` - Requer autenticação JWT
- [ ] Retornar apenas notificações do usuário autenticado

**Checklist Validação:**

- [ ] Notificações criadas automaticamente
- [ ] API retorna notificações não lidas

---

## Card 100: Implementar detecção de urgência

**Labels:** `backend`, `ai`, `business`

**Descrição:**  
LLM detecta urgência em mensagens para priorização.

**Checklist Desenvolvimento:**

- [ ] Adicionar campo `is_urgent` na tabela `conversations`
- [ ] Prompt Gemini detecta palavras-chave (emergência, urgente, dor)
- [ ] Atualizar `ConversationService.update_urgency()`
- [ ] Notificação prioritária para secretárias

**Checklist Validação:**

- [ ] Mensagens urgentes detectadas corretamente
- [ ] Secretárias notificadas imediatamente

---

## Card 101: Implementar sistema de re-engajamento

**Labels:** `backend`, `service`, `automation`

**Descrição:**  
Reativar conversas inativas automaticamente.

**Checklist Desenvolvimento:**

- [ ] Job Redis Queue: `re_engagement_job.py`
- [ ] Detectar conversas inativas > 48h
- [ ] Enviar mensagem automática via WAHA
- [ ] Atualizar status conversation para `AWAITING_RESPONSE`

**Checklist Validação:**

- [ ] Job executa diariamente
- [ ] Mensagens enviadas corretamente

---

## Card 102: Implementar transições de status de conversas

**Labels:** `backend`, `service`, `business`

**Descrição:**  
Validar transições de status com regras de negócio.

**Checklist Desenvolvimento:**

- [ ] Enum `ConversationStatus` (ACTIVE, AWAITING_RESPONSE, CLOSED, TRANSFERRED)
- [ ] Validar transições permitidas
- [ ] `ConversationService.change_status()`
- [ ] Logs de mudança de status

**Checklist Validação:**

- [ ] Transições inválidas bloqueadas
- [ ] Histórico de status rastreável

---

## Card 103: Implementar API de tags para conversas

**Labels:** `backend`, `api`, `crud`

**Descrição:**  
Tags customizáveis para organizar conversas.

**Checklist Desenvolvimento:**

- [ ] Tabela `tags` (`id`, `name`, `color`)
- [ ] Tabela relacional `conversation_tags`
- [ ] API POST `/api/v1/tags` (criar tag) - Requer auth (admin only)
- [ ] API GET `/api/v1/tags` (listar) - Requer auth JWT
- [ ] API POST `/api/v1/conversations/{id}/tags` (adicionar tag) - Requer auth JWT
- [ ] API DELETE `/api/v1/conversations/{id}/tags/{tag_id}` (remover) - Requer auth JWT

**Payload Exemplo (criar tag):**

```json
{
	"name": "Urgente",
	"color": "#FF0000"
}
```

**Responses:**

- 201: Tag criada
- 400: Nome duplicado

**Checklist Validação:**

- [ ] Tags criadas e associadas
- [ ] Listagem com filtro por tags

---

## Card 104: Implementar API de notas em conversas

**Labels:** `backend`, `api`, `crud`

**Descrição:**  
Secretárias podem adicionar notas internas.

**Checklist Desenvolvimento:**

- [ ] Adicionar campo `notes` (TEXT) em `conversations`
- [ ] API PUT `/api/v1/conversations/{id}/notes`
- [ ] Schema `ConversationNotesUpdate`
- [ ] Validação de permissão (apenas dono ou admin)

**Payload Exemplo:**

```json
{
	"notes": "Cliente solicitou retorno amanhã"
}
```

**Responses:**

- 200: Notas atualizadas
- 403: Sem permissão

**Checklist Validação:**

- [ ] Notas salvas corretamente
- [ ] Apenas usuários autorizados editam

---

## Card 105: Implementar soft delete em leads

**Labels:** `backend`, `repository`, `database`

**Descrição:**  
Desativar leads em vez de deletar.

**Checklist Desenvolvimento:**

- [ ] Adicionar campo `deleted_at` (TIMESTAMP NULL) em `leads`
- [ ] `LeadRepository.soft_delete()`
- [ ] Queries filtram `deleted_at IS NULL`
- [ ] API DELETE `/api/v1/leads/{id}` (soft delete)

**Responses:**

- 204: Lead desativado
- 404: Lead não encontrado

**Checklist Validação:**

- [ ] Leads soft-deleted não aparecem em listagens
- [ ] Dados preservados no banco

---

## Card 106: Implementar exportação de conversas

**Labels:** `backend`, `api`, `export`

**Descrição:**  
Exportar histórico de conversas em CSV.

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/conversations/export?format=csv` - Requer auth JWT
- [ ] Query params: `start_date`, `end_date`, `status`
- [ ] Filtrar por `user_id` se não for admin
- [ ] Gerar CSV com: `phone`, `created_at`, `status`, `maturity_score`
- [ ] Stream response para evitar timeout

**Responses:**

- 200: CSV file
- 400: Parâmetros inválidos

**Checklist Validação:**

- [ ] CSV gerado corretamente
- [ ] Filtros aplicados

---

## Card 107: Implementar limitação de taxa (rate limiting)

**Labels:** `backend`, `infra`, `security`

**Descrição:**  
Prevenir abuso de APIs com rate limiting.

**Checklist Desenvolvimento:**

- [ ] Adicionar `slowapi` ou `fastapi-limiter` com `uv add slowapi` ou `uv add fastapi-limiter`
- [ ] Configurar Redis como backend
- [ ] Limites: 100 req/min por IP (público), 1000 req/min (autenticado)
- [ ] Aplicar em rotas sensíveis (POST, PUT, DELETE)

**Checklist Validação:**

- [ ] Requisições excessivas bloqueadas
- [ ] Headers `X-RateLimit-*` retornados

---

## Card 108: Implementar versionamento de API

**Labels:** `backend`, `api`, `architecture`

**Descrição:**  
Preparar para evolução futura da API.

**Checklist Desenvolvimento:**

- [ ] Estrutura atual: `/api/v1/`
- [ ] Criar diretório `api/v2/` (futuro)
- [ ] Documentar estratégia de deprecation
- [ ] Headers `X-API-Version`

**Checklist Validação:**

- [ ] Estrutura permite múltiplas versões
- [ ] Documentação atualizada

---

## Card 109: Implementar auditoria de ações

**Labels:** `backend`, `database`, `security`

**Descrição:**  
Registrar ações críticas para compliance.

**Checklist Desenvolvimento:**

- [ ] Tabela `audit_logs`
- [ ] Campos: `user_id`, `action`, `entity_type`, `entity_id`, `old_value`, `new_value`, `created_at`
- [ ] Trigger em operações sensíveis (delete, update status)
- [ ] API GET `/api/v1/audit-logs` (admin only)

**Checklist Validação:**

- [ ] Ações registradas automaticamente
- [ ] Apenas admins acessam logs

---

## Card 110: Implementar sistema de permissões granulares

**Labels:** `backend`, `security`, `business`

**Descrição:**  
Controle fino de permissões além de roles.

**Checklist Desenvolvimento:**

- [ ] Tabela `permissions` (`name`, `description`)
- [ ] Tabela `role_permissions`
- [ ] Enum `Permission` (READ_LEADS, WRITE_LEADS, DELETE_CONVERSATIONS, etc.)
- [ ] Decorador `@require_permission("READ_LEADS")`

**Checklist Validação:**

- [ ] Permissões validadas em cada endpoint
- [ ] Usuários sem permissão recebem 403

---

## Card 111: Implementar paginação em todas as listagens

**Labels:** `backend`, `api`, `optimization`

**Descrição:**  
Padronizar paginação com query params.

**Checklist Desenvolvimento:**

- [ ] Query params: `page` (default 1), `limit` (default 20, max 100)
- [ ] Response: `{ items: [], total: 0, page: 1, limit: 20, pages: 5 }`
- [ ] Aplicar em: `/conversations`, `/leads`, `/messages`, `/users`

**Checklist Validação:**

- [ ] Paginação funciona em todas as listagens
- [ ] Performance melhorada

---

## Card 112: Implementar busca full-text em conversas

**Labels:** `backend`, `database`, `search`

**Descrição:**  
Buscar por conteúdo de mensagens.

**Checklist Desenvolvimento:**

- [ ] Índice full-text em `messages.content`
- [ ] API GET `/api/v1/conversations/search?q=dor` - Requer auth JWT
- [ ] Filtrar conversas do usuário autenticado (ou todas se admin)
- [ ] Query PostgreSQL com `to_tsvector()`
- [ ] Ranqueamento por relevância

**Checklist Validação:**

- [ ] Busca retorna resultados relevantes
- [ ] Performance aceitável (< 500ms)

---

## Card 113: Implementar webhooks para eventos

**Labels:** `backend`, `integration`, `webhooks`

**Descrição:**  
Notificar sistemas externos via webhooks.

**Checklist Desenvolvimento:**

- [ ] Tabela `webhooks` (`url`, `events`, `secret`)
- [ ] Eventos: `lead.created`, `conversation.closed`, `message.received`
- [ ] Retry com exponential backoff
- [ ] Assinatura HMAC para segurança

**Checklist Validação:**

- [ ] Webhooks disparados corretamente
- [ ] Retry funciona em falhas

---

## Card 114: Implementar cache de respostas LLM

**Labels:** `backend`, `optimization`, `ai`

**Descrição:**  
Cachear respostas do Gemini para perguntas frequentes.

**Checklist Desenvolvimento:**

- [ ] Redis para cache com TTL 24h
- [ ] Chave: hash da mensagem + contexto
- [ ] Invalidação em mudanças de prompt
- [ ] Métricas de hit/miss

**Checklist Validação:**

- [ ] Respostas idênticas retornam do cache
- [ ] Custo API Gemini reduzido

---

## Card 115: Implementar fallback para falhas do Gemini

**Labels:** `backend`, `ai`, `resilience`

**Descrição:**  
Resposta padrão quando LLM falha.

**Checklist Desenvolvimento:**

- [ ] Try-catch em `GeminiClient.generate()`
- [ ] Mensagem fallback: "Desculpe, estou processando sua mensagem..."
- [ ] Log erro em Sentry
- [ ] Retry automático (3 tentativas)

**Checklist Validação:**

- [ ] Bot não fica mudo em falhas
- [ ] Erros logados corretamente

---

## Card 116: Implementar rotação de API keys

**Labels:** `backend`, `security`, `infra`

**Descrição:**  
Rotacionar secrets sem downtime.

**Checklist Desenvolvimento:**

- [ ] Suporte a múltiplas `GEMINI_API_KEY` (separadas por vírgula)
- [ ] Load balancing entre keys
- [ ] Detecção de key expirada (switch automático)
- [ ] Admin pode desabilitar keys via env

**Checklist Validação:**

- [ ] Rotação não causa downtime
- [ ] Keys inválidas descartadas automaticamente

---

## Card 117: Implementar monitoramento de saúde do WAHA

**Labels:** `backend`, `integration`, `monitoring`

**Descrição:**  
Health check do serviço WAHA.

**Checklist Desenvolvimento:**

- [ ] Job Redis Queue: `waha_health_check.py` (a cada 5min)
- [ ] GET `{WAHA_URL}/api/health`
- [ ] Alerta se WAHA offline
- [ ] Tentar reconectar automaticamente

**Checklist Validação:**

- [ ] Detecção de WAHA offline funciona
- [ ] Alertas disparados

---

## Card 118: Implementar backup automático de conversas

**Labels:** `backend`, `infra`, `backup`

**Descrição:**  
Backup diário de conversas críticas.

**Checklist Desenvolvimento:**

- [ ] Job Redis Queue: `backup_conversations.py` (diário, 2AM)
- [ ] Exportar conversas para S3/blob storage
- [ ] Formato: JSON com metadados
- [ ] Retenção: 90 dias

**Checklist Validação:**

- [ ] Backups criados diariamente
- [ ] Restauração funciona

---

## Card 119: Implementar modo manutenção

**Labels:** `backend`, `infra`, `operations`

**Descrição:**  
Desabilitar bot durante deploys.

**Checklist Desenvolvimento:**

- [ ] Variável env `MAINTENANCE_MODE=true`
- [ ] Webhook WAHA retorna 503
- [ ] Mensagem automática: "Sistema em manutenção, retornamos em breve"
- [ ] Health check reporta status

**Checklist Validação:**

- [ ] Bot para de responder em manutenção
- [ ] Mensagem enviada aos usuários

---

## Card 120: Implementar agendamento de mensagens

**Labels:** `backend`, `service`, `feature`

**Descrição:**  
Secretárias podem agendar mensagens futuras.

**Checklist Desenvolvimento:**

- [ ] Tabela `scheduled_messages` (`phone`, `content`, `scheduled_at`, `sent`, `user_id`)
- [ ] Job Redis Queue: `send_scheduled_messages.py` (a cada 1min)
- [ ] API POST `/api/v1/messages/schedule` - Requer auth JWT
- [ ] Associar mensagem ao usuário autenticado
- [ ] Cancelamento de mensagens agendadas (apenas próprio usuário ou admin)

**Payload Exemplo:**

```json
{
	"phone": "5511999999999",
	"content": "Lembrete: consulta amanhã às 14h",
	"scheduled_at": "2025-01-20T14:00:00Z"
}
```

**Responses:**

- 201: Mensagem agendada
- 400: Data no passado

**Checklist Validação:**

- [ ] Mensagens enviadas no horário correto
- [ ] Cancelamento funciona

---

## Card 121: Implementar templates de mensagens

**Labels:** `backend`, `api`, `feature`

**Descrição:**  
Templates reutilizáveis para secretárias.

**Checklist Desenvolvimento:**

- [ ] Tabela `message_templates` (`name`, `content`, `variables`)
- [ ] API POST `/api/v1/templates` (criar)
- [ ] API GET `/api/v1/templates` (listar)
- [ ] Suporte a variáveis: `{{nome}}`, `{{data}}`

**Payload Exemplo:**

```json
{
	"name": "Confirmação Consulta",
	"content": "Olá {{nome}}, confirmamos sua consulta para {{data}}."
}
```

**Checklist Validação:**

- [ ] Templates criados e usados
- [ ] Variáveis substituídas corretamente

---

## Card 122: Implementar respostas rápidas

**Labels:** `backend`, `api`, `feature`

**Descrição:**  
Sugestões de respostas para secretárias.

**Checklist Desenvolvimento:**

- [ ] Tabela `quick_replies` (`trigger`, `response`)
- [ ] API retorna sugestões baseadas em contexto
- [ ] GET `/api/v1/quick-replies?context=agendamento`
- [ ] Admin pode gerenciar respostas

**Checklist Validação:**

- [ ] Sugestões aparecem no dashboard
- [ ] Secretárias usam com 1 clique

---

## Card 123: Implementar histórico de edições

**Labels:** `backend`, `database`, `audit`

**Descrição:**  
Rastrear edições em leads e conversas.

**Checklist Desenvolvimento:**

- [ ] Tabela `edit_history` (`entity_type`, `entity_id`, `field`, `old_value`, `new_value`, `user_id`, `edited_at`)
- [ ] Trigger automático em UPDATEs
- [ ] API GET `/api/v1/{entity}/{id}/history`

**Checklist Validação:**

- [ ] Edições rastreadas automaticamente
- [ ] Histórico consultável

---

## Card 124: Implementar duplicação de leads

**Labels:** `backend`, `service`, `business`

**Descrição:**  
Detectar e mesclar leads duplicados.

**Checklist Desenvolvimento:**

- [ ] Verificar `phone` duplicado em `leads`
- [ ] API POST `/api/v1/leads/merge` (unir 2 leads)
- [ ] Preservar histórico completo
- [ ] Notificar secretária sobre duplicatas

**Payload Exemplo:**

```json
{
	"source_id": "uuid1",
	"target_id": "uuid2"
}
```

**Checklist Validação:**

- [ ] Leads mesclados corretamente
- [ ] Sem perda de dados

---

## Card 125: Implementar relatório de produtividade

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
Métricas de produtividade por secretária.

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/reports/productivity` - Requer auth JWT
- [ ] Query params: `user_id`, `start_date`, `end_date`
- [ ] Admin pode ver qualquer `user_id`, secretária apenas próprio ID
- [ ] Métricas: mensagens enviadas, leads convertidos, tempo médio de resposta
- [ ] Gráfico de tendência semanal

**Response Exemplo:**

```json
{
	"user_id": "uuid",
	"period": "2025-01-01 to 2025-01-31",
	"messages_sent": 340,
	"leads_converted": 12,
	"avg_response_time_seconds": 120
}
```

**Checklist Validação:**

- [ ] Relatórios calculados corretamente
- [ ] Admin visualiza todos os usuários

---

# ÉPICO 7: DASHBOARD E MÉTRICAS

> **⚠️ IMPORTANTE:** Todas as APIs de métricas e dashboard **REQUEREM autenticação JWT**.
>
> - **Admin:** Acesso a métricas globais e de qualquer usuário
> - **Secretária:** Acesso apenas às próprias métricas
> - Implementar filtros por `user_id` do token JWT
> - Cache Redis deve incluir `user_id` na chave para evitar vazamento de dados

## Card 126: Criar API de resumo do dashboard

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
Endpoint central com resumo de KPIs.

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/dashboard/summary` - Requer auth JWT
- [ ] Métricas filtradas por role: admin vê tudo, secretária vê apenas seus dados
- [ ] Métricas: total conversas ativas, novos leads hoje, taxa conversão, tempo médio resposta
- [ ] Filtro por `start_date`, `end_date`
- [ ] Cache Redis (TTL 5min) com chave por `user_id`

**Response Exemplo:**

```json
{
	"active_conversations": 45,
	"new_leads_today": 12,
	"conversion_rate": 0.18,
	"avg_response_time_seconds": 145
}
```

**Responses:**

- 200: Resumo retornado
- 401: Não autenticado

**Checklist Validação:**

- [ ] Métricas atualizadas em tempo real
- [ ] Performance < 200ms

---

## Card 127: Criar API de métricas por role

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
Visão diferente para admin vs secretária.

**Checklist Desenvolvimento:**

- [ ] Admin: métricas globais + por usuário
- [ ] Secretária: apenas suas próprias métricas
- [ ] GET `/api/v1/metrics/my` (usuário logado)
- [ ] GET `/api/v1/metrics/user/{user_id}` (admin only)

**Checklist Validação:**

- [ ] Secretárias não veem dados de outros
- [ ] Admin vê tudo

---

## Card 128: Implementar API de gráfico de volume de mensagens

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
Dados para gráfico de volume temporal.

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/metrics/message-volume` - Requer auth JWT
- [ ] Query params: `granularity` (hour/day/week), `start_date`, `end_date`
- [ ] Filtrar dados por role: admin vê global, secretária vê apenas suas conversas
- [ ] Retornar array: `[{ date, count }]`
- [ ] Group by data/hora

**Response Exemplo:**

```json
{
	"granularity": "day",
	"data": [
		{ "date": "2025-01-15", "count": 234 },
		{ "date": "2025-01-16", "count": 189 }
	]
}
```

**Checklist Validação:**

- [ ] Dados corretos para diferentes granularidades
- [ ] Performance aceitável

---

## Card 129: Implementar API de taxa de conversão

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
Métricas de conversão de leads.

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/metrics/conversion-rate` - Requer auth JWT
- [ ] Cálculo: `(leads_convertidos / total_leads) * 100`
- [ ] Filtros: `start_date`, `end_date`, `user_id` (admin pode filtrar qualquer user)
- [ ] Secretária vê apenas suas métricas
- [ ] Breakdown por status (`NEW`, `QUALIFIED`, `CONVERTED`, `LOST`)

**Response Exemplo:**

```json
{
	"period": "2025-01-01 to 2025-01-31",
	"total_leads": 100,
	"converted": 18,
	"conversion_rate": 18.0,
	"by_status": {
		"NEW": 30,
		"QUALIFIED": 25,
		"CONVERTED": 18,
		"LOST": 27
	}
}
```

**Checklist Validação:**

- [ ] Cálculo matemático correto
- [ ] Breakdown por status

---

## Card 130: Implementar API de tempo médio de resposta

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
Tempo entre mensagem do lead e resposta.

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/metrics/response-time` - Requer auth JWT
- [ ] Calcular diferença entre `message.created_at` (lead) e primeira resposta (secretária)
- [ ] Filtros: `user_id`, `start_date`, `end_date`
- [ ] Secretária vê apenas seu próprio tempo de resposta
- [ ] Retornar média, mediana, p95

**Response Exemplo:**

```json
{
	"avg_seconds": 145,
	"median_seconds": 120,
	"p95_seconds": 300
}
```

**Checklist Validação:**

- [ ] Cálculo estatístico correto
- [ ] Métricas por usuário

---

## Card 131: Implementar API de funil de conversão

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
Visualizar funil completo do lead.

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/metrics/funnel` - Requer auth JWT
- [ ] Etapas: Primeira Mensagem → Lead Criado → Qualificado → Convertido
- [ ] Filtrar por role: admin vê funil global, secretária vê apenas seus leads
- [ ] Taxas de drop-off entre etapas
- [ ] Filtro por período

**Response Exemplo:**

```json
{
	"funnel": [
		{ "stage": "Primeira Mensagem", "count": 500, "dropoff": 0 },
		{ "stage": "Lead Criado", "count": 450, "dropoff": 10 },
		{ "stage": "Qualificado", "count": 200, "dropoff": 55.6 },
		{ "stage": "Convertido", "count": 90, "dropoff": 55 }
	]
}
```

**Checklist Validação:**

- [ ] Funil calculado corretamente
- [ ] Drop-off percentual correto

---

## Card 132: Implementar API de horários de pico

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
Identificar horários com mais mensagens.

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/metrics/peak-hours` - Requer auth JWT
- [ ] Agregar mensagens por hora do dia (0-23)
- [ ] Filtrar por role: admin vê dados globais, secretária vê apenas suas conversas
- [ ] Retornar top 3 horários
- [ ] Filtro por dia da semana

**Response Exemplo:**

```json
{
	"peak_hours": [
		{ "hour": 14, "count": 340 },
		{ "hour": 10, "count": 298 },
		{ "hour": 16, "count": 267 }
	]
}
```

**Checklist Validação:**

- [ ] Horários corretos
- [ ] Útil para planejamento de equipe

---

## Card 133: Implementar API de taxa de resposta do bot

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
Quantas mensagens foram respondidas pelo bot vs transferidas.

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/metrics/bot-response-rate` - Requer auth JWT
- [ ] Calcular: `(respostas_bot / total_mensagens) * 100`
- [ ] Filtrar por role: admin vê métrica global, secretária vê apenas suas transferências
- [ ] Separate: resolvidas pelo bot vs transferidas para secretária
- [ ] Filtro por período

**Response Exemplo:**

```json
{
	"total_messages": 1000,
	"bot_resolved": 650,
	"transferred": 350,
	"bot_response_rate": 65.0
}
```

**Checklist Validação:**

- [ ] Métrica reflete autonomia do bot
- [ ] Ajuda a medir eficácia da IA

---

## Card 134: Implementar API de satisfação (NPS)

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
Coletar feedback dos usuários.

**Checklist Desenvolvimento:**

- [ ] Tabela `feedback` (`conversation_id`, `score`, `comment`, `created_at`)
- [ ] Bot pergunta: "De 0-10, como avalia o atendimento?"
- [ ] API POST `/api/v1/feedback` (criar) - NÃO requer auth (feedback do lead)
- [ ] API GET `/api/v1/metrics/nps` (calcular NPS) - Requer auth JWT
- [ ] Filtrar NPS por role: admin vê NPS global, secretária vê apenas suas avaliações

**NPS Cálculo:**  
`(% promotores - % detratores)`

**Checklist Validação:**

- [ ] Feedback coletado automaticamente
- [ ] NPS calculado corretamente

---

## Card 135: Implementar API de leads por origem

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
De onde vieram os leads (redes sociais, site, etc).

**Checklist Desenvolvimento:**

- [ ] Adicionar campo `source` (ENUM) em `leads`
- [ ] Valores: `WHATSAPP`, `WEBSITE`, `INSTAGRAM`, `REFERRAL`
- [ ] API GET `/api/v1/metrics/leads-by-source` - Requer auth JWT
- [ ] Filtrar por role: admin vê todos, secretária vê apenas seus leads
- [ ] Gráfico pizza

**Response Exemplo:**

```json
{
	"sources": [
		{ "source": "WHATSAPP", "count": 456 },
		{ "source": "INSTAGRAM", "count": 234 },
		{ "source": "WEBSITE", "count": 120 }
	]
}
```

**Checklist Validação:**

- [ ] Origens rastreadas corretamente
- [ ] Útil para marketing

---

## Card 136: Implementar API de custo por lead

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
Calcular custo operacional por lead convertido.

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/metrics/cost-per-lead`
- [ ] Input: `operational_cost` (mensal)
- [ ] Cálculo: `cost / leads_converted`
- [ ] Comparar com mês anterior

**Response Exemplo:**

```json
{
	"operational_cost": 5000.0,
	"leads_converted": 90,
	"cost_per_lead": 55.56,
	"previous_month_cost_per_lead": 62.5,
	"improvement_percent": 11.1
}
```

**Checklist Validação:**

- [ ] Cálculo financeiro correto
- [ ] Comparação temporal

---

## Card 137: Implementar API de retenção de leads

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
Quantos leads retornam após primeira interação.

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/metrics/lead-retention`
- [ ] Calcular: leads com > 1 conversa / total leads
- [ ] Breakdown por semana
- [ ] Cohort analysis

**Response Exemplo:**

```json
{
	"total_leads": 500,
	"returning_leads": 120,
	"retention_rate": 24.0,
	"cohorts": [
		{ "week": "2025-W03", "retention": 28.0 },
		{ "week": "2025-W02", "retention": 22.0 }
	]
}
```

**Checklist Validação:**

- [ ] Retenção calculada corretamente
- [ ] Cohorts úteis para análise

---

## Card 138: Implementar API de SLA compliance

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
Medir cumprimento de SLA (ex: responder em < 5min).

**Checklist Desenvolvimento:**

- [ ] Definir SLA: `MAX_RESPONSE_TIME_SECONDS = 300` (5min)
- [ ] API GET `/api/v1/metrics/sla-compliance`
- [ ] Calcular: `(respostas_dentro_sla / total_respostas) * 100`
- [ ] Alertar secretárias se SLA violado

**Response Exemplo:**

```json
{
	"sla_target_seconds": 300,
	"total_responses": 1000,
	"within_sla": 850,
	"compliance_rate": 85.0
}
```

**Checklist Validação:**

- [ ] SLA monitorado continuamente
- [ ] Alertas funcionam

---

## Card 139: Implementar API de export de métricas

**Labels:** `backend`, `api`, `export`

**Descrição:**  
Exportar todas as métricas em CSV/Excel.

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/metrics/export?format=csv` - Requer auth JWT
- [ ] Incluir todas as métricas do dashboard filtradas por role
- [ ] Query params: `start_date`, `end_date`
- [ ] Admin pode exportar dados de qualquer usuário
- [ ] Stream response

**Checklist Validação:**

- [ ] Arquivo gerado corretamente
- [ ] Todas as métricas incluídas

---

## Card 140: Implementar API de comparação temporal

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
Comparar métricas entre períodos.

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/metrics/compare`
- [ ] Query params: `period1_start`, `period1_end`, `period2_start`, `period2_end`
- [ ] Retornar delta percentual para cada métrica
- [ ] Highlight melhoras/pioras

**Response Exemplo:**

```json
{
	"period1": { "leads": 100, "conversion_rate": 15.0 },
	"period2": { "leads": 120, "conversion_rate": 18.0 },
	"deltas": { "leads": 20.0, "conversion_rate": 20.0 }
}
```

**Checklist Validação:**

- [ ] Comparação matemática correta
- [ ] Visualização útil

---

## Card 141: Implementar API de ranking de secretárias

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
Leaderboard de performance.

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/metrics/leaderboard`
- [ ] Critérios: leads convertidos, tempo médio resposta, satisfação
- [ ] Ponderação configurável
- [ ] Top 10 secretárias

**Response Exemplo:**

```json
{
	"leaderboard": [
		{ "user_id": "uuid1", "name": "Ana Silva", "score": 95 },
		{ "user_id": "uuid2", "name": "João Santos", "score": 88 }
	]
}
```

**Checklist Validação:**

- [ ] Ranking justo e motivador
- [ ] Score calculado corretamente

---

## Card 142: Implementar API de alertas de anomalias

**Labels:** `backend`, `api`, `monitoring`

**Descrição:**  
Detectar padrões anormais automaticamente.

**Checklist Desenvolvimento:**

- [ ] Baseline: média últimas 4 semanas
- [ ] Alertar se métrica desvia > 30%
- [ ] Exemplos: queda brusca conversões, aumento tempo resposta
- [ ] API GET `/api/v1/alerts/anomalies`

**Response Exemplo:**

```json
{
	"anomalies": [
		{
			"metric": "conversion_rate",
			"current": 12.0,
			"baseline": 18.0,
			"deviation": -33.3,
			"severity": "high"
		}
	]
}
```

**Checklist Validação:**

- [ ] Anomalias detectadas corretamente
- [ ] Alertas enviados para admins

---

## Card 143: Implementar API de previsão de demanda

**Labels:** `backend`, `api`, `ai`, `advanced`

**Descrição:**  
Prever volume de mensagens futuras (ML simples).

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/metrics/forecast?days=7`
- [ ] Algoritmo: média móvel ponderada ou Prophet (Facebook)
- [ ] Retornar previsão com intervalo de confiança
- [ ] Útil para escalar equipe

**Response Exemplo:**

```json
{
	"forecast": [
		{ "date": "2025-01-20", "predicted_messages": 245, "confidence": 0.85 },
		{ "date": "2025-01-21", "predicted_messages": 230, "confidence": 0.82 }
	]
}
```

**Checklist Validação:**

- [ ] Previsões razoáveis
- [ ] Intervalo de confiança calculado

---

## Card 144: Implementar API de ROI do bot

**Labels:** `backend`, `api`, `metrics`, `business`

**Descrição:**  
Calcular retorno sobre investimento do sistema.

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/metrics/roi`
- [ ] Input: `implementation_cost`, `monthly_operational_cost`
- [ ] Calcular: economia em horas humanas, aumento conversões
- [ ] ROI = `(ganhos - custos) / custos * 100`

**Response Exemplo:**

```json
{
	"implementation_cost": 50000.0,
	"monthly_operational_cost": 2000.0,
	"monthly_savings": 8000.0,
	"roi_percent": 300.0,
	"payback_months": 6.25
}
```

**Checklist Validação:**

- [ ] Cálculo financeiro robusto
- [ ] Ajuda a justificar investimento

---

## Card 145: Implementar dashboard real-time (WebSocket)

**Labels:** `backend`, `websocket`, `realtime`

**Descrição:**  
Métricas atualizadas em tempo real no dashboard.

**Checklist Desenvolvimento:**

- [ ] WebSocket endpoint: `ws://api/v1/dashboard/stream`
- [ ] Publicar eventos: nova mensagem, lead criado, conversão
- [ ] Frontend subscreve e atualiza UI
- [ ] Throttle updates (max 1/segundo)

**Checklist Validação:**

- [ ] Dashboard atualiza sem refresh
- [ ] Performance não degrada

---

## Card 146: Criar visualização de mapa de calor

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
Heatmap de atividade (hora x dia da semana).

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/metrics/heatmap`
- [ ] Matriz 7 dias x 24 horas
- [ ] Contagem de mensagens por célula
- [ ] Cores baseadas em intensidade

**Response Exemplo:**

```json
{
	"heatmap": [
		{ "day": "monday", "hour": 14, "count": 45 },
		{ "day": "tuesday", "hour": 10, "count": 38 }
	]
}
```

**Checklist Validação:**

- [ ] Heatmap representa padrões reais
- [ ] Útil para staffing

---

## Card 147: Implementar API de métricas de AI

**Labels:** `backend`, `api`, `ai`, `metrics`

**Descrição:**  
Métricas específicas da IA (tokens, custo, latência).

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/metrics/ai`
- [ ] Métricas: total tokens, custo API Gemini, latência média
- [ ] Custo estimado: `tokens * $0.000002` (Gemini pricing)
- [ ] Breakdown por tipo de interação

**Response Exemplo:**

```json
{
	"total_tokens": 1500000,
	"estimated_cost_usd": 3.0,
	"avg_latency_ms": 850,
	"interactions": 5000
}
```

**Checklist Validação:**

- [ ] Custos calculados corretamente
- [ ] Latência monitorada

---

## Card 148: Implementar API de análise de sentimentos

**Labels:** `backend`, `api`, `ai`, `advanced`

**Descrição:**  
Análise de sentimento das mensagens (positivo/negativo/neutro).

**Checklist Desenvolvimento:**

- [ ] Usar Gemini para classificar sentimento
- [ ] Adicionar campo `sentiment` em `messages`
- [ ] API GET `/api/v1/metrics/sentiment`
- [ ] Tendência temporal de sentimentos

**Response Exemplo:**

```json
{
	"positive": 560,
	"neutral": 320,
	"negative": 120,
	"overall_sentiment_score": 0.44
}
```

**Checklist Validação:**

- [ ] Sentimentos classificados corretamente
- [ ] Útil para detectar insatisfação

---

## Card 149: Implementar API de tópicos mais discutidos

**Labels:** `backend`, `api`, `nlp`

**Descrição:**  
Extrair tópicos frequentes das conversas.

**Checklist Desenvolvimento:**

- [ ] LLM extrai keywords/tópicos
- [ ] API GET `/api/v1/metrics/topics`
- [ ] Ranking por frequência
- [ ] Word cloud

**Response Exemplo:**

```json
{
	"topics": [
		{ "topic": "agendamento", "count": 340 },
		{ "topic": "preços", "count": 210 },
		{ "topic": "localização", "count": 180 }
	]
}
```

**Checklist Validação:**

- [ ] Tópicos relevantes identificados
- [ ] Ajuda a entender demanda

---

## Card 150: Implementar API de jornada do lead

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
Timeline completa de um lead.

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/leads/{id}/journey`
- [ ] Retornar: todas mensagens, mudanças de status, atribuições
- [ ] Ordenado cronologicamente
- [ ] Incluir tempo entre etapas

**Response Exemplo:**

```json
{
	"lead_id": "uuid",
	"journey": [
		{
			"timestamp": "2025-01-15T10:00:00Z",
			"event": "Primeira Mensagem",
			"details": "..."
		},
		{
			"timestamp": "2025-01-15T10:02:30Z",
			"event": "Lead Criado",
			"details": "..."
		},
		{
			"timestamp": "2025-01-15T14:30:00Z",
			"event": "Qualificado",
			"details": "..."
		}
	]
}
```

**Checklist Validação:**

- [ ] Timeline completa e precisa
- [ ] Útil para análise de comportamento

---

## Card 151: Implementar API de distribuição de maturity score

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
Histograma de maturity scores dos leads.

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/metrics/maturity-distribution`
- [ ] Buckets: 0-20, 21-40, 41-60, 61-80, 81-100
- [ ] Contagem de leads por bucket
- [ ] Identificar padrões

**Response Exemplo:**

```json
{
	"distribution": [
		{ "range": "0-20", "count": 45 },
		{ "range": "21-40", "count": 120 },
		{ "range": "41-60", "count": 200 },
		{ "range": "61-80", "count": 100 },
		{ "range": "81-100", "count": 35 }
	]
}
```

**Checklist Validação:**

- [ ] Distribuição correta
- [ ] Ajuda a calibrar scoring

---

## Card 152: Implementar API de taxa de abandono

**Labels:** `backend`, `api`, `metrics`

**Descrição:**  
Quantos leads param de responder.

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/metrics/abandonment-rate`
- [ ] Calcular: conversas sem resposta há > 72h
- [ ] Taxa: `(abandonadas / total) * 100`
- [ ] Identificar em qual etapa abandonam

**Response Exemplo:**

```json
{
	"total_conversations": 500,
	"abandoned": 85,
	"abandonment_rate": 17.0,
	"common_abandonment_stage": "Qualificação"
}
```

**Checklist Validação:**

- [ ] Taxa calculada corretamente
- [ ] Insights acionáveis

---

## Card 153: Implementar API de análise de concorrência

**Labels:** `backend`, `api`, `advanced`

**Descrição:**  
Rastrear menções a concorrentes.

**Checklist Desenvolvimento:**

- [ ] Lista de concorrentes configurável
- [ ] Detectar menções em mensagens
- [ ] API GET `/api/v1/metrics/competitor-mentions`
- [ ] Alertar quando concorrente citado

**Response Exemplo:**

```json
{
	"competitors": [
		{ "name": "Clínica X", "mentions": 23 },
		{ "name": "Clínica Y", "mentions": 12 }
	]
}
```

**Checklist Validação:**

- [ ] Menções detectadas
- [ ] Útil para posicionamento

---

## Card 154: Implementar API de lifetime value (LTV)

**Labels:** `backend`, `api`, `metrics`, `business`

**Descrição:**  
Valor médio de um lead convertido.

**Checklist Desenvolvimento:**

- [ ] API GET `/api/v1/metrics/ltv`
- [ ] Input: `avg_transaction_value`
- [ ] Calcular: LTV = avg*transaction * conversão \_ retenção
- [ ] Segmentar por origem de lead

**Response Exemplo:**

```json
{
	"avg_transaction_value": 500.0,
	"conversion_rate": 0.18,
	"retention_rate": 0.65,
	"ltv": 58.5
}
```

**Checklist Validação:**

- [ ] LTV calculado corretamente
- [ ] Segmentações úteis

---

## Card 155: Implementar API de relatórios agendados

**Labels:** `backend`, `api`, `automation`

**Descrição:**  
Enviar relatórios por email automaticamente.

**Checklist Desenvolvimento:**

- [ ] Tabela `scheduled_reports` (`user_id`, `frequency`, `metrics`, `next_run`)
- [ ] Job Redis Queue: `send_reports.py` (diário)
- [ ] Gerar PDF com métricas selecionadas
- [ ] Enviar por email (SMTP)

**Checklist Validação:**

- [ ] Relatórios enviados no horário
- [ ] PDF formatado corretamente

---

# ÉPICO 8: MELHORIAS E TESTES

## Card 156: Criar testes unitários para repositories

**Labels:** `testing`, `unit`, `quality`

**Descrição:**  
Testar camada de dados isoladamente.

**Checklist Desenvolvimento:**

- [ ] Instalar `pytest==7.4.0`, `pytest-asyncio==0.21.0`
- [ ] Mock SQLAlchemy sessions
- [ ] Testar todos os métodos CRUD
- [ ] Coverage mínimo: 80%

**Checklist Validação:**

- [ ] Todos os repositories testados
- [ ] Testes passam consistentemente

---

## Card 157: Criar testes unitários para services

**Labels:** `testing`, `unit`, `quality`

**Descrição:**  
Testar lógica de negócio isoladamente.

**Checklist Desenvolvimento:**

- [ ] Mock dependencies (repositories, clients)
- [ ] Testar fluxos de negócio
- [ ] Testar validações e erros
- [ ] Coverage mínimo: 80%

**Checklist Validação:**

- [ ] Todos os services testados
- [ ] Edge cases cobertos

---

## Card 158: Criar testes de integração para APIs

**Labels:** `testing`, `integration`, `api`

**Descrição:**  
Testar endpoints end-to-end.

**Checklist Desenvolvimento:**

- [ ] Usar `TestClient` do FastAPI
- [ ] Setup/teardown de database test
- [ ] Testar autenticação e autorização
- [ ] Testar payloads e responses

**Checklist Validação:**

- [ ] Todos os endpoints testados
- [ ] Status codes corretos

---

## Card 159: Criar testes de integração para WAHA

**Labels:** `testing`, `integration`, `waha`

**Descrição:**  
Testar comunicação com WAHA API.

**Checklist Desenvolvimento:**

- [ ] Mock HTTP requests (`pytest-httpx`)
- [ ] Testar envio de mensagens
- [ ] Testar recebimento de webhooks
- [ ] Testar erros de rede

**Checklist Validação:**

- [ ] Integração WAHA testada
- [ ] Retry e fallback funcionam

---

## Card 160: Criar testes de integração para Gemini

**Labels:** `testing`, `integration`, `ai`

**Descrição:**  
Testar integração com Gemini API.

**Checklist Desenvolvimento:**

- [ ] Mock respostas do Gemini
- [ ] Testar prompts e contexts
- [ ] Testar token counting
- [ ] Testar rate limiting

**Checklist Validação:**

- [ ] LLM integration testada
- [ ] Custos calculados corretamente

---

## Card 161: Implementar testes de carga (load testing)

**Labels:** `testing`, `performance`, `load`

**Descrição:**  
Testar performance sob alta carga.

**Checklist Desenvolvimento:**

- [ ] Adicionar `locust` ao dev group com `uv add --dev locust`
- [ ] Simular 100 usuários simultâneos
- [ ] Testar endpoints críticos (webhook, send message)
- [ ] Medir latência p95 e throughput

**Checklist Validação:**

- [ ] API aguenta carga esperada
- [ ] Latência aceitável (< 500ms p95)

---

## Card 162: Implementar monitoramento com Prometheus

**Labels:** `monitoring`, `infra`, `observability`

**Descrição:**  
Coletar métricas de aplicação.

**Checklist Desenvolvimento:**

- [ ] Adicionar `prometheus-fastapi-instrumentator` com `uv add prometheus-fastapi-instrumentator`
- [ ] Exportar métricas: request count, latency, errors
- [ ] Endpoint `/metrics` (Prometheus format)
- [ ] Dashboard Grafana

**Checklist Validação:**

- [ ] Métricas coletadas
- [ ] Grafana visualiza corretamente

---

## Card 163: Implementar logging estruturado

**Labels:** `logging`, `observability`, `quality`

**Descrição:**  
Logs em formato JSON para melhor análise.

**Checklist Desenvolvimento:**

- [ ] Adicionar `structlog` com `uv add structlog`
- [ ] Configurar JSON formatter
- [ ] Adicionar context (request_id, user_id)
- [ ] Níveis: DEBUG, INFO, WARNING, ERROR

**Checklist Validação:**

- [ ] Logs estruturados em produção
- [ ] Fácil de parsear e buscar

---

## Card 164: Implementar CI/CD pipeline

**Labels:** `devops`, `automation`, `ci-cd`

**Descrição:**  
Automatizar testes e deploy.

**Checklist Desenvolvimento:**

- [ ] GitHub Actions workflow
- [ ] Etapas: lint, test, build, deploy
- [ ] Deploy automático em `main` branch
- [ ] Notificação de falhas

**Checklist Validação:**

- [ ] Pipeline executa em cada commit
- [ ] Deploy automático funciona

---

## Card 165: Implementar migrations seeders

**Labels:** `database`, `infra`, `development`

**Descrição:**  
Popular banco de dados para desenvolvimento.

**Checklist Desenvolvimento:**

- [ ] Script `seeds/dev_seed.py`
- [ ] Criar: 5 users, 20 leads, 50 conversations, 200 messages
- [ ] Dados realistas e variados
- [ ] Comando: `python -m seeds.dev_seed`

**Checklist Validação:**

- [ ] Seed popula banco corretamente
- [ ] Desenvolvimento mais ágil

---

## Card 166: Documentar arquitetura e fluxos

**Labels:** `documentation`, `architecture`

**Descrição:**  
Documentação técnica completa.

**Checklist Desenvolvimento:**

- [ ] README.md atualizado (setup, run, test)
- [ ] ARCHITECTURE.md (diagramas, decisões)
- [ ] API_REFERENCE.md (todos os endpoints)
- [ ] DEPLOYMENT.md (guia de deploy)

**Checklist Validação:**

- [ ] Documentação completa e clara
- [ ] Novos devs conseguem onboarding

---

## Card 167: Otimizar queries N+1

**Labels:** `performance`, `database`, `optimization`

**Descrição:**  
Eliminar queries desnecessárias.

**Checklist Desenvolvimento:**

- [ ] Usar `selectinload()` / `joinedload()` em relationships
- [ ] Analisar com `EXPLAIN ANALYZE`
- [ ] Indexar foreign keys
- [ ] Testar performance antes/depois

**Checklist Validação:**

- [ ] Queries N+1 eliminadas
- [ ] Performance melhorada (< 50ms queries)

---

---

# FIM DO BACKLOG

## Resumo Final

**Total de Cards:** 167  
**Total de Épicos:** 8

### Distribuição por Épico:

1. **Infraestrutura Base:** 15 cards
2. **Integração WAHA:** 20 cards
3. **Sistema de Filas:** 10 cards
4. **Banco de Dados Core:** 30 cards
5. **Integração Gemini AI:** 20 cards
6. **Lógica de Negócio:** 30 cards
7. **Dashboard e Métricas:** 30 cards
8. **Melhorias e Testes:** 12 cards

### Próximos Passos:

1. **Revisar e Priorizar:** Validar prioridades com stakeholders
2. **Sprint Planning:** Dividir cards em sprints (sugestão: 2 semanas cada)
3. **Estimation:** Estimar complexidade (story points ou horas)
4. **Começar pelo ÉPICO 1:** Infraestrutura é bloqueador para o resto

### Observações Importantes:

- ✅ Cada card é uma **micro-task** implementável
- ✅ Cards seguem **dependências técnicas** (infraestrutura → features → testes)
- ✅ APIs incluem **payloads de exemplo** e **status codes**
- ✅ Checklists de **desenvolvimento** e **validação** em cada card
- ✅ Labels facilitam **filtragem** e organização
- ✅ Pronto para importar no **Trello, Jira, GitHub Projects**, etc.

### Stack Tecnológica Completa:

**Backend:**

- FastAPI 0.121.2
- SQLAlchemy 2.0.44
- Pydantic 2.12.4
- PostgreSQL 15
- Alembic 1.17.2

**Queue & Cache:**

- Redis 5.0.0
- redis-om 0.2.1
- rq 1.15.0

**AI & ML:**

- LangChain 0.1.0
- langchain-google-genai 0.0.5
- ChromaDB 0.4.20
- google-generativeai 0.3.0
- tiktoken 0.5.0

**Integrations:**

- WAHA (WhatsApp HTTP API)

**DevOps & Monitoring:**

- Docker & Docker Compose
- Prometheus
- Grafana
- structlog

**Testing:**

- pytest 7.4.0
- pytest-asyncio 0.21.0
- locust 2.15.0

---

**��� Objetivo:** Desenvolver bot WhatsApp inteligente para clínicas com:

- LLM (Gemini) como orquestrador de conversas
- Qualificação automática de leads
- Dashboard com métricas em tempo real
- Integração completa com WhatsApp via WAHA

**��� Status:** Backlog completo e pronto para execução!

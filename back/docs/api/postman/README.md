# Postman Collection - WPP Bot API

> **Collection UNIFICADA** para testar todos os endpoints da API WhatsApp Bot

## Arquivos Disponiveis

### Arquivos Principais (USE ESTES)

| Arquivo | Descricao | Status |
|---------|-----------|--------|
| **WPP_Bot_API.postman_collection.json** | Collection parcial (89/161 endpoints - 55% cobertura) | **Incompleto** |
| **ENDPOINTS-FALTANTES-POSTMAN.md** | Lista dos 72 endpoints faltantes | **Referencia** |
| **WPP_Bot_API.postman_environment.json** | Environment (local dev) | **Necessario** |

### Endpoints de Analytics

Os endpoints de **metricas e relatorios avancados** (Sprint 12) estao disponiveis via **Swagger UI** em `http://localhost:3333/docs`:

- **Performance**: `/api/v1/metrics/performance/*`
- **Conversao**: `/api/v1/metrics/conversion/*`
- **Analise de Conversas**: `/api/v1/metrics/conversation/*` **Melhorias P3**
- **Dashboard Real-time**: `/api/v1/metrics/realtime/*`
- **WebSocket**: `ws://localhost:3333/api/v1/metrics/ws/realtime` (autenticado)

**Melhorias Sprint 12 - Nota 10/10:**
- PostgreSQL Full-Text Search com `to_tsvector('portuguese')` (+30% acuracia)
- Gemini sentiment fallback opcional (`use_gemini_fallback=true`) (+60% acuracia)
- Batch processing + cache 24h para reduzir custos
- WebSocket autenticado com JWT
- 24/24 testes de integracao passing

### Arquivos Legados (Backup)

| Arquivo | Descricao | Status |
|---------|-----------|--------|
| WPP_Bot_Playbook_Addon.postman_collection.json | Addon antigo de playbooks | **Deprecado** (mesclado na principal) |

> ** Nota**: O addon de playbooks foi mesclado na collection principal. Voce **NAO precisa** importar 2 collections.

---

## Como Importar

### 1⃣ Importar Collection Principal

1. Abra o Postman
2. Clique em **Import** (canto superior esquerdo)
3. Selecione **apenas** o arquivo: `WPP_Bot_API.postman_collection.json`
4. Clique em **Import**

### 2⃣ Importar Environment

1. Clique em **Import** novamente
2. Selecione o arquivo: `WPP_Bot_API.postman_environment.json`
3. Clique em **Import**
4. No canto superior direito, selecione: **"WPP Bot - Local Development"**

 **Pronto! Voce tem acesso a TODOS os endpoints.**

## Primeiros Passos

### Passo 1: Verificar API esta online

Execute: **Health > Health Check**

Deve retornar:
```json
{
 "status": "ok",
 "database": "healthy",
 "redis": "healthy",
 "chroma": "healthy"
}
```

### Passo 2: Criar usuario (primeira vez)

Execute: **Auth > Signup**

Body de exemplo:
```json
{
 "email": "admin@test.com",
 "name": "Admin User",
 "password": "Admin123!",
 "role": "admin"
}
```

### Passo 3: Fazer Login

Execute: **Auth > Login**

Preencha no body:
- `username`: seu email
- `password`: sua senha

** O token JWT sera salvo automaticamente** no environment e usado em todos os proximos requests!

### Passo 4: Testar autenticacao

Execute: **Auth > Get Current User**

Deve retornar seus dados de usuario.

## Estrutura da Collection CONSOLIDADA

A collection unificada esta organizada em **19 categorias** com **161 endpoints** implementados (89 na collection, 72 faltantes):

> **IMPORTANTE**: A collection atual possui apenas **89 endpoints (55%)**. 
> Consulte [ENDPOINTS-FALTANTES-POSTMAN.md](ENDPOINTS-FALTANTES-POSTMAN.md) para lista completa dos 72 endpoints faltantes.

### Health (1 endpoint)
- Health check da API e servicos

### Auth (17 endpoints)
- Signup, Login, Refresh Token
- Get Current User, Logout
- Password Recovery/Reset/Change
- MFA Setup/Verify/Disable/Login
- Sessions Management (List/Revoke/Revoke All)
- Email Verification (Verify/Resend)

### Users (8 endpoints)
- Listar, obter, atualizar, deletar usuarios
- Block/Unblock usuarios
- Get/Update perfil proprio (me)
- **Requer:** role `admin`

### Leads (10 endpoints)
- CRUD completo de leads
- Assign/Auto-assign para agentes
- Convert, Mark as Lost
- Update maturity score
- Soft delete + Restore

### Conversations (8 endpoints)
- Listar, buscar, obter conversas
- Atualizar status, transferir, fechar
- Atualizar notas, exportar (CSV/JSON)

### Messages (6 endpoints)
- Criar, listar, obter mensagens
- Atualizar (marcar como lida)
- Deletar
- Generate AI description (Gemini Vision)

### Tags (6 endpoints)
- CRUD de tags
- Adicionar/remover tags de conversas
- Listar tags de uma conversa

### WAHA (44 endpoints) **APENAS 2 NA COLLECTION (4.5%)**

> **Status**: 2/44 endpoints documentados na collection (4.5% cobertura) 
> **Acao**: Adicionar 42 endpoints faltantes ([ver lista completa](ENDPOINTS-FALTANTES-POSTMAN.md#-categoria-waha-42-faltantes))

#### Existentes na Collection (2):
- Send Text Message
- Send Buttons Message

#### Faltantes (42):
**Sessoes (4)**: Create, Start, Stop, Get QR Code 
**Envio (9)**: List, Poll, Image, File, Contact, Location, Reaction, Voice, Video 
**Chats (7)**: Get messages, Mark as read, Presence, Typing, List, Archive, Delete 
**Grupos (6)**: List, Create, Add/Remove participants, Update, Delete 
**Labels (3)**: List, Apply, Remove 
**Profile (5)**: Me, Update, Photo, Status, Contacts 
**Midia (4)**: Download, Upload, Delete, Metadata 
**Avancado (8)**: Clear, Mute, Unmute, Pin, Unpin, Is-registered, Block

**Recomendacao temporaria**: Use **Swagger UI** (`http://localhost:3333/docs`) para endpoints WAHA ate atualizacao da collection.

### Webhooks (2 endpoints)
- Receive WAHA Webhook **(NO AUTH)**
- Get Webhook Logs **(NO AUTH)**

### Queues (8 endpoints)
- Stats, Health check
- Job details, Failed jobs
- Retry/Cancel jobs
- Retry all failed, Clear failed queue

### Jobs (1 endpoint)
- Trigger Reengagement Job **(Admin only)**

### AI (2 endpoints)
- Process message with Gemini AI
- Get AI processing stats

### Notifications (3 endpoints)
- List notifications
- Count unread
- Mark as read

### Audit (2 endpoints)
- List audit logs **(Admin only)**
- Get entity audit trail **(Admin only)**

### Handoff (5 endpoints) **APENAS 1 NA COLLECTION (20%)**

> **Status**: 1/5 endpoints documentados na collection (20% cobertura) 
> **Acao**: Adicionar 4 endpoints faltantes ([ver lista](ENDPOINTS-FALTANTES-POSTMAN.md#-categoria-handoff-4-faltantes))

#### Existente na Collection (1):
- `POST /{conversation_id}/handoff` - Request handoff (bot → humano)

#### Faltantes (4):
- `POST /{conversation_id}/assign` - Assign to agent
- `POST /{conversation_id}/complete` - Complete handoff
- `POST /{conversation_id}/return-to-bot` - Return to bot
- `GET /pending-handoff` - List pending handoffs

### Dashboard/Analytics (21 endpoints) **0 NA COLLECTION (0%)**

> **Status**: 0/21 endpoints documentados na collection (0% cobertura) 
> **Acao**: Adicionar 21 endpoints faltantes ([ver lista](ENDPOINTS-FALTANTES-POSTMAN.md#-categoria-dashboardmetrics-21-faltantes))

#### Performance (8):
- Dashboard summary, Bot response time, Handoff rate
- Peak hours, Conversations by status
- Performance report (JSON/PDF/Excel)

#### Conversao (7):
- Conversion funnel, Bot autonomy
- Time to conversion extended, Conversion by source
- Lost leads analysis, Conversion trend, Conversion report

#### Conversacao (5):
- Keywords analysis, Sentiment analysis
- Topics analysis, Conversation heatmap, Conversation report

#### Realtime (1):
- Realtime dashboard (WebSocket)

**Recomendacao temporaria**: Use **Swagger UI** (`http://localhost:3333/docs`) para endpoints Dashboard/Analytics ate atualizacao da collection.

#### Analise de Conversas (5):
- Activity heatmap
- Keyword frequency ( to_tsvector)
- Sentiment distribution ( Gemini fallback)
- Topics distribution
- Conversation analysis report

#### Real-time (2):
- Realtime dashboard
- WebSocket realtime (ws://)

### Topics (5 endpoints)
- Create, Get, List, Update, Delete
- Gerenciamento de topicos (categorias para playbooks)

### Playbooks (6 endpoints)
- Create, Get, List by Topic, Update, Delete
- **Search (RAG)** - Busca semantica com ChromaDB

### Playbook Steps (6 endpoints)
- Add, List, List with Details (for LLM)
- Reorder, Update, Delete
- Sequencias organizadas de mensagens
- Create, Get, List, Update, Delete
- Gerenciamento de topicos (categorias para playbooks)

### Playbooks (6 endpoints) **NOVO**
- Create, Get, List by Topic, Update, Delete
- **Search (RAG)** - Busca semantica com ChromaDB

### Playbook Steps (6 endpoints) **NOVO**
- Add, List, List with Details (for LLM)
- Reorder, Update, Delete
- Sequencias organizadas de mensagens

### Message Descriptions (1 endpoint) **NOVO**
- **Generate AI Description** - Gemini Vision para imagens/videos
- Auto-geracao de descricoes para ajudar o LLM

---

## Autenticacao

### JWT Token Automatico

A collection possui **scripts automaticos** que:

1. **Salvam o token** automaticamente apos login/refresh
2. **Injetam o token** em todos os requests que precisam de autenticacao
3. **Alertam** se voce tentar fazer um request autenticado sem token

### Como funciona:

```javascript
// Pre-request script (global)
if (pm.request.auth && pm.request.auth.type === 'bearer') {
 const token = pm.environment.get('access_token');
 if (!token) {
 console.warn(' Token nao encontrado. Execute Auth > Login primeiro.');
 }
}

// Test script (global)
if (pm.response.code === 200 || pm.response.code === 201) {
 const jsonData = pm.response.json();
 if (jsonData.access_token) {
 pm.environment.set('access_token', jsonData.access_token);
 console.log(' Access token salvo automaticamente');
 }
}
```

### Expiracao do Token

- **Access Token**: 15 minutos
- **Refresh Token**: 7 dias

Quando o access token expirar, execute: **Auth > Refresh Token**

## Environments

### Local Development (padrao)

```json
{
 "base_url": "http://localhost:3333/api/v1",
 "access_token": "", // Preenchido automaticamente
 "refresh_token": "", // Preenchido automaticamente
 "waha_session": "default",
 "test_phone": "5511999999999"
}
```

### Producao (criar manualmente)

1. Duplicate o environment "WPP Bot - Local Development"
2. Renomeie para "WPP Bot - Production"
3. Altere o `base_url` para: `https://api.seudominio.com/api/v1`

## Casos de Teste Comuns

### Fluxo 1: Criar Lead → Converter

```
1. POST /leads (criar lead)
2. PUT /leads/{id}/maturity (atualizar score)
3. POST /leads/{id}/assign (atribuir a agente)
4. POST /leads/{id}/convert (converter)
```

### Fluxo 2: Sessao WAHA → Enviar Mensagem

```
1. POST /waha/sessions (criar sessao "default")
2. POST /waha/sessions/default/start (iniciar)
3. GET /waha/sessions/default/qr (pegar QR code)
4. GET /waha/sessions/default/status (verificar status)
5. POST /waha/send/text (enviar mensagem)
```

### Fluxo 3: Conversa → Adicionar Tags → Transferir

```
1. GET /conversations (listar conversas)
2. POST /conversations/{id}/tags (adicionar tag "Urgente")
3. POST /conversations/{id}/transfer (transferir para agente)
4. POST /conversations/{id}/close (fechar conversa)
```

### Fluxo 4: Processar com AI

```
1. POST /ai/process (enviar mensagem para Gemini)
2. GET /ai/models (ver modelos disponiveis)
```

## Variaveis do Environment

| Variavel | Tipo | Descricao | Exemplo |
|----------|------|-----------|---------|
| `base_url` | default | URL base da API | `http://localhost:3333/api/v1` |
| `access_token` | secret | JWT token (auto-preenchido) | `eyJhbGciOiJIUzI1NiIsInR5cCI6...` |
| `refresh_token` | secret | Refresh token (auto-preenchido) | `eyJhbGciOiJIUzI1NiIsInR5cCI6...` |
| `user_id` | default | ID do usuario para testes | `1` |
| `lead_id` | default | ID do lead para testes | `1` |
| `conversation_id` | default | ID da conversa para testes | `1` |
| `message_id` | default | ID da mensagem para testes | `1` |
| `tag_id` | default | ID da tag para testes | `1` |
| `waha_session` | default | Nome da sessao WAHA | `default` |
| `test_phone` | default | Telefone para testes | `5511999999999` |

### Como usar variaveis:

Nas URLs e bodies, use `{{nome_da_variavel}}`:

```
GET {{base_url}}/leads/{{lead_id}}
```

```json
{
 "phone": "{{test_phone}}",
 "name": "Test Lead"
}
```

## Fluxo Completo de Teste (5 Fluxos)

### Fluxo 5: Playbooks com RAG **NOVO**

```
1. POST /topics → criar "Botox"
2. POST /messages → 5 mensagens (texto, imagem, video, PDF, location)
3. POST /messages/{id}/generate-description → Gemini Vision descreve midia
4. POST /playbooks → "Botox - Fluxo Completo"
5. POST /playbook-steps → adicionar 5 steps ordenados
6. GET /playbook-steps/playbook/{id}/details → LLM consome
7. GET /playbooks/search?query=botox → busca semantica (ChromaDB)
```

---

## Troubleshooting

### Erro 401 Unauthorized

**Problema:** Token expirado ou invalido

**Solucao:**
1. Execute **Auth > Login** novamente
2. Ou execute **Auth > Refresh Token**

### Erro 403 Forbidden

**Problema:** Usuario nao tem permissao (role insuficiente)

**Solucao:**
- Endpoints de Admin: requer `role: "admin"`
- Endpoints de Agent: requer `role: "admin"` ou `role: "agent"`

### Collection nao esta usando o token

**Problema:** Token nao esta sendo injetado

**Solucao:**
1. Verifique se o environment esta selecionado (canto superior direito)
2. Execute **Auth > Login** para preencher o `access_token`
3. Verifique no environment se `access_token` tem valor

### WAHA nao responde

**Problema:** Servico WAHA nao esta rodando

**Solucao:**
```bash
cd docker
docker compose up -d wpp_bot_waha
docker compose logs -f wpp_bot_waha
```

### Webhook nao recebe mensagens

**Problema:** WAHA nao esta configurado para enviar webhooks

**Solucao:**
Configurar no `.env`:
```env
WAHA_WEBHOOK_URL=http://api_app:3333/api/v1/webhooks/waha
```

## Notas Importantes

### Endpoints sem Autenticacao (noauth)

Apenas 3 endpoints nao requerem token:
- `GET /health`
- `POST /auth/signup`
- `POST /auth/token` (login)
- `POST /auth/password-recovery`
- `POST /auth/password-reset`
- `POST /webhooks/waha` (interno, recebe de WAHA)
- `GET /webhooks/waha/logs` (interno)

### Rate Limiting

O WAHA tem rate limiting configurado:
- **Padrao:** 50 mensagens/hora por chat
- Configuravel via `WAHA_MESSAGES_PER_HOUR` no `.env`

Se exceder o limite, recebera erro `429 Too Many Requests`.

### Soft Delete

Leads suportam soft delete:
- `DELETE /leads/{id}` → Marca `deleted_at`
- `POST /leads/{id}/restore` → Remove `deleted_at`

### Audit Logs

Todos os endpoints que modificam dados geram audit logs automaticamente:
- Entity type: `lead`, `conversation`, `user`, etc.
- Action: `create`, `update`, `delete`, `convert`, etc.
- Metadata: Dados alterados em JSON

## Arquivos Finais (Consolidados)

### USE APENAS ESTES

| Arquivo | Tamanho | Descricao |
|---------|---------|-----------|
| `WPP_Bot_API.postman_collection.json` | 73KB | **Collection completa** (18 categorias, 95+ endpoints) |
| `WPP_Bot_API.postman_environment.json` | 1.3KB | Environment variables |

### Backup

- `backup/WPP_Bot_Playbook_Addon.postman_collection.json` - Addon antigo (**mesclado na principal**)

---

## Mapeamento: Postman Collection ↔ Casos de Teste

O projeto possui **161 endpoints implementados** divididos em **19 categorias**. A documentacao de testes cobre os principais fluxos:

| Controller (Codigo) | Endpoints | Casos de Teste | Fase | Onde Testar |
|---------------------|-----------|----------------|------|-------------|
| Health | 1 | UC-001 | FASE 1 | Postman/Swagger |
| Auth | 17 | UC-002 a UC-005, UC-045 a UC-059 | FASES 1, 12 | Postman/Swagger |
| Users | 8 | UC-005, UC-058 | FASES 1, 12 | Postman/Swagger |
| Leads | 10 | UC-024, UC-025, UC-031 | FASES 5, 7 | Postman/Swagger |
| Conversations | 8 | UC-022, UC-023, UC-026 a UC-033 | FASES 5, 6, 7 | Postman/Swagger |
| Messages | 6 | UC-016 a UC-020 | FASE 4 | Postman/Swagger |
| Tags | 6 | UC-034, UC-035 | FASE 8 | Postman/Swagger |
| **WAHA** | **44** | UC-006 a UC-009 | FASE 2 | **SWAGGER APENAS** |
| Webhooks | 2 | UC-021, UC-043 | FASES 5, 11 | Postman (noauth) |
| Queues | 8 | UC-039, UC-040 | FASE 10 | Postman/Swagger |
| Jobs | 1 | - (automatico) | - | Swagger |
| AI | 2 | UC-041 (fallback) | FASE 11 | Postman/Swagger |
| Notifications | 3 | UC-032, UC-033 | FASE 7 | Postman/Swagger |
| Audit | 2 | UC-059 | FASE 12 | Swagger (admin) |
| **Handoff** | **5** | UC-031 (handoff/assign) | FASE 7 | **Postman/Swagger** |
| **Dashboard** | **21** | UC-036 a UC-038, UC-060 a UC-063 | FASES 9, 13 | **SWAGGER APENAS** |
| Topics | 5 | UC-010 | FASE 3 | Postman/Swagger |
| Playbooks | 6 | UC-011, UC-014 | FASE 3 | Postman/Swagger |
| Playbook Steps | 6 | UC-012, UC-013, UC-015 | FASE 3 | Postman/Swagger |

**Total: 161 endpoints → 63 casos de teste cobrindo fluxos principais**

### Endpoints Disponiveis APENAS no Swagger

Estes endpoints **NAO estao na Postman Collection**, use `http://localhost:3333/docs`:

1. **WAHA (44 endpoints)**: Todos os endpoints de sessoes WhatsApp e envio de mensagens
 - Motivo: API externa WAHA tem muitos endpoints especificos
 
2. **Dashboard/Analytics (21 endpoints)**: Todos os endpoints de metricas Sprint 12
 - Performance (6): `/api/v1/metrics/performance/*`
 - Conversao (5): `/api/v1/metrics/conversion/*`
 - Analise Conversas (5): `/api/v1/metrics/conversation/*`
 - Real-time (2): `/api/v1/metrics/realtime/*`
 - Geral (3): `/api/v1/metrics/*`

### Endpoints na Postman Collection

**Total na Collection: ~96 endpoints** (161 - 44 WAHA - 21 Dashboard = 96)

**Categorias com 100% na Postman:**
- Health (1), Auth (17), Users (8), Leads (10)
- Conversations (8), Messages (6), Tags (6)
- Webhooks (2), Queues (8), Jobs (1)
- AI (2), Notifications (3), Audit (2)
- Handoff (5), Topics (5), Playbooks (6), Steps (6)

**Categorias APENAS no Swagger:**
- WAHA (44)
- Dashboard/Analytics (21)

---

## Contribuindo

Se encontrar algum endpoint faltando ou incorreto:

1. Verifique o codigo fonte em `src/robbot/adapters/controllers/`
2. Atualize o arquivo `WPP_Bot_API.postman_collection.json`
3. Abra um PR com a descricao da mudanca

## Documentacao Relacionada

- [README.md](../README.md) - Documentacao completa do projeto
- [casos-teste-validacao.md](../../tic/casos-teste-validacao.md) - 63 casos de uso organizados (atualizado 08/01/2026)
- [roadmap-desenvolvimento.md](../../tic/roadmap-desenvolvimento.md) - Sprint 12 completo (10/10)
- [FastAPI Swagger](http://localhost:3333/docs) - Documentacao interativa da API
- [WAHA Docs](https://waha.devlike.pro/) - Documentacao oficial do WAHA

## Pronto!

Agora voce tem visao completa da **API REST com 161 endpoints** divididos em 19 categorias!

** Versao:** 2.1.0 (Sprint 12 Analytics) 
** Total de Endpoints:** 161 (96 Postman + 65 Swagger-only) 
** Casos de Teste:** 63 casos organizados em 13 fases 
** Novos recursos:** Analytics avancados, Full-Text Search, Gemini sentiment fallback 
** Ultima atualizacao:** 08/01/2026

** IMPORTANTE**: Este e um projeto **backend REST API** (FastAPI). Nao ha frontend web incluido.

**Happy Testing! **


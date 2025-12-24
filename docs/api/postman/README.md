# 📮 Postman Collection - WPP Bot API

> **Collection UNIFICADA** para testar todos os endpoints da API WhatsApp Bot

## 📦 Arquivos Disponíveis

### ✅ Arquivos Principais (USE ESTES)

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| **WPP_Bot_API.postman_collection.json** | Collection completa (90+ endpoints) | ✅ **Recomendado** |
| **WPP_Bot_API.postman_environment.json** | Environment (local dev) | ✅ **Necessário** |

### 📁 Arquivos Legados (Backup)

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| WPP_Bot_Playbook_Addon.postman_collection.json | Addon antigo de playbooks | ⚠️ **Deprecado** (mesclado na principal) |

> **⚠️ Nota**: O addon de playbooks foi mesclado na collection principal. Você **NÃO precisa** importar 2 collections.

---

## 📥 Como Importar

### 1️⃣ Importar Collection Principal

1. Abra o Postman
2. Clique em **Import** (canto superior esquerdo)
3. Selecione **apenas** o arquivo: `WPP_Bot_API.postman_collection.json`
4. Clique em **Import**

### 2️⃣ Importar Environment

1. Clique em **Import** novamente
2. Selecione o arquivo: `WPP_Bot_API.postman_environment.json`
3. Clique em **Import**
4. No canto superior direito, selecione: **"WPP Bot - Local Development"**

✅ **Pronto! Você tem acesso a TODOS os endpoints.**

## 🚀 Primeiros Passos

### Passo 1: Verificar API está online

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

### Passo 2: Criar usuário (primeira vez)

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

**✅ O token JWT será salvo automaticamente** no environment e usado em todos os próximos requests!

### Passo 4: Testar autenticação

Execute: **Auth > Get Current User**

Deve retornar seus dados de usuário.

## 📋 Estrutura da Collection CONSOLIDADA

A collection unificada está organizada em **18 categorias** com 95+ endpoints:

### 🏥 Health (1 endpoint)
- Health check da API e serviços

### 🔐 Auth (7 endpoints)
- Signup, Login, Refresh Token
- Get Current User, Logout
- Password Recovery/Reset

### 👥 Users (4 endpoints)
- Listar, obter, atualizar, deletar usuários
- **Requer:** role `admin`

### 🎯 Leads (10 endpoints)
- CRUD completo de leads
- Assign/Auto-assign para agentes
- Convert, Mark as Lost
- Soft delete + Restore

### 💬 Conversations (8 endpoints)
- Listar, buscar, obter conversas
- Atualizar status, transferir, fechar
- Atualizar notas, exportar (CSV/JSON)

### 📨 Messages (5 endpoints)
- Criar, listar, obter mensagens
- Atualizar (marcar como lida)
- Deletar

### 🏷️ Tags (6 endpoints)
- CRUD de tags
- Adicionar/remover tags de conversas
- Listar tags de uma conversa

### 📱 WAHA (19 endpoints)
#### Sessões WhatsApp:
- Create, Start, Stop, Restart
- Get Status, QR Code, Logout

#### Envio de Mensagens:
- Send Text, Image, File, Location
- Send Voice, Video, Contact
- Send Buttons, List, Poll
- Forward, Edit messages
- Send "Seen" (read receipt)

### 🔗 Webhooks (2 endpoints)
- Receive WAHA Webhook **(NO AUTH)**
- Get Webhook Logs **(NO AUTH)**

### 🔄 Queues (8 endpoints)
- Stats, Health check
- Job details, Failed jobs
- Retry/Cancel jobs
- Clear failed queue

### ⚙️ Jobs (1 endpoint)
- Trigger Reengagement Job **(Admin only)**

### 🤖 AI (2 endpoints)
- Process message with Gemini AI
- Get AI processing stats

### 🔔 Notifications (3 endpoints)
- List notifications
- Count unread
- Mark as read

### 📋 Audit (2 endpoints)
- List audit logs **(Admin only)**
- Get entity audit trail **(Admin only)**

### 🎯 Topics (5 endpoints) ⭐ **NOVO**
- Create, Get, List, Update, Delete
- Gerenciamento de tópicos (categorias para playbooks)

### 📚 Playbooks (6 endpoints) ⭐ **NOVO**
- Create, Get, List by Topic, Update, Delete
- **Search (RAG)** - Busca semântica com ChromaDB

### 📝 Playbook Steps (6 endpoints) ⭐ **NOVO**
- Add, List, List with Details (for LLM)
- Reorder, Update, Delete
- Sequências organizadas de mensagens

### 🤖 Message Descriptions (1 endpoint) ⭐ **NOVO**
- **Generate AI Description** - Gemini Vision para imagens/vídeos
- Auto-geração de descrições para ajudar o LLM

---

## 🔑 Autenticação

### JWT Token Automático

A collection possui **scripts automáticos** que:

1. **Salvam o token** automaticamente após login/refresh
2. **Injetam o token** em todos os requests que precisam de autenticação
3. **Alertam** se você tentar fazer um request autenticado sem token

### Como funciona:

```javascript
// Pre-request script (global)
if (pm.request.auth && pm.request.auth.type === 'bearer') {
    const token = pm.environment.get('access_token');
    if (!token) {
        console.warn('⚠️ Token não encontrado. Execute Auth > Login primeiro.');
    }
}

// Test script (global)
if (pm.response.code === 200 || pm.response.code === 201) {
    const jsonData = pm.response.json();
    if (jsonData.access_token) {
        pm.environment.set('access_token', jsonData.access_token);
        console.log('✅ Access token salvo automaticamente');
    }
}
```

### Expiração do Token

- **Access Token**: 15 minutos
- **Refresh Token**: 7 dias

Quando o access token expirar, execute: **Auth > Refresh Token**

## 🌍 Environments

### Local Development (padrão)

```json
{
  "base_url": "http://localhost:3333/api/v1",
  "access_token": "",  // Preenchido automaticamente
  "refresh_token": "", // Preenchido automaticamente
  "waha_session": "default",
  "test_phone": "5511999999999"
}
```

### Produção (criar manualmente)

1. Duplicate o environment "WPP Bot - Local Development"
2. Renomeie para "WPP Bot - Production"
3. Altere o `base_url` para: `https://api.seudominio.com/api/v1`

## 🧪 Casos de Teste Comuns

### Fluxo 1: Criar Lead → Converter

```
1. POST /leads (criar lead)
2. PUT /leads/{id}/maturity (atualizar score)
3. POST /leads/{id}/assign (atribuir a agente)
4. POST /leads/{id}/convert (converter)
```

### Fluxo 2: Sessão WAHA → Enviar Mensagem

```
1. POST /waha/sessions (criar sessão "default")
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
2. GET /ai/models (ver modelos disponíveis)
```

## 📊 Variáveis do Environment

| Variável | Tipo | Descrição | Exemplo |
|----------|------|-----------|---------|
| `base_url` | default | URL base da API | `http://localhost:3333/api/v1` |
| `access_token` | secret | JWT token (auto-preenchido) | `eyJhbGciOiJIUzI1NiIsInR5cCI6...` |
| `refresh_token` | secret | Refresh token (auto-preenchido) | `eyJhbGciOiJIUzI1NiIsInR5cCI6...` |
| `user_id` | default | ID do usuário para testes | `1` |
| `lead_id` | default | ID do lead para testes | `1` |
| `conversation_id` | default | ID da conversa para testes | `1` |
| `message_id` | default | ID da mensagem para testes | `1` |
| `tag_id` | default | ID da tag para testes | `1` |
| `waha_session` | default | Nome da sessão WAHA | `default` |
| `test_phone` | default | Telefone para testes | `5511999999999` |

### Como usar variáveis:

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

## 🧪 Fluxo Completo de Teste (5 Fluxos)

### Fluxo 5: Playbooks com RAG ⭐ **NOVO**

```
1. POST /topics → criar "Botox"
2. POST /messages → 5 mensagens (texto, imagem, vídeo, PDF, location)
3. POST /messages/{id}/generate-description → Gemini Vision descreve mídia
4. POST /playbooks → "Botox - Fluxo Completo"
5. POST /playbook-steps → adicionar 5 steps ordenados
6. GET /playbook-steps/playbook/{id}/details → LLM consome
7. GET /playbooks/search?query=botox → busca semântica (ChromaDB)
```

---

## 🐛 Troubleshooting

### ❌ Erro 401 Unauthorized

**Problema:** Token expirado ou inválido

**Solução:**
1. Execute **Auth > Login** novamente
2. Ou execute **Auth > Refresh Token**

### ❌ Erro 403 Forbidden

**Problema:** Usuário não tem permissão (role insuficiente)

**Solução:**
- Endpoints de Admin: requer `role: "admin"`
- Endpoints de Agent: requer `role: "admin"` ou `role: "agent"`

### ❌ Collection não está usando o token

**Problema:** Token não está sendo injetado

**Solução:**
1. Verifique se o environment está selecionado (canto superior direito)
2. Execute **Auth > Login** para preencher o `access_token`
3. Verifique no environment se `access_token` tem valor

### ❌ WAHA não responde

**Problema:** Serviço WAHA não está rodando

**Solução:**
```bash
cd docker
docker compose up -d wpp_bot_waha
docker compose logs -f wpp_bot_waha
```

### ❌ Webhook não recebe mensagens

**Problema:** WAHA não está configurado para enviar webhooks

**Solução:**
Configurar no `.env`:
```env
WAHA_WEBHOOK_URL=http://api_app:3333/api/v1/webhooks/waha
```

## 📝 Notas Importantes

### Endpoints sem Autenticação (noauth)

Apenas 3 endpoints não requerem token:
- `GET /health`
- `POST /auth/signup`
- `POST /auth/token` (login)
- `POST /auth/password-recovery`
- `POST /auth/password-reset`
- `POST /webhooks/waha` (interno, recebe de WAHA)
- `GET /webhooks/waha/logs` (interno)

### Rate Limiting

O WAHA tem rate limiting configurado:
- **Padrão:** 50 mensagens/hora por chat
- Configurável via `WAHA_MESSAGES_PER_HOUR` no `.env`

Se exceder o limite, receberá erro `429 Too Many Requests`.

### Soft Delete

Leads suportam soft delete:
- `DELETE /leads/{id}` → Marca `deleted_at`
- `POST /leads/{id}/restore` → Remove `deleted_at`

### Audit Logs

Todos os endpoints que modificam dados geram audit logs automaticamente:
- Entity type: `lead`, `conversation`, `user`, etc.
- Action: `create`, `update`, `delete`, `convert`, etc.
- Metadata: Dados alterados em JSON

## 📦 Arquivos Finais (Consolidados)

### ✅ USE APENAS ESTES

| Arquivo | Tamanho | Descrição |
|---------|---------|-----------|
| `WPP_Bot_API.postman_collection.json` | 73KB | **Collection completa** (18 categorias, 95+ endpoints) |
| `WPP_Bot_API.postman_environment.json` | 1.3KB | Environment variables |

### 📁 Backup

- `backup/WPP_Bot_Playbook_Addon.postman_collection.json` - Addon antigo (**mesclado na principal**)

---

## 🤝 Contribuindo

Se encontrar algum endpoint faltando ou incorreto:

1. Verifique o código fonte em `src/robbot/adapters/controllers/`
2. Atualize o arquivo `WPP_Bot_API.postman_collection.json`
3. Abra um PR com a descrição da mudança

## 📚 Documentação Relacionada

- [README.md](../README.md) - Documentação completa do projeto
- [PLANO_TESTES_CASOS_USO.md](../PLANO_TESTES_CASOS_USO.md) - 44 casos de uso organizados
- [FastAPI Swagger](http://localhost:3333/docs) - Documentação interativa da API
- [WAHA Docs](https://waha.devlike.pro/) - Documentação oficial do WAHA

## 🎉 Pronto!

Agora você tem uma **collection ÚNICA e consolidada** para testar todos os 95+ endpoints da API!

**📊 Versão:** 2.0.0 (Consolidada)  
**🆕 Novos recursos:** Topics, Playbooks (RAG), Steps, AI Descriptions  
**🗓️ Última atualização:** Dezembro 2024

**Happy Testing! 🚀**

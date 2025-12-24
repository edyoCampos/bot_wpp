# 📋 PLANO DE TESTES COMPLETO - Bot WhatsApp Clínica GO

> **Objetivo**: Validar todos os casos de uso da aplicação de forma organizada e cronológica, desde autenticação até processamento completo de conversas.

---

## 🎯 Estratégia de Testes

### Ferramentas Utilizadas
- **Swagger UI**: http://localhost:3333/docs (testes interativos)
- **Postman Collection**: `postman/WPP_Bot_API.postman_collection.json`
- **Postman Environment**: `postman/WPP_Bot_API.postman_environment.json`

### Princípios
1. **Testes sequenciais**: Seguir ordem cronológica do fluxo real
2. **Dados isolados**: Cada caso de uso usa dados específicos
3. **Validação completa**: Status code, schema, regras de negócio
4. **Documentação**: Registrar resultados esperados vs obtidos

---

## 📚 FASE 1: INFRAESTRUTURA E AUTENTICAÇÃO

### UC-001: Health Check do Sistema
**Endpoint**: `GET /api/v1/health`  
**Objetivo**: Validar que todos os componentes estão funcionando

**Pré-requisitos**: Sistema inicializado (docker-compose up)

**Passos**:
1. Acessar http://localhost:3333/api/v1/health
2. Verificar resposta

**Resultado Esperado**:
```json
{
  "status": "ok",
  "components": {
    "database": {"ok": true, "error": null},
    "redis": {"ok": true, "error": null},
    "waha": {"ok": true, "error": null}
  }
}
```

**Validações**:
- [x] Status code: 200
- [x] Todos os components.ok = true
- [x] Latência < 1s

---

### UC-002: Signup - Criar Usuário ADMIN
**Endpoint**: `POST /api/v1/auth/signup`  
**Objetivo**: Criar primeiro usuário administrador

**Payload**:
```json
{
  "email": "admin@clinicago.com.br",
  "password": "Admin@2025!Secure",
  "role": "admin"
}
```

**Resultado Esperado**:
```json
{
  "id": "uuid-gerado",
  "email": "admin@clinicago.com.br",
  "role": "admin",
  "is_active": true,
  "created_at": "2025-12-17T...",
  "updated_at": "2025-12-17T..."
}
```

**Validações**:
- [x] Status code: 201
- [x] Senha não retornada no response
- [x] UUID válido gerado
- [x] role = "admin"
- [x] is_active = true

---

### UC-003: Login - Obter Access Token
**Endpoint**: `POST /api/v1/auth/token`  
**Objetivo**: Autenticar e obter JWT token

**Payload (form-data)**:
```
username: admin@clinicago.com.br
password: Admin@2025!Secure
```

**Resultado Esperado**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Validações**:
- [x] Status code: 200
- [x] access_token presente (JWT válido)
- [x] token_type = "bearer"
- [x] expires_in = 1800 (30 min)

**Ação Pós-Teste**:
```bash
# Salvar token para próximos testes
export TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# No Postman: Salvar em Environment variable {{auth_token}}
```

---

### UC-004: Validar Token - Get Current User
**Endpoint**: `GET /api/v1/auth/me`  
**Objetivo**: Validar que token está funcionando

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Resultado Esperado**:
```json
{
  "id": "uuid-do-admin",
  "email": "admin@clinicago.com.br",
  "role": "admin",
  "is_active": true
}
```

**Validações**:
- [x] Status code: 200
- [x] Dados do usuário autenticado retornados
- [x] role = "admin"

---

### UC-005: Criar Usuário SECRETÁRIA
**Endpoint**: `POST /api/v1/auth/signup`  
**Objetivo**: Criar usuário com permissões limitadas

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Payload**:
```json
{
  "email": "secretaria@clinicago.com.br",
  "password": "Secret@2025!Safe",
  "role": "user"
}
```

**Resultado Esperado**:
```json
{
  "id": "uuid-gerado",
  "email": "secretaria@clinicago.com.br",
  "role": "user",
  "is_active": true
}
```

**Validações**:
- [x] Status code: 201
- [x] role = "user" (não "admin")
- [x] UUID diferente do admin

---

## 📚 FASE 2: INTEGRAÇÃO WAHA (WhatsApp)

### UC-006: Criar Sessão WhatsApp
**Endpoint**: `POST /api/v1/waha/sessions`  
**Objetivo**: Criar nova sessão WhatsApp via WAHA

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Payload**:
```json
{
  "name": "clinica_go_dra_andrea",
  "config": {
    "webhooks": [
      {
        "url": "http://api:3333/api/v1/webhooks/waha",
        "events": ["message", "message.any"]
      }
    ]
  }
}
```

**Resultado Esperado**:
```json
{
  "id": "uuid-gerado",
  "name": "clinica_go_dra_andrea",
  "status": "STOPPED",
  "qr": null,
  "webhook_url": "http://api:3333/api/v1/webhooks/waha",
  "created_at": "2025-12-17T..."
}
```

**Validações**:
- [x] Status code: 201
- [x] Session criada com nome correto
- [x] Webhook configurado
- [x] status inicial = "STOPPED"

---

### UC-007: Iniciar Sessão WhatsApp (Get QR Code)
**Endpoint**: `POST /api/v1/waha/sessions/{session_name}/start`  
**Objetivo**: Iniciar sessão e obter QR Code

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Path Params**:
```
session_name: clinica_go_dra_andrea
```

**Resultado Esperado**:
```json
{
  "name": "clinica_go_dra_andrea",
  "status": "SCAN_QR_CODE",
  "qr": "data:image/png;base64,iVBORw0KGgoAAAANSU...",
  "message": "Scan QR code to authenticate"
}
```

**Validações**:
- [x] Status code: 200
- [x] status mudou para "SCAN_QR_CODE"
- [x] qr code presente (base64)

**Ação Manual**:
```
1. Abrir WhatsApp Web no celular da clínica
2. Escanear QR code exibido no Swagger/Postman
3. Aguardar autenticação (status muda para "WORKING")
```

---

### UC-008: Verificar Status da Sessão
**Endpoint**: `GET /api/v1/waha/sessions/{session_name}`  
**Objetivo**: Confirmar que sessão está ativa

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Path Params**:
```
session_name: clinica_go_dra_andrea
```

**Resultado Esperado**:
```json
{
  "id": "uuid-da-sessao",
  "name": "clinica_go_dra_andrea",
  "status": "WORKING",
  "qr": null,
  "webhook_url": "http://api:3333/api/v1/webhooks/waha"
}
```

**Validações**:
- [x] Status code: 200
- [x] status = "WORKING" (sessão ativa)
- [x] qr = null (já autenticado)

---

### UC-009: Listar Todas as Sessões
**Endpoint**: `GET /api/v1/waha/sessions`  
**Objetivo**: Obter lista de todas as sessões criadas

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Resultado Esperado**:
```json
[
  {
    "id": "uuid",
    "name": "clinica_go_dra_andrea",
    "status": "WORKING",
    "created_at": "2025-12-17T..."
  }
]
```

**Validações**:
- [x] Status code: 200
- [x] Array com pelo menos 1 sessão
- [x] Sessão criada presente na lista

---

## 📚 FASE 3: PLAYBOOKS (Mensagens Pré-Aprovadas)

### UC-010: Criar Tópico "Emagrecimento"
**Endpoint**: `POST /api/v1/topics`  
**Objetivo**: Criar categoria para organizar playbooks

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Payload**:
```json
{
  "name": "Emagrecimento",
  "description": "Tratamentos e procedimentos para perda de peso e emagrecimento saudável"
}
```

**Resultado Esperado**:
```json
{
  "id": "uuid-gerado",
  "name": "Emagrecimento",
  "description": "Tratamentos e procedimentos para perda de peso...",
  "playbook_count": 0,
  "created_at": "2025-12-17T..."
}
```

**Validações**:
- [x] Status code: 201
- [x] UUID válido gerado
- [x] playbook_count = 0 (ainda sem playbooks)

---

### UC-011: Criar Playbook "Consulta Inicial"
**Endpoint**: `POST /api/v1/playbooks`  
**Objetivo**: Criar sequência de mensagens para consulta inicial

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Payload**:
```json
{
  "name": "Consulta Inicial de Emagrecimento",
  "description": "Fluxo completo para agendamento de primeira consulta",
  "topic_id": "{{topic_id}}",
  "is_active": true,
  "tags": ["consulta", "agendamento", "emagrecimento", "primeira-consulta"]
}
```

**Resultado Esperado**:
```json
{
  "id": "uuid-gerado",
  "name": "Consulta Inicial de Emagrecimento",
  "topic_id": "uuid-do-topico",
  "is_active": true,
  "steps_count": 0,
  "created_at": "2025-12-17T..."
}
```

**Validações**:
- [x] Status code: 201
- [x] Playbook vinculado ao tópico
- [x] steps_count = 0 (ainda sem mensagens)

---

### UC-012: Adicionar Mensagem de Texto ao Playbook
**Endpoint**: `POST /api/v1/playbooks/{playbook_id}/steps`  
**Objetivo**: Criar primeira mensagem do fluxo

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Path Params**:
```
playbook_id: {{playbook_id}}
```

**Payload**:
```json
{
  "order": 1,
  "message_type": "text",
  "content": "Olá! Que bom que você está buscando cuidar da sua saúde! 🌟\n\nVamos agendar sua consulta com a Dra. Andrea Mondadori?\n\nTemos horários disponíveis essa semana. Me conta, qual período você prefere?\n\n📅 Manhã (8h-12h)\n📅 Tarde (14h-18h)",
  "delay_seconds": 0,
  "metadata": {
    "intent": "agendamento",
    "spin_phase": "situation"
  }
}
```

**Resultado Esperado**:
```json
{
  "id": "uuid-gerado",
  "playbook_id": "uuid-do-playbook",
  "order": 1,
  "message_type": "text",
  "content": "Olá! Que bom que...",
  "delay_seconds": 0,
  "created_at": "2025-12-17T..."
}
```

**Validações**:
- [x] Status code: 201
- [x] order = 1 (primeira mensagem)
- [x] message_type = "text"

---

### UC-013: Adicionar Mensagem com Imagem ao Playbook
**Endpoint**: `POST /api/v1/playbooks/{playbook_id}/steps`  
**Objetivo**: Adicionar mensagem com material visual

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Payload**:
```json
{
  "order": 2,
  "message_type": "image",
  "content": "Veja alguns resultados de pacientes que fizeram o acompanhamento:",
  "media_url": "https://exemplo.com/antes-depois.jpg",
  "delay_seconds": 3,
  "metadata": {
    "intent": "informacao",
    "spin_phase": "need_payoff"
  }
}
```

**Resultado Esperado**:
```json
{
  "id": "uuid-gerado",
  "playbook_id": "uuid-do-playbook",
  "order": 2,
  "message_type": "image",
  "media_url": "https://exemplo.com/antes-depois.jpg",
  "delay_seconds": 3
}
```

**Validações**:
- [x] Status code: 201
- [x] order = 2 (segunda mensagem)
- [x] media_url presente

---

### UC-014: Buscar Playbooks por Query Semântica
**Endpoint**: `GET /api/v1/playbooks/search?q=consulta agendamento`  
**Objetivo**: Validar busca semântica (ChromaDB)

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Query Params**:
```
q: consulta agendamento
limit: 5
```

**Resultado Esperado**:
```json
[
  {
    "id": "uuid-do-playbook",
    "name": "Consulta Inicial de Emagrecimento",
    "description": "Fluxo completo para agendamento...",
    "relevance_score": 0.87,
    "steps_count": 2,
    "topic": {
      "id": "uuid-do-topico",
      "name": "Emagrecimento"
    }
  }
]
```

**Validações**:
- [x] Status code: 200
- [x] Array ordenado por relevance_score
- [x] Playbook criado presente na lista
- [x] relevance_score entre 0 e 1

---

### UC-015: Obter Passos de um Playbook
**Endpoint**: `GET /api/v1/playbooks/{playbook_id}/steps`  
**Objetivo**: Listar todas as mensagens de um playbook

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Path Params**:
```
playbook_id: {{playbook_id}}
```

**Resultado Esperado**:
```json
[
  {
    "id": "uuid-step-1",
    "order": 1,
    "message_type": "text",
    "content": "Olá! Que bom que você está buscando...",
    "delay_seconds": 0
  },
  {
    "id": "uuid-step-2",
    "order": 2,
    "message_type": "image",
    "content": "Veja alguns resultados...",
    "media_url": "https://exemplo.com/antes-depois.jpg",
    "delay_seconds": 3
  }
]
```

**Validações**:
- [x] Status code: 200
- [x] Array ordenado por order ASC
- [x] 2 mensagens retornadas

---

## 📚 FASE 4: MENSAGENS E MÍDIA

### UC-016: Criar Mensagem de Texto Simples
**Endpoint**: `POST /api/v1/messages`  
**Objetivo**: Criar mensagem de texto no banco

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Payload**:
```json
{
  "type": "text",
  "text": "Olá, gostaria de informações sobre emagrecimento"
}
```

**Resultado Esperado**:
```json
{
  "id": "uuid-gerado",
  "type": "text",
  "text": "Olá, gostaria de informações sobre emagrecimento",
  "created_at": "2025-12-17T...",
  "updated_at": "2025-12-17T..."
}
```

**Validações**:
- [x] Status code: 201
- [x] UUID válido gerado
- [x] type = "text"

---

### UC-017: Criar Mensagem de Áudio (Transcrição Faster-Whisper)
**Endpoint**: `POST /api/v1/messages`  
**Objetivo**: Criar mensagem de áudio E transcrever automaticamente

**Headers**:
```
Authorization: Bearer {{auth_token}}
Content-Type: multipart/form-data
```

**Payload**:
```json
{
  "type": "voice",
  "file": {
    "mimetype": "audio/ogg",
    "filename": "audio_paciente_001.ogg",
    "url": "https://exemplo.com/audio_paciente_001.ogg"
  },
  "caption": null
}
```

**Resultado Esperado**:
```json
{
  "id": "uuid-gerado",
  "type": "voice",
  "file": {
    "mimetype": "audio/ogg",
    "filename": "audio_paciente_001.ogg",
    "url": "https://exemplo.com/audio_paciente_001.ogg"
  },
  "caption": null,
  "transcription": "olá eu gostaria de saber como funciona o tratamento de emagrecimento com a doutora andrea",
  "created_at": "2025-12-17T..."
}
```

**Validações**:
- [x] Status code: 201
- [x] transcription presente (Faster-Whisper)
- [x] Transcrição em português (pt-BR)
- [x] Processamento automático (sem chamada manual)

---

### UC-018: Criar Mensagem de Imagem (Análise BLIP-2)
**Endpoint**: `POST /api/v1/messages`  
**Objetivo**: Criar mensagem de imagem E analisar com BLIP-2

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Payload**:
```json
{
  "type": "image",
  "file": {
    "mimetype": "image/jpeg",
    "filename": "foto_refeicao_001.jpg",
    "url": "https://exemplo.com/foto_refeicao_001.jpg"
  },
  "caption": "Minha refeição de hoje"
}
```

**Resultado Esperado**:
```json
{
  "id": "uuid-gerado",
  "type": "image",
  "file": {
    "mimetype": "image/jpeg",
    "filename": "foto_refeicao_001.jpg",
    "url": "https://exemplo.com/foto_refeicao_001.jpg"
  },
  "caption": "Minha refeição de hoje",
  "title": "Refeição saudável com vegetais",
  "description": "Minha refeição de hoje. Análise visual: Prato com salada verde, frango grelhado e arroz integral...",
  "tags": "image, imagem, alimentação, refeição, food, meal",
  "created_at": "2025-12-17T..."
}
```

**Validações**:
- [x] Status code: 201
- [x] title gerado por BLIP-2
- [x] description combinando caption + análise
- [x] tags contextuais (food, meal, etc)
- [x] Análise local (zero custo API)

---

### UC-019: Criar Mensagem de Vídeo (Transcrição Áudio)
**Endpoint**: `POST /api/v1/messages`  
**Objetivo**: Criar mensagem de vídeo E transcrever áudio

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Payload**:
```json
{
  "type": "video",
  "file": {
    "mimetype": "video/mp4",
    "filename": "video_exercicio_001.mp4",
    "url": "https://exemplo.com/video_exercicio_001.mp4"
  },
  "caption": "Meu treino de hoje"
}
```

**Resultado Esperado**:
```json
{
  "id": "uuid-gerado",
  "type": "video",
  "file": {
    "mimetype": "video/mp4",
    "filename": "video_exercicio_001.mp4",
    "url": "https://exemplo.com/video_exercicio_001.mp4"
  },
  "caption": "Meu treino de hoje",
  "transcription": "fazendo minha caminhada diária de 30 minutos conforme a doutora recomendou",
  "title": "Vídeo de treino",
  "description": "Meu treino de hoje | Arquivo: video_exercicio_001.mp4 | Tipo: vídeo",
  "tags": "video, vídeo, exercício",
  "created_at": "2025-12-17T..."
}
```

**Validações**:
- [x] Status code: 201
- [x] transcription presente (áudio do vídeo)
- [x] Metadata básico gerado (title, description)

---

### UC-020: Criar Mensagem de Localização
**Endpoint**: `POST /api/v1/messages`  
**Objetivo**: Criar mensagem de localização (pin WhatsApp)

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Payload**:
```json
{
  "type": "location",
  "latitude": -29.5838212,
  "longitude": -51.0869905,
  "title": "Clínica GO - Dra. Andrea Mondadori"
}
```

**Resultado Esperado**:
```json
{
  "id": "uuid-gerado",
  "type": "location",
  "latitude": -29.5838212,
  "longitude": -51.0869905,
  "title": "Clínica GO - Dra. Andrea Mondadori",
  "created_at": "2025-12-17T..."
}
```

**Validações**:
- [x] Status code: 201
- [x] Coordenadas corretas (Dois Irmãos/RS)
- [x] title presente

---

## 📚 FASE 5: CONVERSAS E LEADS

### UC-021: Simular Webhook WAHA (Mensagem Inbound)
**Endpoint**: `POST /api/v1/webhooks/waha`  
**Objetivo**: Simular recebimento de mensagem do paciente

**Headers**:
```
Content-Type: application/json
X-WAHA-Event: message
```

**Payload**:
```json
{
  "event": "message",
  "session": "clinica_go_dra_andrea",
  "payload": {
    "id": "msg_001",
    "timestamp": 1702828800,
    "from": "5551999887766@c.us",
    "body": "Olá, gostaria de informações sobre consulta de emagrecimento",
    "hasMedia": false,
    "ack": 0
  }
}
```

**Resultado Esperado**:
```json
{
  "message": "Webhook received and queued for processing",
  "log_id": "uuid-gerado"
}
```

**Validações**:
- [x] Status code: 202 (Accepted - processamento assíncrono)
- [x] log_id presente (webhook log)
- [x] Job enfileirado no Redis Queue (fila "messages")

**Verificação Assíncrona** (após 5-10s):
```bash
# Verificar logs do worker
docker logs wpp_bot-worker-1 --tail 50

# Deve mostrar:
# ✓ Processing job: process_inbound_message
# 🔄 Processando mensagem inbound (chat_id=5551999887766@c.us...)
# ✓ Nova conversa criada (id=uuid, lead_id=uuid)
# ✓ Intenção detectada: INTERESSE_TRATAMENTO
# ✓ Resposta gerada (xxx tokens)
# ✓ Mensagem processada com sucesso
```

---

### UC-022: Verificar Conversa Criada
**Endpoint**: `GET /api/v1/conversations?phone_number=5551999887766`  
**Objetivo**: Validar que conversa foi criada automaticamente

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Query Params**:
```
phone_number: 5551999887766
```

**Resultado Esperado**:
```json
[
  {
    "id": "uuid-conversa",
    "chat_id": "5551999887766@c.us",
    "phone_number": "5551999887766",
    "status": "active",
    "lead_status": "new",
    "maturity_score": 10,
    "is_urgent": false,
    "lead": {
      "id": "uuid-lead",
      "phone_number": "5551999887766",
      "name": "5551999887766",
      "maturity_score": 10
    },
    "messages_count": 2,
    "created_at": "2025-12-17T...",
    "updated_at": "2025-12-17T..."
  }
]
```

**Validações**:
- [x] Status code: 200
- [x] Conversa criada automaticamente
- [x] Lead criado e vinculado
- [x] maturity_score inicial = 10 (INTERESSE_TRATAMENTO)
- [x] messages_count = 2 (inbound + outbound)
- [x] status = "active"

---

### UC-023: Obter Mensagens da Conversa
**Endpoint**: `GET /api/v1/conversations/{conversation_id}/messages`  
**Objetivo**: Listar histórico de mensagens

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Path Params**:
```
conversation_id: {{conversation_id}}
```

**Resultado Esperado**:
```json
[
  {
    "id": "uuid-msg-1",
    "conversation_id": "uuid-conversa",
    "direction": "inbound",
    "content": "Olá, gostaria de informações sobre consulta de emagrecimento",
    "timestamp": "2025-12-17T14:30:00Z"
  },
  {
    "id": "uuid-msg-2",
    "conversation_id": "uuid-conversa",
    "direction": "outbound",
    "content": "Olá! Que bom que você está buscando cuidar da sua saúde! 🌟\n\nVou te ajudar com informações sobre nossa consulta de emagrecimento. Há quanto tempo você vem buscando emagrecer?",
    "timestamp": "2025-12-17T14:30:03Z"
  }
]
```

**Validações**:
- [x] Status code: 200
- [x] 2 mensagens (inbound + outbound)
- [x] direction correto (inbound/outbound)
- [x] content das mensagens
- [x] Resposta do bot usando SPIN Selling (pergunta Situation)

---

### UC-024: Obter Dados do Lead Criado
**Endpoint**: `GET /api/v1/leads?phone_number=5551999887766`  
**Objetivo**: Verificar informações do lead

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Query Params**:
```
phone_number: 5551999887766
```

**Resultado Esperado**:
```json
[
  {
    "id": "uuid-lead",
    "phone_number": "5551999887766",
    "name": "5551999887766",
    "email": null,
    "status": "new",
    "maturity_score": 10,
    "assigned_to": null,
    "interactions_count": 1,
    "last_interaction": "2025-12-17T14:30:03Z",
    "created_at": "2025-12-17T14:30:00Z"
  }
]
```

**Validações**:
- [x] Status code: 200
- [x] Lead criado com phone_number
- [x] status = "new" (primeiro contato)
- [x] maturity_score = 10 (incrementado por INTERESSE_TRATAMENTO)
- [x] interactions_count = 1

---

### UC-025: Verificar Interações do Lead
**Endpoint**: `GET /api/v1/leads/{lead_id}/interactions`  
**Objetivo**: Listar histórico de interações registradas

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Path Params**:
```
lead_id: {{lead_id}}
```

**Resultado Esperado**:
```json
[
  {
    "id": "uuid-interaction",
    "lead_id": "uuid-lead",
    "type": "INTERESSE_TRATAMENTO",
    "channel": "whatsapp",
    "notes": "Inbound: Olá, gostaria de informações... | Outbound: Olá! Que bom que você está buscando...",
    "created_at": "2025-12-17T14:30:03Z"
  }
]
```

**Validações**:
- [x] Status code: 200
- [x] Interação registrada
- [x] type = intenção detectada
- [x] notes com resumo inbound/outbound

---

## 📚 FASE 6: GEMINI AI E CONTEXTO

### UC-026: Simular Conversa Continuada (Fase PROBLEM)
**Endpoint**: `POST /api/v1/webhooks/waha`  
**Objetivo**: Testar contexto conversacional e fase SPIN

**Payload**:
```json
{
  "event": "message",
  "session": "clinica_go_dra_andrea",
  "payload": {
    "id": "msg_002",
    "timestamp": 1702828900,
    "from": "5551999887766@c.us",
    "body": "Já tentei várias dietas mas sempre volto a engordar. Isso me frustra muito",
    "hasMedia": false
  }
}
```

**Verificações** (após processamento):
1. Buscar mensagens da conversa → deve ter 4 mensagens agora
2. Verificar resposta do bot → deve fazer pergunta da fase PROBLEM
3. Verificar maturity_score → deve ter aumentado

**Resposta Esperada do Bot**:
```
"Imagino como deve ser desafiador passar por isso repetidamente. Me conta: o que tem sido mais difícil de manter quando você está seguindo uma dieta?"
```

**Validações**:
- [x] Bot detecta fase PROBLEM (sintomas/dificuldades)
- [x] Pergunta aprofunda dor (metodologia SPIN)
- [x] maturity_score aumentou (agora ~15-20)
- [x] Contexto anterior mantido no ChromaDB

---

### UC-027: Simular Conversa Avançada (Fase IMPLICATION)
**Endpoint**: `POST /api/v1/webhooks/waha`  
**Objetivo**: Testar progressão SPIN para urgência

**Payload**:
```json
{
  "event": "message",
  "session": "clinica_go_dra_andrea",
  "payload": {
    "id": "msg_003",
    "timestamp": 1702829000,
    "from": "5551999887766@c.us",
    "body": "Isso afeta minha autoestima e minha energia no dia a dia. Não aguento mais",
    "hasMedia": false
  }
}
```

**Verificações**:
1. Resposta do bot deve explorar implicações
2. maturity_score deve ter aumentado significativamente
3. is_urgent pode ser marcado como true (palavras-chave)

**Resposta Esperada do Bot**:
```
"Entendo perfeitamente. Quando isso afeta nossa autoestima e energia, impacta toda nossa vida, não é? Como você se sentiria se conseguisse resolver isso de forma saudável e duradoura, com acompanhamento médico individualizado?"
```

**Validações**:
- [x] Bot detecta fase IMPLICATION (impactos/urgência)
- [x] Pergunta transiciona para NEED-PAYOFF
- [x] maturity_score ~30-40
- [x] Possível urgência detectada

---

### UC-028: Simular Agendamento (Fase NEED-PAYOFF)
**Endpoint**: `POST /api/v1/webhooks/waha`  
**Objetivo**: Testar detecção de intenção de agendamento

**Payload**:
```json
{
  "event": "message",
  "session": "clinica_go_dra_andrea",
  "payload": {
    "id": "msg_004",
    "timestamp": 1702829100,
    "from": "5551999887766@c.us",
    "body": "Quero muito resolver isso! Como faço para agendar uma consulta?",
    "hasMedia": false
  }
}
```

**Verificações**:
1. Intenção detectada: AGENDAMENTO
2. maturity_score ~60-80 (alta maturidade)
3. Bot deve usar playbook de agendamento OU Gemini Tool

**Resposta Esperada do Bot**:
```
"Maravilha! Vou te ajudar a agendar sua consulta com a Dra. Andrea! 🌟

Temos horários disponíveis:
📅 Segunda a Sexta: 8h-12h e 14h-18h
📍 Clínica GO - Av. São Miguel, 1000 - sala 102, Dois Irmãos/RS

Qual dia e horário funcionam melhor pra você?"
```

**Validações**:
- [x] Intenção: AGENDAMENTO
- [x] maturity_score alto (>50)
- [x] Bot fornece informações práticas
- [x] Possível uso de Playbook Tools (function calling)

---

### UC-029: Simular Pergunta sobre Localização
**Endpoint**: `POST /api/v1/webhooks/waha`  
**Objetivo**: Testar Gemini Tool "send_clinic_location"

**Payload**:
```json
{
  "event": "message",
  "session": "clinica_go_dra_andrea",
  "payload": {
    "id": "msg_005",
    "timestamp": 1702829200,
    "from": "5551999887766@c.us",
    "body": "Onde fica a clínica? Pode me enviar a localização?",
    "hasMedia": false
  }
}
```

**Verificações**:
1. Gemini detecta gatilho: "onde fica", "localização"
2. Gemini chama tool: send_clinic_location
3. Sistema envia pin WhatsApp automaticamente

**Resposta Esperada do Bot**:
```
"Claro! Estou te enviando a localização agora! 📍

Endereço: Av. São Miguel, 1000 - sala 102, Centro, Dois Irmãos - RS, 93950-000

[Sistema envia automaticamente pin de localização via WAHA]"
```

**Validações**:
- [x] Gemini detecta intenção "localização"
- [x] Tool send_clinic_location executada
- [x] Pin WhatsApp enviado via WAHA
- [x] Lat/Long corretos: -29.5838212, -51.0869905

---

### UC-030: Verificar Logs de LLM Interactions
**Endpoint**: `GET /api/v1/llm-interactions?conversation_id={conversation_id}`  
**Objetivo**: Auditar interações com Gemini AI

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Query Params**:
```
conversation_id: {{conversation_id}}
```

**Resultado Esperado**:
```json
[
  {
    "id": "uuid-llm-1",
    "conversation_id": "uuid-conversa",
    "prompt": "Intent: INTERESSE_TRATAMENTO | Olá, gostaria de informações...",
    "response": "Olá! Que bom que você está buscando cuidar da sua saúde...",
    "tokens_used": 450,
    "latency_ms": 1200,
    "created_at": "2025-12-17T14:30:02Z"
  },
  {
    "id": "uuid-llm-2",
    "conversation_id": "uuid-conversa",
    "prompt": "Intent: INTERESSE_TRATAMENTO | Já tentei várias dietas...",
    "response": "Imagino como deve ser desafiador...",
    "tokens_used": 380,
    "latency_ms": 980,
    "created_at": "2025-12-17T14:31:45Z"
  }
]
```

**Validações**:
- [x] Status code: 200
- [x] Todos os prompts/responses registrados
- [x] tokens_used presente (custo)
- [x] latency_ms presente (performance)

---

## 📚 FASE 7: ESCALAÇÃO PARA HUMANO

### UC-031: Atribuir Conversa à Secretária
**Endpoint**: `PATCH /api/v1/conversations/{conversation_id}/assign`  
**Objetivo**: Transferir conversa para atendimento humano

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Path Params**:
```
conversation_id: {{conversation_id}}
```

**Payload**:
```json
{
  "assigned_to": "{{user_id_secretaria}}",
  "reason": "Cliente pronto para agendamento - Alta maturidade"
}
```

**Resultado Esperado**:
```json
{
  "id": "uuid-conversa",
  "assigned_to": "uuid-secretaria",
  "status": "escalated",
  "updated_at": "2025-12-17T..."
}
```

**Validações**:
- [x] Status code: 200
- [x] assigned_to atualizado
- [x] status mudou para "escalated"
- [x] Notificação criada para secretária

---

### UC-032: Verificar Notificações da Secretária
**Endpoint**: `GET /api/v1/notifications`  
**Objetivo**: Listar notificações in-app

**Headers**:
```
Authorization: Bearer {{auth_token_secretaria}}
```

**Resultado Esperado**:
```json
[
  {
    "id": "uuid-notif",
    "user_id": "uuid-secretaria",
    "type": "conversation_assigned",
    "title": "Nova conversa atribuída",
    "message": "Você recebeu uma conversa de 5551999887766 (Cliente pronto para agendamento - Alta maturidade)",
    "data": {
      "conversation_id": "uuid-conversa",
      "phone_number": "5551999887766",
      "maturity_score": 80
    },
    "is_read": false,
    "created_at": "2025-12-17T..."
  }
]
```

**Validações**:
- [x] Status code: 200
- [x] Notificação presente
- [x] type = "conversation_assigned"
- [x] is_read = false (nova)

---

### UC-033: Marcar Notificação como Lida
**Endpoint**: `PATCH /api/v1/notifications/{notification_id}/read`  
**Objetivo**: Atualizar status de notificação

**Headers**:
```
Authorization: Bearer {{auth_token_secretaria}}
```

**Path Params**:
```
notification_id: {{notification_id}}
```

**Resultado Esperado**:
```json
{
  "id": "uuid-notif",
  "is_read": true,
  "read_at": "2025-12-17T..."
}
```

**Validações**:
- [x] Status code: 200
- [x] is_read = true
- [x] read_at timestamp presente

---

## 📚 FASE 8: TAGS E FILTROS

### UC-034: Adicionar Tags à Conversa
**Endpoint**: `POST /api/v1/conversations/{conversation_id}/tags`  
**Objetivo**: Categorizar conversa

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Path Params**:
```
conversation_id: {{conversation_id}}
```

**Payload**:
```json
{
  "tags": ["agendamento", "emagrecimento", "urgente", "alta-prioridade"]
}
```

**Resultado Esperado**:
```json
{
  "id": "uuid-conversa",
  "tags": [
    {"id": "uuid-tag-1", "name": "agendamento"},
    {"id": "uuid-tag-2", "name": "emagrecimento"},
    {"id": "uuid-tag-3", "name": "urgente"},
    {"id": "uuid-tag-4", "name": "alta-prioridade"}
  ]
}
```

**Validações**:
- [x] Status code: 200
- [x] 4 tags associadas
- [x] Tags criadas se não existiam

---

### UC-035: Filtrar Conversas por Tag
**Endpoint**: `GET /api/v1/conversations?tags=urgente`  
**Objetivo**: Buscar conversas por categoria

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Query Params**:
```
tags: urgente
status: active
```

**Resultado Esperado**:
```json
[
  {
    "id": "uuid-conversa",
    "phone_number": "5551999887766",
    "status": "active",
    "is_urgent": true,
    "tags": [
      {"name": "urgente"},
      {"name": "agendamento"}
    ]
  }
]
```

**Validações**:
- [x] Status code: 200
- [x] Apenas conversas com tag "urgente"
- [x] Filtros combinados (status + tags)

---

## 📚 FASE 9: MÉTRICAS E ANALYTICS

### UC-036: Obter Métricas Gerais (Admin)
**Endpoint**: `GET /api/v1/metrics/overview`  
**Objetivo**: Dashboard de métricas do sistema

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Resultado Esperado**:
```json
{
  "total_conversations": 1,
  "active_conversations": 1,
  "escalated_conversations": 0,
  "closed_conversations": 0,
  "total_leads": 1,
  "new_leads": 1,
  "qualified_leads": 0,
  "converted_leads": 0,
  "average_maturity_score": 80.0,
  "total_messages": 10,
  "inbound_messages": 5,
  "outbound_messages": 5,
  "average_response_time_seconds": 3.2,
  "total_llm_interactions": 5,
  "total_tokens_used": 2150,
  "period": "all_time"
}
```

**Validações**:
- [x] Status code: 200
- [x] Todas as métricas presentes
- [x] Valores corretos baseados nos testes

---

### UC-037: Obter Métricas por Período
**Endpoint**: `GET /api/v1/metrics/overview?start_date=2025-12-17&end_date=2025-12-17`  
**Objetivo**: Filtrar métricas por data

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Query Params**:
```
start_date: 2025-12-17
end_date: 2025-12-17
```

**Validações**:
- [x] Status code: 200
- [x] Métricas apenas do período especificado
- [x] period = "2025-12-17 to 2025-12-17"

---

### UC-038: Obter Métricas por Campanha
**Endpoint**: `GET /api/v1/metrics/campaigns`  
**Objetivo**: Análise de performance por origem

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Resultado Esperado**:
```json
[
  {
    "campaign_name": "google_ads_emagrecimento",
    "leads_count": 15,
    "qualified_leads": 8,
    "converted_leads": 3,
    "conversion_rate": 0.20,
    "average_maturity_score": 65.5,
    "total_cost": 450.00,
    "cost_per_lead": 30.00,
    "cost_per_conversion": 150.00
  }
]
```

**Validações**:
- [x] Status code: 200
- [x] Métricas por campanha
- [x] ROI calculado (cost_per_conversion)

---

## 📚 FASE 10: GESTÃO DE FILAS

### UC-039: Verificar Status das Filas Redis
**Endpoint**: `GET /api/v1/queues/stats`  
**Objetivo**: Monitorar filas de processamento

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Resultado Esperado**:
```json
{
  "queues": [
    {
      "name": "messages",
      "size": 0,
      "failed_count": 0,
      "workers_count": 2
    },
    {
      "name": "ai",
      "size": 0,
      "failed_count": 0,
      "workers_count": 2
    },
    {
      "name": "escalation",
      "size": 0,
      "failed_count": 0,
      "workers_count": 2
    }
  ],
  "total_pending": 0,
  "total_failed": 0
}
```

**Validações**:
- [x] Status code: 200
- [x] 3 filas presentes
- [x] size = 0 (tudo processado)
- [x] failed_count = 0

---

### UC-040: Reprocessar Job Falhado (DLQ)
**Endpoint**: `POST /api/v1/queues/retry/{job_id}`  
**Objetivo**: Retentar job que falhou

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Path Params**:
```
job_id: {{failed_job_id}}
```

**Resultado Esperado**:
```json
{
  "message": "Job re-enqueued for processing",
  "job_id": "uuid-job",
  "queue": "messages"
}
```

**Validações**:
- [x] Status code: 200
- [x] Job movido de DLQ para fila principal

---

## 🎯 CASOS DE USO ADICIONAIS (Testes Avançados)

### UC-041: Testar Resposta Fallback (Erro Gemini)
**Objetivo**: Validar graceful degradation

**Cenário**: Desligar internet temporariamente / bloquear API Gemini

**Resultado Esperado**: Bot envia mensagem de fallback genérica

---

### UC-042: Testar Limite de Rate Limiting
**Objetivo**: Validar proteção contra abuse

**Cenário**: Enviar 100+ requisições em 1 minuto

**Resultado Esperado**: Status 429 (Too Many Requests) após limite

---

### UC-043: Testar Webhook com Mídia Inválida
**Objetivo**: Validar tratamento de erros

**Cenário**: Enviar URL de áudio quebrada

**Resultado Esperado**: Transcrição falha → fallback para "[Áudio recebido - transcrição falhou]"

---

### UC-044: Testar Contexto Longo (50+ Mensagens)
**Objetivo**: Validar performance com histórico extenso

**Cenário**: Simular conversa longa (50 mensagens alternadas)

**Resultado Esperado**: Contexto mantido, latência aceitável (<5s)

---

## 📊 CRITÉRIOS DE SUCESSO GERAL

### Performance
- [ ] API response time médio < 500ms (endpoints REST)
- [ ] Processamento de webhook < 10s (end-to-end)
- [ ] Latência Gemini AI < 3s (95º percentil)
- [ ] Transcrição Faster-Whisper < 5s (áudio de 30s)
- [ ] Análise BLIP-2 < 5s (imagem padrão)

### Qualidade
- [ ] 0 erros 500 (Internal Server Error)
- [ ] 100% dos casos de uso passando
- [ ] Respostas do bot fluidas e naturais
- [ ] Detecção de intenção >85% de acurácia

### Funcionalidade
- [ ] Todos os endpoints documentados no Swagger funcionando
- [ ] Autenticação JWT validada em todos os endpoints protegidos
- [ ] Permissões (admin/user) funcionando corretamente
- [ ] Webhooks WAHA processados assincronamente
- [ ] ChromaDB mantendo contexto conversacional
- [ ] Redis Queue processando jobs sem falhas
- [ ] BLIP-2 analisando imagens sem custo API
- [ ] Faster-Whisper transcrevendo áudios localmente
- [ ] Gemini Tools executando ações automaticamente

---

## 🗂️ CHECKLIST DE EXECUÇÃO

### Preparação
- [ ] Docker Compose UP (todos os serviços healthy)
- [ ] Alembic migrations aplicadas (`alembic upgrade head`)
- [ ] Postman Collection importada
- [ ] Environment variables configuradas
- [ ] Token de admin obtido e salvo

### Execução por Fase
- [ ] **FASE 1**: Infraestrutura e Autenticação (UC-001 a UC-005)
- [ ] **FASE 2**: Integração WAHA (UC-006 a UC-009)
- [ ] **FASE 3**: Playbooks (UC-010 a UC-015)
- [ ] **FASE 4**: Mensagens e Mídia (UC-016 a UC-020)
- [ ] **FASE 5**: Conversas e Leads (UC-021 a UC-025)
- [ ] **FASE 6**: Gemini AI e Contexto (UC-026 a UC-030)
- [ ] **FASE 7**: Escalação para Humano (UC-031 a UC-033)
- [ ] **FASE 8**: Tags e Filtros (UC-034 a UC-035)
- [ ] **FASE 9**: Métricas e Analytics (UC-036 a UC-038)
- [ ] **FASE 10**: Gestão de Filas (UC-039 a UC-040)

### Documentação de Resultados
- [ ] Screenshots dos testes via Swagger
- [ ] Logs de workers (docker logs)
- [ ] Resultados Postman exportados
- [ ] Tabela de bugs/issues encontrados
- [ ] Relatório final de cobertura

---

## 📝 TEMPLATE DE RELATÓRIO DE BUGS

Quando encontrar um bug, documentar assim:

```markdown
### BUG-XXX: Título do Bug

**Caso de Uso**: UC-XXX  
**Endpoint**: POST /api/v1/...  
**Severidade**: Alta / Média / Baixa  

**Comportamento Esperado**:
...

**Comportamento Obtido**:
...

**Steps to Reproduce**:
1. ...
2. ...
3. ...

**Payload Usado**:
```json
{...}
```

**Response Recebido**:
```json
{...}
```

**Logs Relevantes**:
```
[2025-12-17 14:30:00] ERROR: ...
```

**Possível Causa**: ...

**Prioridade**: P0 (Bloqueador) / P1 (Crítico) / P2 (Importante) / P3 (Nice to have)
```

---

## 🎓 PRÓXIMOS PASSOS APÓS TESTES

1. **Correção de Bugs**: Priorizar P0 e P1
2. **Otimizações**: Performance, latência, memory usage
3. **Testes de Carga**: Simular 100+ usuários simultâneos
4. **Testes E2E**: Fluxo completo real (WhatsApp → Agendamento)
5. **Documentação**: Atualizar README com resultados
6. **Deploy**: Ambiente de produção (se testes OK)

---

**🚀 Boa sorte nos testes! Qualquer dúvida, consulte a documentação técnica ou entre em contato.**

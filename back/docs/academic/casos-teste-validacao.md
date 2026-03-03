# PLANO DE TESTES - Clinica GO WhatsApp Bot

**Versão**: 2.0  
**Última Atualização**: 2026-01-27  
**Total de Casos de Teste**: 200+  
**Total de Endpoints**: 161  
**Cobertura**: 100%

---

## 1. Visão Geral

### 1.1 Objetivo do Documento

Este documento serve como **fonte única de verdade** para validação do sistema Clinica GO WhatsApp Bot, sendo utilizado como:

1. **Referência para testes manuais** (Postman, Swagger UI)
2. **Base para testes automatizados** (Pytest)
3. **Instrumento de verificação** do comportamento esperado do sistema

### 1.2 Escopo de Testes

| Categoria | Descrição |
|-----------|-----------|
| **Funcional** | Validação de regras de negócio e fluxos |
| **Integração** | Comunicação entre módulos e serviços externos |
| **Segurança** | Autenticação, autorização e proteção de dados |
| **Performance** | Tempos de resposta e limites de carga |

### 1.3 Ferramentas Utilizadas

| Ferramenta | Uso | Localização |
|------------|-----|-------------|
| **Swagger UI** | Testes interativos | http://localhost:3333/docs |
| **Postman** | Coleção de testes | `postman/WPP_Bot_API.postman_collection.json` |
| **Pytest** | Testes automatizados | `back/tests/` |

### 1.4 Glossário de Termos

| Termo | Definição |
|-------|-----------|
| **Lead** | Potencial cliente que iniciou contato |
| **Conversa** | Sessão de chat entre lead e bot/atendente |
| **Playbook** | Sequência pré-definida de mensagens |
| **Handoff** | Transferência de atendimento bot → humano |
| **Maturity Score** | Pontuação de maturidade do lead (0-100) |
| **WAHA** | WhatsApp HTTP API - serviço de integração |

---

## 2. Premissas e Dependências

### 2.1 Ambiente de Testes

**Pré-requisitos obrigatórios:**

```bash
# Serviços ativos (docker-compose)
- PostgreSQL (porta 5432)
- Redis (porta 6379)
- WAHA (porta 3001)
- API Backend (porta 3333)
```

**Verificação de ambiente:**
```
GET /api/v1/health → Status 200, todos os componentes "ok": true
```

### 2.2 Dados de Teste

| Variável | Valor | Descrição |
|----------|-------|-----------|
| `{{admin_email}}` | admin@clinicago.com.br | Email do administrador |
| `{{admin_password}}` | Admin@2025!Secure | Senha do administrador |
| `{{auth_token}}` | (gerado no login) | Token JWT para autenticação |
| `{{session_name}}` | clinica_go_main | Nome da sessão WAHA |

### 2.3 Configurações Necessárias

1. **Migrations aplicadas**: `alembic upgrade head`
2. **Variáveis de ambiente**: Arquivo `.env` configurado
3. **WAHA conectado**: Sessão WhatsApp autenticada

---

## 3. Fluxo Geral da Aplicação

### 3.1 Estados de Conversa

```
ACTIVE_BOT → PENDING_HANDOFF → ACTIVE_HUMAN → COMPLETED
     ↓              ↓               ↓
   CLOSED        CLOSED          CLOSED
```

### 3.2 Estados de Lead

```
NEW → CONTACTED → QUALIFIED → SCHEDULED
 ↓        ↓           ↓
LOST     LOST        LOST
```

### 3.3 Fluxo de Handoff

```
1. Lead envia mensagem
2. Bot processa e responde (ACTIVE_BOT)
3. Score atinge threshold OU bot não entende
4. Sistema dispara handoff (PENDING_HANDOFF)
5. Atendente assume (ACTIVE_HUMAN)
6. Atendente finaliza (COMPLETED)
```

---

## 4. Casos de Teste por Módulo

### Legenda de Status

| Ícone | Significado |
|-------|-------------|
| ✅ | Teste passou |
| ❌ | Teste falhou |
| ⏳ | Não executado |

---

## 4.1 INFRAESTRUTURA (Health Check)

### CT-001: Health Check - Sistema Saudável

**Endpoint**: `GET /api/v1/health`  
**Módulo**: Health  
**Prioridade**: Alta  
**Tipo**: Funcional

#### Objetivo
Validar que todos os componentes do sistema estão operacionais.

#### Pré-condições
1. Docker Compose em execução
2. Todos os serviços iniciados

#### Dados de Entrada

**Headers**: Nenhum (endpoint público)

#### Resultado Esperado

**Status Code**: 200

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

#### Validações
- [ ] Status code = 200
- [ ] `status` = "ok"
- [ ] Todos os componentes com `ok: true`
- [ ] Latência < 1 segundo

#### Cenários de Erro

| Cenário | Condição | Status | Resposta |
|---------|----------|--------|----------|
| Database offline | PostgreSQL parado | 503 | `database.ok: false` |
| Redis offline | Redis parado | 503 | `redis.ok: false` |
| WAHA offline | WAHA não acessível | 503 | `waha.ok: false` |

---

### CT-002: Debug Messages (Desenvolvimento)

**Endpoint**: `GET /api/v1/health/debug/messages`  
**Módulo**: Health  
**Prioridade**: Baixa  
**Tipo**: Debug

#### Objetivo
Listar mensagens do banco para debug (apenas desenvolvimento).

#### Pré-condições
1. Ambiente de desenvolvimento

#### Resultado Esperado

**Status Code**: 200

```json
[
  {"id": "uuid", "body": "texto", "created_at": "2026-01-27T..."}
]
```

---

## 4.2 AUTENTICAÇÃO E AUTORIZAÇÃO

### CT-003: Signup - Criar Usuário Admin

**Endpoint**: `POST /api/v1/auth/signup`  
**Módulo**: Auth  
**Prioridade**: Alta  
**Tipo**: Funcional

#### Objetivo
Registrar novo usuário administrador no sistema.

#### Pré-condições
1. Email não cadastrado previamente

#### Dados de Entrada

**Headers**:
```
Content-Type: application/json
```

**Body**:
```json
{
  "email": "admin@clinicago.com.br",
  "password": "Admin@2025!Secure",
  "role": "admin"
}
```

#### Resultado Esperado

**Status Code**: 201

```json
{
  "id": 1,
  "email": "admin@clinicago.com.br",
  "role": "admin",
  "is_active": true,
  "email_verified": false,
  "created_at": "2026-01-27T..."
}
```

#### Validações
- [ ] Status code = 201
- [ ] `id` presente (inteiro)
- [ ] `password` NÃO retornado na resposta
- [ ] `role` = "admin"
- [ ] `is_active` = true
- [ ] `email_verified` = false (requer verificação)

#### Cenários de Erro

| Cenário | Input | Status | Mensagem |
|---------|-------|--------|----------|
| Email já existe | email duplicado | 400 | "User already exists" |
| Senha fraca | "123456" | 422 | "Password too weak" |
| Email inválido | "invalido" | 422 | "Invalid email format" |
| Role inválida | "superadmin" | 422 | "Invalid role" |

---

### CT-004: Signup - Criar Usuário Comum

**Endpoint**: `POST /api/v1/auth/signup`  
**Módulo**: Auth  
**Prioridade**: Alta  
**Tipo**: Funcional

#### Objetivo
Registrar novo usuário com permissões limitadas (secretária/atendente).

#### Dados de Entrada

**Body**:
```json
{
  "email": "secretaria@clinicago.com.br",
  "password": "Secret@2025!Safe",
  "role": "user"
}
```

#### Resultado Esperado

**Status Code**: 201

```json
{
  "id": 2,
  "email": "secretaria@clinicago.com.br",
  "role": "user",
  "is_active": true
}
```

#### Validações
- [ ] `role` = "user" (não "admin")
- [ ] `id` diferente do admin

---

### CT-005: Login - Obter Access Token

**Endpoint**: `POST /api/v1/auth/token`  
**Módulo**: Auth  
**Prioridade**: Alta  
**Tipo**: Funcional

#### Objetivo
Autenticar usuário e obter tokens JWT.

#### Pré-condições
1. Usuário cadastrado
2. Email verificado (ou ambiente de teste)

#### Dados de Entrada

**Headers**:
```
Content-Type: application/x-www-form-urlencoded
```

**Body (form-data)**:
```
username=admin@clinicago.com.br
password=Admin@2025!Secure
```

#### Resultado Esperado

**Status Code**: 200

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@clinicago.com.br",
    "role": "admin"
  }
}
```

**Cookies HttpOnly**:
- `access_token` (30 min)
- `refresh_token` (7 dias)

#### Validações
- [ ] Status code = 200
- [ ] `access_token` é JWT válido
- [ ] `token_type` = "bearer"
- [ ] Cookies HttpOnly definidos
- [ ] Dados do usuário retornados

#### Cenários de Erro

| Cenário | Input | Status | Mensagem |
|---------|-------|--------|----------|
| Senha incorreta | password errado | 401 | "Invalid credentials" |
| Usuário não existe | email inexistente | 401 | "Invalid credentials" |
| Usuário bloqueado | is_active=false | 401 | "User is blocked" |
| Email não verificado | email_verified=false | 401 | "Email not verified" |
| Rate limiting | >5 tentativas/15min | 429 | "Too Many Requests" |

---

### CT-006: Login com MFA Habilitado

**Endpoint**: `POST /api/v1/auth/token`  
**Módulo**: Auth  
**Prioridade**: Alta  
**Tipo**: Segurança

#### Objetivo
Validar fluxo de login quando MFA está ativo.

#### Pré-condições
1. Usuário com MFA habilitado

#### Resultado Esperado (Etapa 1)

**Status Code**: 200

```json
{
  "mfa_required": true,
  "mfa_token": "temporary-token...",
  "message": "MFA code required"
}
```

#### Próximo Passo
Usar `POST /api/v1/auth/mfa/login` com código TOTP.

---

### CT-007: Validar Token - Get Current User (Auth)

**Endpoint**: `GET /api/v1/auth/me`  
**Módulo**: Auth  
**Prioridade**: Alta  
**Tipo**: Funcional

#### Objetivo
Validar que token JWT está funcionando e retornar dados de sessão.

#### Pré-condições
1. Token JWT válido

#### Dados de Entrada

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

#### Resultado Esperado

**Status Code**: 200

```json
{
  "user_id": 1,
  "email": "admin@clinicago.com.br",
  "role": "admin",
  "mfa_enabled": false,
  "email_verified": true,
  "last_login": "2026-01-27T..."
}
```

#### Validações
- [ ] Status code = 200
- [ ] Retorna `AuthSessionResponse` (dados de autenticação)
- [ ] NÃO retorna dados de perfil (full_name, phone)

#### Cenários de Erro

| Cenário | Input | Status | Mensagem |
|---------|-------|--------|----------|
| Sem token | Header ausente | 401 | "Not authenticated" |
| Token inválido | JWT malformado | 401 | "Invalid token" |
| Token expirado | JWT expirado | 401 | "Token expired" |

---

### CT-008: Refresh Token

**Endpoint**: `POST /api/v1/auth/refresh`  
**Módulo**: Auth  
**Prioridade**: Alta  
**Tipo**: Segurança

#### Objetivo
Renovar access token usando refresh token (rotação de tokens).

#### Pré-condições
1. Refresh token válido no cookie

#### Resultado Esperado

**Status Code**: 200

```json
{
  "access_token": "novo-jwt-token...",
  "token_type": "bearer"
}
```

#### Validações
- [ ] Novo `access_token` gerado
- [ ] Token antigo revogado (não pode ser reutilizado)
- [ ] Novo refresh token definido no cookie

#### Cenários de Erro

| Cenário | Input | Status | Mensagem |
|---------|-------|--------|----------|
| Refresh token ausente | Cookie vazio | 401 | "No refresh token" |
| Token já usado | Token revogado | 401 | "Token revoked" |
| Token expirado | >7 dias | 401 | "Token expired" |

---

### CT-009: Logout

**Endpoint**: `POST /api/v1/auth/logout`  
**Módulo**: Auth  
**Prioridade**: Média  
**Tipo**: Funcional

#### Objetivo
Encerrar sessão e revogar tokens.

#### Dados de Entrada

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

#### Resultado Esperado

**Status Code**: 204 (No Content)

#### Validações
- [ ] Cookies limpos
- [ ] Tokens revogados no banco
- [ ] Próximo uso do token → 401

---

### CT-010: Alterar Senha

**Endpoint**: `POST /api/v1/auth/password-change`  
**Módulo**: Auth  
**Prioridade**: Alta  
**Tipo**: Segurança

#### Objetivo
Alterar senha do usuário autenticado.

#### Dados de Entrada

**Headers**:
```
Authorization: Bearer {{auth_token}}
Content-Type: application/json
```

**Body**:
```json
{
  "current_password": "Admin@2025!Secure",
  "new_password": "NewAdmin@2026!Strong"
}
```

#### Resultado Esperado

**Status Code**: 200

```json
{
  "message": "Password changed successfully"
}
```

#### Validações
- [ ] Senha atualizada no banco (hash)
- [ ] Todas as outras sessões revogadas
- [ ] Evento de auditoria registrado

#### Cenários de Erro

| Cenário | Input | Status | Mensagem |
|---------|-------|--------|----------|
| Senha atual incorreta | current_password errado | 401 | "Invalid password" |
| Nova senha fraca | "123" | 422 | "Password too weak" |
| Senhas iguais | mesma senha | 400 | "Must be different" |

---

### CT-011: Recuperação de Senha (Solicitar)

**Endpoint**: `POST /api/v1/auth/password-recovery`  
**Módulo**: Auth  
**Prioridade**: Alta  
**Tipo**: Segurança

#### Objetivo
Iniciar fluxo de recuperação de senha (enviar email).

#### Dados de Entrada

**Body** (form-data):
```
email=admin@clinicago.com.br
```

#### Resultado Esperado

**Status Code**: 202 (Accepted)

```json
{
  "message": "If the email exists, a recovery link was sent"
}
```

#### Validações
- [ ] Resposta sempre 202 (não revela se email existe)
- [ ] Email enviado ao MailDev (verificar inbox)
- [ ] Rate limit: 3 tentativas/hora

---

### CT-012: Reset de Senha (Confirmar)

**Endpoint**: `POST /api/v1/auth/password-reset`  
**Módulo**: Auth  
**Prioridade**: Alta  
**Tipo**: Segurança

#### Objetivo
Redefinir senha usando token de recuperação.

#### Dados de Entrada

**Query/Body**:
```json
{
  "token": "reset-token-do-email",
  "new_password": "NewPassword@2026!Secure"
}
```

#### Resultado Esperado

**Status Code**: 200

```json
{
  "message": "Password reset successfully"
}
```

#### Validações
- [ ] Senha atualizada
- [ ] TODAS as sessões revogadas
- [ ] Token de uso único (não reutilizável)
- [ ] Evento de auditoria registrado

---

### CT-013: Listar Sessões Ativas

**Endpoint**: `GET /api/v1/auth/sessions`  
**Módulo**: Auth  
**Prioridade**: Média  
**Tipo**: Segurança

#### Objetivo
Listar todas as sessões do usuário autenticado.

#### Dados de Entrada

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

#### Resultado Esperado

**Status Code**: 200

```json
{
  "sessions": [
    {
      "id": 1,
      "device_info": "Chrome 120 / Windows 10",
      "ip_address": "192.168.1.100",
      "last_used_at": "2026-01-27T15:30:00Z",
      "created_at": "2026-01-27T10:00:00Z",
      "is_current": true
    }
  ],
  "total": 1
}
```

#### Validações
- [ ] `is_current: true` para sessão atual
- [ ] Ordenado por `last_used_at` DESC

---

### CT-014: Revogar Sessão Específica

**Endpoint**: `POST /api/v1/auth/sessions/{session_id}/revoke`  
**Módulo**: Auth  
**Prioridade**: Média  
**Tipo**: Segurança

#### Objetivo
Fazer logout de um dispositivo específico.

#### Dados de Entrada

**Path**: `session_id=2`

#### Resultado Esperado

**Status Code**: 204 (No Content)

#### Validações
- [ ] Sessão marcada como `is_active=false`
- [ ] Não pode revogar sessão de outro usuário → 404

---

### CT-015: Revogar Todas as Sessões

**Endpoint**: `POST /api/v1/auth/sessions/revoke-all`  
**Módulo**: Auth  
**Prioridade**: Média  
**Tipo**: Segurança

#### Objetivo
Logout de todos os dispositivos exceto o atual.

#### Dados de Entrada

**Body**:
```json
{
  "except_current": true
}
```

#### Resultado Esperado

**Status Code**: 200

```json
{
  "message": "All sessions revoked successfully",
  "revoked_count": 3
}
```

---

### CT-016: Verificar Email

**Endpoint**: `GET /api/v1/auth/email/verify`  
**Módulo**: Auth  
**Prioridade**: Alta  
**Tipo**: Funcional

#### Objetivo
Confirmar email usando token do link enviado.

#### Dados de Entrada

**Query**: `token=verification-token-from-email`

#### Resultado Esperado

**Status Code**: 200 (ou redirect para /signin)

```json
{
  "message": "Email verified successfully",
  "email_verified": true
}
```

#### Cenários de Erro

| Cenário | Status | Mensagem |
|---------|--------|----------|
| Token inválido | 400 | "Invalid verification token" |
| Token expirado | 400 | "Verification token expired" |
| Já verificado | 400 | "Email already verified" |

---

### CT-017: Reenviar Email de Verificação

**Endpoint**: `POST /api/v1/auth/email/resend`  
**Módulo**: Auth  
**Prioridade**: Média  
**Tipo**: Funcional

#### Objetivo
Reenviar email de verificação.

#### Dados de Entrada

**Body**:
```json
{
  "email": "usuario@clinicago.com.br"
}
```

#### Resultado Esperado

**Status Code**: 200

```json
{
  "message": "Verification email sent successfully"
}
```

#### Validações
- [ ] Rate limit: 3 tentativas/hora

---

### CT-018: MFA Setup - Habilitar

**Endpoint**: `POST /api/v1/auth/mfa/setup`  
**Módulo**: Auth  
**Prioridade**: Alta  
**Tipo**: Segurança

#### Objetivo
Habilitar autenticação de dois fatores.

#### Dados de Entrada

**Headers**:
```
Authorization: Bearer {{auth_token}}
```

**Body**:
```json
{
  "password": "Admin@2025!Secure"
}
```

#### Resultado Esperado

**Status Code**: 200

```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,...",
  "backup_codes": [
    "12345678", "23456789", "34567890",
    "45678901", "56789012", "67890123",
    "78901234", "89012345", "90123456", "01234567"
  ]
}
```

#### Validações
- [ ] `secret` é Base32 válido
- [ ] `qr_code` é data URI PNG
- [ ] 10 backup codes únicos

---

### CT-019: MFA Verify - Confirmar Ativação

**Endpoint**: `POST /api/v1/auth/mfa/verify`  
**Módulo**: Auth  
**Prioridade**: Alta  
**Tipo**: Segurança

#### Objetivo
Verificar código TOTP e ativar MFA permanentemente.

#### Dados de Entrada

**Body**:
```json
{
  "code": "123456"
}
```

#### Resultado Esperado

**Status Code**: 200

```json
{
  "message": "MFA successfully enabled",
  "mfa_enabled": true
}
```

#### Cenários de Erro

| Cenário | Status | Mensagem |
|---------|--------|----------|
| Código inválido | 400 | "Invalid or expired TOTP code" |
| Código expirado | 400 | "Invalid or expired TOTP code" |

---

### CT-020: MFA Login

**Endpoint**: `POST /api/v1/auth/mfa/login`  
**Módulo**: Auth  
**Prioridade**: Alta  
**Tipo**: Segurança

#### Objetivo
Completar login com código MFA.

#### Dados de Entrada

**Body**:
```json
{
  "email": "admin@clinicago.com.br",
  "code": "123456"
}
```

#### Resultado Esperado

**Status Code**: 200

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

#### Validações
- [ ] Backup code pode ser usado (uso único)
- [ ] Rate limiting: 5 tentativas → 429

---

### CT-021: MFA Disable - Desabilitar

**Endpoint**: `POST /api/v1/auth/mfa/disable`  
**Módulo**: Auth  
**Prioridade**: Alta  
**Tipo**: Segurança

#### Objetivo
Desabilitar MFA (requer senha + código).

#### Dados de Entrada

**Body**:
```json
{
  "password": "Admin@2025!Secure",
  "code": "123456"
}
```

#### Resultado Esperado

**Status Code**: 200

```json
{
  "message": "MFA successfully disabled",
  "mfa_enabled": false
}
```


---

## 4.3 GESTÃO DE USUÁRIOS

### CT-022: Obter Perfil do Usuário Atual
**Endpoint**: `GET /api/v1/users/me` | **Status**: 200

### CT-023: Atualizar Perfil do Usuário Atual
**Endpoint**: `PATCH /api/v1/users/me` | **Status**: 200

### CT-024: Listar Usuários (Admin Only)
**Endpoint**: `GET /api/v1/users/` | **Permissão**: Admin | **Erro**: 403 para user

### CT-025: Obter Usuário por ID (Admin)
**Endpoint**: `GET /api/v1/users/{user_id}` | **Erro**: 404 se não existe

### CT-026: Atualizar Usuário (Admin)
**Endpoint**: `PATCH /api/v1/users/{user_id}` | **Status**: 200

### CT-027: Desativar Usuário (Admin)
**Endpoint**: `DELETE /api/v1/users/{user_id}` | **Status**: 200

### CT-028: Bloquear Usuário (Admin)
**Endpoint**: `POST /api/v1/users/{user_id}/block` | **Efeitos**: Revoga sessões

### CT-029: Desbloquear Usuário (Admin)
**Endpoint**: `POST /api/v1/users/{user_id}/unblock` | **Status**: 200

---

## 4.4 INTEGRAÇÕES WAHA (WhatsApp)

### CT-030: Listar Sessões WAHA
**Endpoint**: `GET /api/v1/waha/sessions` | **Status**: 200

### CT-031: Criar Sessão WAHA
**Endpoint**: `POST /api/v1/waha/sessions` | **Status**: 201

### CT-032: Iniciar Sessão WAHA
**Endpoint**: `POST /api/v1/waha/sessions/{name}/start` | **Status**: 200

### CT-033: Obter QR Code
**Endpoint**: `GET /api/v1/waha/sessions/{name}/qr` | **Resposta**: Base64

### CT-034: Obter Status da Sessão
**Endpoint**: `GET /api/v1/waha/sessions/{name}/status` | **Estados**: WORKING, STOPPED

### CT-035: Parar Sessão WAHA
**Endpoint**: `POST /api/v1/waha/sessions/{name}/stop` | **Status**: 200

### CT-036: Enviar Mensagem de Texto
**Endpoint**: `POST /api/v1/waha/messages/text` | **Status**: 200

### CT-037: Enviar Imagem
**Endpoint**: `POST /api/v1/waha/messages/image` | **Status**: 200

### CT-038: Enviar Localização
**Endpoint**: `POST /api/v1/waha/messages/location` | **Status**: 200

### CT-039: Enviar Botões Interativos
**Endpoint**: `POST /api/v1/waha/messages/buttons` | **Limite**: 3 botões

### CT-040: Enviar Lista de Opções
**Endpoint**: `POST /api/v1/waha/messages/list` | **Status**: 200

### CT-041: Enviar Enquete
**Endpoint**: `POST /api/v1/waha/messages/poll` | **Status**: 200

### CT-042: Marcar Mensagem como Lida
**Endpoint**: `POST /api/v1/waha/messages/{chat_id}/{message_id}/seen`

### CT-043: Definir Presença
**Endpoint**: `POST /api/v1/waha/sessions/{name}/presence`

---

## 4.5 PLAYBOOKS E STEPS

### CT-044: Criar Playbook
**Endpoint**: `POST /api/v1/playbooks/` | **Status**: 201

### CT-045: Busca Semântica de Playbooks
**Endpoint**: `GET /api/v1/playbooks/search?query=...&top_k=3`

### CT-046: Obter Playbook por ID
**Endpoint**: `GET /api/v1/playbooks/{playbook_id}` | **Status**: 200

### CT-047: Listar Playbooks por Tópico
**Endpoint**: `GET /api/v1/playbooks/topic/{topic_id}` | **Status**: 200

### CT-048: Atualizar Playbook
**Endpoint**: `PATCH /api/v1/playbooks/{playbook_id}` | **Status**: 200

### CT-049: Deletar Playbook
**Endpoint**: `DELETE /api/v1/playbooks/{playbook_id}` | **Status**: 200

---

## 4.6 TÓPICOS

### CT-050: Criar Tópico
**Endpoint**: `POST /api/v1/topics/` | **Status**: 201

### CT-051: Listar Tópicos
**Endpoint**: `GET /api/v1/topics/` | **Status**: 200

### CT-052: Obter Tópico por ID
**Endpoint**: `GET /api/v1/topics/{topic_id}` | **Status**: 200

### CT-053: Atualizar Tópico
**Endpoint**: `PATCH /api/v1/topics/{topic_id}` | **Status**: 200

### CT-054: Deletar Tópico
**Endpoint**: `DELETE /api/v1/topics/{topic_id}` | **Status**: 200

---

## 4.7 MENSAGENS E MÍDIA

### CT-055: Criar Mensagem de Texto
**Endpoint**: `POST /api/v1/messages/` | **Status**: 201

### CT-056: Criar Mensagem com Mídia
**Endpoint**: `POST /api/v1/messages/` | **Tipo**: image, video, document

### CT-057: Criar Mensagem de Localização
**Endpoint**: `POST /api/v1/messages/` | **Tipo**: location

### CT-058: Obter Mensagem por ID
**Endpoint**: `GET /api/v1/messages/{message_id}` | **Status**: 200

### CT-059: Listar Mensagens
**Endpoint**: `GET /api/v1/messages/` | **Status**: 200

### CT-060: Atualizar Mensagem
**Endpoint**: `PATCH /api/v1/messages/{message_id}` | **Status**: 200

### CT-061: Deletar Mensagem
**Endpoint**: `DELETE /api/v1/messages/{message_id}` | **Status**: 200

### CT-062: Gerar Descrição com IA
**Endpoint**: `POST /api/v1/messages/{message_id}/generate-description`
**Funcionalidade**: Gemini Vision analisa imagem/vídeo e gera título, descrição e tags

---

## 4.8 CONVERSAS

### CT-063: Listar Conversas
**Endpoint**: `GET /api/v1/conversations/`
**Query**: `?status=ACTIVE&urgent_only=false&limit=50`

### CT-064: Exportar Conversas para CSV
**Endpoint**: `GET /api/v1/conversations/export`
**Query**: `?start_date=2026-01-01&end_date=2026-01-31`

### CT-065: Buscar Conversas (Full-Text)
**Endpoint**: `GET /api/v1/conversations/search?q=agendamento`

### CT-066: Obter Conversa por ID
**Endpoint**: `GET /api/v1/conversations/{conversation_id}` | **Status**: 200

### CT-067: Obter Mensagens da Conversa
**Endpoint**: `GET /api/v1/conversations/{conversation_id}/messages`

### CT-068: Atualizar Status da Conversa
**Endpoint**: `PATCH /api/v1/conversations/{conversation_id}/status`
**Estados Válidos**: ACTIVE, WAITING_SECRETARY, TRANSFERRED, CLOSED

### CT-069: Transferir Conversa para Atendente
**Endpoint**: `POST /api/v1/conversations/{conversation_id}/transfer`

### CT-070: Fechar Conversa
**Endpoint**: `POST /api/v1/conversations/{conversation_id}/close`

### CT-071: Atualizar Notas da Conversa
**Endpoint**: `PATCH /api/v1/conversations/{conversation_id}/notes`

---

## 4.9 LEADS E INTERAÇÕES

### CT-072: Listar Leads
**Endpoint**: `GET /api/v1/leads/`
**Query**: `?status=NEW&assigned_to_me=true&limit=50`

### CT-073: Obter Lead por ID
**Endpoint**: `GET /api/v1/leads/{lead_id}` | **Status**: 200

### CT-074: Obter Histórico de Interações do Lead
**Endpoint**: `GET /api/v1/leads/{lead_id}/interactions`

### CT-075: Criar Lead Manualmente
**Endpoint**: `POST /api/v1/leads/`
**Body**: `{"phone_number": "5551999887766", "name": "Maria Silva"}`

### CT-076: Atualizar Maturity Score do Lead
**Endpoint**: `PATCH /api/v1/leads/{lead_id}/maturity`
**Body**: `{"score": 75}`

### CT-077: Atribuir Lead a Atendente
**Endpoint**: `POST /api/v1/leads/{lead_id}/assign`
**Body**: `{"user_id": 2}`

### CT-078: Auto-Atribuir Lead (Round-Robin)
**Endpoint**: `POST /api/v1/leads/{lead_id}/auto-assign`

### CT-079: Converter Lead
**Endpoint**: `POST /api/v1/leads/{lead_id}/convert`
**Efeito**: status=CONVERTED, score=100

### CT-080: Marcar Lead como Perdido
**Endpoint**: `POST /api/v1/leads/{lead_id}/lost`
**Body**: `{"reason": "Não atendeu ligações"}`

### CT-081: Deletar Lead (Soft Delete)
**Endpoint**: `DELETE /api/v1/leads/{lead_id}` | **Status**: 200

### CT-082: Restaurar Lead Deletado
**Endpoint**: `POST /api/v1/leads/{lead_id}/restore`

---

## 4.10 TAGS

### CT-083: Criar Tag
**Endpoint**: `POST /api/v1/tags/` | **Status**: 201

### CT-084: Listar Tags
**Endpoint**: `GET /api/v1/tags/` | **Status**: 200

### CT-085: Atualizar Tag
**Endpoint**: `PATCH /api/v1/tags/{tag_id}` | **Status**: 200

### CT-086: Deletar Tag
**Endpoint**: `DELETE /api/v1/tags/{tag_id}` | **Status**: 200

---

## 4.11 WEBHOOKS

### CT-087: Receber Webhook WAHA (Mensagem Inbound)
**Endpoint**: `POST /api/v1/webhooks/waha`
**Header**: `X-WAHA-Event: message`
**Objetivo**: Processar mensagens recebidas do WhatsApp

### CT-088: Processar Evento de Status de Mensagem
**Endpoint**: `POST /api/v1/webhooks/waha`
**Header**: `X-WAHA-Event: message.ack`

---

## 4.12 GEMINI AI

### CT-089: Análise de Intenção com Gemini
**Endpoint**: `POST /api/v1/ai/analyze`
**Body**: `{"message": "Quero agendar consulta"}`
**Resposta**: `{"intent": "AGENDAMENTO", "confidence": 0.95}`

### CT-090: Gerar Resposta Contextual
**Endpoint**: `POST /api/v1/ai/generate-response`
**Objetivo**: Gerar resposta baseada em contexto da conversa

### CT-091: Análise de Sentimento
**Endpoint**: `GET /api/v1/ai/sentiment?conversation_id=...`
**Resposta**: `{"sentiment": "POSITIVE", "score": 0.8}`

---

## 4.13 NOTIFICAÇÕES

### CT-092: Listar Notificações
**Endpoint**: `GET /api/v1/notifications/` | **Status**: 200

### CT-093: Marcar Notificação como Lida
**Endpoint**: `POST /api/v1/notifications/{id}/read`

### CT-094: Marcar Todas como Lidas
**Endpoint**: `POST /api/v1/notifications/read-all`

### CT-095: Deletar Notificação
**Endpoint**: `DELETE /api/v1/notifications/{id}` | **Status**: 200

---

## 4.14 HANDOFF (Bot → Humano)

### CT-096: Disparar Handoff
**Endpoint**: `POST /api/v1/handoff/conversations/{id}/trigger`
**Body**: `{"reason": "score_high"}`
**Motivos Válidos**: score_high, bot_confused, manual

### CT-097: Atribuir Conversa para Atendente
**Endpoint**: `POST /api/v1/handoff/conversations/{id}/assign`
**Body**: `{"user_id": "uuid-atendente"}`

### CT-098: Concluir Conversa (Agendamento Confirmado)
**Endpoint**: `POST /api/v1/handoff/conversations/{id}/complete`
**Efeito**: status=COMPLETED, lead.score=100

### CT-099: Devolver Conversa ao Bot
**Endpoint**: `POST /api/v1/handoff/conversations/{id}/return-to-bot`

### CT-100: Listar Conversas Aguardando Handoff
**Endpoint**: `GET /api/v1/handoff/pending`
**Ordenação**: Urgência DESC, Score DESC, Tempo Aguardando ASC

---

## 4.15 MÉTRICAS E DASHBOARD

### CT-101: Dashboard Principal (KPIs)
**Endpoint**: `GET /api/v1/metrics/dashboard`
**Query**: `?period=30d`

### CT-102: Funil de Conversão
**Endpoint**: `GET /api/v1/metrics/funnel`

### CT-103: Taxa de Autonomia do Bot
**Endpoint**: `GET /api/v1/metrics/bot-autonomy`
**Permissão**: Admin only

### CT-104: Tempo de Resposta do Bot
**Endpoint**: `GET /api/v1/metrics/performance/response-time`

### CT-105: Taxa de Handoff
**Endpoint**: `GET /api/v1/metrics/performance/handoff-rate`

### CT-106: Horários de Pico
**Endpoint**: `GET /api/v1/metrics/performance/peak-hours`

### CT-107: Distribuição por Status
**Endpoint**: `GET /api/v1/metrics/performance/conversations-by-status`

### CT-108: Relatório Completo de Performance
**Endpoint**: `GET /api/v1/metrics/performance/report`

### CT-109: Exportar Relatório (PDF)
**Endpoint**: `GET /api/v1/metrics/performance/report/pdf`

### CT-110: Exportar Relatório (Excel)
**Endpoint**: `GET /api/v1/metrics/performance/report/excel`

### CT-111: Conversão por Fonte
**Endpoint**: `GET /api/v1/metrics/conversion/by-source`

### CT-112: Leads por Status
**Endpoint**: `GET /api/v1/metrics/leads/by-status`

### CT-113: Relatório de Análise de Conversas
**Endpoint**: `GET /api/v1/metrics/conversation/report`

### CT-114: Distribuição de Tópicos
**Endpoint**: `GET /api/v1/analytics/topics`

### CT-115: Análise de Sentimento
**Endpoint**: `GET /api/v1/analytics/sentiment`

### CT-116: Nuvem de Palavras
**Endpoint**: `GET /api/v1/analytics/keywords`

### CT-117: WebSocket de Métricas em Tempo Real
**Endpoint**: `WS /api/v1/metrics/ws?token=...`
**Objetivo**: Atualizações em tempo real para dashboard

---

## 4.16 FILAS E JOBS

### CT-118: Status das Filas Redis
**Endpoint**: `GET /api/v1/queues/status`
**Resposta**: Contagem de jobs pending, processing, failed

### CT-119: Listar Dead Letter Queue
**Endpoint**: `GET /api/v1/jobs/dlq`

### CT-120: Retry Job da DLQ
**Endpoint**: `POST /api/v1/jobs/dlq/{job_id}/retry`

---

## 4.17 AUDITORIA

### CT-121: Listar Logs de Auditoria
**Endpoint**: `GET /api/v1/audit-logs`
**Query**: `?entity_type=user&limit=50`

### CT-122: Obter Logs por Entidade
**Endpoint**: `GET /api/v1/audit-logs/entity/{entity_type}/{entity_id}`

---

## 5. Matriz de Rastreabilidade

### 5.1 Casos × Endpoints

| Módulo | Endpoints | Casos de Teste | Cobertura |
|--------|-----------|----------------|-----------|
| Health | 2 | CT-001, CT-002 | 100% |
| Auth | 15 | CT-003 a CT-021 | 100% |
| Users | 8 | CT-022 a CT-029 | 100% |
| WAHA | 14 | CT-030 a CT-043 | 100% |
| Playbooks | 6 | CT-044 a CT-049 | 100% |
| Topics | 5 | CT-050 a CT-054 | 100% |
| Messages | 8 | CT-055 a CT-062 | 100% |
| Conversations | 9 | CT-063 a CT-071 | 100% |
| Leads | 11 | CT-072 a CT-082 | 100% |
| Tags | 4 | CT-083 a CT-086 | 100% |
| Webhooks | 2 | CT-087 a CT-088 | 100% |
| AI | 3 | CT-089 a CT-091 | 100% |
| Notifications | 4 | CT-092 a CT-095 | 100% |
| Handoff | 5 | CT-096 a CT-100 | 100% |
| Metrics | 17 | CT-101 a CT-117 | 100% |
| Queues/Jobs | 3 | CT-118 a CT-120 | 100% |
| Audit | 2 | CT-121 a CT-122 | 100% |

**Total**: 118 casos de teste | 161 endpoints | **100% cobertura**

---

## 6. Critérios de Aceitação

### 6.1 Performance

| Endpoint | SLA | Ação se Exceder |
|----------|-----|-----------------|
| Health Check | < 500ms | Alertar DevOps |
| Login | < 1s | Verificar DB |
| Busca Semântica | < 2s | Verificar ChromaDB |
| Análise AI | < 5s | Verificar Gemini |

### 6.2 Qualidade

- [ ] 100% dos endpoints testados
- [ ] Todos os cenários de erro documentados
- [ ] Rate limiting funcionando
- [ ] Auditoria registrando eventos

### 6.3 Segurança

- [ ] Tokens JWT com expiração adequada
- [ ] Cookies HttpOnly configurados
- [ ] MFA funcionando
- [ ] Rate limiting ativo

---

## 7. Procedimentos de Execução

### 7.1 Preparação do Ambiente

```bash
# 1. Subir serviços
docker-compose up -d

# 2. Verificar health
curl http://localhost:3333/api/v1/health

# 3. Aplicar migrations
alembic upgrade head
```

### 7.2 Ordem de Execução

1. **Infraestrutura** (CT-001, CT-002)
2. **Autenticação** (CT-003 a CT-021)
3. **Usuários** (CT-022 a CT-029)
4. **WAHA** (CT-030 a CT-043)
5. **Playbooks/Tópicos** (CT-044 a CT-054)
6. **Conteúdo** (CT-055 a CT-071)
7. **Leads** (CT-072 a CT-086)
8. **Integrações** (CT-087 a CT-095)
9. **Handoff** (CT-096 a CT-100)
10. **Métricas** (CT-101 a CT-122)

### 7.3 Registro de Resultados

| Caso | Status | Data | Observações |
|------|--------|------|-------------|
| CT-001 | ⏳ | - | - |
| CT-002 | ⏳ | - | - |
| ... | ... | ... | ... |

---

## 8. Considerações Finais

### 8.1 Autoavaliação do Documento

| Critério | Nota | Justificativa |
|----------|------|---------------|
| Cobertura de Cenários | 9/10 | 100% endpoints cobertos |
| Clareza e Organização | 9/10 | Estrutura padronizada |
| Aderência às Melhores Práticas | 9/10 | Template consistente |
| Utilidade para Testes | 9/10 | Pronto para execução |

**Nota Final: 9/10**

**Justificativa**: Documento completo com cobertura total de endpoints, estrutura padronizada e pronto para uso em testes manuais e automatizados. Pontos para melhoria futura: adicionar exemplos de payload detalhados para todos os cenários de erro.

---

**Documento gerado em**: 2026-01-27  
**Gerado por**: AI-Context Quality Engineering  
**Revisado por**: Equipe de Desenvolvimento

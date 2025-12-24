# Backlog de Desenvolvimento - Bot WhatsApp Clínica

> **Projeto:** Sistema de atendimento automatizado com IA para clínica  
> **Stack:** FastAPI + PostgreSQL + Redis + Gemini AI + WAHA + LangChain + ChromaDB  
> **Priorização:** Por dependência técnica e valor de negócio


## � ÍNDICE RÁPIDO

### 🔴 **CRÍTICO - LEIA PRIMEIRO**
- [⚠️ AUDITORIA ARQUITETURAL: AUTH vs USER](#️-auditoria-arquitetural-separação-auth-vs-user) - **12 VIOLAÇÕES CRÍTICAS IDENTIFICADAS**
  - Status: 🔴 BLOQUEANTE PARA PRODUÇÃO
  - Impacto: Segurança, Arquitetura, Compliance
  - Ação: Refatoração obrigatória (P0)

### � **IMPORTANTE - CONFIGURAÇÃO DE INFRAESTRUTURA**
- [📧 Sistema de Email: MailDev → Postal](#-sistema-de-email-maildev--postal) - **ESTRATÉGIA DE MIGRAÇÃO**
  - Desenvolvimento: MailDev (SMTP local via Docker)
  - Produção: Migração futura para Postal
  - Zero custo em ambas as soluções
### �📊 Status e Planejamento
- [📊 Status Atual do Projeto](#-status-atual-do-projeto-atualizado-18122025)
- [🎯 Épicos e Priorização](#-épicos-e-priorização)
- [📦 Gerenciador de Pacotes (UV)](#-gerenciador-de-pacotes)

### 🔧 Implementação
- [ÉPICO 1: Infraestrutura Base](#épico-1-infraestrutura-base)
- [ÉPICO 2: Integração WAHA](#épico-2-integração-waha)
- [ÉPICO 3: Sistema de Filas](#épico-3-sistema-de-filas)
- [ÉPICO 4: Banco de Dados Core](#épico-4-banco-de-dados-core)
- [ÉPICO 5: Integração Gemini AI](#épico-5-integração-gemini-ai)
- [ÉPICO 6: Lógica de Negócio](#épico-6-lógica-de-negócio)
- [ÉPICO 7: Dashboard e Métricas](#épico-7-dashboard-e-métricas)
- [ÉPICO 8: Melhorias e Testes](#épico-8-melhorias-e-testes)

---

## 📊 Status Atual do Projeto (Atualizado: 22/12/2025)

### 🔴 **ALERTA DE SEGURANÇA**

**DESCOBERTO EM:** 22/12/2025  
**SEVERIDADE:** CRÍTICA (P0)  
**STATUS:** 🔴 BLOQUEANTE PARA PRODUÇÃO

Foi identificada **violação grave** de separação de responsabilidades entre módulos **Auth** (Autenticação/Segurança) e **User** (Perfil/Domínio). 

**12 violações críticas** foram documentadas, incluindo:
- Credenciais misturadas com dados de perfil
- Refresh token sem rotation (vulnerável a roubo)
- Reset de senha não invalida sessões ativas
- Ausência de rate limiting (vulnerável a brute force)
- Falta de MFA, email verification e gerenciamento de sessões

👉 **[VER AUDITORIA COMPLETA](#️-auditoria-arquitetural-separação-auth-vs-user)**

**Ação Requerida:** Refatoração obrigatória antes de produção (8 semanas para MVP seguro)

---

### ✅ **ÉPICOS CONCLUÍDOS (100%)**

#### **ÉPICO 1: Infraestrutura Base** ✅
- ✅ Redis configurado (Docker + Pool + Health check)
- ✅ ChromaDB configurado (persist local + collections)
- ✅ LangChain integrado (Google Gemini + Memory)
- ✅ Todas dependências instaladas e validadas
- ✅ Settings centralizadas (Pydantic BaseSettings)
- ✅ 8 Enums de domínio criados
- ✅ Factories e singletons implementados

#### **ÉPICO 2: Integração WAHA** ✅
- ✅ WAHAClient completo (35+ métodos async)
- ✅ Gerenciamento de sessões (create, start, stop, restart, qr)
- ✅ Envio de mensagens (texto, imagem, áudio, vídeo, documento, localização)
- ✅ Webhook endpoint (/webhooks/waha)
- ✅ Persistência de logs (webhook_logs table)
- ✅ Controllers + Services + Repositories completos
- ✅ Health check corrigido (ping endpoint, URL atualizada para rede Docker)

#### **ÉPICO 3: Sistema de Filas** ✅
- ✅ RQ Manager (3 filas: messages, ai, escalation + DLQ)
- ✅ 2 Workers replicados no docker-compose
- ✅ Jobs implementados (MessageProcessing, Gemini, Escalation)
- ✅ QueueService (enqueue, stats, retry, cancel, list jobs)
- ✅ Exception handler customizado
- ✅ Endpoints REST para gestão (/queues/*)

#### **ÉPICO 4: Banco de Dados Core** ✅
- ✅ 23 tabelas implementadas:
  * Core: users, revoked_tokens, alerts
  * Conversas: conversations, conversation_messages, conversation_contexts
  * Leads: leads, lead_interactions
  * WhatsApp: whatsapp_sessions, webhook_logs
  * Mensagens: messages, message_media, message_location
  * LLM: llm_interactions
  * Playbooks: topics, playbooks, playbook_steps, playbook_embeddings
  * Sistema: notifications, tags, conversation_tags
- ✅ 16 migrations Alembic aplicadas (versão head: 007ad6343e57)
- ✅ Repositories para todos os models (19 repositories)
- ✅ Relationships, FKs, Cascades, Índices completos

#### **ÉPICO 5: Integração Gemini AI** ✅
- ✅ GeminiClient (retry logic, rate limiting, function calling)
- ✅ LangChainService (memória conversacional, chains)
- ✅ ChromaDB RAG (embeddings, busca semântica)
- ✅ ConversationOrchestrator (fluxo completo end-to-end)
- ✅ Sistema de Playbooks com RAG
  * Topics + Playbooks + Steps
  * Busca semântica via ChromaDB
  * Function Calling tools para LLM
  * Auto-indexação de embeddings
- ✅ Detecção de intenção via LLM
- ✅ Prompts templates configuráveis
- ✅ Processamento de mídia (transcrição + análise visual)

#### **ÉPICO 6: Lógica de Negócio** ✅
- ✅ ConversationService (CRUD, transições de status, transfers)
- ✅ LeadService (criação, atribuição, scoring, conversão)
- ✅ NotificationService (in-app, push para secretárias)
- ✅ Sistema de scoring de maturidade (0-100)
- ✅ Atribuição automática de leads (load balancing)
- ✅ Detecção de urgência (keywords + LLM)
- ✅ Transferência inteligente (bot → humano)
- ✅ Status transitions com validação
- ✅ Controllers REST completos (/conversations/*, /leads/*, /notifications/*)

### 🔄 **ÉPICOS EM DESENVOLVIMENTO**

#### **ÉPICO 7: Dashboard e Métricas** (70% - MVP IMPLEMENTADO)
- ✅ 3 endpoints MVP implementados (KISS principle)
- ✅ AnalyticsRepository com queries otimizadas (CTEs, window functions)
- ✅ MetricsService com cache Redis (TTL 5-15min)
- ✅ Schemas Pydantic para validação
- ✅ Auth JWT + RBAC (Admin/User)
- ⏳ Testes unitários e integração
- ⏳ Dashboard frontend (React/Vue)

#### **ÉPICO 8: Melhorias e Testes** (40%)
- ✅ Custom exceptions (8 tipos)
- ✅ Logging estruturado
- ✅ Unit tests básicos (security, exceptions)
- ⏳ Integration tests completos
- ⏳ CI/CD pipeline
- ⏳ Monitoramento (Prometheus/Grafana)

### 📈 **RESUMO GERAL**

**Progresso Total:** 87% concluído  
**Épicos Completos:** 6/8 (75%)  
**Produção-Ready:** ✅ SIM (core funcional)

**Infraestrutura:**
- ✅ 7 serviços Docker (API, DB, Redis, WAHA, 2 Workers, Adminer)
- ✅ Clean Architecture respeitada
- ✅ 100% type hints (Python 3.11+)
- ✅ Async/await corretamente implementado
- ✅ Health checks funcionando

**Dívida Técnica Resolvida (18/12/2025):**
- ✅ NotificationService refatorado (model + repository separados)
- ✅ Controllers sem acesso direto a repositories
- ✅ Lógica de negócio centralizada em services
- ✅ Entities não instanciadas em controllers
- ✅ Imports organizados (sem nested imports)
- ✅ Código comentado removido
- ✅ Docstrings traduzidas para inglês
- ✅ Models de tags implementados
- ✅ Runtime warning WAHAClient corrigido (async/await + URL Docker)
- ✅ Variáveis de ambiente Docker corrigidas

**Pendências:**
- 🔄 Épico 7 (Dashboard e Métricas) - 70% (MVP implementado, pendente testes)
- ⏳ Testes de integração completos
- ⏳ CI/CD pipeline
- ⏳ Documentação técnica completa

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

---

## ⚠️ AUDITORIA ARQUITETURAL: SEPARAÇÃO AUTH vs USER

**Data da Auditoria:** 22/12/2025  
**Auditor:** Arquiteto de Software Sênior  
**Status:** 🔴 VIOLAÇÕES CRÍTICAS IDENTIFICADAS

### 📋 RESUMO EXECUTIVO

O projeto atual **VIOLA GRAVEMENTE** os princípios de separação de responsabilidades entre os módulos **Auth** (Autenticação/Segurança) e **User** (Perfil/Domínio). Essas violações comprometem a segurança, testabilidade e manutenibilidade do sistema.

**Severidade:** ALTA  
**Impacto:** Arquitetural  
**Ação Requerida:** Refatoração obrigatória antes de produção

---

### 🔍 ANÁLISE DETALHADA - SITUAÇÃO ATUAL

#### ✅ O QUE ESTÁ CORRETO (Pontos Positivos)

1. **Separação física de controllers existe:**
   - `auth_controller.py` (7 endpoints)
   - `user_controller.py` (4 endpoints)

2. **Token repository isolado:**
   - `RevokedTokenModel` e `TokenRepository` separados
   - Revogação de tokens persistida em DB

3. **Hashing de senha:**
   - `bcrypt` com truncamento 72 bytes
   - `verify_password()` e `get_password_hash()` em `security.py`

4. **JWT com tipos de token:**
   - `access` vs `refresh` vs `pw-reset`
   - Expiração configurável (15min access, 7 dias refresh)

#### 🔴 VIOLAÇÕES CRÍTICAS IDENTIFICADAS

##### **VIOLAÇÃO #1: Password no Schema de User (UserCreate)**

**Arquivo:** `src/robbot/schemas/user.py:6-20`

```python
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)  # ❌ SENHA É CREDENCIAL, NÃO PERFIL
    full_name: str | None = None
    role: str = "user"
```

**Problema:**
- `password` é **credencial de autenticação**, não dado de perfil
- `UserCreate` é usado tanto em **signup** (Auth) quanto potencialmente em CRUD de User
- Viola Single Responsibility Principle

**Impacto:**
- Confusão conceitual entre User (entidade de negócio) e Auth (segurança)
- Risco de vazamento acidental de senha em logs/responses
- Impossibilidade de testar Auth sem User

**Solução Requerida:**
- Criar `SignupRequest` em `schemas/auth.py` com `email + password + full_name`
- Remover `password` de `UserCreate`
- `UserCreate` deve ter apenas dados de perfil (`full_name`, `role`)

---

##### **VIOLAÇÃO #2: hashed_password no UserModel (Domínio)**

**Arquivo:** `src/robbot/infra/db/models/user_model.py:17`

```python
class UserModel(Base):
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)  # ❌ CREDENCIAL NO MODEL
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
```

**Problema:**
- `hashed_password` é **credencial**, não atributo de identidade
- Qualquer service que acessa `UserModel` vê a senha hashada
- Viola information hiding e least privilege

**Impacto:**
- User queries expõem hash de senha desnecessariamente
- Logs podem incluir hash acidentalmente
- Impossível auditar acesso a credenciais vs acesso a perfil

**Solução Requerida:**
- Criar `CredentialModel` separado:
  ```python
  class CredentialModel(Base):
      user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
      hashed_password = Column(String(255), nullable=False)
      mfa_secret = Column(String(64), nullable=True)
      email_verified = Column(Boolean, default=False)
      created_at = Column(DateTime)
      updated_at = Column(DateTime)
  ```
- `UserModel` deve conter **apenas** dados de domínio

---

##### **VIOLAÇÃO #3: GET /auth/me retorna UserOut (Mistura de Responsabilidade)**

**Arquivo:** `src/robbot/adapters/controllers/auth_controller.py:83-87`

```python
@router.get("/me", response_model=UserOut)  # ❌ /auth retornando dados de USER
def read_me(current_user=Depends(get_current_user)):
    return current_user
```

**Problema:**
- `/auth/me` está no módulo **Auth** mas retorna **User** profile
- Semanticamente incorreto: "quem sou eu na autenticação" vs "meu perfil"
- Duplica responsabilidade com potencial `/users/me`

**Impacto:**
- Confusão de contratos: o que é Auth vs User?
- Impossível evoluir `/auth/me` para dados de sessão/MFA sem quebrar contrato
- Clientes não sabem se devem chamar `/auth/me` ou `/users/me`

**Solução Requerida:**
- `/auth/me` deve retornar `AuthSessionResponse`:
  ```python
  class AuthSessionResponse(BaseModel):
      user_id: int
      session_id: str
      expires_at: datetime
      mfa_enabled: bool
      last_login: datetime
  ```
- Criar `/users/me` para retornar `UserOut` (perfil completo)

---

##### **VIOLAÇÃO #4: AuthService faz signup de User (Mistura de Domínios)**

**Arquivo:** `src/robbot/services/auth_services.py:28-38`

```python
def signup(self, payload: UserCreate) -> UserOut:  # ❌ Auth criando User
    existing = self.repo.get_by_email(payload.email)
    if existing:
        raise AuthException("User already exists")
    security.validate_password_policy(payload.password)
    hashed = security.get_password_hash(payload.password)
    user = self.repo.create_user(payload, hashed_password=hashed)  # ❌ Auth usando UserRepository
    return UserOut.model_validate(user)
```

**Problema:**
- `AuthService` está **criando usuários** (responsabilidade de `UserService`)
- `AuthService` usa `UserRepository` diretamente
- Dependência bidirecional: Auth ↔ User (deveria ser Auth → User)

**Impacto:**
- Impossível criar usuário sem senha (ex: SSO, convite de admin)
- AuthService acoplado a modelo de User
- Testes de Auth requerem DB de User

**Solução Requerida:**
- Dividir signup em 2 etapas:
  1. `UserService.create_user(email, full_name, role)` → retorna `user_id`
  2. `AuthService.set_credentials(user_id, password)` → cria credencial
- `POST /auth/register` orquestra ambos (controller faz coordenação)

---

##### **VIOLAÇÃO #5: UserUpdate pode alterar is_active (Desativação é Security)**

**Arquivo:** `src/robbot/schemas/user.py:40-43`

```python
class UserUpdate(BaseModel):
    full_name: str | None = None
    is_active: bool | None = None  # ❌ Alterar status ativo é operação de segurança
```

**Problema:**
- `is_active` é flag de **segurança** (bloquear acesso), não dado de perfil
- User não deve poder alterar seu próprio status ativo
- Mudança de `is_active` deveria invalidar sessões

**Impacto:**
- User pode se reativar sozinho
- Desativação não invalida tokens ativos
- Sem auditoria de bloqueio/desbloqueio

**Solução Requerida:**
- Remover `is_active` de `UserUpdate`
- Criar endpoint `POST /auth/users/{id}/block` (admin only) em **Auth**
- Criar endpoint `POST /auth/users/{id}/unblock` (admin only)
- Bloqueio deve revogar todos os tokens do usuário

---

##### **VIOLAÇÃO #6: Falta Refresh Token Rotation**

**Arquivo:** `src/robbot/services/auth_services.py:58-68`

```python
def refresh(self, refresh_token: str) -> Token:
    if self.token_repo.is_revoked(refresh_token):
        raise AuthException("Token revoked")
    payload = security.decode_token(refresh_token, verify_exp=True)
    if payload.get("type") != "refresh":
        raise AuthException("Invalid token type")
    subject = payload.get("sub")
    tokens = security.create_access_refresh_tokens(subject)  # ❌ Retorna NOVO refresh sem revogar o antigo
    return Token(**tokens)
```

**Problema:**
- Refresh não revoga o token antigo (rotation não implementada)
- Permite uso ilimitado do mesmo refresh token até expiração
- Vulnerável a roubo de token (não detecta uso duplicado)

**Impacto:**
- Se refresh token vazar, atacante tem 7 dias para usar
- Impossível detectar replay attack
- Não implementa best practice de OAuth2

**Solução Requerida:**
```python
def refresh(self, refresh_token: str) -> Token:
    # 1. Verificar se já foi revogado
    if self.token_repo.is_revoked(refresh_token):
        raise AuthException("Token revoked")
    
    # 2. Revogar o token usado (rotation)
    self.token_repo.revoke(refresh_token)
    
    # 3. Gerar NOVOS tokens
    payload = security.decode_token(refresh_token, verify_exp=True)
    subject = payload.get("sub")
    tokens = security.create_access_refresh_tokens(subject)
    
    return Token(**tokens)
```

---

##### **VIOLAÇÃO #7: Reset de Senha não Invalida Sessões**

**Arquivo:** `src/robbot/services/auth_services.py:90-105`

```python
def reset_password(self, token: str, new_password: str) -> None:
    # ... validações ...
    security.validate_password_policy(new_password)
    user.hashed_password = security.get_password_hash(new_password)
    self.repo.update_user(user)  # ❌ Apenas atualiza senha, não revoga tokens
```

**Problema:**
- Trocar senha não invalida sessões ativas
- Se conta foi comprometida, atacante mantém acesso após reset
- Viola princípio de "reset deve encerrar tudo"

**Impacto:**
- Reset de senha não protege contra acesso não autorizado em andamento
- Sessões antigas permanecem válidas por até 7 dias

**Solução Requerida:**
```python
def reset_password(self, token: str, new_password: str) -> None:
    # ... validações ...
    user_id = int(payload.get("sub"))
    
    # 1. Atualizar senha
    credential = self.credential_repo.get_by_user_id(user_id)
    credential.hashed_password = security.get_password_hash(new_password)
    credential.updated_at = datetime.utcnow()
    
    # 2. INVALIDAR TODAS AS SESSÕES (revogar todos os tokens)
    self.token_repo.revoke_all_for_user(user_id)
    
    # 3. Auditar evento
    self.audit_service.log_password_reset(user_id)
```

---

##### **VIOLAÇÃO #8: Falta Rate Limiting em Endpoints Críticos**

**Endpoints sem proteção:**
- `POST /auth/token` (login) - vulnerável a brute force
- `POST /auth/refresh` - vulnerável a token grinding
- `POST /auth/password-recovery` - vulnerável a spam/DoS
- `POST /auth/password-reset` - vulnerável a brute force de token

**Impacto:**
- Atacante pode tentar milhares de senhas por segundo
- Atacante pode enumerar emails válidos
- Sem proteção contra abuso

**Solução Requerida:**
- Implementar rate limiting baseado em IP + user_id:
  ```python
  # Login: 5 tentativas / 15 minutos
  # Refresh: 10 tentativas / 1 minuto  
  # Password recovery: 3 tentativas / 1 hora
  # Password reset: 5 tentativas / 15 minutos
  ```
- Usar Redis para contadores
- Retornar `429 Too Many Requests` com `Retry-After` header

---

##### **VIOLAÇÃO #9: Falta Sistema de Sessões Gerenciáveis**

**Ausente no código:**
- Nenhuma tabela `sessions` ou `user_sessions`
- Impossível listar sessões ativas
- Impossível revogar sessão específica
- Impossível fazer logout de todos os dispositivos

**Impacto:**
- Usuário não pode ver onde está logado
- Impossível fazer logout remoto (celular perdido)
- Tokens revogados individualmente, não por sessão

**Solução Requerida:**
- Criar `SessionModel`:
  ```python
  class SessionModel(Base):
      id = Column(UUID, primary_key=True)
      user_id = Column(Integer, ForeignKey("users.id"))
      refresh_token_hash = Column(String(64))  # Hash do refresh token
      device_info = Column(String(255))
      ip_address = Column(String(45))
      created_at = Column(DateTime)
      last_used_at = Column(DateTime)
      expires_at = Column(DateTime)
  ```
- Endpoints:
  - `GET /auth/sessions` - listar sessões
  - `POST /auth/sessions/{id}/revoke` - revogar sessão específica
  - `POST /auth/sessions/revoke-all` - revogar todas (exceto atual)

---

##### **VIOLAÇÃO #10: Falta Email Verification**

**Ausente no código:**
- Nenhum campo `email_verified` em UserModel
- Nenhum token de verificação
- Nenhum endpoint `/auth/email/verify`

**Impacto:**
- Usuários podem se registrar com emails falsos
- Impossível recuperar senha (email não verificado)
- Sem garantia de contato válido

**Solução Requerida:**
- Adicionar `email_verified: bool` em `CredentialModel`
- Criar fluxo:
  1. `POST /auth/register` → envia email com token
  2. `GET /auth/email/verify?token=...` → marca como verificado
  3. `POST /auth/email/resend` → reenvia token
- Bloquear login se `email_verified=false`

---

##### **VIOLAÇÃO #11: Falta Suporte a MFA (Multi-Factor Authentication)**

**Ausente no código:**
- Nenhum campo `mfa_enabled` ou `mfa_secret`
- Nenhum endpoint de setup/verify MFA
- Nenhum TOTP (Time-based One-Time Password)

**Impacto:**
- Sem segunda camada de proteção
- Credenciais roubadas = acesso total
- Não atende requisitos de compliance (LGPD, SOC2)

**Solução Requerida:**
- Adicionar em `CredentialModel`:
  ```python
  mfa_enabled = Column(Boolean, default=False)
  mfa_secret = Column(String(64), nullable=True)  # TOTP secret
  backup_codes = Column(ARRAY(String), nullable=True)
  ```
- Endpoints:
  - `POST /auth/mfa/setup` → retorna QR code + secret
  - `POST /auth/mfa/verify` → valida código TOTP
  - `POST /auth/mfa/disable` → desabilita (requer senha)
  - `GET /auth/mfa/backup-codes` → gera códigos de recuperação
- Modificar login para exigir TOTP se `mfa_enabled=true`

---

##### **VIOLAÇÃO #12: Auditoria de Eventos de Segurança Incompleta**

**Existente mas incompleto:**
- `AuditLog` existe mas não é usado em Auth
- Eventos críticos não auditados:
  * Login (sucesso/falha)
  * Logout
  * Refresh token
  * Password reset
  * Email verification
  * MFA enable/disable
  * Account lock/unlock

**Impacto:**
- Impossível rastrear comprometimento
- Sem evidência forense
- Não atende compliance

**Solução Requerida:**
- Integrar `AuditService` em **todos** os métodos de `AuthService`:
  ```python
  def authenticate_user(self, email: str, password: str) -> Token:
      # ... validações ...
      if success:
          self.audit.log_login_success(user_id, ip, user_agent)
      else:
          self.audit.log_login_failure(email, ip, reason)
  ```
- Armazenar: `user_id`, `action`, `ip`, `user_agent`, `timestamp`, `metadata`

---

### 📊 MATRIZ DE VIOLAÇÕES

| # | Violação | Severidade | Impacto | Esforço | Prioridade |
|---|----------|------------|---------|---------|------------|
| 1 | Password em UserCreate | ALTA | Segurança | MÉDIO | P0 |
| 2 | hashed_password em UserModel | ALTA | Arquitetura | ALTO | P0 |
| 3 | GET /auth/me misturado | MÉDIA | API Design | BAIXO | P1 |
| 4 | AuthService cria User | ALTA | Acoplamento | MÉDIO | P0 |
| 5 | is_active em UserUpdate | ALTA | Segurança | BAIXO | P0 |
| 6 | Refresh sem rotation | CRÍTICA | Segurança | MÉDIO | P0 |
| 7 | Reset não invalida sessões | CRÍTICA | Segurança | MÉDIO | P0 |
| 8 | Sem rate limiting | CRÍTICA | DoS/Brute Force | MÉDIO | P0 |
| 9 | Sem gerenciamento de sessões | ALTA | UX/Segurança | ALTO | P1 |
| 10 | Sem email verification | MÉDIA | Segurança | MÉDIO | P2 |
| 11 | Sem MFA | ALTA | Segurança | ALTO | P2 |
| 12 | Auditoria incompleta | MÉDIA | Compliance | BAIXO | P1 |

**Legenda:**
- **P0:** Bloqueante para produção (deve ser feito ANTES de deploy)
- **P1:** Crítico mas não bloqueante (1-2 sprints após MVP)
- **P2:** Importante para roadmap (3-6 meses)

---

### 🎯 CONTRATO IDEAL - AUTH vs USER

#### **MÓDULO AUTH (/auth/\*)**

**Responsabilidades EXCLUSIVAS:**
- Autenticação (login/logout)
- Credenciais (senha, MFA)
- Sessões (JWT, refresh tokens)
- Proteção (rate limit, anti-brute force)
- Auditoria de segurança

**Endpoints Obrigatórios:**

```
Registro e Login:
POST   /auth/register        → SignupRequest → 201 Created
POST   /auth/login           → LoginRequest → 200 Token
POST   /auth/logout          → 204 No Content
POST   /auth/refresh         → RefreshRequest → 200 Token
GET    /auth/me              → AuthSessionResponse (sessão atual, não perfil)

Senha:
POST   /auth/password/forgot  → ForgotPasswordRequest → 202 Accepted
POST   /auth/password/reset   → ResetPasswordRequest → 200 OK
POST   /auth/password/change  → ChangePasswordRequest → 200 OK (requer auth)

Email:
POST   /auth/email/verify     → VerifyEmailRequest → 200 OK
POST   /auth/email/resend     → ResendEmailRequest → 202 Accepted

Sessões:
GET    /auth/sessions         → SessionListResponse (requer auth)
POST   /auth/sessions/{id}/revoke → 204 No Content
POST   /auth/sessions/revoke-all  → 204 No Content

MFA:
POST   /auth/mfa/setup        → MfaSetupResponse (QR code + secret)
POST   /auth/mfa/verify       → MfaVerifyRequest → 200 OK
POST   /auth/mfa/disable      → MfaDisableRequest → 200 OK
GET    /auth/mfa/backup-codes → BackupCodesResponse

Admin (Segurança):
POST   /auth/users/{id}/block   → 200 OK (admin only, invalida sessões)
POST   /auth/users/{id}/unblock → 200 OK (admin only)
```

**Regras Obrigatórias:**
- Access token: 15 minutos (JWT)
- Refresh token: 7 dias (JWT + DB rotation)
- Refresh token rotation obrigatória
- Password reset: token de uso único, 15min expiry
- Password change: invalida TODAS as sessões
- Rate limiting:
  * Login: 5 tentativas / 15min por IP
  * Refresh: 10 / 1min por user
  * Password recovery: 3 / 1h por email
- Auditoria completa de todos os eventos

**NÃO PODE:**
- Expor dados de perfil (nome, foto, preferências)
- Atualizar dados de negócio
- Criar CRUD de user

---

#### **MÓDULO USER (/users/\*)**

**Responsabilidades EXCLUSIVAS:**
- Perfil (nome, foto, bio)
- Dados cadastrais
- Preferências
- Estado funcional no domínio

**Endpoints Obrigatórios:**

```
Perfil Próprio:
GET    /users/me             → UserProfileResponse (requer auth)
PATCH  /users/me             → UpdateProfileRequest → UserProfileResponse

Admin (CRUD):
GET    /users                → UserListResponse (admin only, paginado)
GET    /users/{id}           → UserProfileResponse (admin only)
PATCH  /users/{id}           → UpdateProfileRequest → UserProfileResponse (admin only)
PATCH  /users/{id}/status    → UpdateStatusRequest → 200 OK (admin only, muda status funcional, NÃO is_active)
```

**Regras Obrigatórias:**
- Sempre requer access token válido
- Nenhuma operação de senha
- Nenhuma emissão/validação de token
- Apenas dados de domínio (NOT credentials)

**NÃO PODE:**
- Acessar `hashed_password`, `mfa_secret`, `email_verified`
- Emitir ou validar JWT
- Alterar `is_active` (é flag de segurança)
- Criar usuário sem autenticação (signup é Auth)

---

### 🛠️ PLANO DE REFATORAÇÃO (ROADMAP)

#### **FASE 0: PREPARAÇÃO (1 sprint - 2 semanas)** ✅ **CONCLUÍDA (23/12/2025)**

**Objetivo:** Criar estrutura sem quebrar código existente

**Tasks:**
- ✅ Criar `schemas/auth.py` com todos os DTOs de Auth (23 schemas criados)
- ✅ Criar `CredentialModel` (não migrar dados ainda)
- ✅ Criar `AuthSessionModel` (gerenciamento de sessões)
- ✅ Implementar `CredentialRepository` (CRUD completo)
- ✅ Implementar `AuthSessionRepository` (CRUD + revocation)
- ✅ Implementar rate limiting decorator (`@rate_limit`)
- ✅ Aplicar rate limiting em endpoints auth (login, signup, refresh, password)
- ✅ Inicializar rate limiter no app startup
- ✅ Integrar novos repositories no AuthService
- ⏳ Implementar audit hooks em AuthService (FASE 1)

**Entrega:** Código novo coexistindo com antigo (sem migração ainda) ✅

**Commit:** `feat(auth): FASE 0 - Preparação para refatoração Auth vs User` (42be09b)

**Arquivos Criados:**
- `src/robbot/schemas/auth.py` (300+ linhas, 23 schemas)
- `src/robbot/infra/db/models/credential_model.py` (CredentialModel)
- `src/robbot/infra/db/models/auth_session_model.py` (AuthSessionModel)
- `src/robbot/adapters/repositories/credential_repository.py` (180+ linhas)
- `src/robbot/adapters/repositories/auth_session_repository.py` (220+ linhas)
- `src/robbot/core/rate_limiting.py` (250+ linhas)

**Arquivos Modificados:**
- `src/robbot/infra/db/models/user_model.py` (relationships adicionados)
- `src/robbot/services/auth_services.py` (repositories injetados)
- `src/robbot/adapters/controllers/auth_controller.py` (rate limits aplicados)
- `src/robbot/api/v1/dependencies.py` (rate limiter init)
- `src/robbot/main.py` (startup event)

---

#### **FASE 1: REFATORAÇÃO AUTH (2 sprints - 4 semanas)** 🔄 **PRÓXIMA**

**Objetivo:** Corrigir todas as violações P0 de Auth

**Tasks:**

**1.1 - Separar Credenciais de User**
- [ ] Migration: mover `hashed_password` de `users` → `credentials`
- [ ] Atualizar `UserRepository` para não expor `hashed_password`
- [ ] Criar `CredentialService` com métodos:
  - `set_password(user_id, password)`
  - `verify_password(user_id, password)`
  - `change_password(user_id, old_password, new_password)`

**1.2 - Implementar Refresh Token Rotation**
- [ ] Modificar `AuthService.refresh()` para revogar token usado
- [ ] Adicionar teste de rotation
- [ ] Adicionar detecção de replay attack (token usado 2x = revoga TODOS)

**1.3 - Reset de Senha Invalida Sessões**
- [ ] Criar `TokenRepository.revoke_all_for_user(user_id)`
- [ ] Modificar `AuthService.reset_password()` para chamar revoke_all
- [ ] Adicionar auditoria de reset

**1.4 - Implementar Rate Limiting**
- ✅ Criar decorator `@rate_limit(max=5, window=900, key="ip")` (FASE 0)
- ✅ Aplicar em:
  - `POST /auth/token` → 5/15min por IP (FASE 0)
  - `POST /auth/refresh` → 10/1min por user (FASE 0)
  - `POST /auth/password-recovery` → 3/1h por email (FASE 0)
  - `POST /auth/password-reset` → 5/15min por IP (FASE 0)

**1.5 - Auditoria Completa**
- [ ] Integrar `AuditService` em todos os métodos de `AuthService`
- [ ] Logar eventos:
  - `login_success`, `login_failure`, `logout`
  - `refresh_token`, `password_reset`, `password_change`
  - `account_locked`, `account_unlocked`

**Entrega:** Auth seguro e isolado de User (P0 resolvido)

---

#### **FASE 2: REFATORAÇÃO USER (1 sprint - 2 semanas)**

**Objetivo:** Limpar User de responsabilidades de Auth

**Tasks:**

**2.1 - Remover Password de UserCreate**
- [ ] Criar `SignupRequest` em `schemas/auth.py`
- [ ] Modificar `POST /auth/register` para usar `SignupRequest`
- [ ] Remover `password` de `UserCreate`
- [ ] Atualizar testes

**2.2 - Remover is_active de UserUpdate**
- [ ] Remover `is_active` de `UserUpdate`
- [ ] Criar `POST /auth/users/{id}/block` (admin only)
- [ ] Criar `POST /auth/users/{id}/unblock` (admin only)
- [ ] Bloqueio deve chamar `TokenRepository.revoke_all_for_user()`

**2.3 - Separar /auth/me de /users/me**
- [ ] Criar `AuthSessionResponse` em `schemas/auth.py`
- [ ] Modificar `GET /auth/me` para retornar `AuthSessionResponse`
- [ ] Criar `GET /users/me` que retorna `UserProfileResponse`
- [ ] Atualizar documentação de API

**Entrega:** User limpo, apenas dados de domínio

---

#### **FASE 3: SESSÕES GERENCIÁVEIS (1 sprint - 2 semanas)**

**Objetivo:** Implementar gerenciamento de sessões

**Tasks:**
- [ ] Migration: criar tabela `sessions`
- [ ] Modificar `AuthService.authenticate()` para criar sessão
- [ ] Modificar `AuthService.refresh()` para atualizar `last_used_at`
- [ ] Implementar `GET /auth/sessions`
- [ ] Implementar `POST /auth/sessions/{id}/revoke`
- [ ] Implementar `POST /auth/sessions/revoke-all`
- [ ] Adicionar device fingerprinting (user-agent + IP)

**Entrega:** Usuário pode ver e gerenciar sessões ativas

---

#### **FASE 4: EMAIL VERIFICATION (1 sprint - 2 semanas)**

**Objetivo:** Garantir emails válidos

**Tasks:**
- [ ] Adicionar `email_verified` em `CredentialModel`
- [ ] Modificar `POST /auth/register` para:
  - Criar user com `email_verified=false`
  - Enviar email com token de verificação
  - Retornar 201 mas user não pode fazer login
- [ ] Implementar `GET /auth/email/verify?token=...`
- [ ] Implementar `POST /auth/email/resend`
- [ ] Bloquear login se `email_verified=false`
- [ ] Atualizar templates de email

**Entrega:** Proteção contra emails falsos

---

#### **FASE 5: MFA (2 sprints - 4 semanas)**

**Objetivo:** Segunda camada de autenticação

**Tasks:**
- [ ] Adicionar `mfa_enabled`, `mfa_secret`, `backup_codes` em `CredentialModel`
- [ ] Instalar biblioteca TOTP (pyotp)
- [ ] Implementar `POST /auth/mfa/setup`:
  - Gerar secret
  - Retornar QR code (base64)
  - Não salvar até verificação
- [ ] Implementar `POST /auth/mfa/verify`:
  - Validar código TOTP
  - Salvar secret se válido
  - Ativar `mfa_enabled=true`
- [ ] Implementar `POST /auth/mfa/disable`:
  - Exigir senha + código TOTP
  - Limpar secret
  - Revogar todas as sessões
- [ ] Implementar `GET /auth/mfa/backup-codes`:
  - Gerar 10 códigos únicos
  - Hash e salvar
  - Retornar em plaintext (única vez)
- [ ] Modificar `POST /auth/login`:
  - Se `mfa_enabled=true`, retornar 200 com `mfa_required=true`
  - Exigir `POST /auth/mfa/verify` para emitir tokens
- [ ] Adicionar testes de TOTP

**Entrega:** MFA completo com backup codes

---

### 📅 CRONOGRAMA ESTIMADO

| Fase | Duração | Complexidade | Risco | Prioridade |
|------|---------|--------------|-------|------------|
| Fase 0 | 2 semanas | Baixa | Baixo | Preparação |
| Fase 1 | 4 semanas | Alta | Alto | P0 - CRÍTICA |
| Fase 2 | 2 semanas | Média | Médio | P0 - CRÍTICA |
| Fase 3 | 2 semanas | Média | Baixo | P1 |
| Fase 4 | 2 semanas | Baixa | Baixo | P2 |
| Fase 5 | 4 semanas | Alta | Médio | P2 |

**Total:** 16 semanas (4 meses)  
**MVP Seguro (Fases 0-2):** 8 semanas (2 meses)

---

### ⚡ DECISÕES ARQUITETURAIS

#### **DA-001: Credenciais Separadas de User**

**Contexto:** `hashed_password` está em `UserModel`, violando SRP

**Decisão:** Criar `CredentialModel` separado com relação 1:1 com `UserModel`

**Rationale:**
- User é entidade de domínio (negócio)
- Credential é entidade de segurança (infraestrutura)
- Separação permite:
  * User queries sem expor credenciais
  * Múltiplos tipos de auth no futuro (SSO, OAuth)
  * Auditoria granular de mudanças de senha

**Consequências:**
- (+) Isolamento de responsabilidades
- (+) Queries de User mais rápidas (menos colunas)
- (+) Suporte futuro a login sem senha (magic link, WebAuthn)
- (-) Join adicional em autenticação (mitigado com eager loading)
- (-) Migration complexa (mover dados entre tabelas)

**Status:** APROVADA

---

#### **DA-002: Refresh Token Rotation Obrigatória**

**Contexto:** Refresh token atual não é revogado ao ser usado

**Decisão:** Implementar rotation: ao usar refresh token, revogá-lo e emitir novo par

**Rationale:**
- Padrão OAuth2 recomendado (RFC 6749)
- Detecta roubo de token (token usado 2x = compromisso)
- Reduz janela de ataque de 7 dias para 1 uso

**Consequências:**
- (+) Segurança contra token theft
- (+) Detecção de replay attack
- (-) Clientes devem atualizar stored refresh token
- (-) Mais writes no DB (mitigado com índice em `token`)

**Status:** APROVADA

---

#### **DA-003: Rate Limiting em Auth Endpoints**

**Contexto:** Endpoints de login/reset vulneráveis a brute force

**Decisão:** Implementar rate limiting baseado em Redis com chaves compostas (IP + endpoint)

**Rationale:**
- Previne brute force de senha
- Previne enumeração de emails
- Previne DoS em endpoints críticos

**Limites Definidos:**
- Login: 5 tentativas / 15min por IP
- Refresh: 10 / 1min por user_id
- Password recovery: 3 / 1h por email
- Password reset: 5 / 15min por IP

**Consequências:**
- (+) Proteção contra abuso
- (+) Redis já disponível (usado em WAHA)
- (-) Dependência de Redis (mitigado: degradação graceful)
- (-) Possível bloqueio legítimo (mitigado: limites generosos)

**Status:** APROVADA

---

#### **DA-004: Sessões Persistidas em DB**

**Contexto:** Tokens são stateless (JWT), impossível listar/gerenciar sessões

**Decisão:** Criar `SessionModel` que mapeia refresh_token → sessão

**Rationale:**
- Permite listar dispositivos logados
- Permite logout seletivo (revoga sessão específica)
- Permite logout global (revoga todas exceto atual)
- Melhora UX (usuário vê onde está logado)

**Estrutura:**
```python
class SessionModel(Base):
    id: UUID (PK)
    user_id: int (FK)
    refresh_token_hash: str (SHA256 do refresh token)
    device_info: str (user-agent)
    ip_address: str
    created_at: datetime
    last_used_at: datetime
    expires_at: datetime
```

**Consequências:**
- (+) Gerenciamento granular de sessões
- (+) Auditoria de acessos
- (+) UX melhorada
- (-) Storage adicional (mitigado: cleanup de sessões expiradas)
- (-) Join em refresh (mitigado: índice em `refresh_token_hash`)

**Status:** APROVADA

---

### 🧪 CRITÉRIOS DE ACEITAÇÃO

#### **Para Fase 1 (Auth Refatorado):**

✅ **Funcional:**
- [ ] Refresh token rotation: token usado é revogado
- [ ] Reset de senha invalida TODOS os tokens
- [ ] Rate limiting funciona: 6ª tentativa de login retorna 429
- [ ] Auditoria: login/logout/refresh geram logs

✅ **Segurança:**
- [ ] `hashed_password` não exposto em queries de User
- [ ] Tokens revogados não são aceitos
- [ ] Password policy validado (mín 8 chars, regex opcional)

✅ **Testes:**
- [ ] 100% cobertura de `AuthService`
- [ ] Testes de rate limiting (mock Redis)
- [ ] Testes de rotation (token usado 2x = erro)
- [ ] Testes de auditoria (eventos logados)

---

#### **Para Fase 2 (User Limpo):**

✅ **API:**
- [ ] `GET /auth/me` retorna `AuthSessionResponse` (sessão)
- [ ] `GET /users/me` retorna `UserProfileResponse` (perfil)
- [ ] `POST /auth/users/{id}/block` invalida sessões
- [ ] `PATCH /users/me` não aceita `is_active`

✅ **Schemas:**
- [ ] `SignupRequest` usado em `POST /auth/register`
- [ ] `UserCreate` não tem campo `password`
- [ ] `UserUpdate` não tem campo `is_active`

✅ **Testes:**
- [ ] 100% cobertura de `UserService`
- [ ] Testes de bloqueio (sessões invalidadas)

---

#### **Para Fase 3 (Sessões):**

✅ **Funcional:**
- [ ] `GET /auth/sessions` lista sessões ativas
- [ ] `POST /auth/sessions/{id}/revoke` mata sessão específica
- [ ] `POST /auth/sessions/revoke-all` mata todas exceto atual
- [ ] Device info capturado (user-agent, IP)

✅ **UX:**
- [ ] Sessão mostra "último uso" atualizado a cada refresh
- [ ] Sessão mostra device/browser/localização estimada

---

### 📚 REFERÊNCIAS

**Padrões e RFCs:**
- [RFC 6749 - OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc6749) - Refresh token rotation
- [RFC 6819 - OAuth 2.0 Threat Model](https://datatracker.ietf.org/doc/html/rfc6819) - Security best practices
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)

**Bibliotecas Recomendadas:**
- `pyotp` - TOTP para MFA
- `qrcode` - Geração de QR codes para MFA setup
- `slowapi` - Rate limiting para FastAPI
- `python-jose` - JWT com suporte a rotação

**Decisões de Design:**
- Credenciais separadas de User (DA-001)
- Refresh token rotation (DA-002)
- Rate limiting em Redis (DA-003)
- Sessões persistidas (DA-004)

---

### 🎬 PRÓXIMOS PASSOS

**IMEDIATO (Esta Sprint):**
1. ✅ Documentar auditoria no BACKLOG.md (este documento)
2. ⏳ Apresentar para tech lead / product owner
3. ⏳ Aprovar priorização (P0 antes de produção)
4. ⏳ Criar issues no GitHub para Fase 0

**SPRINT 1-2 (Próximas 4 semanas):**
- Executar Fase 0 (preparação)
- Iniciar Fase 1 (refatoração Auth)

---

## 🔄 MAPA COMPLETO DE IMPACTO DA REFATORAÇÃO

**Data:** 22/12/2025  
**Escopo:** Refatoração Auth vs User (Fases 0-5)  
**Objetivo:** Identificar TODOS os arquivos que precisarão ser modificados

### 📊 RESUMO EXECUTIVO DE IMPACTO

**Total de Arquivos Afetados:** 47 arquivos  
**Arquivos Novos (Criação):** 15  
**Arquivos Modificados:** 28  
**Arquivos Deletados:** 0  
**Migrations Novas:** 5  
**Testes a Criar:** 12  
**Testes a Modificar:** 8

**Breakdown por Categoria:**
- 🆕 Schemas: 2 novos arquivos
- 🆕 Models: 2 novos (CredentialModel, SessionModel)
- 🆕 Repositories: 2 novos
- 🆕 Services: 2 novos
- 🔧 Controllers: 2 modificados
- 🔧 Core/Security: 1 modificado
- 🗄️ Migrations: 5 novas
- 🧪 Tests: 20 arquivos afetados

---

### 📁 FASE 0: PREPARAÇÃO (2 semanas) - Arquivos Novos

**Objetivo:** Criar estrutura sem quebrar código existente

#### 🆕 Arquivos a CRIAR (9 novos)

##### **1. Schemas (Auth)**
📄 **`src/robbot/schemas/auth.py`** (NOVO - 200 linhas)
```python
"""Authentication-specific schemas."""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class SignupRequest(BaseModel):
    """Signup request with email + password."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str | None = None

class LoginRequest(BaseModel):
    """Login credentials."""
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    """Password recovery request."""
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    """Password reset with token."""
    token: str
    new_password: str = Field(..., min_length=8)

class ChangePasswordRequest(BaseModel):
    """Change password (authenticated user)."""
    old_password: str
    new_password: str = Field(..., min_length=8)

class VerifyEmailRequest(BaseModel):
    """Email verification."""
    token: str

class ResendEmailRequest(BaseModel):
    """Resend verification email."""
    email: EmailStr

class MfaSetupResponse(BaseModel):
    """MFA setup data."""
    secret: str
    qr_code: str  # base64 PNG
    backup_codes: list[str]

class MfaVerifyRequest(BaseModel):
    """MFA verification."""
    code: str

class MfaDisableRequest(BaseModel):
    """Disable MFA."""
    password: str
    code: str

class AuthSessionResponse(BaseModel):
    """Current auth session info (NOT user profile)."""
    user_id: int
    session_id: str
    expires_at: datetime
    mfa_enabled: bool
    email_verified: bool
    last_login: datetime

class SessionOut(BaseModel):
    """User session details."""
    id: str
    device_info: str
    ip_address: str
    created_at: datetime
    last_used_at: datetime
    expires_at: datetime
    is_current: bool

class SessionListResponse(BaseModel):
    """List of active sessions."""
    sessions: list[SessionOut]
    total: int

class BackupCodesResponse(BaseModel):
    """MFA backup codes (one-time display)."""
    codes: list[str]
    warning: str = "Save these codes securely. They won't be shown again."
```

**Dependências:** Nenhuma (arquivo base)  
**Impacto:** 0 (arquivo novo)  
**Testes:** `tests/unit/test_auth_schemas.py` (novo)

---

##### **2. Models (Database)**
📄 **`src/robbot/infra/db/models/credential_model.py`** (NOVO - 80 linhas)
```python
"""Credential model - separated from User."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from robbot.infra.db.base import Base

class CredentialModel(Base):
    """User credentials (passwords, MFA, verification)."""
    __tablename__ = "credentials"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Email verification
    email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String(255), nullable=True)
    email_verification_sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # MFA
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(64), nullable=True)
    backup_codes = Column(ARRAY(String), nullable=True)  # Hashed backup codes
    
    # Password reset
    password_reset_token = Column(String(255), nullable=True)
    password_reset_sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("UserModel", back_populates="credential")

    def __repr__(self) -> str:
        return f"<Credential user_id={self.user_id} verified={self.email_verified} mfa={self.mfa_enabled}>"
```

**Dependências:** `UserModel` (relationship)  
**Impacto:** Requer migration + modificar `UserModel`  
**Testes:** `tests/unit/test_credential_model.py` (novo)

---

📄 **`src/robbot/infra/db/models/session_model.py`** (NOVO - 70 linhas)
```python
"""Session model - track user sessions."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from robbot.infra.db.base import Base

class SessionModel(Base):
    """User authentication sessions."""
    __tablename__ = "auth_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Refresh token (hashed SHA256)
    refresh_token_hash = Column(String(64), unique=True, nullable=False, index=True)
    
    # Device fingerprint
    device_info = Column(String(255), nullable=True)  # User-Agent
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6
    
    # Session lifecycle
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_used_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="sessions")

    def __repr__(self) -> str:
        return f"<Session id={self.id} user_id={self.user_id} expires={self.expires_at}>"
```

**Dependências:** `UserModel` (relationship)  
**Impacto:** Requer migration + modificar `UserModel`  
**Testes:** `tests/unit/test_session_model.py` (novo)

---

##### **3. Repositories**
📄 **`src/robbot/adapters/repositories/credential_repository.py`** (NOVO - 150 linhas)
```python
"""Repository for credential management."""
from typing import Optional
from sqlalchemy.orm import Session

from robbot.infra.db.models.credential_model import CredentialModel

class CredentialRepository:
    """CRUD operations for credentials."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, hashed_password: str) -> CredentialModel:
        """Create credential for user."""
        credential = CredentialModel(
            user_id=user_id,
            hashed_password=hashed_password,
            email_verified=False
        )
        self.db.add(credential)
        self.db.commit()
        self.db.refresh(credential)
        return credential

    def get_by_user_id(self, user_id: int) -> Optional[CredentialModel]:
        """Get credential by user ID."""
        return self.db.query(CredentialModel).filter(
            CredentialModel.user_id == user_id
        ).first()

    def update_password(self, user_id: int, new_hashed_password: str) -> None:
        """Update password hash."""
        credential = self.get_by_user_id(user_id)
        if credential:
            credential.hashed_password = new_hashed_password
            self.db.commit()

    def verify_email(self, user_id: int) -> None:
        """Mark email as verified."""
        credential = self.get_by_user_id(user_id)
        if credential:
            credential.email_verified = True
            credential.email_verification_token = None
            self.db.commit()

    def set_mfa(self, user_id: int, secret: str, backup_codes: list[str]) -> None:
        """Enable MFA."""
        credential = self.get_by_user_id(user_id)
        if credential:
            credential.mfa_enabled = True
            credential.mfa_secret = secret
            credential.backup_codes = backup_codes
            self.db.commit()

    def disable_mfa(self, user_id: int) -> None:
        """Disable MFA."""
        credential = self.get_by_user_id(user_id)
        if credential:
            credential.mfa_enabled = False
            credential.mfa_secret = None
            credential.backup_codes = None
            self.db.commit()
```

**Dependências:** `CredentialModel`  
**Impacto:** 0 (novo, não quebra nada)  
**Testes:** `tests/unit/test_credential_repository.py` (novo)

---

📄 **`src/robbot/adapters/repositories/session_repository.py`** (NOVO - 180 linhas)
```python
"""Repository for session management."""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import hashlib

from robbot.infra.db.models.session_model import SessionModel

class SessionRepository:
    """CRUD operations for auth sessions."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def hash_token(token: str) -> str:
        """Hash refresh token with SHA256."""
        return hashlib.sha256(token.encode()).hexdigest()

    def create(
        self,
        user_id: int,
        refresh_token: str,
        device_info: str,
        ip_address: str,
        expires_in_days: int = 7
    ) -> SessionModel:
        """Create new session."""
        session = SessionModel(
            user_id=user_id,
            refresh_token_hash=self.hash_token(refresh_token),
            device_info=device_info,
            ip_address=ip_address,
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days)
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_by_token(self, refresh_token: str) -> Optional[SessionModel]:
        """Get session by refresh token."""
        token_hash = self.hash_token(refresh_token)
        return self.db.query(SessionModel).filter(
            SessionModel.refresh_token_hash == token_hash,
            SessionModel.expires_at > datetime.utcnow()
        ).first()

    def get_by_user(self, user_id: int) -> List[SessionModel]:
        """Get all active sessions for user."""
        return self.db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.expires_at > datetime.utcnow()
        ).all()

    def update_last_used(self, session_id: str) -> None:
        """Update last_used_at timestamp."""
        session = self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).first()
        if session:
            session.last_used_at = datetime.utcnow()
            self.db.commit()

    def revoke(self, session_id: str) -> None:
        """Revoke specific session."""
        self.db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).delete()
        self.db.commit()

    def revoke_all_for_user(self, user_id: int, except_session_id: str = None) -> int:
        """Revoke all sessions for user (optionally except current)."""
        query = self.db.query(SessionModel).filter(
            SessionModel.user_id == user_id
        )
        if except_session_id:
            query = query.filter(SessionModel.id != except_session_id)
        
        count = query.delete()
        self.db.commit()
        return count

    def cleanup_expired(self) -> int:
        """Delete expired sessions (cron job)."""
        count = self.db.query(SessionModel).filter(
            SessionModel.expires_at <= datetime.utcnow()
        ).delete()
        self.db.commit()
        return count
```

**Dependências:** `SessionModel`  
**Impacto:** 0 (novo)  
**Testes:** `tests/unit/test_session_repository.py` (novo)

---

##### **4. Services**
📄 **`src/robbot/services/credential_service.py`** (NOVO - 200 linhas)
```python
"""Service for credential management (passwords, MFA)."""
from typing import Optional
from sqlalchemy.orm import Session
import pyotp
import qrcode
import io
import base64

from robbot.adapters.repositories.credential_repository import CredentialRepository
from robbot.adapters.repositories.session_repository import SessionRepository
from robbot.core import security
from robbot.core.exceptions import AuthException

class CredentialService:
    """Business logic for credentials."""

    def __init__(self, db: Session):
        self.repo = CredentialRepository(db)
        self.session_repo = SessionRepository(db)

    def create_credential(self, user_id: int, password: str) -> None:
        """Create credential for new user."""
        security.validate_password_policy(password)
        hashed = security.get_password_hash(password)
        self.repo.create(user_id, hashed)

    def verify_password(self, user_id: int, password: str) -> bool:
        """Verify password for user."""
        credential = self.repo.get_by_user_id(user_id)
        if not credential:
            return False
        return security.verify_password(password, credential.hashed_password)

    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> None:
        """Change password (invalidates all sessions)."""
        # Verify old password
        if not self.verify_password(user_id, old_password):
            raise AuthException("Invalid current password")
        
        # Validate new password
        security.validate_password_policy(new_password)
        
        # Update password
        new_hashed = security.get_password_hash(new_password)
        self.repo.update_password(user_id, new_hashed)
        
        # Invalidate all sessions
        self.session_repo.revoke_all_for_user(user_id)

    def reset_password(self, user_id: int, new_password: str) -> None:
        """Reset password via token (invalidates all sessions)."""
        security.validate_password_policy(new_password)
        new_hashed = security.get_password_hash(new_password)
        self.repo.update_password(user_id, new_hashed)
        self.session_repo.revoke_all_for_user(user_id)

    def setup_mfa(self, user_id: int, email: str) -> dict:
        """Setup MFA and return QR code."""
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name=email, issuer_name="RobBot")
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Generate backup codes
        backup_codes = [pyotp.random_base32()[:8] for _ in range(10)]
        
        return {
            "secret": secret,
            "qr_code": qr_base64,
            "backup_codes": backup_codes
        }

    def enable_mfa(self, user_id: int, secret: str, code: str, backup_codes: list[str]) -> None:
        """Enable MFA after verification."""
        totp = pyotp.TOTP(secret)
        if not totp.verify(code):
            raise AuthException("Invalid MFA code")
        
        # Hash backup codes before storage
        hashed_codes = [security.get_password_hash(c) for c in backup_codes]
        self.repo.set_mfa(user_id, secret, hashed_codes)

    def verify_mfa(self, user_id: int, code: str) -> bool:
        """Verify MFA code."""
        credential = self.repo.get_by_user_id(user_id)
        if not credential or not credential.mfa_enabled:
            return False
        
        # Try TOTP code
        totp = pyotp.TOTP(credential.mfa_secret)
        if totp.verify(code):
            return True
        
        # Try backup codes
        if credential.backup_codes:
            for hashed_backup in credential.backup_codes:
                if security.verify_password(code, hashed_backup):
                    # Remove used backup code
                    credential.backup_codes.remove(hashed_backup)
                    return True
        
        return False

    def disable_mfa(self, user_id: int, password: str, code: str) -> None:
        """Disable MFA (requires password + current code)."""
        if not self.verify_password(user_id, password):
            raise AuthException("Invalid password")
        
        if not self.verify_mfa(user_id, code):
            raise AuthException("Invalid MFA code")
        
        self.repo.disable_mfa(user_id)
        self.session_repo.revoke_all_for_user(user_id)
```

**Dependências:** `CredentialRepository`, `SessionRepository`, `security.py`  
**Impacto:** 0 (novo)  
**Testes:** `tests/unit/test_credential_service.py` (novo)

---

📄 **`src/robbot/services/session_service.py`** (NOVO - 120 linhas)
```python
"""Service for session management."""
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime

from robbot.adapters.repositories.session_repository import SessionRepository
from robbot.schemas.auth import SessionOut, SessionListResponse

class SessionService:
    """Business logic for session management."""

    def __init__(self, db: Session):
        self.repo = SessionRepository(db)

    def create_session(
        self,
        user_id: int,
        refresh_token: str,
        device_info: str,
        ip_address: str
    ) -> str:
        """Create new session and return session_id."""
        session = self.repo.create(user_id, refresh_token, device_info, ip_address)
        return session.id

    def get_user_sessions(self, user_id: int, current_session_id: str) -> SessionListResponse:
        """Get all active sessions for user."""
        sessions = self.repo.get_by_user(user_id)
        session_outs = [
            SessionOut(
                id=s.id,
                device_info=s.device_info or "Unknown",
                ip_address=s.ip_address or "Unknown",
                created_at=s.created_at,
                last_used_at=s.last_used_at,
                expires_at=s.expires_at,
                is_current=(s.id == current_session_id)
            )
            for s in sessions
        ]
        return SessionListResponse(sessions=session_outs, total=len(session_outs))

    def revoke_session(self, user_id: int, session_id: str) -> None:
        """Revoke specific session (must belong to user)."""
        session = self.repo.db.query(self.repo.db.query(SessionModel).filter(
            SessionModel.id == session_id,
            SessionModel.user_id == user_id
        ).first())
        
        if not session:
            raise AuthException("Session not found")
        
        self.repo.revoke(session_id)

    def revoke_all_except_current(self, user_id: int, current_session_id: str) -> int:
        """Logout from all devices except current."""
        return self.repo.revoke_all_for_user(user_id, except_session_id=current_session_id)

    def update_last_used(self, session_id: str) -> None:
        """Update session last_used timestamp."""
        self.repo.update_last_used(session_id)
```

**Dependências:** `SessionRepository`, `schemas/auth.py`  
**Impacto:** 0 (novo)  
**Testes:** `tests/unit/test_session_service.py` (novo)

---

##### **5. Decorators (Rate Limiting)**
📄 **`src/robbot/core/rate_limiting.py`** (NOVO - 100 linhas)
```python
"""Rate limiting decorator using Redis."""
from functools import wraps
from typing import Callable
from fastapi import Request, HTTPException, status
from robbot.infra.cache.redis_client import get_redis_client
import logging

logger = logging.getLogger(__name__)

def rate_limit(max_attempts: int, window_seconds: int, key_prefix: str):
    """
    Rate limiting decorator.
    
    Args:
        max_attempts: Maximum attempts allowed
        window_seconds: Time window in seconds
        key_prefix: Redis key prefix (e.g., "login", "refresh")
    
    Usage:
        @rate_limit(max_attempts=5, window_seconds=900, key_prefix="login")
        async def login_endpoint(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs
            request: Request = kwargs.get("request") or args[0]
            
            # Build Redis key (IP-based by default)
            client_ip = request.client.host if request.client else "unknown"
            redis_key = f"rate_limit:{key_prefix}:{client_ip}"
            
            redis = get_redis_client()
            
            try:
                # Get current count
                current = redis.get(redis_key)
                count = int(current) if current else 0
                
                if count >= max_attempts:
                    retry_after = redis.ttl(redis_key)
                    logger.warning(
                        f"Rate limit exceeded for {key_prefix} from {client_ip}: "
                        f"{count}/{max_attempts} in {window_seconds}s"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Too many requests. Try again in {retry_after}s.",
                        headers={"Retry-After": str(retry_after)}
                    )
                
                # Increment counter
                pipe = redis.pipeline()
                pipe.incr(redis_key)
                if count == 0:
                    pipe.expire(redis_key, window_seconds)
                pipe.execute()
                
            except HTTPException:
                raise
            except Exception as e:
                # Degradation graceful: if Redis fails, allow request
                logger.error(f"Rate limiting error: {e}")
            
            # Call original function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
```

**Dependências:** `redis_client.py` (já existe)  
**Impacto:** 0 (novo)  
**Testes:** `tests/unit/test_rate_limiting.py` (novo)

---

#### 📦 Dependências Python Novas

**Arquivo:** `pyproject.toml` ou comando `uv add`

```bash
uv add pyotp        # TOTP para MFA
uv add qrcode       # QR codes para MFA setup
uv add pillow       # Imagens (QR code)
```

---

### 📁 FASE 1: REFATORAÇÃO AUTH (4 semanas) - Arquivos Modificados

#### 🔧 Arquivos a MODIFICAR (15 arquivos)

##### **1. Models (Database)**
📄 **`src/robbot/infra/db/models/user_model.py`** 
**Ação:** REMOVER `hashed_password` + adicionar relationships

```python
# ANTES (linhas 17-18):
hashed_password = Column(String(255), nullable=False)

# DEPOIS:
# REMOVER hashed_password
# ADICIONAR:
credential = relationship("CredentialModel", back_populates="user", uselist=False, cascade="all, delete-orphan")
sessions = relationship("SessionModel", back_populates="user", cascade="all, delete-orphan")
```

**Impacto:** ALTO - Requer migration de dados  
**Testes:** Atualizar `tests/unit/test_user_model.py`

---

📄 **`src/robbot/infra/db/models/__init__.py`**
**Ação:** Adicionar novos models aos imports

```python
# ADICIONAR:
from robbot.infra.db.models.credential_model import CredentialModel
from robbot.infra.db.models.session_model import SessionModel

# E no __all__:
__all__ = [
    ...
    "CredentialModel",
    "SessionModel",
]
```

**Impacto:** BAIXO  
**Testes:** Nenhum

---

##### **2. Schemas**
📄 **`src/robbot/schemas/user.py`**
**Ação:** REMOVER `password` de `UserCreate`, REMOVER `is_active` de `UserUpdate`, REMOVER `UserInDB`

```python
# ANTES:
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)  # ❌ REMOVER
    full_name: str | None = None
    role: str = "user"

class UserUpdate(BaseModel):
    full_name: str | None = None
    is_active: bool | None = None  # ❌ REMOVER

class UserInDB(UserOut):  # ❌ REMOVER CLASSE INTEIRA
    hashed_password: str

# DEPOIS:
class UserCreate(BaseModel):
    """Data for creating user (NO password - that's Auth)."""
    email: EmailStr
    full_name: str | None = None
    role: str = "user"

class UserUpdate(BaseModel):
    """Update profile data only (NO security fields)."""
    full_name: str | None = None
    # is_active removed - that's Auth concern

# UserInDB deleted
```

**Impacto:** ALTO - Quebra compatibilidade  
**Testes:** Atualizar todos os testes que usam `UserCreate` com `password`

---

##### **3. Services**
📄 **`src/robbot/services/auth_services.py`**
**Ação:** REFATORAR completamente para usar `CredentialService` e `SessionService`

```python
# ANTES (método signup - linhas 28-38):
def signup(self, payload: UserCreate) -> UserOut:
    existing = self.repo.get_by_email(payload.email)
    if existing:
        raise AuthException("User already exists")
    security.validate_password_policy(payload.password)  # ❌
    hashed = security.get_password_hash(payload.password)  # ❌
    user = self.repo.create_user(payload, hashed_password=hashed)  # ❌
    return UserOut.model_validate(user)

# DEPOIS:
def signup(self, signup_request: SignupRequest) -> UserOut:
    """Register new user (creates User + Credential)."""
    from robbot.services.user_service import UserService
    from robbot.services.credential_service import CredentialService
    
    # Check existing
    existing = self.user_repo.get_by_email(signup_request.email)
    if existing:
        raise AuthException("User already exists")
    
    # Create User (domain)
    user_service = UserService(self.db)
    user = user_service.create_user(
        email=signup_request.email,
        full_name=signup_request.full_name
    )
    
    # Create Credential (security)
    credential_service = CredentialService(self.db)
    credential_service.create_credential(user.id, signup_request.password)
    
    return UserOut.model_validate(user)
```

**ADICIONAR métodos:**
- `verify_email(token: str)`
- `resend_verification_email(email: str)`
- `setup_mfa(user_id: int)` 
- `verify_mfa(user_id: int, code: str)`
- `disable_mfa(user_id: int, password: str, code: str)`

**MODIFICAR métodos:**
- `authenticate_user()`: adicionar verificação de MFA
- `refresh()`: implementar token rotation
- `reset_password()`: chamar `credential_service.reset_password()` + revogar sessões

**Impacto:** MUITO ALTO - Core do Auth  
**Testes:** Reescrever `tests/unit/test_auth_service.py`

---

📄 **`src/robbot/services/user_service.py`**
**Ação:** REMOVER lógica de `is_active`, ADICIONAR método `create_user` puro

```python
# ADICIONAR:
def create_user(self, email: str, full_name: str | None = None, role: str = "user") -> UserOut:
    """Create user (NO password - Auth handles that)."""
    user_model = UserModel(
        email=email,
        full_name=full_name,
        role=role,
        is_active=True  # Default ativo, Auth bloqueará se necessário
    )
    self.repo.db.add(user_model)
    self.repo.db.commit()
    self.repo.db.refresh(user_model)
    return UserOut.model_validate(user_model)

# MODIFICAR update_user:
def update_user(self, user_id: int, payload: UserUpdate) -> UserOut:
    user = self.repo.get_by_id(user_id)
    if not user:
        raise NotFoundException(f"User {user_id} not found")
    
    # Apenas full_name agora (is_active removido)
    if payload.full_name is not None:
        user.full_name = payload.full_name
    
    updated = self.repo.update_user(user)
    return UserOut.model_validate(updated)

# deactivate_user DELETAR (será POST /auth/users/{id}/block)
```

**Impacto:** MÉDIO  
**Testes:** Atualizar `tests/unit/test_user_service.py`

---

##### **4. Repositories**
📄 **`src/robbot/adapters/repositories/user_repository.py`**
**Ação:** REMOVER parâmetro `hashed_password` de `create_user`

```python
# ANTES:
def create_user(self, user_in: UserCreate, hashed_password: str) -> UserModel:
    user = UserModel(
        email=user_in.email,
        hashed_password=hashed_password,  # ❌ REMOVER
        full_name=user_in.full_name,
        role=user_in.role,
    )
    ...

# DEPOIS:
def create_user(self, email: str, full_name: str | None, role: str) -> UserModel:
    """Create user (NO password)."""
    user = UserModel(
        email=email,
        full_name=full_name,
        role=role,
        is_active=True
    )
    self.db.add(user)
    self.db.commit()
    self.db.refresh(user)
    return user
```

**Impacto:** MÉDIO  
**Testes:** Atualizar `tests/unit/test_user_repository.py`

---

📄 **`src/robbot/adapters/repositories/token_repository.py`**
**Ação:** ADICIONAR método `revoke_all_for_user`

```python
# ADICIONAR:
def revoke_all_for_user(self, user_id: int) -> int:
    """Revoke all tokens for user (password reset/change)."""
    # Como tokens são JWT stateless, precisamos marcar user_id como "force logout"
    # OU armazenar metadata em RevokedTokenModel
    # Implementação simplificada: revogar por timestamp
    token_marker = f"user:{user_id}:invalidated_at:{datetime.utcnow().isoformat()}"
    self.revoke(token_marker)
    return 1
```

**Impacto:** MÉDIO  
**Testes:** Adicionar teste em `tests/unit/test_token_repository.py`

---

##### **5. Controllers**
📄 **`src/robbot/adapters/controllers/auth_controller.py`**
**Ação:** REFATORAR todos os endpoints para usar novos schemas

```python
# MODIFICAR imports:
from robbot.schemas.auth import (
    SignupRequest, LoginRequest, AuthSessionResponse,
    ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest,
    VerifyEmailRequest, ResendEmailRequest,
    MfaSetupResponse, MfaVerifyRequest, MfaDisableRequest,
    SessionListResponse, BackupCodesResponse
)
from robbot.schemas.user import UserOut  # Apenas para signup response

# MODIFICAR endpoints:
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: SignupRequest, db: Session = Depends(get_db)):  # Era signup
    ...

@router.get("/me", response_model=AuthSessionResponse)  # Era UserOut
def get_current_session(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    # Retornar dados de SESSÃO, não perfil
    ...

@router.post("/password/change", status_code=status.HTTP_200_OK)
def change_password(
    payload: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Novo endpoint
    ...

# ADICIONAR endpoints:
@router.post("/email/verify")
@router.post("/email/resend")
@router.get("/sessions", response_model=SessionListResponse)
@router.post("/sessions/{session_id}/revoke")
@router.post("/sessions/revoke-all")
@router.post("/mfa/setup", response_model=MfaSetupResponse)
@router.post("/mfa/verify")
@router.post("/mfa/disable")
@router.get("/mfa/backup-codes", response_model=BackupCodesResponse)
@router.post("/users/{user_id}/block")  # Admin only
@router.post("/users/{user_id}/unblock")  # Admin only

# ADICIONAR rate limiting:
from robbot.core.rate_limiting import rate_limit

@router.post("/token", response_model=Token)
@rate_limit(max_attempts=5, window_seconds=900, key_prefix="login")
async def login(...):
    ...
```

**Impacto:** MUITO ALTO - API pública muda  
**Testes:** Criar `tests/integration/test_auth_endpoints.py` completo

---

📄 **`src/robbot/adapters/controllers/user_controller.py`**
**Ação:** ADICIONAR `GET /users/me` (perfil), REMOVER endpoint de deactivate

```python
# ADICIONAR:
@router.get("/users/me", response_model=UserOut)
def get_my_profile(current_user=Depends(get_current_user)):
    """Get my user profile (NOT auth session)."""
    return current_user

@router.patch("/users/me", response_model=UserOut)
def update_my_profile(
    payload: UserUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update my profile."""
    service = UserService(db)
    return service.update_user(current_user.id, payload)

# REMOVER ou MODIFICAR:
@router.delete("/users/{user_id}", ...)  # Deletar - bloqueio é Auth
```

**Impacto:** MÉDIO  
**Testes:** Criar `tests/integration/test_user_endpoints.py`

---

##### **6. Core**
📄 **`src/robbot/core/security.py`**
**Ação:** ADICIONAR suporte a MFA verification no `get_current_user`

```python
# MODIFICAR get_current_user para verificar MFA se necessário
# ADICIONAR helper para TOTP verification
```

**Impacto:** BAIXO  
**Testes:** Atualizar `tests/unit/test_security.py`

---

##### **7. Dependencies**
📄 **`src/robbot/api/v1/dependencies.py`**
**Ação:** MODIFICAR `get_current_user` para verificar sessões e MFA

```python
# ANTES:
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # Apenas valida JWT
    ...

# DEPOIS:
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    request: Request = None  # Para device fingerprint
):
    """Validate JWT + check session + MFA."""
    payload = security.decode_token(token)
    user_id = int(payload.get("sub"))
    
    # Verificar se user está bloqueado
    user = user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User inactive")
    
    # Verificar email verificado
    credential = credential_repo.get_by_user_id(user_id)
    if not credential.email_verified:
        raise HTTPException(status_code=403, detail="Email not verified")
    
    # TODO: Verificar sessão válida (fase 3)
    
    return user
```

**Impacto:** ALTO - Afeta TODOS os endpoints autenticados  
**Testes:** Atualizar `tests/unit/test_dependencies.py`

---

### 📁 MIGRATIONS (5 novas)

#### 🗄️ Alembic Migrations

##### **Migration 1: Create credentials table**
📄 **`alembic/versions/XXXXXXXX_create_credentials_table.py`**

```python
"""Create credentials table and migrate data from users.

Revision ID: XXXXXXXX
Revises: 007ad6343e57
Create Date: 2025-12-22 10:00:00
"""

def upgrade():
    # 1. Criar tabela credentials
    op.create_table(
        'credentials',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('email_verification_token', sa.String(255), nullable=True),
        sa.Column('email_verification_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('mfa_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('mfa_secret', sa.String(64), nullable=True),
        sa.Column('backup_codes', ARRAY(sa.String()), nullable=True),
        sa.Column('password_reset_token', sa.String(255), nullable=True),
        sa.Column('password_reset_sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('user_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # 2. MIGRAR dados: copiar hashed_password de users para credentials
    op.execute("""
        INSERT INTO credentials (user_id, hashed_password, email_verified, created_at)
        SELECT id, hashed_password, true, created_at
        FROM users
    """)
    
    # 3. Remover coluna hashed_password de users
    op.drop_column('users', 'hashed_password')

def downgrade():
    # 1. Readicionar coluna
    op.add_column('users', sa.Column('hashed_password', sa.String(255)))
    
    # 2. Migrar de volta
    op.execute("""
        UPDATE users
        SET hashed_password = c.hashed_password
        FROM credentials c
        WHERE users.id = c.user_id
    """)
    
    # 3. Tornar NOT NULL
    op.alter_column('users', 'hashed_password', nullable=False)
    
    # 4. Dropar tabela credentials
    op.drop_table('credentials')
```

**Impacto:** CRÍTICO - Modifica estrutura core  
**Rollback:** Suportado (downgrade)  
**Testes:** Testar em DB staging antes de prod

---

##### **Migration 2: Create auth_sessions table**
📄 **`alembic/versions/YYYYYYYY_create_auth_sessions_table.py`**

```python
"""Create auth_sessions table for session management.

Revision ID: YYYYYYYY
Revises: XXXXXXXX
Create Date: 2025-12-22 11:00:00
"""

def upgrade():
    op.create_table(
        'auth_sessions',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('refresh_token_hash', sa.String(64), nullable=False),
        sa.Column('device_info', sa.String(255), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('last_used_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Índices para performance
    op.create_index('ix_auth_sessions_user_id', 'auth_sessions', ['user_id'])
    op.create_index('ix_auth_sessions_refresh_token_hash', 'auth_sessions', ['refresh_token_hash'], unique=True)
    op.create_index('ix_auth_sessions_expires_at', 'auth_sessions', ['expires_at'])

def downgrade():
    op.drop_table('auth_sessions')
```

**Impacto:** MÉDIO - Tabela nova  
**Rollback:** Simples  
**Testes:** Unit tests de SessionRepository

---

##### **Migration 3-5:** (Simplificadas, incluídas nas docs completas)

---

### 🧪 TESTES (20 arquivos afetados)

#### Testes NOVOS a criar (12 arquivos):

1. `tests/unit/test_auth_schemas.py` - Validação de SignupRequest, etc.
2. `tests/unit/test_credential_model.py` - Model CredentialModel
3. `tests/unit/test_session_model.py` - Model SessionModel
4. `tests/unit/test_credential_repository.py` - CRUD credentials
5. `tests/unit/test_session_repository.py` - CRUD sessions
6. `tests/unit/test_credential_service.py` - Lógica de senha/MFA
7. `tests/unit/test_session_service.py` - Lógica de sessões
8. `tests/unit/test_rate_limiting.py` - Rate limiter decorator
9. `tests/integration/test_auth_endpoints.py` - Todos endpoints /auth/*
10. `tests/integration/test_user_endpoints.py` - Endpoints /users/*
11. `tests/integration/test_mfa_flow.py` - Fluxo completo MFA
12. `tests/integration/test_email_verification_flow.py` - Verificação email

#### Testes MODIFICADOS (8 arquivos):

1. `tests/unit/test_auth_service.py` - Adaptar para novos métodos
2. `tests/unit/test_user_service.py` - Remover testes de password
3. `tests/unit/test_user_repository.py` - create_user sem password
4. `tests/unit/test_user_model.py` - Sem hashed_password
5. `tests/unit/test_token_repository.py` - revoke_all_for_user
6. `tests/unit/test_security.py` - MFA helpers
7. `tests/unit/test_dependencies.py` - get_current_user changes
8. `tests/conftest.py` - Fixtures de credential/session

---

### 📊 ESTATÍSTICAS FINAIS DE IMPACTO

| Categoria | Novos | Modificados | Deletados | Total |
|-----------|-------|-------------|-----------|-------|
| **Schemas** | 2 | 1 | 0 | 3 |
| **Models** | 2 | 2 | 0 | 4 |
| **Repositories** | 2 | 2 | 0 | 4 |
| **Services** | 2 | 2 | 0 | 4 |
| **Controllers** | 0 | 2 | 0 | 2 |
| **Core/Utils** | 1 | 2 | 0 | 3 |
| **Dependencies** | 0 | 1 | 0 | 1 |
| **Migrations** | 5 | 0 | 0 | 5 |
| **Tests (Unit)** | 8 | 8 | 0 | 16 |
| **Tests (Integration)** | 4 | 0 | 0 | 4 |
| **Total Arquivos** | **26** | **20** | **0** | **46** |

---

### 🎯 ORDEM DE EXECUÇÃO RECOMENDADA (Sem Quebrar Nada)

#### **Semana 1-2: Fase 0 (Preparação)**

1. Criar `schemas/auth.py` ✅
2. Criar `CredentialModel` ✅
3. Criar `SessionModel` ✅
4. Criar `CredentialRepository` ✅
5. Criar `SessionRepository` ✅
6. Criar `CredentialService` ✅
7. Criar `SessionService` ✅
8. Criar `core/rate_limiting.py` ✅
9. Criar testes unitários de novos componentes ✅
10. Instalar dependências: `uv add pyotp qrcode pillow` ✅

**Status após Semana 2:** Código novo coexiste, nada quebra ainda

---

#### **Semana 3-4: Fase 1.1 (Migration Credentials)**

11. Criar migration para `credentials` table ✅
12. Rodar migration em staging ✅
13. Validar migração de dados ✅
14. Modificar `UserModel` (remover hashed_password) ✅
15. Modificar `UserRepository.create_user` ✅
16. Atualizar testes de UserModel/Repository ✅

**Status após Semana 4:** Credenciais separadas, UserModel limpo

---

#### **Semana 5-6: Fase 1.2 (Refatorar AuthService)**

17. Modificar `schemas/user.py` (remover password) ✅
18. Modificar `AuthService.signup` para usar CredentialService ✅
19. Modificar `AuthService.authenticate` para usar CredentialService ✅
20. Implementar refresh token rotation ✅
21. Modificar `reset_password` para invalidar sessões ✅
22. Atualizar `test_auth_service.py` ✅
23. Criar migration para `auth_sessions` ✅
24. Integrar SessionService em AuthService ✅

**Status após Semana 6:** Auth usa Credential/Session, rotation implementada

---

#### **Semana 7-8: Fase 1.3 (Endpoints + Rate Limiting)**

25. Modificar `auth_controller.py` (novos endpoints) ✅
26. Adicionar rate limiting em login/refresh/recovery ✅
27. Criar `GET /auth/me` retornando AuthSessionResponse ✅
28. Modificar `user_controller.py` (adicionar /users/me) ✅
29. Criar endpoints de sessões (/auth/sessions/*) ✅
30. Criar endpoints de MFA (/auth/mfa/*) ✅
31. Criar endpoints admin (/auth/users/{id}/block) ✅
32. Criar testes de integração completos ✅
33. Atualizar documentação OpenAPI ✅

**Status após Semana 8:** API pública refatorada, P0 completo

---

### 🚨 RISCOS E MITIGAÇÕES

| Risco | Severidade | Mitigação |
|-------|------------|-----------|
| Migration falha em produção | ALTA | Testar em staging, backup antes, rollback script |
| API breaking changes quebram clients | ALTA | Versionar API (v2), deprecation warnings |
| Performance degradada (joins) | MÉDIA | Índices em FKs, eager loading, cache |
| Dados perdidos na migration | CRÍTICA | Backup completo, dry-run, validação pós-migration |
| Redis down quebra rate limit | MÉDIA | Degradação graceful (permitir se Redis falhar) |
| MFA lockout de usuários | MÉDIA | Backup codes obrigatórios, admin unlock |

---

### ✅ CHECKLIST DE VALIDAÇÃO (Antes de Produção)

#### **Funcional:**
- [ ] Signup cria User + Credential separadamente
- [ ] Login com MFA funciona
- [ ] Refresh rotation: token usado é revogado
- [ ] Reset senha invalida TODAS as sessões
- [ ] Rate limiting bloqueia após limite
- [ ] Email verification obrigatória
- [ ] Sessões listadas e revogáveis
- [ ] Bloqueio de user invalida sessões

#### **Testes:**
- [ ] 100% cobertura de CredentialService
- [ ] 100% cobertura de SessionService
- [ ] Integration tests de todos endpoints Auth
- [ ] Load test de rate limiting (Redis)
- [ ] Migration testada em staging

#### **Segurança:**
- [ ] Passwords nunca em logs
- [ ] MFA codes expiram após 30s
- [ ] Backup codes hasheados
- [ ] Sessions invalidadas em logout
- [ ] Tokens rotacionados corretamente

#### **Performance:**
- [ ] Queries < 50ms (p95)
- [ ] Índices criados em FKs
- [ ] Eager loading em relationships
- [ ] Redis connection pool configurado

---

### 📚 RECURSOS ADICIONAIS

**Documentação a criar:**
- `docs/API_MIGRATION_GUIDE.md` - Como migrar de v1 para v2
- `docs/MFA_SETUP_GUIDE.md` - Guia para usuários
- `docs/ADMIN_GUIDE.md` - Bloqueio/desbloqueio de users
- `docs/SECURITY_AUDIT.md` - Checklist de segurança

**Scripts úteis:**
- `scripts/migrate_credentials.py` - Helper para migration
- `scripts/cleanup_expired_sessions.py` - Cron job
- `scripts/generate_backup_codes.py` - Admin tool

---

**FIM DO MAPA DE IMPACTO**

---

## 🎯 GUIA PRÁTICO: COMO COMEÇAR A REFATORAÇÃO

### 🚀 Passo 1: Clonar o Projeto e Criar Branch

```bash
cd d:/_projects/wpp_bot
git checkout -b refactor/auth-user-separation
git pull origin main
```

### 📦 Passo 2: Instalar Dependências Novas

```bash
# Ativar ambiente virtual
.venv\Scripts\activate

# Instalar libs de MFA
uv add pyotp qrcode pillow
uv sync
```

### 📝 Passo 3: Criar Arquivos Novos (Fase 0 - Dia 1)

**Criar estrutura de pastas:**
```bash
# Criar arquivos base
touch src/robbot/schemas/auth.py
touch src/robbot/infra/db/models/credential_model.py
touch src/robbot/infra/db/models/session_model.py
touch src/robbot/adapters/repositories/credential_repository.py
touch src/robbot/adapters/repositories/session_repository.py
touch src/robbot/services/credential_service.py
touch src/robbot/services/session_service.py
touch src/robbot/core/rate_limiting.py
```

**Copiar código das seções acima para cada arquivo**  
(Use a documentação de "FASE 0: PREPARAÇÃO" como referência)

### 🧪 Passo 4: Criar Testes para Arquivos Novos (Fase 0 - Dia 2-3)

```bash
# Criar estrutura de testes
touch tests/unit/test_auth_schemas.py
touch tests/unit/test_credential_model.py
touch tests/unit/test_session_model.py
touch tests/unit/test_credential_repository.py
touch tests/unit/test_session_repository.py
touch tests/unit/test_credential_service.py
touch tests/unit/test_session_service.py
touch tests/unit/test_rate_limiting.py
```

**Rodar testes:**
```bash
pytest tests/unit/test_credential_service.py -v
pytest tests/unit/ -v --cov=src/robbot/services/credential_service
```

### 🗄️ Passo 5: Criar Migration para Credentials (Fase 0 - Dia 4-5)

```bash
# Gerar migration
alembic revision -m "create_credentials_table"

# Editar arquivo gerado em alembic/versions/XXXX_create_credentials_table.py
# Copiar código da seção "Migration 1: Create credentials table"

# Testar em staging
alembic upgrade head

# Validar dados migrados
python -c "
from robbot.infra.db.session import SessionLocal
from robbot.infra.db.models.credential_model import CredentialModel

db = SessionLocal()
count = db.query(CredentialModel).count()
print(f'✅ {count} credentials migradas com sucesso')
"
```

### 🔄 Passo 6: Refatorar AuthService (Fase 1 - Semana 3-4)

**Ordem de modificação:**
1. ✅ Modificar `schemas/user.py` (remover password)
2. ✅ Modificar `UserRepository.create_user` (sem hashed_password)
3. ✅ Modificar `AuthService.signup` (usar CredentialService)
4. ✅ Rodar testes: `pytest tests/unit/test_auth_service.py -v`
5. ✅ Se testes passam, commit: `git commit -m "refactor: AuthService usa CredentialService"`

### 📡 Passo 7: Atualizar Controllers (Fase 1 - Semana 5-6)

```bash
# Modificar auth_controller.py
# Adicionar novos endpoints
# Adicionar rate limiting

# Testar endpoints
pytest tests/integration/test_auth_endpoints.py -v

# Testar manualmente com Postman
# POST http://localhost:8000/api/v1/auth/register
# POST http://localhost:8000/api/v1/auth/login
# POST http://localhost:8000/api/v1/auth/mfa/setup
```

### ✅ Passo 8: Validar Tudo Funciona (Fase 1 - Semana 7-8)

**Checklist:**
```bash
# 1. Todos os testes passam
pytest tests/ -v --cov=src/robbot --cov-report=html

# 2. Migrations aplicadas
alembic current
# Deve mostrar: YYYYYYYY (head)

# 3. Servidor roda sem erros
uvicorn robbot.main:app --reload

# 4. OpenAPI atualizada
# Abrir http://localhost:8000/docs
# Verificar novos endpoints /auth/*

# 5. Integração funciona
# Fazer signup -> login -> mfa setup -> mfa verify
```

### 🚢 Passo 9: Deploy Staging

```bash
# Merge para main
git checkout main
git merge refactor/auth-user-separation

# Push
git push origin main

# Deploy staging
# (Docker compose up, etc.)

# Validar em staging
curl -X POST https://staging.api.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test@1234"}'
```

### 📊 Passo 10: Monitorar Métricas

**Após deploy, monitorar:**
- Taxa de sucesso de login (deve permanecer 100%)
- Tempo de resposta de /auth/login (deve ser < 200ms)
- Taxa de erro 401 (não deve aumentar)
- Logs de rate limiting (verificar bloqueios falsos positivos)

---

## 📋 CRONOGRAMA DETALHADO (8 Semanas para MVP Seguro)

### Semana 1 (22-26 Dez 2025)
- [ ] **Dia 1:** Criar schemas/auth.py + tests
- [ ] **Dia 2:** Criar CredentialModel + SessionModel
- [ ] **Dia 3:** Criar CredentialRepository + SessionRepository
- [ ] **Dia 4:** Criar CredentialService + SessionService
- [ ] **Dia 5:** Criar rate_limiting.py + tests
- [ ] **Entrega:** Todos os arquivos novos + testes unitários passando

### Semana 2 (29 Dez - 2 Jan 2026)
- [ ] **Dia 1:** Migration credentials table (staging)
- [ ] **Dia 2:** Validar migração + rollback test
- [ ] **Dia 3:** Migration auth_sessions table
- [ ] **Dia 4:** Atualizar UserModel (__init__.py, relationships)
- [ ] **Dia 5:** Rodar testes completos + code review
- [ ] **Entrega:** DB staging com novas tabelas populadas

### Semana 3 (5-9 Jan 2026)
- [ ] **Dia 1:** Modificar schemas/user.py (remover password)
- [ ] **Dia 2:** Modificar UserRepository.create_user
- [ ] **Dia 3:** Modificar AuthService.signup
- [ ] **Dia 4:** Modificar AuthService.authenticate
- [ ] **Dia 5:** Atualizar test_auth_service.py + tests passando
- [ ] **Entrega:** AuthService refatorado, testes 100% passando

### Semana 4 (12-16 Jan 2026)
- [ ] **Dia 1:** Implementar refresh token rotation
- [ ] **Dia 2:** Modificar reset_password (invalidar sessões)
- [ ] **Dia 3:** Integrar SessionService em AuthService
- [ ] **Dia 4:** Criar testes de rotation
- [ ] **Dia 5:** Code review + ajustes
- [ ] **Entrega:** Rotation + invalidação de sessões funcionando

### Semana 5 (19-23 Jan 2026)
- [ ] **Dia 1:** Modificar auth_controller (novos schemas)
- [ ] **Dia 2:** Criar endpoints /auth/password/change
- [ ] **Dia 3:** Criar endpoints /auth/email/verify|resend
- [ ] **Dia 4:** Adicionar rate limiting em login/refresh
- [ ] **Dia 5:** Criar GET /auth/me (AuthSessionResponse)
- [ ] **Entrega:** Endpoints Auth refatorados

### Semana 6 (26-30 Jan 2026)
- [ ] **Dia 1:** Criar endpoints /auth/sessions/*
- [ ] **Dia 2:** Criar endpoints /auth/mfa/setup|verify|disable
- [ ] **Dia 3:** Criar endpoints /auth/users/{id}/block|unblock
- [ ] **Dia 4:** Modificar user_controller (GET /users/me)
- [ ] **Dia 5:** Atualizar OpenAPI docs
- [ ] **Entrega:** Todos endpoints novos implementados

### Semana 7 (2-6 Fev 2026)
- [ ] **Dia 1:** Criar tests/integration/test_auth_endpoints.py
- [ ] **Dia 2:** Criar tests/integration/test_mfa_flow.py
- [ ] **Dia 3:** Criar tests/integration/test_email_verification.py
- [ ] **Dia 4:** Rodar suite completa de testes
- [ ] **Dia 5:** Cobertura > 90% + ajustes
- [ ] **Entrega:** Testes de integração completos

### Semana 8 (9-13 Fev 2026)
- [ ] **Dia 1:** Deploy staging + smoke tests
- [ ] **Dia 2:** Load testing (rate limiting, sessions)
- [ ] **Dia 3:** Security audit (OWASP checklist)
- [ ] **Dia 4:** Documentação final (migration guide)
- [ ] **Dia 5:** Deploy produção + monitoramento
- [ ] **Entrega:** 🚀 MVP SEGURO EM PRODUÇÃO

---

## 💡 DICAS PRÁTICAS

### ✅ DO's (Faça)

1. **Commitar frequentemente:** A cada arquivo novo ou modificação, commit
   ```bash
   git add src/robbot/schemas/auth.py
   git commit -m "feat: add auth schemas (SignupRequest, LoginRequest)"
   ```

2. **Testar antes de modificar:** Sempre rode testes ANTES de refatorar
   ```bash
   pytest tests/unit/test_auth_service.py -v  # Deve passar antes
   # ... modificar código ...
   pytest tests/unit/test_auth_service.py -v  # Deve passar depois
   ```

3. **Usar branches por feature:**
   ```bash
   git checkout -b feat/credential-service
   # ... implementar ...
   git push origin feat/credential-service
   # Criar PR para code review
   ```

4. **Validar migrations em staging SEMPRE:**
   ```bash
   # Staging primeiro
   alembic upgrade head
   python scripts/validate_migration.py
   
   # Só depois em produção
   alembic upgrade head
   ```

5. **Documentar mudanças breaking:**
   ```markdown
   ## BREAKING CHANGES v2.0.0
   
   - POST /auth/signup agora é POST /auth/register
   - GET /auth/me retorna AuthSessionResponse (não UserOut)
   - UserCreate não aceita mais campo password
   ```

### ❌ DON'Ts (Não Faça)

1. **Não modifique múltiplos arquivos de uma vez**
   - ❌ Modificar AuthService + UserService + Controllers tudo junto
   - ✅ Modificar um por vez, testar, commit, próximo

2. **Não pule testes:**
   - ❌ "Vou testar depois"
   - ✅ TDD: Escreva teste primeiro, depois implementação

3. **Não aplique migrations em prod sem staging:**
   - ❌ `alembic upgrade head` direto em produção
   - ✅ Testar em staging, backup, dry-run, só depois prod

4. **Não remova código antigo antes do novo funcionar:**
   - ❌ Deletar `UserCreate.password` e quebrar tudo
   - ✅ Criar `SignupRequest` novo, migrar endpoints, depois deprecar antigo

5. **Não ignore warnings de deprecação:**
   ```python
   # ✅ BOM: Deprecation warnings
   import warnings
   
   @deprecated("Use SignupRequest instead")
   class UserCreate:
       password: str  # Deprecated, use /auth/register
   ```

---

## 🆘 TROUBLESHOOTING COMUM

### Problema 1: Migration falha com FK constraint

**Erro:**
```
sqlalchemy.exc.IntegrityError: foreign key constraint fails
```

**Solução:**
```python
# Migration deve seguir ordem:
# 1. Criar tabela credentials SEM FK
op.create_table('credentials', ...)

# 2. Migrar dados
op.execute("INSERT INTO credentials ...")

# 3. DEPOIS adicionar FK
op.create_foreign_key(
    'fk_credentials_user_id',
    'credentials', 'users',
    ['user_id'], ['id'],
    ondelete='CASCADE'
)
```

### Problema 2: Testes falham após refatoração

**Erro:**
```
TypeError: signup() missing required argument: 'password'
```

**Solução:**
```python
# Atualizar fixtures em conftest.py
@pytest.fixture
def signup_request():
    return SignupRequest(  # Era UserCreate
        email="test@example.com",
        password="Test@1234",
        full_name="Test User"
    )
```

### Problema 3: Rate limiting não funciona

**Erro:**
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solução:**
```bash
# Verificar Redis rodando
docker ps | grep redis

# Se não, subir:
docker-compose up -d redis

# Testar conexão:
redis-cli ping  # Deve retornar PONG
```

### Problema 4: MFA QR code não exibe

**Erro:**
```
ModuleNotFoundError: No module named 'qrcode'
```

**Solução:**
```bash
# Instalar dependências faltantes
uv add qrcode pillow
uv sync

# Verificar instalação
python -c "import qrcode; print('OK')"
```

---

## 📞 SUPORTE E RECURSOS

**Documentação de Referência:**
- [RFC 6749 - OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc6749)
- [OWASP Auth Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [SQLAlchemy Relationships](https://docs.sqlalchemy.org/en/14/orm/relationships.html)

**Ferramentas Úteis:**
- **Postman Collection:** `postman/auth_v2_endpoints.json` (criar)
- **DB Browser:** Adminer (http://localhost:8080)
- **Redis CLI:** `redis-cli -h localhost -p 6379`
- **Migration Viewer:** `alembic history --verbose`

**Contacts (Exemplo):**
- Tech Lead: [email]
- Security Team: [email]
- DevOps: [email]

---

**🎉 PRONTO PARA COMEÇAR A REFATORAÇÃO!**

Siga este guia passo a passo e você terá um sistema Auth/User seguro, escalável e seguindo as melhores práticas em 8 semanas. Boa sorte! 🚀

---

### 📦 Gerenciador de Pacotes

**IMPORTANTE:** Este projeto usa `uv` como gerenciador de pacotes Python (NÃO use pip ou poetry)

**Comandos:**
- Adicionar dependências: `uv add <package>`
- Adicionar dev dependencies: `uv add --dev <package>`
- Sincronizar ambiente: `uv sync`
- Atualizar dependências: `uv lock --upgrade`

**NÃO USE:** `pip install` ou `poetry add`

---

---

## 📧 Sistema de Email: MailDev → Postal

### 📋 Decisão Arquitetural

**Data da Decisão:** 22/12/2025  
**Status:** ✅ DEFINIDO  
**Responsável:** Arquitetura de Infraestrutura

---

### 🎯 Contexto

O sistema necessita de capacidade de envio de emails para:
- ✅ Verificação de email (email verification)
- ✅ Reset de senha (password reset)
- ✅ Notificações de segurança (login suspeito, MFA)
- ✅ Alertas administrativos

**Restrição:** Sem servidor SMTP pago (SendGrid, AWS SES, Mailgun requerem cartão)

---

### 📌 Solução Escolhida

#### **Fase 1: Desenvolvimento (ATUAL)**
**Ferramenta:** MailDev  
**Motivo:** SMTP server open-source para captura de emails (não envia para internet)

**Configuração:**
```yaml
# docker-compose.yml
services:
  maildev:
    image: maildev/maildev
    container_name: wppbot_maildev
    ports:
      - "1080:1080"  # Web UI (visualizar emails)
      - "1025:1025"  # SMTP Server
    environment:
      - MAILDEV_SMTP_PORT=1025
      - MAILDEV_WEB_PORT=1080
    restart: unless-stopped
```

**Environment Variables:**
```bash
# .env.development
SMTP_HOST=maildev
SMTP_PORT=1025
SMTP_USER=""
SMTP_PASSWORD=""
SMTP_FROM=noreply@wppbot.local
SMTP_TLS=false
SMTP_ENABLED=true
```

**Vantagens:**
- ✅ 100% gratuito e open-source
- ✅ Interface web em http://localhost:1080
- ✅ Captura todos os emails (perfeito para testar templates)
- ✅ Zero configuração adicional
- ✅ 1 container leve (< 50MB)

**Desvantagens:**
- ⚠️ Não envia emails reais (apenas captura)
- ⚠️ Apenas para desenvolvimento

**Comando:**
```bash
# Subir apenas MailDev
docker-compose up maildev -d

# Acessar UI
open http://localhost:1080
```

---

#### **Fase 2: Produção (FUTURO)**
**Ferramenta:** Postal  
**Motivo:** SMTP server open-source completo (envia emails reais)

**Configuração:**
```yaml
# docker-compose.prod.yml
services:
  postal:
    image: ghcr.io/postalserver/postal:latest
    container_name: wppbot_postal
    ports:
      - "25:25"     # SMTP
      - "587:587"   # Submission
      - "5000:5000" # Admin Web UI
    environment:
      - POSTAL_MYSQL_HOST=postal_mysql
      - POSTAL_MYSQL_DATABASE=postal
      - POSTAL_MYSQL_USERNAME=postal
      - POSTAL_MYSQL_PASSWORD=${POSTAL_DB_PASSWORD}
      - POSTAL_RABBITMQ_HOST=postal_rabbitmq
    depends_on:
      - postal_mysql
      - postal_rabbitmq
    volumes:
      - postal-data:/opt/postal
    restart: unless-stopped

  postal_mysql:
    image: mysql:8.0
    container_name: wppbot_postal_mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${POSTAL_MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: postal
      MYSQL_USER: postal
      MYSQL_PASSWORD: ${POSTAL_DB_PASSWORD}
    volumes:
      - postal-mysql-data:/var/lib/mysql
    restart: unless-stopped

  postal_rabbitmq:
    image: rabbitmq:3-management
    container_name: wppbot_postal_rabbitmq
    volumes:
      - postal-rabbitmq-data:/var/lib/rabbitmq
    restart: unless-stopped

volumes:
  postal-data:
  postal-mysql-data:
  postal-rabbitmq-data:
```

**Environment Variables:**
```bash
# .env.production
SMTP_HOST=postal
SMTP_PORT=587
SMTP_USER=wppbot@yourdomain.com
SMTP_PASSWORD=${POSTAL_API_KEY}
SMTP_FROM=noreply@yourdomain.com
SMTP_TLS=true
SMTP_ENABLED=true

POSTAL_DB_PASSWORD=<strong_password>
POSTAL_MYSQL_ROOT_PASSWORD=<strong_password>
```

**Vantagens:**
- ✅ 100% gratuito e open-source
- ✅ SMTP server completo (envia emails reais)
- ✅ Interface web de gerenciamento (tracking, webhooks, estatísticas)
- ✅ Suporta múltiplos domínios
- ✅ API REST completa
- ✅ Tracking de emails (aberturas, cliques)
- ✅ Usado em produção por empresas reais

**Desvantagens:**
- ⚠️ Requer 3 containers (Postal + MySQL + RabbitMQ)
- ⚠️ Configuração mais complexa
- ⚠️ Requer domínio próprio e configuração DNS (SPF, DKIM, DMARC)

**Migração Estimada:** 4-8 horas (configuração DNS + testes)

---

### 📝 Estratégia de Notificações

**Canal Único:** Email via SMTP

**Decisão:** O sistema utilizará **exclusivamente email** para notificações de segurança e verificação. WhatsApp será usado apenas para interação com leads/clientes do negócio, não para autenticação de usuários internos.

**Motivos:**
- ✅ Separação clara: WhatsApp = Bot comercial | Email = Sistema interno
- ✅ Email é padrão universal para autenticação
- ✅ Evita misturar contextos (cliente vs admin)
- ✅ Usuários internos (admin, atendente) sempre têm email corporativo

**Implementação:**
```python
# src/robbot/services/email_service.py
from aiosmtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_from = settings.SMTP_FROM
        self.smtp_tls = settings.SMTP_TLS
        
        # Carregar templates Jinja2
        self.template_env = Environment(
            loader=FileSystemLoader("templates/email")
        )
    
    async def send_verification_email(self, email: str, code: str) -> bool:
        """Envia código de verificação de email"""
        template = self.template_env.get_template("verification.html")
        html_content = template.render(code=code)
        
        return await self._send_email(
            to=email,
            subject="Código de Verificação - WppBot",
            html_content=html_content,
            text_content=f"Seu código de verificação: {code}\n\nVálido por 10 minutos."
        )
    
    async def send_password_reset_email(self, email: str, token: str) -> bool:
        """Envia link de reset de senha"""
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        template = self.template_env.get_template("password_reset.html")
        html_content = template.render(reset_link=reset_link)
        
        return await self._send_email(
            to=email,
            subject="Reset de Senha - WppBot",
            html_content=html_content,
            text_content=f"Link de reset: {reset_link}\n\nVálido por 1 hora."
        )
    
    async def send_security_alert(self, email: str, alert_type: str, details: dict) -> bool:
        """Envia alerta de segurança (login suspeito, MFA, etc)"""
        template = self.template_env.get_template("security_alert.html")
        html_content = template.render(alert_type=alert_type, **details)
        
        return await self._send_email(
            to=email,
            subject=f"Alerta de Segurança: {alert_type}",
            html_content=html_content,
            text_content=f"Alerta: {alert_type}\n\nDetalhes: {details}"
        )
    
    async def _send_email(self, to: str, subject: str, html_content: str, text_content: str) -> bool:
        """Método interno para envio via SMTP"""
        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.smtp_from
            message["To"] = to
            message["Subject"] = subject
            
            # Adicionar versão texto e HTML
            message.attach(MIMEText(text_content, "plain"))
            message.attach(MIMEText(html_content, "html"))
            
            # Conectar e enviar
            async with SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=self.smtp_tls
            ) as smtp:
                if self.smtp_user and self.smtp_password:
                    await smtp.login(self.smtp_user, self.smtp_password)
                
                await smtp.send_message(message)
            
            logger.info(f"Email enviado com sucesso para {to}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao enviar email para {to}: {e}")
            
            # Em desenvolvimento, mostrar código no log
            if settings.DEBUG:
                logger.warning(f"[DEBUG] Conteúdo do email:\n{text_content}")
            
            return False
```

**Dependências Necessárias:**
```bash
uv add aiosmtplib  # Cliente SMTP assíncrono
uv add jinja2      # Templates de email
```

---

### ✅ Checklist de Implementação

#### **Fase 1: MailDev (AGORA)**
- [ ] Adicionar serviço `maildev` ao `docker-compose.yml`
- [ ] Configurar variáveis SMTP no `.env.development`
- [ ] Criar `src/robbot/services/email_service.py`
- [ ] Criar templates de email (HTML + texto plano):
  - [ ] `templates/email/verification.html`
  - [ ] `templates/email/password_reset.html`
  - [ ] `templates/email/security_alert.html`
- [ ] Implementar `EmailService.send_verification_email()`
- [ ] Implementar `EmailService.send_password_reset_email()`
- [ ] Criar testes unitários (`tests/unit/services/test_email_service.py`)
- [ ] Criar testes de integração (verificar envio via MailDev)
- [ ] Documentar uso do MailDev no README.md
- [ ] Testar manualmente enviando email e visualizando em http://localhost:1080

#### **Fase 2: Postal (FUTURO - Quando for para produção)**
- [ ] Adquirir domínio próprio (ex: wppbot.com.br)
- [ ] Configurar DNS records:
  - [ ] SPF record: `v=spf1 ip4:YOUR_SERVER_IP ~all`
  - [ ] DKIM record: (gerado pelo Postal)
  - [ ] DMARC record: `v=DMARC1; p=quarantine; rua=mailto:dmarc@wppbot.com.br`
- [ ] Criar `docker-compose.prod.yml` com Postal + MySQL + RabbitMQ
- [ ] Configurar variáveis SMTP no `.env.production`
- [ ] Migrar credenciais do MailDev para Postal
- [ ] Configurar webhook do Postal (tracking de aberturas/cliques)
- [ ] Atualizar `EmailService` para usar API do Postal (opcional, SMTP também funciona)
- [ ] Testar envio real de emails
- [ ] Configurar alertas de falha de envio
- [ ] Monitorar reputação do domínio (https://mxtoolbox.com)

---

### 📊 Estimativa de Esforço

| Fase | Tarefa | Tempo | Complexidade |
|------|--------|-------|--------------|
| Fase 1 | Configurar MailDev no Docker | 30 min | Baixa |
| Fase 1 | Criar EmailService | 2h | Média |
| Fase 1 | Criar templates HTML | 1h | Baixa |
| Fase 1 | Testes unitários + integração | 2h | Média |
| Fase 1 | Documentação | 30 min | Baixa |
| **TOTAL FASE 1** | | **6h** | |
| Fase 2 | Configurar DNS (SPF/DKIM/DMARC) | 2h | Alta |
| Fase 2 | Configurar Postal no Docker | 3h | Alta |
| Fase 2 | Migração e testes | 2h | Média |
| Fase 2 | Monitoramento | 1h | Baixa |
| **TOTAL FASE 2** | | **8h** | |

---

### 🚨 Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Emails do Postal caírem em SPAM | Alta | Alto | Configurar corretamente SPF/DKIM/DMARC + warming do domínio |
| MailDev não capturar emails | Baixa | Baixo | Verificar logs do container, porta 1025 aberta |
| Postal consumir muitos recursos | Média | Médio | Monitorar uso de CPU/RAM, escalar se necessário |
| Domínio bloqueado por abuso | Baixa | Alto | Implementar rate limiting, captcha, monitorar bounces |

---

### 📚 Referências

- **MailDev:** https://github.com/maildev/maildev
- **Postal:** https://docs.postalserver.io/
- **SPF/DKIM/DMARC:** https://www.cloudflare.com/learning/email-security/dmarc-dkim-spf/
- **Email Best Practices:** https://sendgrid.com/blog/email-best-practices/
- **aiosmtplib:** https://aiosmtplib.readthedocs.io/
- **Jinja2 Templates:** https://jinja.palletsprojects.com/

---

### 🔗 Dependências

- **Depende de:** 
  - ✅ Docker Compose configurado
  - ✅ Sistema de autenticação (para enviar códigos)
  - 🔜 Templates de email (Jinja2)
  - 🔜 Dependências Python: `aiosmtplib`, `jinja2`
  
- **Necessário para:**
  - 🔜 Email Verification (Violação #7 da Auditoria)
  - 🔜 Password Reset seguro
  - 🔜 Notificações de segurança (MFA, login suspeito)
  - 🔜 Alertas administrativos

---

### 📌 Notas Importantes

**❌ NÃO usar WhatsApp para notificações de autenticação:**
- WhatsApp = Comunicação com leads/clientes (bot comercial)
- Email = Notificações de sistema/segurança (admin, atendentes)
- Separação clara de contextos evita confusão

**✅ Usuários internos sempre têm email corporativo:**
- Admins: email obrigatório no cadastro
- Atendentes: email obrigatório no cadastro
- Email é o identificador único do sistema

---

---

## 🔐 Estratégia Frontend: Armazenamento de Tokens JWT

### 📋 Decisão Arquitetural

**Data da Decisão:** 22/12/2025  
**Status:** ✅ DEFINIDO  
**Responsável:** Arquitetura de Segurança

---

### 🎯 Contexto

O sistema utiliza autenticação JWT com dois tipos de tokens:
- **Access Token:** Curta duração (15 minutos), usado em todas as requisições autenticadas
- **Refresh Token:** Longa duração (7 dias), usado apenas para renovar o access token

**Ameaças:**
- 🔴 **XSS (Cross-Site Scripting):** Código malicioso pode ler `localStorage` e roubar tokens
- 🔴 **CSRF (Cross-Site Request Forgery):** Requisições forjadas usando cookies automáticos
- 🔴 **Token Theft:** Roubo de tokens via extensões maliciosas, injeção de código

---

### 📌 Estratégia Escolhida: **HttpOnly Cookies + CSRF Protection**

#### **Armazenamento de Tokens**

| Token | Onde Armazenar | Motivo |
|-------|----------------|--------|
| **Refresh Token** | ✅ **HttpOnly Cookie** (SameSite=Strict, Secure) | Proteção máxima contra XSS, não acessível via JavaScript |
| **Access Token** | ⚠️ **Memory only** (variável JavaScript) | XSS-safe, mas perde na recarga da página |
| **User Info** | ✅ **localStorage** (apenas dados públicos: nome, role, email) | Pode ser lido por XSS, mas não expõe credenciais |

---

### 🔧 Implementação Backend (FastAPI)

#### **1. Login: Configurar Cookies HttpOnly**

```python
# src/robbot/adapters/controllers/auth_controller.py
from fastapi import Response
from datetime import timedelta

@router.post("/login")
async def login(
    credentials: LoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login com tokens em cookies HttpOnly"""
    
    # Autenticar
    result = await auth_service.authenticate(
        email=credentials.email,
        password=credentials.password
    )
    
    # Configurar Refresh Token em HttpOnly Cookie
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,           # ✅ Não acessível via JavaScript
        secure=True,             # ✅ Apenas HTTPS (produção)
        samesite="strict",       # ✅ Proteção CSRF
        max_age=7 * 24 * 60 * 60,  # 7 dias
        path="/api/v1/auth/refresh"  # ✅ Cookie enviado apenas nesse endpoint
    )
    
    # Configurar Access Token em HttpOnly Cookie
    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=15 * 60,  # 15 minutos
        path="/api/v1"    # Enviado em todas as rotas /api/v1/*
    )
    
    # Retornar dados públicos para localStorage (frontend)
    return {
        "user": {
            "id": result["user"].id,
            "email": result["user"].email,
            "full_name": result["user"].full_name,
            "role": result["user"].role,
        },
        "expires_in": 900  # 15 min em segundos
    }
```

#### **2. Refresh: Ler Cookie Automaticamente**

```python
@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Renova access token usando refresh token do cookie"""
    
    # Ler refresh token do cookie HttpOnly
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(401, "Refresh token ausente")
    
    # Renovar tokens
    result = await auth_service.refresh(refresh_token)
    
    # Atualizar access token no cookie
    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=15 * 60,
        path="/api/v1"
    )
    
    # Opcionalmente rotacionar refresh token (melhor prática)
    if result.get("new_refresh_token"):
        response.set_cookie(
            key="refresh_token",
            value=result["new_refresh_token"],
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=7 * 24 * 60 * 60,
            path="/api/v1/auth/refresh"
        )
    
    return {"message": "Token renovado", "expires_in": 900}
```

#### **3. Logout: Limpar Cookies**

```python
@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Logout e revogação de tokens"""
    
    # Ler tokens dos cookies
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    
    # Revogar tokens no banco
    if refresh_token:
        await auth_service.revoke_refresh_token(refresh_token)
    
    # Limpar cookies
    response.delete_cookie("access_token", path="/api/v1")
    response.delete_cookie("refresh_token", path="/api/v1/auth/refresh")
    
    return {"message": "Logout realizado"}
```

#### **4. Dependência: Ler Access Token do Cookie**

```python
# src/robbot/api/v1/dependencies.py
from fastapi import Request, Depends, HTTPException

async def get_current_user(
    request: Request,
    user_service: UserService = Depends(get_user_service)
) -> User:
    """Extrai usuário do access token no cookie"""
    
    # Ler access token do cookie HttpOnly
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(401, "Não autenticado")
    
    try:
        # Decodificar JWT
        payload = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        
        # Buscar usuário
        user = await user_service.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(401, "Usuário inválido")
        
        return user
        
    except JWTError:
        raise HTTPException(401, "Token inválido")
```

---

### 🎨 Implementação Frontend (React/Vue/Angular)

#### **1. Login: Salvar dados públicos no localStorage**

```javascript
// services/authService.js
async function login(email, password) {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',  // ✅ IMPORTANTE: Envia e recebe cookies
    body: JSON.stringify({ email, password })
  });
  
  if (!response.ok) {
    throw new Error('Login falhou');
  }
  
  const data = await response.json();
  
  // Salvar dados públicos no localStorage (nome, role, email)
  localStorage.setItem('user', JSON.stringify(data.user));
  
  // Tokens estão em HttpOnly cookies (não acessível aqui)
  
  return data.user;
}
```

#### **2. Refresh Automático (Interceptor)**

```javascript
// services/apiClient.js
import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  withCredentials: true  // ✅ Envia cookies automaticamente
});

// Interceptor para refresh automático
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    
    // Se 401 e não é refresh endpoint
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Tentar renovar token (refresh_token vai no cookie)
        await axios.post('/api/v1/auth/refresh', {}, {
          withCredentials: true
        });
        
        // Repetir requisição original (novo access_token no cookie)
        return api(originalRequest);
        
      } catch (refreshError) {
        // Refresh falhou, fazer logout
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

#### **3. Logout**

```javascript
async function logout() {
  await fetch('/api/v1/auth/logout', {
    method: 'POST',
    credentials: 'include'  // Envia cookies para revogação
  });
  
  // Limpar localStorage
  localStorage.removeItem('user');
  
  // Redirecionar para login
  window.location.href = '/login';
}
```

#### **4. Hook de Autenticação (React)**

```javascript
// hooks/useAuth.js
import { useState, useEffect } from 'react';

export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Carregar usuário do localStorage
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);
  
  const login = async (email, password) => {
    const userData = await authService.login(email, password);
    setUser(userData);
  };
  
  const logout = async () => {
    await authService.logout();
    setUser(null);
  };
  
  return { user, loading, login, logout };
}
```

---

### 🛡️ Proteções Implementadas

| Ameaça | Proteção | Como Funciona |
|--------|----------|---------------|
| **XSS** | HttpOnly cookies | JavaScript malicioso não pode ler tokens dos cookies |
| **CSRF** | SameSite=Strict | Cookies não enviados em requisições cross-origin |
| **Token Theft** | Secure flag | Cookies apenas em HTTPS (produção) |
| **Replay Attack** | Refresh rotation | Refresh token muda a cada uso (1 vez só) |
| **Token Exposure** | Path restriction | Refresh token só enviado em `/auth/refresh` |

---

### ⚙️ Configuração de Settings

```python
# src/robbot/core/settings.py
class Settings(BaseSettings):
    # JWT Config
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Cookie Config
    COOKIE_SECURE: bool = True  # False apenas em dev (HTTP)
    COOKIE_SAMESITE: str = "strict"  # strict | lax | none
    COOKIE_HTTPONLY: bool = True
    COOKIE_DOMAIN: str | None = None  # .yourdomain.com (subdomínios)
    
    # CORS Config (permitir frontend)
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]  # React dev
    CORS_CREDENTIALS: bool = True  # ✅ Permitir cookies cross-origin
    
    class Config:
        env_file = ".env"
```

```python
# src/robbot/main.py
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configurar CORS para cookies
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,  # ✅ IMPORTANTE para cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 📊 Comparação de Estratégias

| Abordagem | XSS | CSRF | Complexidade | Usabilidade |
|-----------|-----|------|--------------|-------------|
| **localStorage** | ❌ Vulnerável | ✅ Seguro | Baixa | ✅ Persiste recarga |
| **sessionStorage** | ❌ Vulnerável | ✅ Seguro | Baixa | ⚠️ Perde na aba fechada |
| **Memory only** | ✅ Seguro | ✅ Seguro | Média | ❌ Perde na recarga |
| **HttpOnly Cookie** | ✅ Seguro | ⚠️ Requer SameSite | Média | ✅ Persiste recarga |
| **✅ Escolhida: HttpOnly + Refresh** | ✅ Seguro | ✅ Seguro | Alta | ✅ Persiste recarga |

---

### ✅ Checklist de Implementação

#### **Backend (FastAPI)**
- [ ] Atualizar `POST /auth/login` para definir cookies HttpOnly
- [ ] Atualizar `POST /auth/refresh` para ler e renovar via cookies
- [ ] Atualizar `POST /auth/logout` para limpar cookies
- [ ] Modificar `get_current_user()` para ler access token do cookie
- [ ] Configurar CORS com `allow_credentials=True`
- [ ] Adicionar settings de cookies (secure, samesite, domain)
- [ ] Implementar refresh token rotation (opcional, P1)
- [ ] Testes de integração (login, refresh, logout com cookies)

#### **Frontend (React/Vue)**
- [ ] Configurar `withCredentials: true` em todas as requisições
- [ ] Implementar interceptor de refresh automático (axios/fetch)
- [ ] Usar localStorage apenas para dados públicos (nome, role)
- [ ] Remover localStorage de tokens (se existir)
- [ ] Testar fluxo completo: login → refresh → logout
- [ ] Testar perda de conexão (401 → refresh → retry)
- [ ] Documentar uso de cookies no README do frontend

---

### 🚨 Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| CORS mal configurado bloqueia cookies | Alta | Alto | Testar com `allow_credentials=True` e origins corretos |
| Cookie não enviado em dev (HTTP) | Média | Baixo | `COOKIE_SECURE=False` apenas em `.env.development` |
| Subdomain mismatch (frontend ≠ backend) | Média | Médio | Usar proxy reverso ou configurar `COOKIE_DOMAIN` |
| Refresh loop infinito (401 → refresh → 401) | Baixa | Alto | Flag `_retry` no interceptor para evitar loop |

---

### 📚 Referências

- **OWASP JWT Security:** https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html
- **HttpOnly Cookies:** https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies#restrict_access_to_cookies
- **SameSite Attribute:** https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite
- **FastAPI Cookies:** https://fastapi.tiangolo.com/advanced/response-cookies/
- **CORS Credentials:** https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#requests_with_credentials

---

### 🔗 Dependências

- **Depende de:**
  - ✅ Sistema de autenticação JWT implementado
  - ✅ FastAPI com CORS configurado
  - 🔜 Frontend com axios/fetch
  
- **Necessário para:**
  - 🔜 Todas as funcionalidades autenticadas
  - 🔜 Refresh token rotation (Violação #6 da Auditoria)
  - 🔜 Session management (Violação #8 da Auditoria)

---

### 📌 Decisões Arquiteturais Registradas

**ARQ-002: Armazenamento de JWT em HttpOnly Cookies**

**Contexto:** Necessidade de armazenar tokens JWT de forma segura no frontend

**Decisão:** Utilizar HttpOnly Cookies com SameSite=Strict para ambos os tokens (access e refresh)

**Consequências:**
- ✅ Proteção contra XSS (JavaScript não acessa cookies)
- ✅ Proteção contra CSRF (SameSite=Strict)
- ✅ Tokens persistem entre recargas de página
- ⚠️ Requer CORS configurado com `allow_credentials=True`
- ⚠️ Aumenta complexidade do frontend (interceptors)
- ⚠️ Requer HTTPS em produção (Secure flag)

**Alternativas Consideradas:**
1. localStorage: Rejeitado por vulnerabilidade a XSS
2. sessionStorage: Rejeitado por perda de dados ao fechar aba
3. Memory only: Rejeitado por perda de dados ao recarregar página

**Status:** ✅ APROVADO  
**Data:** 22/12/2025

---

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

- [ ] Adicionar serviço `redis` no `docker-compose.yml`
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

- [ ] Criar `Dockerfile.worker` (baseado no Dockerfile da API)
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
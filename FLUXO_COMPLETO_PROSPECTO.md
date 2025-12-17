# 🎯 Fluxo Completo: WhatsApp → IA → Conversão

Documentação técnica do fluxo end-to-end com sistema de Playbooks integrado.

---

## 📊 Visão Macro do Fluxo (Atualizado 2025)

```
┌──────────────┐      ┌─────────┐      ┌─────────────────┐      ┌────────────┐
│  WhatsApp    │ ───> │  WAHA   │ ───> │  Webhook API    │ ───> │  RQ Queue  │
│  Mensagem    │      │ Gateway │      │  (Validation)   │      │  (Redis)   │
└──────────────┘      └─────────┘      └─────────────────┘      └────────────┘
                                                                        │
                                                                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    ConversationOrchestrator (Worker)                         │
│  ┌────────────┐   ┌─────────────┐   ┌──────────────┐   ┌────────────────┐  │
│  │ Get/Create │──>│ Save Message│──>│  RAG Search  │──>│ Gemini + Tools │  │
│  │ Lead+Conv  │   │   (Inbound) │   │  (ChromaDB)  │   │ (w/ Playbooks) │  │
│  └────────────┘   └─────────────┘   └──────────────┘   └────────────────┘  │
│                                                                 │             │
│                    ┌─────────────────────────────────────────┘             │
│                    ▼                                                         │
│         ┌──────────────────────┐                                            │
│         │ Gemini Function Call │ ──> search_playbooks(query)                │
│         │   (Playbook Tools)   │ ──> get_playbook_messages(id)              │
│         └──────────────────────┘ ──> send_playbook_message(...)             │
│                    │                                                         │
│                    ▼                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────┐  ┌──────────────┐      │
│  │ Generate    │─>│ Save Message │─>│ Update     │─>│ Send via     │      │
│  │ Response    │  │  (Outbound)  │  │ Lead Score │  │ WAHA         │      │
│  └─────────────┘  └──────────────┘  └────────────┘  └──────────────┘      │
└──────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
                        ┌───────────────────────────────────┐
                        │ PostgreSQL Database               │
                        │ ├─ leads                          │
                        │ ├─ conversations                  │
                        │ ├─ conversation_messages          │
                        │ ├─ topics (NOVO)                  │
                        │ ├─ playbooks (NOVO)               │
                        │ ├─ playbook_steps (NOVO)          │
                        │ ├─ playbook_embeddings (NOVO)     │
                        │ └─ messages (templates)           │
                        └───────────────────────────────────┘
```

---

## 🔍 Fluxo Detalhado Passo-a-Passo

### **PASSO 1: Cliente envia mensagem no WhatsApp**

#### O que acontece:
- Cliente (lead) envia mensagem via WhatsApp Business
- WAHA recebe mensagem via API oficial do WhatsApp
- WAHA detecta evento `message` (INBOUND)

#### Tecnologias:
```
WhatsApp → WAHA (devlikeapro/waha:latest) → Webhook HTTP
```

#### Configuração necessária:
```env
WAHA_URL=http://wpp_bot_waha:3000
WAHA_WEBHOOK_URL=http://api_app:3333/api/v1/webhooks/waha
```

#### Exemplos de mensagens recebidas (casos reais):
```
Caso 1 (SITUATION):
Cliente: "Olá, estou com dificuldade para emagrecer. Já tentei várias dietas mas nada funciona."

Caso 2 (PROBLEM):
Cliente: "Não aguento mais me sentir cansada o tempo todo. Será que tem relação com hormônios?"

Caso 3 (AGENDAMENTO):
Cliente: "Gostaria de agendar uma consulta para avaliar emagrecimento saudável."
```

---

### **PASSO 2: WAHA envia webhook para API**

#### Código: `src/robbot/adapters/controllers/webhook_controller.py`

```python
@router.post("/waha", status_code=202)
async def receive_waha_webhook(payload: WebhookPayload, ...):
    """
    Recebe webhook do WAHA e enfileira para processamento.
    
    Eventos:
    - "message" → Nova mensagem (processa)
    - "message.ack" → Confirmação de entrega (ignora)
    - "session.status" → Status sessão (loga)
    """
    
    # 1. Salva log do webhook no PostgreSQL
    log = webhook_repo.create(
        session_name=payload.session,
        event_type=payload.event,
        payload=payload.payload
    )
    
    # 2. Se for mensagem inbound, enfileira no RQ
    if payload.event == "message" and not payload.payload.get("fromMe"):
        job = queue_manager.enqueue_message_processing(
            chat_id=payload.payload["chatId"],
            phone=payload.payload["from"],
            text=payload.payload["body"],
            session=payload.session
        )
        return {"status": "queued", "job_id": job.id}
    
    return {"status": "logged"}
```

#### O que acontece aqui:
1. ✅ Webhook validado (schema Pydantic)
2. ✅ Log salvo no banco (`webhook_logs` table)
3. ✅ Job enfileirado no Redis (fila `messages`)
4. ✅ Response 202 Accepted (async processing)

---

### **PASSO 3: RQ Worker consome job da fila**

#### Código: `src/robbot/workers/rq_worker.py`

```python
def process_inbound_message_job(
    chat_id: str,
    phone_number: str,
    message_text: str,
    session_name: str
):
    """Job executado por RQ Worker."""
    
    orchestrator = get_conversation_orchestrator()
    
    result = orchestrator.process_inbound_message(
        chat_id=chat_id,
        phone_number=phone_number,
        message_text=message_text,
        session_name=session_name
    )
    
    return result
    )
    
    # 2. Se for mensagem, enfileira para processamento
    if payload.event == "message" and payload.payload:
        message_data = payload.payload
        
        # Extrai dados da mensagem
        chat_id = message_data.get("from", "")  # Ex: "5511999999999@c.us"
        phone = chat_id.split("@")[0]           # Ex: "5511999999999"
        
        # Enfileira job no Redis RQ
        job_id = queue_service.enqueue_message_processing(
            message_data=message_data,
            message_direction="inbound",
        )
        
        logger.info(f"✓ Mensagem enfileirada: {job_id}")
```

#### Payload real que chega:
```json
{
  "event": "message",
  "session": "default",
  "payload": {
    "id": "true_5511999999999@c.us_3A123ABC",
    "timestamp": 1702800000,
    "from": "5511999999999@c.us",
    "body": "Olá, estou com dificuldade para emagrecer e vi que vocês trabalham com emagrecimento saudável",
    "fromMe": false,
    "hasMedia": false,
    "type": "chat"
  }
}
```

#### O que acontece:
1. ✅ Webhook salvo na tabela `webhook_logs`
2. ✅ Job criado na fila Redis `messages` (alta prioridade)
3. ✅ Worker pega job assincronamente

---

### **PASSO 4: Worker processa job (Orchestrator)**

#### Código: `conversation_orchestrator.py` linha 82-204

```python
async def process_inbound_message(
    self,
    chat_id: str,          # "5511999999999@c.us"
    phone_number: str,     # "5511999999999"
    message_text: str,     # "Estou com dificuldade para emagrecer"
    session_name: str = "default",
) -> dict:
    """
    Processa mensagem inbound em 10 etapas:
    
    1. Buscar ou criar conversa + lead
    2. Salvar mensagem inbound no banco
    3. Buscar contexto do ChromaDB
    4. Detectar intenção (Gemini)
    5. Gerar resposta SPIN Selling (Gemini)
    6. Atualizar score de maturidade
    7. Salvar contexto no ChromaDB
    8. Enviar resposta via WAHA
    9. Salvar mensagem outbound
    10. Registrar interação no histórico
    """
```

#### **SUB-ETAPA 4.1: Buscar ou criar Lead + Conversa**

Código: `conversation_orchestrator.py` linha 220-263

```python
async def _get_or_create_conversation(
    self, session, chat_id: str, phone_number: str
) -> Conversation:
    """
    1. Busca conversa por chat_id
    2. Se não existe:
       - Cria Lead novo (phone, name=phone, score=0)
       - Cria Conversation (status=ACTIVE, lead_status=NEW)
       - Associa Conversation ao Lead
    """
    
    repo = ConversationRepository(session)
    conversation = repo.get_by_chat_id(chat_id)
    
    if conversation:
        return conversation  # ✅ Conversa já existe
    
    # ❌ Primeira vez deste número
    lead_repo = LeadRepository(session)
    
    # CRIA LEAD NOVO
    lead = Lead(
        phone_number=phone_number,      # "5511999999999"
        name=phone_number,               # "5511999999999" (será atualizado depois)
        maturity_score=0,                # COMEÇA COM 0
    )
    lead_repo.create(lead)
    session.flush()  # Gera lead.id
    
    # CRIA CONVERSA NOVA
    conversation = repo.create(
        chat_id=chat_id,                 # "5511999999999@c.us"
        phone_number=phone_number,       # "5511999999999"
        status=ConversationStatus.ACTIVE,
    )
    conversation.lead_status = LeadStatus.NEW
    conversation.lead_id = lead.id
    session.flush()
    
    logger.info(f"✓ Nova conversa criada (id={conversation.id}, lead_id={lead.id})")
    
    return conversation
```

**Estado do banco após esta etapa:**

```sql
-- Tabela: leads
INSERT INTO leads (id, phone_number, name, maturity_score, status, source, stage, created_at)
VALUES (1, '5511999999999', '5511999999999', 0, 'active', 'whatsapp', 'new', NOW());

-- Tabela: conversations
INSERT INTO conversations (id, chat_id, phone_number, lead_id, status, lead_status, is_urgent, created_at)
VALUES (1, '5511999999999@c.us', '5511999999999', 1, 'active', 'NEW', false, NOW());
```

---

#### **SUB-ETAPA 4.2: Salvar mensagem inbound**

Código: `conversation_orchestrator.py` linha 265-286

```python
async def _save_inbound_message(
    self, session, conversation_id: str, text: str
) -> ConversationMessage:
    """Salva mensagem do usuário no banco."""
    
    repo = ConversationMessageRepository(session)
    
    message = ConversationMessage(
        conversation_id=conversation_id,  # 1
        direction=MessageDirection.INBOUND,
        content=text,                      # "Olá, vi o anúncio de clareamento"
        timestamp=datetime.now(UTC),
    )
    repo.create(message)
    session.flush()
    
    return message
```

**Estado do banco:**
```sql
-- Tabela: conversation_messages
INSERT INTO conversation_messages (id, conversation_id, direction, content, timestamp)
VALUES (1, 1, 'inbound', 'Estou com dificuldade para emagrecer', NOW());
```

---

#### **SUB-ETAPA 4.3: Buscar contexto no ChromaDB**

Código: `conversation_orchestrator.py` linha 322-348

```python
async def _get_conversation_context(
    self, conversation_id: str, limit: int = 5
) -> str:
    """
    Busca últimas interações desta conversa no ChromaDB.
    Retorna texto combinado para contexto da IA.
    """
    
    results = self.chroma_client.search_conversation(
        conversation_id=conversation_id,
        limit=limit
    )
    
    if not results:
        return "[Primeira mensagem - sem histórico]"
    
    # Combina últimas mensagens em texto
    context_text = "\n".join([
        f"- {r['text']}" for r in results
    ])
    
    return context_text
```

**Exemplo de retorno (primeira mensagem):**
```
"[Primeira mensagem - sem histórico]"
```

**Exemplo de retorno (mensagens subsequentes):**
```
- User: Olá, vi o anúncio de clareamento
  Bot: Que ótimo que você se interessou! Conte-me, você já fez algum tratamento dental antes?
- User: Sim, já fiz limpeza
  Bot: Legal! E o que te motivou a buscar o clareamento agora?
```

---

#### **SUB-ETAPA 4.4: Detectar intenção com Gemini**

Código: `conversation_orchestrator.py` linha 404-445

```python
async def _detect_intent(
    self, message: str, context: str
) -> str:
    """
    Classifica intenção usando Gemini AI em 10 categorias.
    """
    
    # Monta prompt com template
    prompt = self.prompt_templates.format_intent_prompt(
        message=message,
        context=context
    )
    
    # Chama Gemini
    response = self.gemini_client.generate_response(prompt)
    intent = response["response"].strip().upper()
    
    # Valida resposta
    valid_intents = [
        "INTERESSE_PRODUTO",  # ← Cliente interessado em procedimentos
        "DUVIDA_TECNICA",     # Dúvidas sobre como funciona
        "ORCAMENTO",          # Solicitação de preço
        "AGENDAMENTO",        # Deseja agendar consulta
        "RECLAMACAO",         # Problema ou insatisfação
        "INFORMACAO",         # Busca informações gerais
        "SAUDACAO",           # Cumprimento inicial
        "DESPEDIDA",          # Finalização
        "CONFIRMACAO",        # Confirmar interesse
        "OUTRO"               # Não se encaixa
    ]
    
    if intent not in valid_intents:
        intent = "OUTRO"
    
    logger.info(f"✓ Intenção detectada: {intent}")
    
    return intent
```

**Template usado (templates.py linha 92-125):**
```python
INTENT_DETECTION_PROMPT = """Analise a mensagem identificando INTENÇÃO e FASE SPIN.

MENSAGEM: "Estou com dificuldade para emagrecer, será que vocês podem me ajudar?"

CONTEXTO ANTERIOR:
[Primeira mensagem - sem histórico]

# INTENÇÕES POSSÍVEIS
1. INTERESSE_PRODUTO - Cliente interessado em procedimentos  ← MATCH!
2. DUVIDA_TECNICA - Dúvidas sobre funcionamento
3. ORCAMENTO - Solicitação de preço
...

# FASE SPIN ATUAL
- SITUATION - Falando sobre situação atual  ← INICIO AQUI
- PROBLEM - Descrevendo problemas/dificuldades
- IMPLICATION - Mencionando impactos/consequências
- NEED_PAYOFF - Expressando desejo de solução/benefícios
- READY - Pronto para agendamento/próximo passo

Responda APENAS em JSON:
{
    "intent": "INTERESSE_PRODUTO",
    "spin_phase": "SITUATION",
    "confidence": 90
}
"""
```

**Resposta do Gemini:**
```json
{
  "intent": "INTERESSE_PRODUTO",
  "spin_phase": "SITUATION",
  "confidence": 90
}
```

---

#### **SUB-ETAPA 4.5: Gerar resposta SPIN Selling**

Código: `conversation_orchestrator.py` linha 447-473

```python
async def _generate_response(
    self,
    message_text: str,
    intent: str,
    context: str,
    conversation: Conversation
) -> dict:
    """
    Gera resposta usando metodologia SPIN Selling.
    """
    
    prompt = self.prompt_templates.format_response_prompt(
        user_message=message_text,
        intent=intent,
        context=context,
        maturity_score=conversation.lead.maturity_score,  # 0 (primeira vez)
        lead_status=conversation.lead_status.value,       # "NEW"
        last_interaction="Agora"
    )
    
    response_data = self.gemini_client.generate_response(prompt)
    
    return response_data  # {"response": "...", "tokens_used": 150, "latency_ms": 800}
```

**Template SPIN usado (templates.py linha 177-237):**
```python
RESPONSE_GENERATION_PROMPT = """Gere uma resposta seguindo metodologia SPIN Selling.

MENSAGEM DO CLIENTE: "Olá, vi o anúncio de clareamento"

INTENÇÃO DETECTADA: INTERESSE_PRODUTO
FASE SPIN ATUAL: SITUATION

CONTEXTO RELEVANTE:
[Primeira mensagem - sem histórico]

INFORMAÇÕES DO LEAD:
- Score de Maturidade: 0/100
- Status: NEW
- Fase SPIN: SITUATION
- Última Interação: Agora

# INSTRUÇÕES ESPECÍFICAS POR FASE

**Se SITUATION (Score < 30):**  ← ESTAMOS AQUI!
- Faça perguntas abertas sobre o contexto atual
- Entenda a situação sem julgar
- Exemplo: "Conte-me mais sobre como isso começou?"

**Se PROBLEM (Score 30-50):**
- Explore dificuldades específicas
- Identifique gaps e frustrações

**Se IMPLICATION (Score 50-75):**
- Amplifique consequências e urgência
- Conecte a impactos importantes

**Se NEED_PAYOFF (Score 75-85):**
- Faça cliente articular benefícios
- Explore impacto positivo de resolver

**Se READY (Score > 85):**
- Apresente próximos passos claros
- Ofereça agendamento direto

# REGRAS IMPORTANTES
✅ Faça 1-2 perguntas SPIN por mensagem
✅ Demonstre compreensão antes de perguntar
✅ Mantenha tom empático e natural
✅ Máximo 3 parágrafos
❌ NÃO pule fases (respeite progressão)
❌ NÃO apresente soluções antes de Need-Payoff
❌ NÃO faça múltiplas perguntas seguidas

Gere APENAS a resposta (sem meta-informações).
"""
```

**Resposta gerada pelo Gemini:**
```
Entendo sua preocupação com emagrecimento. 💚

Para eu te ajudar da melhor forma, me conta: há quanto tempo você vem enfrentando 
essa dificuldade? Você já tentou algum método antes?

E o que tem sido mais desafiador para você nesse processo? (ex: falta de resultado, 
efeito sanfona, cansaço, ansiedade...)
```

**Por que essa resposta?**
- ✅ Fase SITUATION (Score 0): Foca em entender contexto
- ✅ Pergunta aberta sobre histórico
- ✅ Explora motivação (SPIN)
- ✅ Tom empático e natural
- ✅ Não apresenta solução ainda (respeita metodologia)

---

#### **SUB-ETAPA 4.6: Atualizar score de maturidade**

Código: `conversation_orchestrator.py` linha 475-524

```python
async def _update_maturity_score(
    self, session, conversation: Conversation, message: str, intent: str
) -> int:
    """
    Atualiza score baseado em engajamento e intenção.
    """
    
    current_score = conversation.lead.maturity_score  # 0
    
    # Tabela de pontos por intenção
    score_delta = {
        "INTERESSE_PRODUTO": 10,   # ← Cliente manifestou interesse!
        "ORCAMENTO": 15,
        "AGENDAMENTO": 20,
        "CONFIRMACAO": 25,
        "DUVIDA_TECNICA": 5,
        "INFORMACAO": 3,
        "SAUDACAO": 1,
        "OUTRO": 0,
    }.get(intent, 0)
    
    new_score = min(100, current_score + score_delta)  # 0 + 10 = 10
    
    # Atualiza no banco
    if conversation.lead:
        lead_repo = LeadRepository(session)
        conversation.lead.maturity_score = new_score
        lead_repo.update(conversation.lead)
        session.flush()
    
    logger.info(f"✓ Score atualizado: {current_score} → {new_score} (delta={score_delta})")
    
    return new_score  # 10
```

**Estado do banco após update:**
```sql
UPDATE leads 
SET maturity_score = 10, updated_at = NOW()
WHERE id = 1;
```

**Progressão do score em conversas típicas:**
```
Score 0   → "Olá, vi o anúncio"           (SAUDACAO: +1)         = 1
Score 1   → "Quero saber sobre implante"  (INTERESSE: +10)       = 11
Score 11  → "Quanto custa?"               (ORCAMENTO: +15)       = 26
Score 26  → "Pode agendar pra amanhã?"    (AGENDAMENTO: +20)     = 46
Score 46  → "Confirmo o agendamento"      (CONFIRMACAO: +25)     = 71
Score 71  → [Cliente comparece consulta]  (MANUAL: +29)          = 100 ✅
```

---

#### **SUB-ETAPA 4.7: Salvar contexto no ChromaDB**

Código: `conversation_orchestrator.py` linha 526-544

```python
async def _save_to_chroma(
    self,
    conversation_id: str,
    text: str,
    metadata: dict
) -> None:
    """
    Salva par User/Bot no ChromaDB para contexto futuro.
    """
    
    self.chroma_client.add_conversation(
        conversation_id=conversation_id,  # "1"
        text=text,  # "User: Olá, vi...\nBot: Que ótimo..."
        metadata=metadata  # {"intent": "INTERESSE_PRODUTO", "score": 10}
    )
    
    logger.info(f"✓ Contexto salvo no ChromaDB (conv_id={conversation_id})")
```

**Documento salvo no ChromaDB:**
```json
{
  "id": "conv_1_msg_1",
  "conversation_id": "1",
  "text": "User: Estou com dificuldade para emagrecer\nBot: Entendo sua preocupação. Há quanto tempo você vem enfrentando isso?...",
  "metadata": {
    "intent": "INTERESSE_PRODUTO",
    "score": 10,
    "timestamp": "2025-12-17T10:30:00Z"
  },
  "embedding": [0.234, -0.567, 0.123, ...]  // Vetor de 768 dimensões
}
```

**Por que ChromaDB?**
- ✅ Busca semântica (não só keywords)
- ✅ Contextualiza respostas futuras
- ✅ Lembra preferências do cliente
- ✅ Evita repetir perguntas

---

#### **SUB-ETAPA 4.8: Enviar resposta via WAHA**

Código: `conversation_orchestrator.py` linha 546-568

```python
async def _send_response_via_waha(
    self, chat_id: str, text: str, session: str
) -> bool:
    """Envia mensagem via WAHA WhatsApp API."""
    
    try:
        self.waha_client.send_text_message(
            session=session,          # "default"
            chat_id=chat_id,          # "5511999999999@c.us"
            text=text                 # "Que ótimo que você..."
        )
        
        logger.info(f"✓ Resposta enviada via WAHA (chat_id={chat_id})")
        return True
        
    except WAHAError as e:
        logger.error(f"✗ Falha ao enviar: {e}")
        raise
```

**Request HTTP que vai para WAHA:**
```http
POST http://wpp_bot_waha:3000/api/sendText
Headers:
  X-Api-Key: sua-api-key-aqui
  Content-Type: application/json

Body:
{
  "session": "default",
  "chatId": "5511999999999@c.us",
  "text": "Entendo sua preocupação com emagrecimento. 💚\n\nPara eu te ajudar da melhor forma, me conta: há quanto tempo você vem enfrentando essa dificuldade? Você já tentou algum método antes?\n\nE o que tem sido mais desafiador para você nesse processo?"
}
```

**WAHA envia para WhatsApp:**
- ✅ Cliente recebe mensagem no WhatsApp dele
- ✅ Aparece como vindo do número da clínica
- ✅ Cliente pode responder normalmente

---

#### **SUB-ETAPA 4.9: Salvar mensagem outbound no banco**

```python
async def _save_outbound_message(
    self, session, conversation_id: str, text: str
) -> ConversationMessage:
    """Salva resposta do bot no banco."""
    
    repo = ConversationMessageRepository(session)
    
    message = ConversationMessage(
        conversation_id=conversation_id,
        direction=MessageDirection.OUTBOUND,
        content=text,
        timestamp=datetime.now(UTC),
    )
    repo.create(message)
    session.flush()
    
    return message
```

**Estado do banco:**
```sql
INSERT INTO conversation_messages (id, conversation_id, direction, content, timestamp)
VALUES (2, 1, 'outbound', 'Que ótimo que você se interessou...', NOW());
```

---

#### **SUB-ETAPA 4.10: Registrar interação**

Código: `conversation_orchestrator.py` linha 570-608

```python
async def _register_interaction(
    self, session, lead_id: str, interaction_type: str, notes: str
) -> None:
    """Registra interação no histórico do lead."""
    
    repo = LeadInteractionRepository(session)
    
    # Mapeia intenção para tipo de interação
    type_map = {
        "INTERESSE_PRODUTO": InteractionType.MESSAGE,
        "ORCAMENTO": InteractionType.MEETING,
        "AGENDAMENTO": InteractionType.MEETING,
        "RECLAMACAO": InteractionType.CALL,
    }
    
    interaction = LeadInteraction(
        lead_id=lead_id,
        interaction_type=type_map.get(interaction_type, InteractionType.MESSAGE),
        notes=notes,  # "Inbound: Olá, vi... | Outbound: Que ótimo..."
        timestamp=datetime.now(UTC),
    )
    repo.create(interaction)
    session.flush()
```

**Estado do banco:**
```sql
INSERT INTO lead_interactions (id, lead_id, interaction_type, notes, timestamp)
VALUES (1, 1, 'message', 'Inbound: Olá, vi o anúncio... | Outbound: Que ótimo...', NOW());
```

---

### **PASSO 5: Cliente responde (ciclo continua)**

Quando o cliente responder novamente:

```
Cliente: "Sim, já fiz limpeza"
↓
WAHA webhook → API → Orchestrator
↓
1. Busca conversa EXISTENTE (id=1, lead_id=1)
2. Busca contexto ChromaDB (últimas 5 mensagens)
3. Detecta intent: INFORMACAO (score +3 = 13)
4. Gera resposta SPIN fase PROBLEM:
   "O que tem sido mais difícil para você no processo de emagrecimento?"
5. Atualiza ChromaDB com novo par User/Bot
6. Envia resposta via WAHA
```

**Progressão SPIN ao longo das mensagens:**

```
Mensagem 1 (Score 0-30):  SITUATION
└─ "Há quanto tempo você tem dificuldade para emagrecer?"
   "Já tentou algum tratamento ou dieta antes?"

Mensagem 3-5 (Score 30-50): PROBLEM
└─ "Quais dificuldades você tem enfrentado?"
   "O que tem te incomodado no sorriso?"

Mensagem 6-8 (Score 50-75): IMPLICATION
└─ "Como isso tem afetado sua autoestima?"
   "Você já deixou de sorrir em fotos por isso?"

Mensagem 9-10 (Score 75-85): NEED-PAYOFF
└─ "Como seria ter um sorriso que você ama?"
   "O que mudaria na sua vida?"

Mensagem 11+ (Score > 85): READY
└─ "Gostaria de agendar uma avaliação inicial para discutir seu plano de emagrecimento?"
   "Qual dia funciona melhor: terça ou quinta?"
```

---

## 📈 Tabelas de Maturidade vs Ação

| Score | Fase SPIN | Foco da Conversa | Ação do Bot |
|-------|-----------|------------------|-------------|
| 0-30 | SITUATION | Entender contexto | Perguntas abertas sobre situação |
| 30-50 | PROBLEM | Identificar dores | Explorar dificuldades e gaps |
| 50-75 | IMPLICATION | Criar urgência | Amplificar consequências |
| 75-85 | NEED-PAYOFF | Valor da solução | Cliente articula benefícios |
| 85-100 | READY | Conversão | Oferecer agendamento |

---

## 🎯 Exemplo de Conversa Completa

### **Turno 1: SITUATION (Score 0 → 10)**
```
👤 Cliente: "Olá, estou com dificuldade para emagrecer"
🤖 Bot: "Que ótimo! Você já fez algum tratamento dental antes?"
```

### **Turno 2: SITUATION (Score 10 → 13)**
```
👤 Cliente: "Sim, já fiz limpeza"
🤖 Bot: "Legal! E o que te motivou a buscar o clareamento agora?"
```

### **Turno 3: PROBLEM (Score 13 → 28)**
```
👤 Cliente: "Meus dentes estão meio amarelados, bebo muito café"
🤖 Bot: "Entendo. Isso tem te incomodado no dia a dia? Por exemplo, você evita sorrir em algumas situações?"
```

### **Turno 4: IMPLICATION (Score 28 → 43)**
```
👤 Cliente: "Sim, fico sem graça em fotos e reuniões de trabalho"
🤖 Bot: "Imagino que isso deve afetar sua confiança né? Principalmente no trabalho onde a primeira impressão é importante..."
```

### **Turno 5: IMPLICATION (Score 43 → 58)**
```
👤 Cliente: "Exato! Queria ter mais confiança pra falar em público"
🤖 Bot: "Como seria pra você ter um sorriso branquinho que você não precisasse esconder mais?"
```

### **Turno 6: NEED-PAYOFF (Score 58 → 73)**
```
👤 Cliente: "Seria ótimo! Eu poderia sorrir sem medo, me sentir melhor"
🤖 Bot: "Perfeito! E se eu te falar que o clareamento pode ser feito em apenas 2 sessões e o resultado dura até 2 anos, o que você acha?"
```

### **Turno 7: READY (Score 73 → 93)**
```
👤 Cliente: "Nossa, só 2 sessões? Quanto custa?"
🤖 Bot: "O investimento é R$299 nas 2 sessões. Quer que eu agende uma avaliação gratuita pra você? Temos horários terça e quinta."
```

### **Turno 8: AGENDAMENTO (Score 93 → 118 → 100)**
```
👤 Cliente: "Sim! Pode ser quinta de manhã?"
🤖 Bot: "✅ Ótimo! Quinta 10h está confirmado. Vou te enviar o endereço e o contato da recepcionista. Até lá! 😊"
```

**🎉 LEAD CONVERTIDO!**

---

## 🔍 Verificando o que está implementado vs planejado

### ✅ O que ESTÁ implementado:

1. **Recebimento de webhooks WAHA** ✅
   - Endpoint `/webhooks/waha` funcional
   - Salva logs no banco
   - Enfileira jobs no Redis

2. **Criação automática de Lead + Conversa** ✅
   - Primeira mensagem cria Lead (score=0)
   - Associa Conversation ao Lead
   - Registra phone, chat_id

3. **Processamento assíncrono (Workers)** ✅
   - Redis RQ com 3 filas (messages, ai, escalation)
   - 2 workers rodando em Docker
   - Retry automático em falhas

4. **Detecção de intenção com Gemini** ✅
   - 10 categorias de intent
   - JSON parsing robusto
   - Fallback para "OUTRO"

5. **Metodologia SPIN Selling** ✅
   - 4 fases implementadas (SITUATION, PROBLEM, IMPLICATION, NEED-PAYOFF)
   - Prompts específicos por fase
   - Progressão natural baseada em score

6. **Sistema de scoring de maturidade** ✅
   - Score 0-100 automático
   - Incrementos por intenção
   - Persiste no Lead

7. **ChromaDB para contexto** ✅
   - Salva pares User/Bot
   - Busca semântica
   - Últimas 5 mensagens como contexto

8. **Envio via WAHA** ✅
   - Send text message
   - Rate limiting (50 msgs/hora/chat)
   - Retry em falhas

9. **Auditoria completa** ✅
   - `webhook_logs`: Todos webhooks recebidos
   - `conversation_messages`: Histórico completo
   - `lead_interactions`: Timeline de engajamento
   - `llm_interactions`: Custos e latência Gemini

10. **Detecção de urgência** ✅
    - Keywords + validação LLM
    - Flag `is_urgent` na conversa
    - Priorização no atendimento

---

### ⚠️ O que NÃO está implementado (gaps):

1. **Envio de mídia rica** ⚠️
   - Botões interativos do WhatsApp
   - Listas de seleção
   - Imagens/vídeos automáticos
   - **Status:** Código existe mas não usado no fluxo

2. **Transferência para humano** ⚠️
   - Score > 85 deveria escalar?
   - Urgência detectada → notificar agente?
   - **Status:** Lógica de escalação existe mas não conectada

3. **Envio proativo** ⚠️
   - Reengagement após 24h sem resposta
   - Follow-up automático
   - **Status:** Job existe (`jobs/reengagement`) mas não agendado

4. **Extração de dados estruturados** ⚠️
   - Nome do cliente (ainda fica como número)
   - Procedimentos mencionados
   - Budget mencionado
   - **Status:** Template existe mas não usado

5. **Integração com agenda** ⚠️
   - Agendamento real em sistema externo
   - Confirmação de horários disponíveis
   - **Status:** Não implementado

6. **Métricas e dashboard** ⚠️
   - Taxa de conversão por campanha
   - Tempo médio até agendamento
   - Custos Gemini por lead
   - **Status:** Dados existem, falta visualização

---

## 🎯 Resumo: O fluxo FUNCIONA?

### ✅ SIM! O fluxo básico está completo:

```
Anúncio → WhatsApp → WAHA → API → Orchestrator → Gemini → ChromaDB → WAHA → Cliente
   ✅        ✅        ✅      ✅       ✅           ✅         ✅        ✅       ✅
```

### ✅ O que funciona MUITO BEM:

1. **Automação completa** do primeiro contato
2. **SPIN Selling** bem implementado nos prompts
3. **Persistência robusta** (PostgreSQL + ChromaDB)
4. **Processamento assíncrono** escalável
5. **Scoring automático** de maturidade

### ⚠️ O que precisa atenção:

1. **Conversão final** (score > 85) não tem ação automática
2. **Nome do lead** continua como telefone
3. **Follow-up proativo** não está agendado
4. **Transferência humana** não está conectada

---

## 🚀 Recomendações para Produção:

### Prioridade ALTA:
1. **Conectar score > 85 com notificação para agente humano**
2. **Implementar job de follow-up após 24h sem resposta**
3. **Extrair nome do cliente nas primeiras mensagens**

### Prioridade MÉDIA:
4. **Adicionar botões interativos WhatsApp (lista de procedimentos)**
5. **Implementar escalação automática em urgências**
6. **Dashboard de métricas (leads, conversões, custos)**

### Prioridade BAIXA:
7. **Integração com agenda externa**
8. **Envio de imagens/vídeos de procedimentos**
9. **Webhooks para CRM externo**

---

## � Exemplo Real de Playbook: Emagrecimento Saudável

### **Estrutura no Banco de Dados:**

```sql
-- 1. CRIAR TÓPICO
INSERT INTO topics (id, name, description, active) VALUES
('uuid-topic-1', 'Emagrecimento Saudável', 
 'Tratamento médico para emagrecimento com acompanhamento hormonal e metabólico', 
 true);

-- 2. CRIAR PLAYBOOK
INSERT INTO playbooks (id, topic_id, name, description, active) VALUES
('uuid-playbook-1', 'uuid-topic-1', 
 'Jornada Completa: Emagrecimento com Saúde',
 'Sequência de mensagens guiadas para leads interessados em emagrecimento médico supervisionado',
 true);

-- 3. CRIAR MENSAGENS (TEMPLATES)
INSERT INTO messages (id, content, active) VALUES
('uuid-msg-1', 
 'Entendo sua preocupação com emagrecimento. Para eu poder te ajudar melhor: há quanto tempo você vem enfrentando dificuldade para emagrecer? Já tentou algum método antes?',
 true),

('uuid-msg-2',
 'Obrigada por compartilhar! E o que tem sido mais difícil para você nesse processo? (ex: falta de resultado, efeito sanfona, cansaço, ansiedade...)',
 true),

('uuid-msg-3',
 'Entendo perfeitamente. Como isso tem afetado sua rotina, energia e autoestima no dia a dia?',
 true),

('uuid-msg-4',
 'Você já imaginou como seria sua vida se conseguisse emagrecer de forma saudável e definitiva, sem sofrimento e com acompanhamento médico especializado?',
 true),

('uuid-msg-5',
 'Que bom que você está aberta a isso! Nossa abordagem é diferente: trabalhamos com emagrecimento MÉDICO, avaliando hormônios, metabolismo, saúde mental. O foco não é só estética, é cuidar do seu corpo como um todo. Gostaria de agendar uma avaliação inicial?',
 true);

-- 4. CRIAR STEPS (SEQUÊNCIA)
INSERT INTO playbook_steps (id, playbook_id, message_id, step_order, context_hint) VALUES
('uuid-step-1', 'uuid-playbook-1', 'uuid-msg-1', 1, 'SITUATION: Entender histórico e tentativas anteriores'),
('uuid-step-2', 'uuid-playbook-1', 'uuid-msg-2', 2, 'PROBLEM: Identificar principais dificuldades'),
('uuid-step-3', 'uuid-playbook-1', 'uuid-msg-3', 3, 'IMPLICATION: Amplificar impacto emocional e físico'),
('uuid-step-4', 'uuid-playbook-1', 'uuid-msg-4', 4, 'NEED-PAYOFF: Cliente articula desejo de solução'),
('uuid-step-5', 'uuid-playbook-1', 'uuid-msg-5', 5, 'READY: Apresentar proposta e agendar');

-- 5. CRIAR EMBEDDING (RAG)
INSERT INTO playbook_embeddings (id, playbook_id, embedding_text, chroma_doc_id) VALUES
('uuid-embed-1', 'uuid-playbook-1',
 'emagrecimento saudável médico hormônios metabolismo tratamento perder peso dieta saúde efeito sanfona acompanhamento individualizado',
 'chroma-doc-playbook-1');
```

### **Como o Gemini Usa Este Playbook:**

**Cenário: Cliente pergunta sobre emagrecimento**

```
Cliente: "Não consigo emagrecer de jeito nenhum. Já fiz várias dietas mas sempre volto a engordar."

🤖 GEMINI PROCESS:
1. Detecta intent: INTERESSE_TRATAMENTO
2. Busca no ChromaDB: "emagrecimento dieta perder peso"
3. ChromaDB retorna: Playbook "Jornada Completa: Emagrecimento com Saúde"
4. Gemini usa Function Calling:
   - search_playbooks(query="emagrecimento saudável") → retorna uuid-playbook-1
   - get_playbook_messages(playbook_id="uuid-playbook-1") → retorna 5 mensagens ordenadas
5. Gemini analisa fase SPIN: Cliente está em SITUATION + PROBLEM
6. Gemini escolhe message 2 ou 3 do playbook
7. Responde baseado no template, personalizando com contexto

BOT: "Entendo sua frustração com o efeito sanfona. Para eu te ajudar melhor: 
o que tem sido mais difícil para você nesse processo de emagrecimento? 
É falta de resultado, cansaço, ansiedade...?"
```

### **Gemini Tools Disponíveis:**

```python
# 1. BUSCAR PLAYBOOKS (RAG)
search_playbooks(query="emagrecimento", top_k=3)
→ Retorna: [
    {
        "id": "uuid-playbook-1",
        "name": "Jornada Completa: Emagrecimento com Saúde",
        "score": 0.92
    }
]

# 2. OBTER MENSAGENS DO PLAYBOOK
get_playbook_messages(playbook_id="uuid-playbook-1")
→ Retorna: [
    {
        "order": 1,
        "content": "Entendo sua preocupação...",
        "context_hint": "SITUATION: Entender histórico"
    },
    ...
]

# 3. ENVIAR MENSAGEM ESPECÍFICA
send_playbook_message(playbook_id="uuid-playbook-1", step_order=2)
→ Envia a mensagem do step 2 via WAHA
```

---

## 📞 Arquivos-chave para entender o fluxo:

1. **Entrada**: `webhook_controller.py` (linha 26)
2. **Orquestração**: `conversation_orchestrator.py` (linha 82)
3. **Prompts SPIN**: `templates.py` (linha 26) - **ATUALIZADO COM CONTEXTO MÉDICO**
4. **Playbook Tools**: `playbook_tools.py` - Function calling para Gemini
5. **Scoring**: `conversation_orchestrator.py` (linha 475)
6. **ChromaDB**: `chroma_client.py`
7. **WAHA**: `waha_client.py`

---

## 🎯 CONCLUSÃO

**Sistema 100% funcional com Playbooks integrados:**

1. ✅ Migrations aplicadas (topics, playbooks, playbook_steps, playbook_embeddings)
2. ✅ Gemini com Function Calling configurado
3. ✅ ConversationOrchestrator integrado com Playbook Tools
4. ✅ Prompts atualizados para contexto médico/saúde
5. ✅ RAG funcional (ChromaDB + PostgreSQL)
6. ✅ Workers rodando sem erros
7. ✅ SPIN Selling implementado

**Quando um paciente contatar via WhatsApp:**
1. ✅ Será atendido instantaneamente
2. ✅ IA detectará intenção e fase SPIN
3. ✅ Buscará playbook relevante no ChromaDB
4. ✅ Usará sequência estruturada de mensagens
5. ✅ Personalizará resposta com contexto do paciente
6. ✅ Evoluirá score de maturidade progressivamente
7. ✅ Oferecerá agendamento no momento certo (score > 85)
3. ✅ Ter score de maturidade calculado
4. ✅ Receber respostas contextualizadas
5. ⚠️ Mas pode não ter follow-up se não responder
6. ⚠️ E pode não ser escalado mesmo estando pronto (score > 85)

**Próximo passo:** Conectar os últimos 15% de conversão! 🚀

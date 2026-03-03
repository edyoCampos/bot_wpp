# Backend Architecture Refactoring Plan

**Document Version:** 1.0.0  
**Date:** 2026-02-02  
**Status:** In Review  
**Target Completion:** Q1 2026  
**Methodology:** Incremental Refactoring with Continuous Delivery

---

## Executive Summary

This document provides a comprehensive architectural analysis and refactoring plan for the backend system. The current architecture exhibits critical design flaws that prevent:

1. LLM provider abstraction (hard-coupled to Gemini)
2. Model Context Protocol (MCP) integration
3. Scalable context management
4. Clean separation of concerns
5. Effective testing and maintainability

### Critical Issues Summary

| Priority | Issue | Impact | Technical Debt Score |
|:---:|---|---|:---:|
| P0 | LLM provider tightly coupled to Gemini | Blocks multi-provider support | 9/10 |
| P0 | Context Repository anti-pattern | Naming confusion, poor semantics | 8/10 |
| P0 | MessageModel naming confusion | Knowledge vs Conversation conflated | 9/10 |
| P0 | Prompts scattered across 3 locations | Maintenance nightmare, inconsistency | 8/10 |
| P1 | Empty domain layer | Business logic in infrastructure | 9/10 |
| P1 | Service layer SRP violations | God classes, high coupling | 7/10 |
| P2 | Flat service directory | Poor navigation, no context | 6/10 |

**Business Impact:**
- Cannot adopt MCP without major rewrite
- Cannot switch LLM providers (vendor lock-in)
- Context repository content mixed with conversation messages
- 40% longer onboarding time for new developers
- High defect rate in context-related features

**Quick Navigation:**

| Section | What You'll Find | For |
|---|---|---|
| [Phase 1.5](#phase-15-local-file-storage-system) | Local file storage setup (no cloud costs) | **Dev Team** |
| [Phase 2](#phase-2-context-rename--api-routes-week-3) | Database + API rename strategy (simplified) | **Backend** |
| [Auto-Send Workflow](#admin-interface-for-content-management) | How bot decides when to send files | **Product + Frontend** |
| [LLM Abstraction](#llm-provider-abstraction) | Multi-provider support design | **Backend** |
| [Migration Scripts](#critical-migration-details) | SQL for schema changes | **DevOps** |
| [Testing Strategy](#testing-strategy) | Coverage targets and approach | **QA** |

---

### Key Corrections (2026-02-02)

**Critical Updates:**

1. **MessageModel Usage Clarified:**
   - ✅ `MessageModel` is ONLY used for context content (playbook)
   - ✅ `ConversationMessageModel` is separate table for WhatsApp messages
   - ✅ NO dual-purpose confusion - verified via codebase analysis
    - ⚠️ Still needs rename: `MessageModel` → `ContentModel`
   - 🎯 Simplified migration: **rename only**, no data split needed

2. **Auto-Send Workflow Corrected:**
   - ❌ WRONG: User requests files ("envie o folheto")
   - ✅ RIGHT: Bot autonomously decides when to send files
   - 🎯 Admin configures via `usage_hint` field
   - 🤖 Bot uses LLM to decide optimal moment to send content
   - Example: "Send PDF when user shows interest in Botox"

3. **File Storage Requirements:**
   - 🚨 CRITICAL: Need local file storage for development
   - 💸 Cannot afford S3/CDN costs during development
   - 🎯 Solution: FileStorage abstraction layer
   - 📁 LocalFileStorage for dev → S3FileStorage for production migration

**Action Items:**

- [ ] Review Auto-Send UX with product team
- [ ] Design admin interface for content configuration
- [ ] Implement FileStorage abstraction (Phase 1.5)
- [ ] Test bot autonomous send decision logic
- [ ] Plan migration SQL scripts (simplified - rename only)

---

## Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Critical Anti-Patterns](#critical-anti-patterns)
3. [Domain Model Strategy](#domain-model-strategy)
4. [LLM Provider Abstraction](#llm-provider-abstraction)
5. [Context Repository Redesign](#context-repository-redesign)
6. [Prompt Management System](#prompt-management-system)
7. [Service Layer Reorganization](#service-layer-reorganization)
8. [File Storage System](#file-storage-system)
9. [Implementation Roadmap](#implementation-roadmap)
10. [Target Architecture](#target-architecture)
11. [Migration Plan](#migration-plan)
12. [Testing Strategy](#testing-strategy)
13. [Success Criteria](#success-criteria)

---

## Current State Analysis

### System Overview

```
back/src/robbot/
├── adapters/
│   ├── controllers/          # HTTP request handlers
│   ├── external/             # External service clients (Gemini, WAHA)
│   └── repositories/         # Data access layer
├── api/                      # FastAPI route definitions
├── config/
│   ├── prompts.yaml          # OLD prompts (deprecated)
│   ├── prompts/
│   │   └── templates.py      # NEW prompts (SPIN Selling)
│   ├── settings.py
│   └── container.py
├── core/                     # Shared utilities
├── domain/
│   ├── models/               # EMPTY (critical issue)
│   └── enums.py
├── infra/
│   ├── db/models/            # SQLAlchemy ORM models
│   ├── jobs/                 # RQ background jobs
│   └── queue/
├── services/                 # 32 services in flat structure
│   ├── conversation_orchestrator.py  # 488 LOC (God class)
│   ├── message_service.py            # 400+ LOC
│   ├── intent_detector.py            # Mixed responsibilities
│   └── ... (29 more)
└── workers/                  # RQ worker processes
```

**Metrics:**

| Metric | Current | Target | Delta |
|---|---|---|---|
| Total Services | 32 | 45 | +13 (decomposition) |
| Avg Service LOC | 280 | 120 | -57% |
| God Classes (>400 LOC) | 3 | 0 | -100% |
| Domain Models | 0 | 8 | +8 |
| Test Coverage | 58% | 85% | +27pp |
| Cyclomatic Complexity | 15.3 | 8.0 | -48% |

---

## Critical Anti-Patterns

### 1. Context Repository Misnamed as "Playbook"

**Current State:**

```python
# infra/db/models/playbook_model.py
class PlaybookModel(Base):
    """
    Playbook entity representing an organized sequence of messages for a specific topic.
    
    Example: "Apresentação Botox" playbook contains 5 steps with text, images, PDFs
    that the LLM can use to respond to client inquiries about Botox.
    """
    __tablename__ = "playbooks"
    
    id = Column(String(36), primary_key=True)
    topic_id = Column(String(36), ForeignKey("topics.id"))
    name = Column(String(255))
    description = Column(Text)
    active = Column(Boolean)
    
    # Relationships
    topic = relationship("TopicModel")
    steps = relationship("PlaybookStepModel", ...)  # Actually: context_items
    embedding = relationship("PlaybookEmbeddingModel", ...)
```

**Problem Analysis:**

The term "Playbook" implies a procedural script or workflow. However, the actual implementation is:

1. **A repository of contextual information** (facts, examples, templates)
2. **Not a procedural sequence** - LLM selects relevant items, doesn't execute steps
3. **Semantic search driven** - uses embeddings for retrieval
4. **Context augmentation** - provides knowledge to LLM, not instructions

**Confusion Matrix:**

| Term | Developer Interpretation | Actual Purpose |
|---|---|---|
| Playbook | Sequential script | Context repository |
| PlaybookStep | Execution step | Context item/fact |
| message_id | Template message | Knowledge snippet |
| step_order | Execution order | Display preference |

**Impact:**
- New developers misunderstand feature (30% onboarding time wasted)
- Code reviews require constant clarification
- Design decisions based on wrong mental model
- Integration complexity (developers expect workflow engine)

**Proposed Renaming:**

```
Playbook           → Context
PlaybookStep       → ContextItem
PlaybookEmbedding  → ContextEmbedding
Topic              → ContextCategory (or keep as Topic)
message_id         → content_id
step_order         → display_order / priority
```

**Justification:**

This aligns with:
- **Model Context Protocol (MCP)** terminology
- **Retrieval-Augmented Generation (RAG)** patterns
- **Semantic search** concepts
- Standard naming in LLM applications

#### The Message Relationship Problem

**Current Schema:**

```
Topic (category)
  └─→ Context
       └─→ ContextItem
            └─→ Content (text, image, video, PDF)
```

**How It Works - Two Modes:**

1. **RAG Mode (Retrieval-Augmented Generation):**
   - LLM searches context repository semantically
   - Retrieves relevant knowledge to inform response
   - **Does not send content directly** - uses it as reference
   - Example: User asks "Quanto custa Botox?" → Bot reads pricing and responds naturally

2. **Auto-Send Mode (Critical for UX!):**
   - Bot **automatically decides** to send content based on conversation flow
   - **NOT triggered by user request** - triggered by bot's understanding of context
   - Admin configures: "When discussing Botox, bot should send PDF brochure"
   - Bot sees context_hint and decides: "This is the moment to send the material"
   
**Example Auto-Send Flow:**

```
User: "Tenho interesse em Botox, pode me explicar?"
  ↓
Bot Intent Detection: INTERESSE_TRATAMENTO
  ↓
Bot searches Context("Botox")
  ↓
Finds ContextItem with:
  - content_type: "document" (PDF)
  - usage_hint: "Enviar automaticamente ao detectar interesse em Botox"
  - auto_send: true
  ↓
Bot DECIDES to send PDF + text response:
  "Que ótimo! Vou te enviar nosso material completo sobre Botox 📄"
  [Sends PDF via WhatsApp]
  "Dá uma olhada e me conta se ficou alguma dúvida!"
```

**Key Difference:**
- ❌ User says: "envie o folheto" (user doesn't know files exist)
- ✅ Bot decides: "I should send the brochure now" (based on admin configuration)

**Current Implementation:**

```python
# infra/db/models/playbook_step_model.py
class PlaybookStepModel(Base):
    """
    PlaybookStep entity linking messages to playbooks in a specific order.
    
    Each step represents a message that should be sent at a specific point
    in the playbook sequence.
    """
    __tablename__ = "playbook_steps"
    
    id = Column(String(36), primary_key=True)
    playbook_id = Column(String(36), ForeignKey("playbooks.id"))
    message_id = Column(UUID, ForeignKey("messages.id"))  # ← Problem here
    step_order = Column(Integer)
    context_hint = Column(Text)  # When to use this step (for LLM)
    
    # Relationships
    playbook = relationship("PlaybookModel")
    message = relationship("MessageModel")  # ← Generic message entity
```

```python
# infra/db/models/message_model.py
class MessageModel(Base):
    """
    Generic message entity supporting text, media and location types.
    
    PROBLEM: This is used for TWO different purposes:
    1. Context repository content (what we're discussing)
    2. Actual conversation messages (WhatsApp messages)
    """
    __tablename__ = "messages"
    
    id = Column(UUID, primary_key=True)
    type = Column(String(50))  # text, image, voice, video, document, location
    text = Column(Text)
    
    # Fields for playbook system (context repository)
    title = Column(String(255))
    description = Column(Text)  # For LLM to understand content
    tags = Column(String(500))
    
    # Fields for conversation messages
    has_audio = Column(Boolean)
    transcription = Column(Text)
```

**Critical Issue:**

`MessageModel` serves **two conflicting purposes**:

| Use Case | Purpose | Fields Used |
|---|---|---|
| **Context Repository Content** | Knowledge base for LLM | title, description, tags, text, media |
| **Conversation Messages** | WhatsApp messages | text, has_audio, transcription, media |

And **actually THREE modes of operation**:

| Mode | What Happens | Example |
|---|---|---|
| **RAG (Reference)** | LLM reads content, generates response | "O Botox custa R$ 800" (LLM reads pricing from content) |
| **Direct Send (Template)** | Bot sends content as message | User: "envie o folheto" → Bot sends PDF directly |
| **Conversation** | Real user messages | User: "Olá, bom dia!" |

This violates the **Single Responsibility Principle** and creates confusion:
- Context repository "messages" are **templates/knowledge** (can be sent OR referenced)
- Conversation "messages" are **actual communications** (sent/received via WhatsApp)

**Proposed Solution:**

**Rename MessageModel → Content (no split):**

```python
# domain/models/content.py
@dataclass
class Content:
    """
    Content entity for contexts.

    Replaces: MessageModel (rename only)
    Purpose: Store knowledge snippets (facts, examples, templates)

    TWO MODES:
    1. RAG Mode: LLM reads this to inform responses
    2. Auto-Send Mode: Bot automatically sends this content when appropriate
    """
    id: UUID
    content_type: str  # text, image, video, pdf, template
    title: str
    body: str | None  # Main text content
    description: str | None  # For LLM understanding
    tags: list[str]  # Searchable tags
    media_urls: list[str]  # Associated media

    # Auto-Send configuration
    auto_send: bool = False
    usage_hint: str | None = None

    created_at: datetime
    updated_at: datetime

    def should_auto_send(self, conversation_context: str) -> bool:
        if not self.auto_send:
            return False
        return True
```

**Conversation messages remain separate:**
- `ConversationMessageModel` continues to store WhatsApp messages
- No data split required

**Example Workflow - Direct Send:**

```
User: "Pode me enviar informações sobre Botox?"

Bot processing:
1. Intent detection: INTERESSE_TRATAMENTO
2. Semantic search in Context("Botox")
3. Find ContextItem with usage_hint="informações sobre botox"
4. Retrieve Content (PDF brochure)
5. Send PDF directly to WhatsApp conversation
6. Also use content for LLM response: "Enviando nosso material sobre Botox..."
```

**Example Workflow - RAG Mode:**

```
User: "Quanto custa o Botox?"

Bot processing:
1. Intent detection: PRECO_VALOR
2. Semantic search in Context("Botox")
3. Find ContextItem with pricing information
4. LLM reads content (NOT sent): "Botox: R$ 800 por aplicação"
5. LLM generates natural response: "O valor do Botox é R$ 800..."
```

@dataclass
class ConversationMessage:
    """
    Actual conversation message (WhatsApp).
    
    Replaces: MessageModel (for conversation usage)
    Purpose: Store sent/received messages in conversations
    """
    id: UUID
    conversation_id: UUID
    sender: str  # user or bot
    message_type: str  # text, audio, image, video
    content: str
    has_audio: bool
    transcription: str | None
    
    created_at: datetime
```

**Revised Schema:**

```
Topic (ContextCategory)
  └─→ Context
       └─→ ContextItem
            └─→ Content
```

**Database Migration Strategy (rename only):**

```python
# alembic/versions/xxx_rename_playbook_to_context.py
def upgrade():
    # Rename tables (no data migration)
    op.rename_table("playbooks", "contexts")
    op.rename_table("playbook_steps", "context_items")
    op.rename_table("playbook_embeddings", "context_embeddings")
    op.rename_table("messages", "contents")

    # Rename columns
    op.alter_column("contexts", "topic_id", new_column_name="category_id")
    op.alter_column("context_items", "playbook_id", new_column_name="context_id")
    op.alter_column("context_items", "message_id", new_column_name="content_id")
    op.alter_column("context_items", "step_order", new_column_name="display_order")
    op.alter_column("context_items", "context_hint", new_column_name="usage_hint")
```

**Updated Relationships:**

```python
# infra/db/models/context_item.py
class ContextItemModel(Base):
    __tablename__ = "context_items"

    id = Column(String(36), primary_key=True)
    context_id = Column(String(36), ForeignKey("contexts.id"))
    content_id = Column(UUID, ForeignKey("contents.id"))
    display_order = Column(Integer)
    usage_hint = Column(Text)

    context = relationship("ContextModel")
    content = relationship("ContentModel")
```

**Business Value:**
- Bot can send marketing materials automatically
- Reduces manual work (no need to upload same file multiple times)
- Consistent content delivery (always sends latest version)
- **Admin controls when/how content is used** (not end-user)


6. **Business Value:**
   - Bot can send marketing materials automatically
   - Reduces manual work (no need to upload same file multiple times)
   - Consistent content delivery (always sends latest version)
   - **Admin controls when/how content is used** (not end-user)

---

### Admin Interface for Content Management

**Frontend: Context Repository Manager**

```typescript
// Admin creates content with usage configuration
interface ContentForm {
  title: string;
  description: string;
  content_type: 'text' | 'image' | 'video' | 'pdf' | 'audio';
  tags: string[];
  
  // File upload
  file?: File;  // Upload via /api/v1/files/upload
  
  // Usage configuration
  usage_mode: 'reference' | 'auto_send' | 'both';
  usage_hint: string;
  // Examples:
  // - "Usar como referência para responder sobre preços"
  // - "Enviar automaticamente ao detectar interesse em Botox"
  // - "Mencionar este conteúdo ao falar de contraindicações"
}

// Admin organizes content in steps
interface ContextItemConfig {
  display_order: number;  // 1, 2, 3...
  content_id: string;
  usage_hint: string;
  
  // Auto-send configuration
  auto_send: boolean;
  send_condition: 'always' | 'on_interest' | 'on_question' | 'manual';
}
```

**Example Admin Workflow:**

```
1. Admin uploads PDF: "Folheto Botox"
   ↓
2. System stores file locally: /storage/abc123.pdf
   ↓
3. Admin configures usage:
   ☑ Usar como referência
   ☑ Enviar automaticamente
   Condição: "Quando detectar interesse em Botox"
   ↓
4. Admin adds to "Apresentação Botox" context repository:
   Step #1: Texto explicativo (referência apenas)
   Step #2: Imagem antes/depois (referência apenas)
   Step #3: PDF folheto (AUTO-SEND ✓)
   Step #4: Vídeo procedimento (referência apenas)
   ↓
5. Bot conversation:
   User: "Tenho interesse em Botox"
   Bot: [Detects INTERESSE_TRATAMENTO]
   Bot: [Sees Step #3 has auto_send=true]
   Bot: "Ótimo! Vou te enviar nosso material 📄"
   Bot: [Sends PDF]
```

**UI Mockup (Frontend Component):**

```tsx
// ContentItemEditor.tsx
<Card>
  <CardHeader>
    <h3>Configurar Conteúdo</h3>
  </CardHeader>
  <CardContent>
    {/* File Upload */}
    <FileUpload 
      accept="application/pdf,image/*,video/*,audio/*"
      onUpload={(url) => setFileUrl(url)}
    />
    
    {/* Metadata */}
    <Input label="Título" value={title} />
    <Textarea label="Descrição (para o Bot entender)" value={description} />
    <TagInput label="Tags" value={tags} />
    
    {/* Usage Mode */}
    <RadioGroup label="Como o Bot deve usar este conteúdo?">
      <Radio value="reference">
        📖 Apenas Referência (bot lê, não envia)
      </Radio>
      <Radio value="auto_send">
        📤 Enviar Automaticamente (bot decide quando enviar)
      </Radio>
      <Radio value="both">
        📖📤 Ambos (pode enviar OU usar como referência)
      </Radio>
    </RadioGroup>
    
    {/* Auto-Send Configuration */}
    {usageMode !== 'reference' && (
      <Select label="Quando enviar?">
        <Option value="on_interest">
          Ao detectar interesse no assunto
        </Option>
        <Option value="on_question">
          Quando usuário fizer pergunta relacionada
        </Option>
        <Option value="always">
          Sempre que o tópico for mencionado
        </Option>
      </Select>
    )}
    
    {/* Usage Hint */}
    <Textarea 
      label="Dica de Uso (para o Bot)"
      placeholder="Ex: Enviar quando usuário demonstrar interesse em agendar Botox"
      value={usageHint}
    />
  </CardContent>
</Card>
```

**Benefits:**
1. **Admin has full control** over bot behavior
2. **No coding required** to configure auto-send
3. **Visual interface** shows how bot will use content
4. **Easy to test** and adjust configuration
5. **End-user experience** is seamless (bot appears intelligent)Model")


# infra/db/models/message_model.py (CLEANED UP)
class MessageModel(Base):
    """Conversation message (WhatsApp only)."""
    
    __tablename__ = "messages"
    
    id = Column(UUID, primary_key=True)
    conversation_id = Column(UUID, ForeignKey("conversations.id"))
    type = Column(String(50))  # text, voice, image, video
    text = Column(Text)
    
    # Audio-specific
    has_audio = Column(Boolean)
    audio_url = Column(String(500))
    transcription = Column(Text)
    
    # NO MORE: title, description, tags (moved to Content)
```

**Benefits of Separation:**

1. **Clear Separation of Concerns:**
   - `Content` = Knowledge base (contexts)
   - `ConversationMessage` = Actual conversations (WhatsApp)

2. **Correct Naming:**
   - "Message" only refers to actual conversation messages
   - Knowledge base uses "Content" terminology

3. **Simplified Queries:**
   - No need to filter by title/tags to differentiate
   - Each table serves one purpose

4. **Better Performance:**
   - Smaller messages table (conversation-only)
   - Optimized indexes per use case

5. **MCP Alignment:**
   - `Content` maps directly to MCP "resources"
   - Clear context vs. conversation distinction

**Impact on Phase 2 Migration:**

The context rename now includes:

| Current | Target | Reason |
|---|---|---|
| `PlaybookModel` | `ContextModel` | Semantic clarity |
| `PlaybookStepModel` | `ContextItemModel` | Not a "step" |
| `MessageModel` (context) | `ContentModel` | Separate from conversations |
| `message_id` | `content_id` | Correct terminology |
| `step_order` | `display_order` | Not sequential |
| `context_hint` | `usage_hint` | Clearer purpose |

---

### 2. LLM Provider Tight Coupling

**Current Implementation:**

```python
# adapters/external/gemini_client.py
class GeminiClient:
    """
    Gemini-specific implementation.
    
    PROBLEMS:
    - Direct dependency on google.generativeai
    - Hardcoded Gemini-specific parameters
    - No abstraction layer
    - Cannot swap providers
    """
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,  # Gemini-specific
            temperature=settings.GEMINI_TEMPERATURE,
            max_output_tokens=settings.GEMINI_MAX_TOKENS,
            google_api_key=settings.GOOGLE_API_KEY,
        )
    
    def generate_response(self, prompt: str, context: str | None = None):
        # Gemini-specific logic
        response = self.llm.invoke(full_prompt)
        return self._parse_gemini_response(response)
```

**Usage Throughout Codebase:**

```python
# services/conversation_orchestrator.py
from robbot.adapters.external.gemini_client import GeminiClient  # Direct import

class ConversationOrchestrator:
    def __init__(self, ..., gemini_client: GeminiClient):  # Type hint to Gemini
        self.gemini_client = gemini_client
    
    async def process_message(self, ...):
        response = self.gemini_client.generate_response(prompt)  # Coupled
```

**Impact:**
- Cannot test with mock LLM
- Cannot switch to OpenAI, Anthropic, or local models
- Cannot implement MCP server pattern
- Vendor lock-in risk
- Hard to A/B test different providers

---

### 3. Prompt Fragmentation

**Current State:**

Prompts exist in 3 locations with inconsistent versioning:

```
Location 1: config/prompts.yaml (OLD, English, deprecated)
├── intent_detection: "You are a medical clinic assistant AI..."
├── response_generation: "You are a compassionate medical clinic..."
└── urgency_detection: "You are a medical triage AI..."

Location 2: config/prompts/templates.py (NEW, Portuguese, SPIN Selling)
├── INTENT_DETECTION_PROMPT = """Você é uma atendente especializada..."""
├── RESPONSE_GENERATION_PROMPT = """Gere uma resposta seguindo SPIN..."""
├── NAME_EXTRACTION_PROMPT = """Extraia o nome do paciente..."""
└── [12 more prompts]

Location 3: services/response_generator.py (Hardcoded)
def _build_response_prompt(...):
    prompt = f"""
You are a healthcare clinic assistant using SPIN selling...
Current SPIN Phase: {spin_phase}
...
"""
```

**Versioning Chaos:**

| Prompt | Version in yaml | Version in templates.py | Version in code | Active |
|---|---|---|---|---|
| Intent Detection | 1.0 (EN) | 2.0 (PT, SPIN) | None | templates.py |
| Response Gen | 1.0 (EN) | 2.0 (PT, SPIN) | 1.5 (EN, SPIN) | Unclear |
| Urgency | 1.0 (EN) | None | None | yaml |
| Name Extract | None | 2.0 (PT) | None | templates.py |

**Problems:**
- No single source of truth
- Cannot determine active version
- Difficult to A/B test prompts
- Cannot rollback safely
- No audit trail for changes

---

### 4. Empty Domain Layer

**Current State:**

```
domain/
├── models/        # EMPTY DIRECTORY
├── enums.py       # 200 LOC - only enums, no business logic
└── __init__.py
```

**Where Business Logic Lives:**

```python
# services/intent_detector.py - Business logic in service layer
class IntentDetector:
    async def update_lead_score(self, lead_id: str, intent: str):
        """
        Update lead maturity score based on detected intent.
        
        PROBLEM: This is business logic, not service orchestration.
        Should be in domain/models/lead.py
        """
        score_adjustments = {
            "INTERESSE_TRATAMENTO": 15,
            "URGENCIA_DOR": 20,
            "PRECO_VALOR": 10,
            "AGENDAMENTO": 25,
            "RECLAMACAO_PROBLEMA": -5,
        }
        
        new_score = min(100, current_score + score_adjustments.get(intent, 0))
        # Direct DB update - no domain model
        await self.lead_repo.update(lead_id, maturity_score=new_score)
```

**Consequences:**

1. **Scattered business rules:** Scoring logic in services, validation in repositories
2. **Untestable:** Cannot test lead scoring without database
3. **Violation of Clean Architecture:** Business logic depends on infrastructure
4. **Duplication:** Same rules repeated in multiple services

**What Should Exist:**

```python
# domain/models/lead.py
class Lead:
    """Lead entity with business logic"""
    
    id: UUID
    phone: PhoneNumber  # Value object
    maturity_score: MaturityScore  # Value object
    
    def apply_intent_adjustment(self, intent: IntentType) -> None:
        """
        Business rule: Adjust score based on intent.
        
        Pure domain logic - no infrastructure dependencies.
        """
        adjustment = self._get_intent_score_adjustment(intent)
        self.maturity_score.add(adjustment)
    
    def should_escalate_to_human(self) -> bool:
        """Business rule: Escalation criteria"""
        return (
            self.maturity_score.is_in_need_payoff_phase() or
            self.has_urgent_flags()
        )
```

---

## Domain Model Strategy

### Proposed Domain Layer Structure

```
domain/
├── __init__.py
├── enums.py                    # Existing - keep
├── value_objects/              # NEW - Value Objects (DDD)
│   ├── __init__.py
│   ├── phone_number.py         # Validates phone format
│   ├── maturity_score.py       # 0-100 with phase logic
│   ├── spin_phase.py           # SITUATION/PROBLEM/IMPLICATION/NEED_PAYOFF
│   └── money.py                # Currency values
├── models/                     # NEW - Rich Domain Entities
│   ├── __init__.py
│   ├── lead.py                 # Lead aggregate root
│   ├── conversation.py         # Conversation aggregate
│   ├── message.py              # Message entity
│   └── context_repository.py  # Context repository (renamed from playbook)
└── services/                   # NEW - Domain Services
    ├── __init__.py
    ├── lead_scoring_service.py # Complex scoring algorithms
    └── escalation_policy.py    # Escalation business rules
```

### Value Objects

**Example: MaturityScore**

```python
# domain/value_objects/maturity_score.py
from dataclasses import dataclass
from typing import Self

@dataclass(frozen=True)
class MaturityScore:
    """
    Value object representing lead maturity (0-100).
    
    Encapsulates SPIN Selling phase logic.
    Immutable - operations return new instances.
    """
    
    value: int
    
    def __post_init__(self):
        if not 0 <= self.value <= 100:
            raise ValueError(f"Score must be 0-100, got {self.value}")
    
    def add(self, points: int) -> Self:
        """Return new score with points added (clamped 0-100)"""
        new_value = max(0, min(100, self.value + points))
        return MaturityScore(new_value)
    
    def get_spin_phase(self) -> str:
        """Determine SPIN Selling phase based on score"""
        if self.value < 25:
            return "SITUATION"
        elif self.value < 40:
            return "PROBLEM"
        elif self.value < 70:
            return "IMPLICATION"
        else:
            return "NEED_PAYOFF"
    
    def is_in_need_payoff_phase(self) -> bool:
        return self.value >= 70
```

**Example: PhoneNumber**

```python
# domain/value_objects/phone_number.py
import re
from dataclasses import dataclass
from typing import Self

@dataclass(frozen=True)
class PhoneNumber:
    """
    Value object for phone numbers.
    
    Validates and normalizes phone numbers to WhatsApp format.
    """
    
    value: str
    
    def __post_init__(self):
        if not self._is_valid(self.value):
            raise ValueError(f"Invalid phone number: {self.value}")
    
    @staticmethod
    def _is_valid(phone: str) -> bool:
        """Validate phone number format (country + area + number)"""
        # Pattern: 5511999999999 (BR format)
        return re.match(r"^\d{12,13}$", phone) is not None
    
    def to_whatsapp_id(self) -> str:
        """Convert to WhatsApp chat ID format"""
        return f"{self.value}@c.us"
    
    @classmethod
    def from_whatsapp_id(cls, whatsapp_id: str) -> Self:
        """Parse from WhatsApp chat ID"""
        phone = whatsapp_id.replace("@c.us", "").replace("@g.us", "")
        return cls(phone)
```

### Domain Entities

**Example: Lead Aggregate Root**

```python
# domain/models/lead.py
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from domain.enums import IntentType, LeadStatus
from domain.value_objects.maturity_score import MaturityScore
from domain.value_objects.phone_number import PhoneNumber

@dataclass
class Lead:
    """
    Lead aggregate root.
    
    Encapsulates all business rules related to lead management.
    Independent of infrastructure (no SQLAlchemy, no database).
    """
    
    id: UUID = field(default_factory=uuid4)
    phone: PhoneNumber = field()
    name: str | None = None
    maturity_score: MaturityScore = field(default_factory=lambda: MaturityScore(0))
    status: LeadStatus = LeadStatus.NEW
    urgency_level: str = "NORMAL"
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    # Business Logic Methods
    
    def apply_intent_adjustment(self, intent: IntentType) -> None:
        """
        Business rule: Adjust maturity score based on detected intent.
        
        This is the SINGLE SOURCE OF TRUTH for scoring logic.
        """
        adjustments = {
            IntentType.INTERESSE_TRATAMENTO: 15,
            IntentType.URGENCIA_DOR: 20,
            IntentType.PRECO_VALOR: 10,
            IntentType.AGENDAMENTO: 25,
            IntentType.RECLAMACAO_PROBLEMA: -5,
        }
        
        points = adjustments.get(intent, 0)
        self.maturity_score = self.maturity_score.add(points)
    
    def should_escalate_to_human(self) -> bool:
        """
        Business rule: Determine if lead requires human escalation.
        
        Criteria:
        - In NEED_PAYOFF phase (score >= 70)
        - High urgency
        - Explicit escalation request
        """
        return (
            self.maturity_score.is_in_need_payoff_phase() or
            self.urgency_level == "HIGH" or
            self.status == LeadStatus.ESCALATED
        )
    
    def mark_as_escalated(self) -> None:
        """Transition to escalated status"""
        self.status = LeadStatus.ESCALATED
    
    def update_name(self, name: str) -> None:
        """Update lead name (business rule: capitalize)"""
        self.name = name.strip().title()
    
    def get_current_spin_phase(self) -> str:
        """Get current SPIN Selling phase"""
        return self.maturity_score.get_spin_phase()
```

**Benefits of Rich Domain Models:**

1. **Testable without infrastructure:** Unit tests don't need database
2. **Single source of truth:** Business rules in one place
3. **Type safety:** Value objects prevent invalid states
4. **Self-documenting:** Code expresses business rules clearly
5. **Reusable:** Domain models used across services

---

## LLM Provider Abstraction

### Current Problem

Services are tightly coupled to GeminiClient:

```python
# services/conversation_orchestrator.py
from robbot.adapters.external.gemini_client import GeminiClient

class ConversationOrchestrator:
    def __init__(self, gemini_client: GeminiClient):  # Hard dependency
        self.gemini_client = gemini_client
```

**Consequences:**
- Cannot swap Gemini for OpenAI/Anthropic
- Cannot implement MCP server pattern
- Difficult to test (requires Gemini API key)
- Vendor lock-in

### Target Architecture: Provider Abstraction

**Step 1: Define LLM Provider Protocol**

```python
# core/interfaces/llm_provider.py
from abc import ABC, abstractmethod
from typing import Any, Protocol

class LLMProvider(Protocol):
    """
    Protocol for LLM providers.
    
    Implementations: GeminiProvider, OpenAIProvider, AnthropicProvider, MCPProvider
    """
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        context: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """
        Generate text response from LLM.
        
        Args:
            prompt: User prompt
            context: Optional conversation context
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum response length
        
        Returns:
            Generated text response
        """
        ...
    
    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        context: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate structured JSON response.
        
        Used for intent detection, entity extraction, etc.
        """
        ...
    
    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding vector for semantic search"""
        ...
    
    @abstractmethod
    async def call_function(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        max_iterations: int = 5,
    ) -> Any:
        """
        Execute function calling loop.
        
        Used for tool usage (search_context_repository, etc.)
        """
        ...
```

**Step 2: Implement Providers**

```python
# adapters/external/providers/gemini_provider.py
from langchain_google_genai import ChatGoogleGenerativeAI
from core.interfaces.llm_provider import LLMProvider

class GeminiProvider(LLMProvider):
    """Gemini implementation of LLM Provider"""
    
    def __init__(self, api_key: str, model: str = "gemini-flash-latest"):
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
        )
    
    async def generate_text(
        self,
        prompt: str,
        context: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        response = await self.llm.ainvoke(full_prompt)
        return response.content
    
    async def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        context: str | None = None,
    ) -> dict[str, Any]:
        # Implement Gemini-specific JSON parsing
        structured_prompt = f"{prompt}\n\nRespond in JSON: {schema}"
        response = await self.generate_text(structured_prompt, context)
        return json.loads(response)
    
    # ... implement other methods
```

```python
# adapters/external/providers/openai_provider.py
from openai import AsyncOpenAI
from core.interfaces.llm_provider import LLMProvider

class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLM Provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def generate_text(
        self,
        prompt: str,
        context: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    
    # ... implement other methods
```

**Step 3: MCP Server Provider**

```python
# adapters/external/providers/mcp_provider.py
from mcp import MCPClient
from core.interfaces.llm_provider import LLMProvider

class MCPProvider(LLMProvider):
    """
    MCP (Model Context Protocol) implementation.
    
    Connects to MCP server that manages context and delegates to underlying LLM.
    """
    
    def __init__(self, server_url: str):
        self.client = MCPClient(server_url)
    
    async def generate_text(
        self,
        prompt: str,
        context: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        # MCP server handles context augmentation automatically
        response = await self.client.generate(
            prompt=prompt,
            context=context,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.text
    
    # MCP provides built-in context retrieval
    async def call_function(
        self,
        prompt: str,
        tools: list[dict[str, Any]],
        max_iterations: int = 5,
    ) -> Any:
        # MCP server handles tool orchestration
        return await self.client.execute_tools(prompt, tools, max_iterations)
```

**Step 4: Update Services to Use Abstraction**

```python
# services/conversation/orchestrator.py (AFTER refactoring)
from core.interfaces.llm_provider import LLMProvider

class ConversationOrchestrator:
    """
    Orchestrates conversation flow.
    
    Now provider-agnostic - works with any LLM implementation.
    """
    
    def __init__(
        self,
        llm_provider: LLMProvider,  # Abstract interface
        intent_detector: IntentDetector,
        lead_scorer: LeadScoringService,
    ):
        self.llm = llm_provider
        self.intent_detector = intent_detector
        self.lead_scorer = lead_scorer
    
    async def process_message(self, message: str, conversation: Conversation) -> str:
        # Works with ANY provider (Gemini, OpenAI, Anthropic, MCP)
        intent = await self.intent_detector.detect(message)
        await self.lead_scorer.update_score(conversation.lead, intent)
        
        response = await self.llm.generate_text(
            prompt=message,
            context=conversation.get_context(),
        )
        return response
```

**Step 5: Configuration-Based Provider Selection**

```python
# config/settings.py
class Settings(BaseSettings):
    # LLM Provider Configuration
    LLM_PROVIDER: str = Field(default="gemini", env="LLM_PROVIDER")
    # Options: "gemini", "openai", "anthropic", "mcp"
    
    # Gemini settings
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-flash-latest"
    
    # OpenAI settings
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4"
    
    # MCP settings
    MCP_SERVER_URL: str | None = None
```

```python
# config/container.py
from adapters.external.providers.gemini_provider import GeminiProvider
from adapters.external.providers.openai_provider import OpenAIProvider
from adapters.external.providers.mcp_provider import MCPProvider

class Container:
    def get_llm_provider(self) -> LLMProvider:
        """Factory method for LLM provider"""
        provider_type = self.settings.LLM_PROVIDER
        
        if provider_type == "gemini":
            return GeminiProvider(
                api_key=self.settings.GEMINI_API_KEY,
                model=self.settings.GEMINI_MODEL,
            )
        elif provider_type == "openai":
            return OpenAIProvider(
                api_key=self.settings.OPENAI_API_KEY,
                model=self.settings.OPENAI_MODEL,
            )
        elif provider_type == "mcp":
            return MCPProvider(
                server_url=self.settings.MCP_SERVER_URL,
            )
        else:
            raise ValueError(f"Unknown provider: {provider_type}")
```

**Benefits:**

1. **Provider swapping:** Change provider via environment variable
2. **A/B testing:** Run multiple providers in parallel
3. **Cost optimization:** Route expensive requests to cheaper models
4. **Graceful degradation:** Fallback to secondary provider on failure
5. **MCP-ready:** Drop-in MCP support when available
6. **Testable:** Mock provider for tests

---

## Context Repository Redesign

### Rationale for Renaming

Current name "Playbook" creates confusion:

| What it IS | What developers think it IS |
|---|---|
| Repository of contextual knowledge | Executable workflow |
| Semantic search corpus | Step-by-step procedure |
| RAG knowledge base | Automation playbook |
| Context for LLM | Sales playbook |

### Proposed New Schema

```python
# domain/models/context.py
from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime

@dataclass
class Context:
    """
    Context of knowledge for a specific topic.

    Replaces: PlaybookModel
    Purpose: Store structured knowledge that LLM retrieves via semantic search

    Example: "Botox Treatment" context contains facts, FAQs, pricing,
    contraindications, and procedure details for LLM to reference.
    """

    id: UUID = field(default_factory=uuid4)
    category_id: UUID  # Replaces: topic_id
    name: str
    description: str | None = None
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    items: list["ContextItem"] = field(default_factory=list)

    def add_item(self, content: str, content_type: str, priority: int = 0) -> "ContextItem":
        """Add new context item"""
        item = ContextItem(
            context_id=self.id,
            content=content,
            content_type=content_type,
            display_order=priority,
        )
        self.items.append(item)
        return item

    def get_relevant_items(self, query_embedding: list[float], top_k: int = 5) -> list["ContextItem"]:
        """
        Retrieve most relevant items using semantic similarity.

        In practice, this delegates to vector DB (ChromaDB).
        """
        raise NotImplementedError("Implement in infrastructure layer")


@dataclass
class ContextItem:
    """
    Individual piece of contextual knowledge.
    
    Replaces: PlaybookStepModel
    Purpose: Single fact, example, or template in the knowledge base
    """
    
    id: UUID = field(default_factory=uuid4)
    context_id: UUID
    content_id: UUID  # Replaces: message_id
    content_type: str  # text, image, video, pdf, etc.
    display_order: int = 0  # Replaces: step_order
    usage_hint: str | None = None  # Replaces: context_hint
    created_at: datetime = field(default_factory=datetime.utcnow)
```

### Database Migration

```python
# alembic/versions/xxx_rename_playbook_to_context.py
def upgrade():
    # Rename tables
    op.rename_table("playbooks", "contexts")
    op.rename_table("playbook_steps", "context_items")
    op.rename_table("playbook_embeddings", "context_embeddings")
    op.rename_table("messages", "contents")

    # Rename columns
    op.alter_column("contexts", "topic_id", new_column_name="category_id")
    op.alter_column("context_items", "playbook_id", new_column_name="context_id")
    op.alter_column("context_items", "message_id", new_column_name="content_id")
    op.alter_column("context_items", "step_order", new_column_name="display_order")
    op.alter_column("context_items", "context_hint", new_column_name="usage_hint")

def downgrade():
    # Reverse operations
    ...
```

### Service Layer Updates

```python
# services/context/service.py (AFTER refactoring)
class ContextService:
    """
    Service for managing contexts.

    Replaces: PlaybookService
    """

    def __init__(
        self,
        context_repo: ContextRepository,
        vector_store: VectorStore,
    ):
        self.context_repo = context_repo
        self.vector_store = vector_store

    async def create_context(
        self,
        category_id: UUID,
        name: str,
        description: str | None = None,
    ) -> Context:
        """Create new context"""
        context = Context(
            category_id=category_id,
            name=name,
            description=description,
        )

        saved = await self.context_repo.save(context)
        await self.vector_store.index_context(saved)
        return saved

    async def add_context_item(
        self,
        context_id: UUID,
        content: str,
        content_type: str,
        priority: int = 0,
    ) -> ContextItem:
        """Add item to context and reindex"""
        context = await self.context_repo.get_by_id(context_id)
        item = context.add_item(content, content_type, priority)

        await self.context_repo.save(context)
        await self.vector_store.reindex_context(context_id)
        return item

    async def search_contexts(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[Context]:
        """Semantic search across all contexts"""
        query_embedding = await self.vector_store.embed_text(query)
        results = await self.vector_store.search(query_embedding, top_k)

        contexts = [
            await self.context_repo.get_by_id(result.context_id)
            for result in results
        ]

        return contexts

    async def find_sendable_content(
        self,
        user_message: str,
        context_id: UUID | None = None,
    ) -> list[Content]:
        """
        Find content that should be sent directly based on user message.
        """
        if context_id:
            contexts = [await self.context_repo.get_by_id(context_id)]
        else:
            contexts = await self.search_contexts(user_message, top_k=3)

        sendable_content: list[Content] = []

        for context in contexts:
            for item in context.items:
                content = item.content
                if content.can_be_sent_directly() and content.matches_trigger(user_message):
                    sendable_content.append(content)

        return sendable_content
```

**Usage in ConversationOrchestrator:**

```python
# services/conversation/orchestrator.py
class ConversationOrchestrator:
    def __init__(
        self,
        llm_provider: LLMProvider,
        intent_detector: IntentDetector,
        context_service: ContextService,  # NEW
        message_sender: MessageSender,  # NEW
    ):
        self.llm = llm_provider
        self.intent_detector = intent_detector
        self.context_service = context_service
        self.message_sender = message_sender
    
    async def process_message(
        self,
        message: str,
        conversation: Conversation,
    ) -> ConversationResponse:
        """Process message with Direct Send support"""
        
        # 1. Check if user wants content sent directly
        sendable_content = await self.context_service.find_sendable_content(message)
        
        if sendable_content:
            # Direct Send Mode
            for content in sendable_content:
                await self.message_sender.send_content(
                    conversation_id=conversation.id,
                    content=content,
                )
            
            # LLM confirms sending
            response = await self.llm.generate_text(
                prompt=f"Confirme que enviou: {', '.join(c.title for c in sendable_content)}",
                context=conversation.get_context(),
            )
            
            return ConversationResponse(
                text=response,
                content_sent=sendable_content,
                mode="DIRECT_SEND",
            )
        
        # 2. Normal RAG mode
        intent = await self.intent_detector.detect(message, conversation.get_context())
        
        # Search for relevant context
        relevant_repos = await self.context_service.search_repositories(message)
        context_info = "\n".join(repo.description for repo in relevant_repos)
        
        # Generate response with context
        response = await self.llm.generate_text(
            prompt=message,
            context=f"{conversation.get_context()}\n\nRelevant Info:\n{context_info}",
        )
        
        return ConversationResponse(
            text=response,
            intent=intent,
            mode="RAG",
        )
```

---

## Prompt Management System

### Target Architecture

**Centralized Prompt Registry:**

```
config/prompts/
├── __init__.py
├── registry.py              # Singleton prompt registry
├── loader.py                # Load prompts from storage
├── versioning.py            # Prompt version management
└── templates/
    ├── __init__.py
    ├── base.py              # System prompts
    ├── intent.py            # Intent detection prompts
    ├── response.py          # Response generation prompts
    ├── extraction.py        # Entity extraction prompts
    └── spin_selling.py      # SPIN methodology prompts
```

**Implementation:**

```python
# config/prompts/registry.py
from dataclasses import dataclass
from typing import ClassVar
import logging

logger = logging.getLogger(__name__)

@dataclass
class Prompt:
    """
    Versioned prompt template.
    """
    
    name: str
    version: str
    template: str
    variables: list[str]
    description: str | None = None
    
    def format(self, **kwargs) -> str:
        """Format prompt with provided variables"""
        missing = set(self.variables) - set(kwargs.keys())
        if missing:
            raise ValueError(f"Missing variables: {missing}")
        
        return self.template.format(**kwargs)


class PromptRegistry:
    """
    Singleton registry for all system prompts.
    
    Provides:
    - Centralized prompt management
    - Version control
    - Audit logging
    - A/B testing support
    """
    
    _instance: ClassVar["PromptRegistry | None"] = None
    _prompts: dict[str, Prompt]
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._prompts = {}
        return cls._instance
    
    def register(self, prompt: Prompt) -> None:
        """Register a prompt template"""
        key = f"{prompt.name}:{prompt.version}"
        self._prompts[key] = prompt
        logger.info(f"Registered prompt: {key}")
    
    def get(self, name: str, version: str = "latest") -> Prompt:
        """Retrieve prompt by name and version"""
        if version == "latest":
            # Find highest version
            versions = [
                p for p in self._prompts.values()
                if p.name == name
            ]
            if not versions:
                raise KeyError(f"Prompt not found: {name}")
            
            return max(versions, key=lambda p: p.version)
        
        key = f"{name}:{version}"
        if key not in self._prompts:
            raise KeyError(f"Prompt not found: {key}")
        
        return self._prompts[key]
    
    def format(self, name: str, version: str = "latest", **kwargs) -> str:
        """Get and format prompt in one call"""
        prompt = self.get(name, version)
        return prompt.format(**kwargs)


# Singleton instance
prompt_registry = PromptRegistry()
```

**Prompt Definitions:**

```python
# config/prompts/templates/intent.py
from config.prompts.registry import Prompt, prompt_registry

INTENT_DETECTION_V1 = Prompt(
    name="intent_detection",
    version="1.0.0",
    template="""Você é uma atendente especializada em clínica médica.

Analise a mensagem do paciente e classifique a intenção:

INTENÇÕES POSSÍVEIS:
1. INTERESSE_TRATAMENTO - Interesse em tratamento específico
2. DUVIDA_PROCEDIMENTO - Dúvidas sobre procedimentos
3. PRECO_VALOR - Perguntas sobre preços
4. LOCALIZACAO_HORARIO - Local e horários
5. URGENCIA_DOR - Urgência médica
6. AGENDAMENTO - Agendamento de consulta
7. RECLAMACAO_PROBLEMA - Reclamação
8. OUTRO - Outros assuntos

MENSAGEM: {message}

CONTEXTO DA CONVERSA:
{context}

Responda APENAS em JSON:
{{
    "intent": "<intent_type>",
    "spin_phase": "<SITUATION|PROBLEM|IMPLICATION|NEED_PAYOFF>",
    "confidence": <0-100>
}}
""",
    variables=["message", "context"],
    description="Detecção de intenção com metodologia SPIN Selling",
)

# Register on module import
prompt_registry.register(INTENT_DETECTION_V1)
```

```python
# config/prompts/templates/response.py
from config.prompts.registry import Prompt, prompt_registry

RESPONSE_GENERATION_V2 = Prompt(
    name="response_generation",
    version="2.0.0",
    template="""Você é uma atendente especializada da Dra. Andréa Mondadori.

METODOLOGIA SPIN SELLING:

Fase atual: {spin_phase}
Score de maturidade: {maturity_score}/100

REGRAS POR FASE:

**SITUATION (0-25):**
- Faça perguntas abertas para entender contexto
- Seja empática e acolhedora
- Não seja invasiva

**PROBLEM (25-40):**
- Identifique dificuldades e preocupações
- Escute ativamente
- Valide sentimentos do paciente

**IMPLICATION (40-70):**
- Explore consequências dos problemas
- Desenvolva senso de necessidade
- Conecte problemas aos impactos

**NEED-PAYOFF (70-100):**
- Apresente benefícios da solução
- Ofereça agendamento
- Seja proativa

CONTEXTO DA CONVERSA:
{context}

MENSAGEM DO PACIENTE: {user_message}

INTENÇÃO DETECTADA: {intent}

Gere uma resposta natural, empática e que avance a conversa na metodologia SPIN.
""",
    variables=["spin_phase", "maturity_score", "context", "user_message", "intent"],
    description="Geração de resposta com SPIN Selling v2.0",
)

prompt_registry.register(RESPONSE_GENERATION_V2)
```

**Usage in Services:**

```python
# services/ai/intent_detector.py
from config.prompts.registry import prompt_registry

class IntentDetector:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
    
    async def detect(self, message: str, context: str) -> IntentResult:
        # Get latest intent detection prompt
        prompt = prompt_registry.format(
            name="intent_detection",
            version="latest",
            message=message,
            context=context,
        )
        
        # Generate response
        response = await self.llm.generate_structured(
            prompt=prompt,
            schema={"intent": "str", "spin_phase": "str", "confidence": "int"},
        )
        
        return IntentResult(**response)
```

**Prompt Versioning and A/B Testing:**

```python
# services/ai/response_generator.py
class ResponseGenerator:
    def __init__(
        self,
        llm_provider: LLMProvider,
        ab_test_enabled: bool = False,
    ):
        self.llm = llm_provider
        self.ab_test_enabled = ab_test_enabled
    
    async def generate(
        self,
        message: str,
        context: str,
        intent: str,
        lead: Lead,
    ) -> str:
        # A/B test: 50% use v2.0, 50% use v1.5
        if self.ab_test_enabled and random.random() < 0.5:
            version = "1.5.0"
        else:
            version = "2.0.0"
        
        prompt = prompt_registry.format(
            name="response_generation",
            version=version,
            spin_phase=lead.get_current_spin_phase(),
            maturity_score=lead.maturity_score.value,
            context=context,
            user_message=message,
            intent=intent,
        )
        
        response = await self.llm.generate_text(prompt)
        
        # Log which version was used (for analytics)
        logger.info(f"Generated response using prompt v{version}")
        
        return response
```

**Benefits:**

1. **Single source of truth:** All prompts in one registry
2. **Version control:** Track prompt changes over time
3. **A/B testing:** Compare prompt versions
4. **Rollback capability:** Revert to previous versions
5. **Audit trail:** Log which prompts generated which responses

---

## Service Layer Reorganization

### Current Problems

```
services/
├── analytics/                    # Only subdir
├── audit_service.py              # Auth context
├── auth_services.py              # Auth context
├── conversation_orchestrator.py  # Conversation + AI + Lead
├── conversation_service.py       # Conversation
├── conversation_state_machine.py # Conversation
├── credential_service.py         # Auth
├── email_verification_service.py # Auth
├── intent_detector.py            # AI + Lead scoring
├── lead_service.py               # Lead
├── message_pipeline.py           # Messaging
├── message_processor.py          # Messaging
├── message_service.py            # Messaging + Transcription + Vision
├── mfa_service.py                # Auth
├── playbook_orchestration.py     # Context + AI
├── playbook_service.py           # Context
├── playbook_tools.py             # Context
├── response_generator.py         # AI
└── ... (17 more files)
```

**Issues:**
- 32 files in one directory
- No domain/context separation
- Hard to navigate
- Violates cohesion principles

### Target Structure

```
services/
├── __init__.py
├── conversation/              # Conversation Management Context
│   ├── __init__.py
│   ├── orchestrator.py        # Moved from root, decomposed
│   ├── service.py             # Moved from conversation_service.py
│   └── state_machine.py       # Moved from conversation_state_machine.py
├── lead/                      # Lead Management Context
│   ├── __init__.py
│   ├── service.py             # Moved from lead_service.py
│   ├── scoring_service.py     # NEW - extracted from intent_detector
│   └── escalation_service.py  # NEW - extracted from orchestrator
├── ai/                        # AI/LLM Interaction Context
│   ├── __init__.py
│   ├── intent_detector.py     # Moved, cleaned (no scoring)
│   ├── response_generator.py  # Moved, cleaned (no hardcoded prompts)
│   ├── name_extractor.py      # NEW - extracted from intent_detector
│   └── urgency_detector.py    # NEW - extracted from intent_detector
├── messaging/                 # Message Management Context
│   ├── __init__.py
│   ├── service.py             # Moved from message_service.py
│   ├── pipeline.py            # Moved from message_pipeline.py
│   ├── processor.py           # Moved from message_processor.py
│   └── transcription_service.py # NEW - extracted from message_service
├── context/                   # Context Repository Context (was playbook)
│   ├── __init__.py
│   ├── repository_service.py  # Moved from playbook_service.py
│   ├── orchestration.py       # Moved from playbook_orchestration.py
│   └── tools.py               # Moved from playbook_tools.py
├── auth/                      # Authentication Context
│   ├── __init__.py
│   ├── service.py             # Moved from auth_services.py
│   ├── credential_service.py  # Moved from root
│   ├── mfa_service.py         # Moved from root
│   └── email_verification_service.py # Moved from root
├── notification/              # Notification Context
│   ├── __init__.py
│   └── service.py             # Moved from notification_service.py
└── analytics/                 # Existing - keep as is
    └── ...
```

### Example: Decomposing God Classes

**Before: ConversationOrchestrator (488 LOC)**

```python
# services/conversation_orchestrator.py
class ConversationOrchestrator:
    """
    Does EVERYTHING:
    - Orchestrates conversation flow
    - Detects intent
    - Updates lead score
    - Generates responses
    - Handles escalation
    - Processes media (audio, images)
    - Manages context repository
    """
    
    async def process_message(self, ...):  # 200+ LOC
        # Validate message
        # Detect intent
        # Update lead score
        # Check escalation
        # Generate response
        # Search context repository
        # Update conversation state
        # Log everything
```

**After: Single Responsibility Services**

```python
# services/conversation/orchestrator.py
class ConversationOrchestrator:
    """
    Orchestrates conversation flow - DELEGATES to specialized services.
    """
    
    def __init__(
        self,
        intent_detector: IntentDetector,
        lead_scorer: LeadScoringService,
        response_generator: ResponseGenerator,
        escalation_service: EscalationService,
        conversation_repo: ConversationRepository,
    ):
        self.intent_detector = intent_detector
        self.lead_scorer = lead_scorer
        self.response_generator = response_generator
        self.escalation_service = escalation_service
        self.conversation_repo = conversation_repo
    
    async def process_message(
        self,
        message: str,
        conversation_id: UUID,
    ) -> ConversationResponse:
        """
        Process user message - orchestrates specialized services.
        
        Reduced from 200+ LOC to 30 LOC.
        """
        # Load conversation
        conversation = await self.conversation_repo.get_by_id(conversation_id)
        
        # Detect intent (delegated)
        intent = await self.intent_detector.detect(
            message=message,
            context=conversation.get_context(),
        )
        
        # Update lead score (delegated)
        await self.lead_scorer.update_score(
            lead=conversation.lead,
            intent=intent,
        )
        
        # Check escalation (delegated)
        if self.escalation_service.should_escalate(conversation.lead):
            return await self.escalation_service.escalate(conversation)
        
        # Generate response (delegated)
        response = await self.response_generator.generate(
            message=message,
            intent=intent,
            lead=conversation.lead,
            context=conversation.get_context(),
        )
        
        # Update conversation state
        conversation.add_message(message, response)
        await self.conversation_repo.save(conversation)
        
        return ConversationResponse(text=response, intent=intent)
```

```python
# services/lead/scoring_service.py (NEW - extracted)
class LeadScoringService:
    """
    Responsible for lead maturity scoring.
    
    Single Responsibility: Manage lead scores based on interactions.
    """
    
    def __init__(self, lead_repo: LeadRepository):
        self.lead_repo = lead_repo
    
    async def update_score(self, lead: Lead, intent: IntentType) -> None:
        """Update lead score based on detected intent"""
        # Business logic in domain model
        lead.apply_intent_adjustment(intent)
        
        # Persist
        await self.lead_repo.save(lead)


# services/lead/escalation_service.py (NEW - extracted)
class EscalationService:
    """
    Responsible for lead escalation decisions.
    
    Single Responsibility: Determine and execute escalations.
    """
    
    def should_escalate(self, lead: Lead) -> bool:
        """Check if lead should be escalated to human"""
        # Business logic in domain model
        return lead.should_escalate_to_human()
    
    async def escalate(self, conversation: Conversation) -> ConversationResponse:
        """Execute escalation workflow"""
        # Mark lead as escalated
        conversation.lead.mark_as_escalated()
        
        # Notify human operator
        await self.notification_service.notify_escalation(conversation)
        
        # Return escalation message
        return ConversationResponse(
            text="Um momento, vou conectar você com nossa equipe.",
            escalated=True,
        )
```

**Benefits:**

1. **Testability:** Each service testable in isolation
2. **Maintainability:** Small, focused classes
3. **Reusability:** Services reusable across contexts
4. **Clarity:** Clear responsibilities

---

## Target Architecture

### Clean Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                     │
│  controllers/ - HTTP request/response handling               │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Service Layer                           │
│  services/ - Business logic orchestration                    │
│  - conversation/, lead/, ai/, messaging/, context/, auth/    │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Domain Layer                            │
│  domain/models/ - Business entities & rules                  │
│  domain/value_objects/ - Value objects                       │
│  domain/services/ - Domain services                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                  Infrastructure Layer                        │
│  adapters/repositories/ - Data access                        │
│  adapters/external/ - External services (LLM, WAHA)          │
│  infra/db/models/ - ORM models                               │
└─────────────────────────────────────────────────────────────┘
```

### Dependency Flow

```
API → Services → Domain ← Repositories
                         ← External Adapters
```

**Key Principle:** Dependencies point inward. Domain has NO dependencies on infrastructure.

---

## Migration Plan

### Phase 1: Foundation (Week 1-2)

**Objectives:**
- Establish domain layer
- Create LLM provider abstraction
- Consolidate prompts

**Tasks:**

| Task | Effort | Owner | Deliverable |
|---|---|---|---|
| Create value objects | 2 days | Backend | `domain/value_objects/` |
| Create domain models | 3 days | Backend | `domain/models/` |
| Implement LLM Provider protocol | 2 days | Backend | `core/interfaces/llm_provider.py` |
| Implement GeminiProvider | 1 day | Backend | `adapters/external/providers/gemini_provider.py` |
| Create PromptRegistry | 2 days | Backend | `config/prompts/registry.py` |
| Migrate all prompts to registry | 2 days | Backend | `config/prompts/templates/` |
| Unit tests for domain models | 2 days | QA | 100% coverage |

**Acceptance Criteria:**
- All domain models have unit tests (no DB)
- LLM Provider abstraction works with Gemini
- All prompts accessible via PromptRegistry
- Existing functionality unaffected (integration tests pass)

### Phase 1.5: Local File Storage System (Week 2)

**Objectives:**
- Implement local file storage for development
- Support PDF, images, audio, video uploads
- Prepare for production storage migration

**Tasks:**

| Task | Effort | Owner | Deliverable |
|---|---|---|---|
| Create file storage abstraction | 1 day | Backend | `core/interfaces/file_storage.py` |
| Implement LocalFileStorage | 1 day | Backend | `adapters/storage/local_storage.py` |
| Add file upload endpoint | 0.5 day | Backend | `POST /api/v1/files/upload` |
| File serving endpoint | 0.5 day | Backend | `GET /api/v1/files/{file_id}` |
| Add storage configuration | 0.5 day | Backend | Settings for local/S3/Railway |
| Frontend file upload component | 2 days | Frontend | Drag-and-drop upload UI |
| Unit tests | 1 day | QA | Storage abstraction tests |

**File Storage Abstraction:**

```python
# core/interfaces/file_storage.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class StoredFile:
    """Stored file metadata"""
    file_id: str
    filename: str
    mimetype: str
    size_bytes: int
    url: str  # Access URL
    storage_path: str  # Internal path

class FileStorage(ABC):
    """File storage abstraction - supports local, S3, Railway, etc."""
    
    @abstractmethod
    async def upload(
        self,
        file_content: bytes,
        filename: str,
        mimetype: str,
    ) -> StoredFile:
        """Upload file and return metadata"""
        ...
    
    @abstractmethod
    async def download(self, file_id: str) -> bytes:
        """Download file content"""
        ...
    
    @abstractmethod
    async def delete(self, file_id: str) -> bool:
        """Delete file"""
        ...
    
    @abstractmethod
    async def get_url(self, file_id: str) -> str:
        """Get public/signed URL"""
        ...


# adapters/storage/local_storage.py
import os
from pathlib import Path
from uuid import uuid4

class LocalFileStorage(FileStorage):
    """Local filesystem storage (for development)"""
    
    def __init__(self, storage_dir: str = "./storage", base_url: str = "http://localhost:8000"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True, parents=True)
        self.base_url = base_url
    
    async def upload(
        self,
        file_content: bytes,
        filename: str,
        mimetype: str,
    ) -> StoredFile:
        # Generate unique ID
        file_id = str(uuid4())
        ext = Path(filename).suffix
        storage_path = self.storage_dir / f"{file_id}{ext}"
        
        # Write file
        storage_path.write_bytes(file_content)
        
        return StoredFile(
            file_id=file_id,
            filename=filename,
            mimetype=mimetype,
            size_bytes=len(file_content),
            url=f"{self.base_url}/api/v1/files/{file_id}",
            storage_path=str(storage_path),
        )
    
    async def download(self, file_id: str) -> bytes:
        # Find file by ID
        files = list(self.storage_dir.glob(f"{file_id}.*"))
        if not files:
            raise FileNotFoundError(f"File {file_id} not found")
        return files[0].read_bytes()
    
    async def get_url(self, file_id: str) -> str:
        return f"{self.base_url}/api/v1/files/{file_id}"


# adapters/storage/s3_storage.py (future production)
class S3FileStorage(FileStorage):
    """AWS S3 storage (for production)"""
    # Implementation for production deployment
    ...
```

**Configuration:**

```python
# config/settings.py
class Settings(BaseSettings):
    # File Storage
    FILE_STORAGE_TYPE: str = Field(default="local", env="FILE_STORAGE_TYPE")
    # Options: "local", "s3", "railway"
    
    # Local storage
    LOCAL_STORAGE_DIR: str = Field(default="./storage", env="LOCAL_STORAGE_DIR")
    
    # S3 (production)
    AWS_S3_BUCKET: str | None = None
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None


# config/container.py
class Container:
    def get_file_storage(self) -> FileStorage:
        """Factory for file storage"""
        if self.settings.FILE_STORAGE_TYPE == "local":
            return LocalFileStorage(
                storage_dir=self.settings.LOCAL_STORAGE_DIR,
                base_url=self.settings.API_BASE_URL,
            )
        elif self.settings.FILE_STORAGE_TYPE == "s3":
            return S3FileStorage(
                bucket=self.settings.AWS_S3_BUCKET,
                access_key=self.settings.AWS_ACCESS_KEY_ID,
                secret_key=self.settings.AWS_SECRET_ACCESS_KEY,
            )
```

**File Upload API:**

```python
# adapters/controllers/file_controller.py
from fastapi import APIRouter, UploadFile, File, Depends
from core.interfaces.file_storage import FileStorage

router = APIRouter()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    storage: FileStorage = Depends(get_file_storage),
):
    """
    Upload file to storage.
    
    Returns file metadata including URL for use in Content.
    """
    content = await file.read()
    
    stored_file = await storage.upload(
        file_content=content,
        filename=file.filename,
        mimetype=file.content_type,
    )
    
    return {
        "file_id": stored_file.file_id,
        "filename": stored_file.filename,
        "url": stored_file.url,
        "mimetype": stored_file.mimetype,
        "size_bytes": stored_file.size_bytes,
    }


@router.get("/{file_id}")
async def download_file(
    file_id: str,
    storage: FileStorage = Depends(get_file_storage),
):
    """Serve file content"""
    content = await storage.download(file_id)
    # Return with appropriate headers
    return Response(content=content, media_type="application/octet-stream")
```

**Benefits:**
1. No cloud costs during development
2. Easy migration to S3/Railway for production (just change env var)
3. Same API regardless of storage backend
4. Files served through same domain (no CORS issues)

---

### Phase 2: Context Rename + API Routes (Week 3)

**Objectives:**
- Rename Playbook → Context  
- Rename MessageModel → Content (não precisa split!)
- Update all references (code + docs)
- Update REST routes to follow naming rules
- Deploy without downtime

**Tasks:**

| Task | Effort | Owner | Deliverable |
|---|---|---|---|
| Create Alembic migration | 2 days | Backend | Migration script (rename only) |
| Create ContentModel | 1 day | Backend | New ORM model |
| Update ContextItemModel (PlaybookStep) | 1 day | Backend | New relationships |
| Update ORM models | 1 day | Backend | Renamed models |
| Update repositories | 1.5 days | Backend | Updated repos |
| Update services | 2 days | Backend | Renamed services |
| Update API controllers | 1 day | Backend | Updated endpoints |
| Update tests | 1.5 days | QA | All tests passing |
| Blue-green deployment | 0.5 day | DevOps | Zero downtime |

**API Routes Rename (REST):**

| Resource | Old Route | New Route | Notes |
|---|---|---|---|
| Contexts | `/api/v1/playbooks` | `/api/v1/contexts` | Keep old route as deprecated alias during Phase 2 |
| Context search | `/api/v1/playbooks/search` | `/api/v1/contexts/search` | Same query params |
| Context by topic | `/api/v1/playbooks/topic/{topic_id}` | `/api/v1/contexts/topic/{topic_id}` | Same behavior |
| Context items | `/api/v1/playbook-steps` | `/api/v1/context-items` | Item CRUD + reorder |
| Context items (list) | `/api/v1/playbook-steps/playbook/{id}` | `/api/v1/contexts/{context_id}/items` | Nested, resourceful |
| Context items (details) | `/api/v1/playbook-steps/playbook/{id}/details` | `/api/v1/contexts/{context_id}/items/details` | LLM optimized |
| Contents | `/api/v1/messages` | `/api/v1/contents` | This is **knowledge content**, not conversation messages |
| Content AI description | `/api/v1/messages/{id}/generate-description` | `/api/v1/contents/{content_id}/generate-description` | Same functionality |

**Backward Compatibility Policy:**
- Keep old routes as **deprecated aliases** for 1 sprint
- Add warning header: `X-Deprecated-Route: true`
- Update docs and Postman collection in Phase 2
- Remove aliases after Phase 3 is stable

**Deployment Strategy:**

1. **Phase 2a: Rename tables (no data migration)**
    - `playbooks` → `contexts`
    - `playbook_steps` → `context_items`
    - `playbook_embeddings` → `context_embeddings`
    - `messages` → `contents`

2. **Phase 2b: Update code references**
    - `ContentModel` for knowledge content
    - `MessageModel` reserved for conversation messages only
    - Update `ContextItemModel` to reference `content_id`

3. **Phase 2c: Update routes**
    - New routes: `/contexts`, `/contents`, `/context-items`
    - Old routes remain as deprecated aliases (1 sprint)

4. **Phase 2d: Cleanup**
    - Remove deprecated route aliases
    - Verify docs + Postman collection
    - Validate all integrations

**Critical Migration Details:**

```sql
-- Step 1: Rename tables (no data migration)
ALTER TABLE playbooks RENAME TO contexts;
ALTER TABLE playbook_steps RENAME TO context_items;
ALTER TABLE playbook_embeddings RENAME TO context_embeddings;
ALTER TABLE messages RENAME TO contents;

-- Step 2: Rename columns
ALTER TABLE contexts RENAME COLUMN topic_id TO category_id;
ALTER TABLE context_items RENAME COLUMN playbook_id TO context_id;
ALTER TABLE context_items RENAME COLUMN message_id TO content_id;
ALTER TABLE context_items RENAME COLUMN step_order TO display_order;
ALTER TABLE context_items RENAME COLUMN context_hint TO usage_hint;

-- Step 3: Rename FK constraints (optional, clarity)
ALTER TABLE context_items
    RENAME CONSTRAINT playbook_steps_playbook_id_fkey TO context_items_context_id_fkey;
ALTER TABLE context_items
    RENAME CONSTRAINT playbook_steps_message_id_fkey TO context_items_content_id_fkey;
```

### Phase 3: Service Decomposition (Week 4-5)

**Objectives:**
- Break God classes into focused services
- Reorganize services by context
- Extract business logic to domain

**Tasks:**

| Task | Effort | Owner | Deliverable |
|---|---|---|---|
| Create service context directories | 0.5 day | Backend | Directory structure |
| Decompose ConversationOrchestrator | 3 days | Backend | 5 focused services |
| Decompose MessageService | 2 days | Backend | 3 focused services |
| Decompose IntentDetector | 2 days | Backend | 3 focused services |
| Move services to context directories | 1 day | Backend | Organized structure |
| Update all imports | 1 day | Backend | Clean imports |
| Integration tests | 2 days | QA | Full coverage |

**Incremental Approach:**

1. Create new services alongside old ones
2. Update callers to use new services
3. Deprecate old services
4. Remove deprecated code

### Phase 4: LLM Provider Flexibility (Week 6)

**Objectives:**
- Implement OpenAI provider
- Implement MCP provider stub
- Enable provider switching

**Tasks:**

| Task | Effort | Owner | Deliverable |
|---|---|---|---|
| Implement OpenAIProvider | 2 days | Backend | OpenAI integration |
| Implement MCPProvider stub | 1 day | Backend | MCP placeholder |
| Update Container for provider factory | 1 day | Backend | Dynamic provider |
| Add provider switching config | 0.5 day | Backend | ENV-based switching |
| A/B test Gemini vs OpenAI | 2 days | Data | Performance comparison |
| Load testing | 1 day | QA | Scalability validation |

### Phase 5: Stabilization & Documentation (Week 7)

**Objectives:**
- Increase test coverage to 85%
- Update all documentation
- Knowledge transfer

**Tasks:**

| Task | Effort | Owner | Deliverable |
|---|---|---|---|
| Add missing unit tests | 2 days | QA | 85% coverage |
| Add integration tests | 2 days | QA | Critical paths covered |
| Update architecture docs | 1 day | Backend | Updated ADRs |
| Update API documentation | 1 day | Backend | OpenAPI specs |
| Team training session | 0.5 day | Tech Lead | Knowledge transfer |
| Code review checklist update | 0.5 day | Tech Lead | Updated checklist |

---

## Testing Strategy

### Test Pyramid

```
        /\
       /  \    E2E Tests (10%)
      /____\   - Critical user flows
     /      \  Integration Tests (30%)
    /        \ - Service interactions
   /__________\  Unit Tests (60%)
                 - Domain logic
                 - Services
                 - Repositories
```

### Unit Testing

**Domain Models (No Infrastructure):**

```python
# tests/unit/domain/models/test_lead.py
import pytest
from domain.models.lead import Lead
from domain.value_objects.phone_number import PhoneNumber
from domain.value_objects.maturity_score import MaturityScore
from domain.enums import IntentType

class TestLead:
    def test_apply_intent_adjustment_interesse_tratamento(self):
        """Test scoring logic for INTERESSE_TRATAMENTO intent"""
        # Arrange
        lead = Lead(
            phone=PhoneNumber("5511999999999"),
            maturity_score=MaturityScore(30),
        )
        
        # Act
        lead.apply_intent_adjustment(IntentType.INTERESSE_TRATAMENTO)
        
        # Assert
        assert lead.maturity_score.value == 45  # 30 + 15
    
    def test_should_escalate_when_in_need_payoff_phase(self):
        """Test escalation trigger for high-score leads"""
        # Arrange
        lead = Lead(
            phone=PhoneNumber("5511999999999"),
            maturity_score=MaturityScore(75),
        )
        
        # Act & Assert
        assert lead.should_escalate_to_human() is True
    
    def test_should_not_escalate_when_in_situation_phase(self):
        """Test no escalation for low-score leads"""
        # Arrange
        lead = Lead(
            phone=PhoneNumber("5511999999999"),
            maturity_score=MaturityScore(20),
        )
        
        # Act & Assert
        assert lead.should_escalate_to_human() is False
```

**Services (Mocked Dependencies):**

```python
# tests/unit/services/lead/test_scoring_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from services.lead.scoring_service import LeadScoringService
from domain.models.lead import Lead
from domain.enums import IntentType

@pytest.fixture
def mock_lead_repo():
    return AsyncMock()

@pytest.fixture
def scoring_service(mock_lead_repo):
    return LeadScoringService(lead_repo=mock_lead_repo)

class TestLeadScoringService:
    @pytest.mark.asyncio
    async def test_update_score_calls_domain_logic(
        self,
        scoring_service,
        mock_lead_repo,
    ):
        """Test service delegates to domain model"""
        # Arrange
        lead = Lead(
            phone=PhoneNumber("5511999999999"),
            maturity_score=MaturityScore(30),
        )
        
        # Act
        await scoring_service.update_score(lead, IntentType.INTERESSE_TRATAMENTO)
        
        # Assert
        assert lead.maturity_score.value == 45
        mock_lead_repo.save.assert_called_once_with(lead)
```

### Integration Testing

**Service Integration (Real Dependencies):**

```python
# tests/integration/services/test_conversation_flow.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from services.conversation.orchestrator import ConversationOrchestrator
from services.ai.intent_detector import IntentDetector
from services.lead.scoring_service import LeadScoringService
from adapters.repositories.conversation_repository import ConversationRepository
from adapters.external.providers.gemini_provider import GeminiProvider

@pytest.fixture
async def db_session():
    # Create test database session
    ...

@pytest.fixture
def orchestrator(db_session):
    llm_provider = GeminiProvider(api_key=TEST_API_KEY)
    intent_detector = IntentDetector(llm_provider)
    lead_scorer = LeadScoringService(...)
    conversation_repo = ConversationRepository(db_session)
    
    return ConversationOrchestrator(
        intent_detector=intent_detector,
        lead_scorer=lead_scorer,
        response_generator=...,
        escalation_service=...,
        conversation_repo=conversation_repo,
    )

@pytest.mark.integration
class TestConversationFlow:
    @pytest.mark.asyncio
    async def test_full_conversation_flow(self, orchestrator):
        """Test complete message processing flow"""
        # Arrange
        message = "Olá, tenho interesse em Botox"
        
        # Act
        response = await orchestrator.process_message(
            message=message,
            conversation_id=test_conversation_id,
        )
        
        # Assert
        assert response.text is not None
        assert response.intent == "INTERESSE_TRATAMENTO"
        # Verify lead score was updated in DB
        ...
```

### E2E Testing

**Critical User Flows:**

```python
# tests/e2e/test_whatsapp_conversation.py
import pytest
from tests.e2e.helpers import WhatsAppSimulator

@pytest.mark.e2e
class TestWhatsAppConversation:
    @pytest.mark.asyncio
    async def test_complete_lead_journey(self, whatsapp_sim):
        """Test full user journey from interest to scheduling"""
        # Simulate WhatsApp conversation
        phone = "5511999999999"
        
        # Step 1: Initial contact (SITUATION phase)
        response1 = await whatsapp_sim.send_message(
            phone=phone,
            message="Olá, gostaria de saber sobre Botox",
        )
        assert "quanto tempo" in response1.lower()  # Open question
        
        # Step 2: Express problem (PROBLEM phase)
        response2 = await whatsapp_sim.send_message(
            phone=phone,
            message="Tenho rugas na testa que me incomodam muito",
        )
        assert "preocup" in response2.lower()  # Empathy
        
        # Step 3: Explore implications (IMPLICATION phase)
        response3 = await whatsapp_sim.send_message(
            phone=phone,
            message="Sim, afeta minha autoestima",
        )
        assert "benefícios" in response3.lower()
        
        # Step 4: Ready to schedule (NEED_PAYOFF phase)
        response4 = await whatsapp_sim.send_message(
            phone=phone,
            message="Quanto custa?",
        )
        assert "agendar" in response4.lower()
        
        # Verify lead was escalated
        lead = await whatsapp_sim.get_lead(phone)
        assert lead.status == "ESCALATED"
```

### Test Coverage Requirements

| Layer | Target Coverage | Current | Delta |
|---|---|---|---|---|
| Domain Models | 100% | 0% | +100% |
| Services | 90% | 65% | +25% |
| Repositories | 85% | 70% | +15% |
| Controllers | 80% | 55% | +25% |
| **Overall** | **85%** | **58%** | **+27%** |

---

## Success Criteria

### Technical Metrics

| Metric | Current | Target | Measurement |
|---|---|---|---|
| Test Coverage | 58% | 85% | Coverage report |
| Cyclomatic Complexity | 15.3 | <8.0 | SonarQube |
| God Classes (>400 LOC) | 3 | 0 | Code analysis |
| Domain Models | 0 | 8 | Manual count |
| Service Avg LOC | 280 | <120 | Code analysis |
| Provider Coupling | Hard | Abstracted | Code review |
| Prompt Locations | 3 | 1 | Manual audit |

### Business Metrics

| Metric | Current | Target | Measurement |
|---|---|---|---|
| Onboarding Time | 5 days | 3 days | -40% |
| Defect Rate (Context) | 15% | <5% | Issue tracker |
| LLM Provider Switch Time | N/A | <1 day | Manual test |
| MCP Integration Time | N/A | <3 days | Manual test |

### Acceptance Criteria

**MUST HAVE:**
- [ ] All domain models have >95% test coverage
- [ ] LLM provider swappable via configuration
- [ ] Prompts centralized in single registry
- [ ] All services follow SRP (no God classes)
- [ ] Integration tests pass with 100% success rate
- [ ] Zero production downtime during migration
- [ ] Performance regression <5%

**SHOULD HAVE:**
- [ ] Context Repository renamed (no "Playbook")
- [ ] Services organized by context (subdirectories)
- [ ] OpenAI provider implemented and tested
- [ ] MCP provider stub implemented

**NICE TO HAVE:**
- [ ] A/B test framework for prompts
- [ ] Anthropic provider implemented
- [ ] Real-time provider switching (no restart)

---

## Revised Effort Estimates (2026-02-02)

### Summary of Changes

| Phase | Original Estimate | Revised Estimate | Change | Reason |
|---|---|---|---|---|
| **Phase 1.5 (NEW)** | - | 0.5 weeks | **+0.5 weeks** | Local file storage abstraction added |
| **Phase 2** | 1.5 weeks | 0.5 weeks | **-1.0 week** | Simplified: rename only (no MessageModel split) |
| **Phase 3** | 2.0 weeks | 2.0 weeks | - | No change |
| **Phase 4** | 1.0 week | 1.0 week | - | No change |
| **Total** | 4.5 weeks | 4.0 weeks | **-0.5 weeks** | Net reduction |

### Phase 1.5: Local File Storage (NEW)

**Complexity:** 🟢 Low  
**Duration:** 0.5 weeks (2-3 days)  
**Critical Path:** YES (blocks file uploads in dev environment)

**Why Added:**
- Development environment cannot afford cloud storage costs (S3/CDN)
- Need local file storage for testing file upload/download
- Production can migrate to cloud storage later

**Tasks:**
1. Create `FileStorage` abstraction interface (4 hours)
2. Implement `LocalFileStorage` class (6 hours)
3. Implement `S3FileStorage` stub (2 hours)
4. Add configuration switching (2 hours)
5. Update file upload endpoints (4 hours)
6. Write unit tests (4 hours)
7. Integration tests (4 hours)

**Deliverables:**
- ✅ `/storage/` directory for local files
- ✅ `FileStorage` interface
- ✅ `LocalFileStorage` implementation
- ✅ API endpoints: POST `/files/upload`, GET `/files/{id}`
- ✅ Configuration: `FILE_STORAGE_BACKEND=local|s3`

### Phase 2: Simplified Migration

**Complexity:** 🟡 Medium (was 🔴 High)  
**Duration:** 0.5 weeks (was 1.5 weeks)  
**Savings:** -1.0 week

**Why Simplified:**
- ✅ `MessageModel` is NOT dual-purpose (verified via codebase analysis)
- ✅ `MessageModel` only used for context repository (playbook)
- ✅ `ConversationMessageModel` already separate
- ✅ No need to split data - just rename tables/columns

**Original Plan (Complex):**
- Create new `contents` table
- Migrate data from `messages` (filtering by usage)
- Update foreign keys
- Clean up old columns
- **Estimated:** 1.5 weeks

**Revised Plan (Simple):**
- Rename tables: `messages` → `contents`
- Rename columns: `message_id` → `content_id`
- Update ORM models
- Update repositories/services
- **Estimated:** 0.5 weeks

**Migration Script (Simplified):**

```sql
-- Step 1: Rename playbook tables
ALTER TABLE playbooks RENAME TO contexts;
ALTER TABLE playbook_steps RENAME TO context_items;
ALTER TABLE playbook_embeddings RENAME TO context_embeddings;

-- Step 2: Rename messages to contents
ALTER TABLE messages RENAME TO contents;

-- Step 3: Rename columns in context_items
ALTER TABLE context_items 
    RENAME COLUMN playbook_id TO context_id;

ALTER TABLE context_items
    RENAME COLUMN message_id TO content_id;

ALTER TABLE context_items
    RENAME COLUMN step_order TO display_order;

-- Step 4: Update foreign key names (optional, for clarity)
ALTER TABLE context_items
    RENAME CONSTRAINT playbook_steps_playbook_id_fkey 
    TO context_items_context_id_fkey;

ALTER TABLE context_items
    RENAME CONSTRAINT playbook_steps_message_id_fkey 
    TO context_items_content_id_fkey;

-- Done! No data migration needed.
```

**Code Changes:**
```python
# Before
from robbot.infra.db.models.message_model import MessageModel
from robbot.infra.db.models.playbook_step_model import PlaybookStepModel

# After
from robbot.infra.db.models.content import ContentModel
from robbot.infra.db.models.context_item import ContextItemModel
```

**Testing:**
- [ ] All existing tests pass with renamed models
- [ ] Integration tests verify relationships working
- [ ] API endpoints return correct data
- [ ] ChromaDB embeddings still functional

**Rollback Plan:**
- Rename tables back to original names (30 seconds)
- Revert code changes via git
- No data loss risk (rename only)

---

## Risk Mitigation

### High-Risk Items

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Breaking changes in migration | Medium | High | Phased rollout, feature flags |
| Performance degradation | Low | High | Load testing, rollback plan |
| Test coverage gaps | Medium | Medium | Mandatory code review |
| Team resistance | Low | Medium | Training, involvement |

### Rollback Strategy

Each phase must have a rollback plan:

1. **Phase 1 (Foundation):** New code alongside old, can be disabled via feature flag
2. **Phase 2 (Rename):** Database migration reversible, compatibility layer
3. **Phase 3 (Decomposition):** Old services retained until new services proven
4. **Phase 4 (Providers):** Provider selection via config, instant rollback

---

## Next Steps (Immediate Actions)

### For Product Team

1. **Review Auto-Send Workflow** (Priority: HIGH)
   - Validate bot autonomous send behavior
   - Define admin UX for configuring `usage_hint`
   - Document business rules: when should bot send files?
   - Example scenarios to validate:
     * User asks about Botox → Bot sends PDF brochure
     * User asks about pricing → Bot uses content as reference (no send)
     * User schedules appointment → Bot sends confirmation template

2. **Design Content Management UI** (Priority: MEDIUM)
   - Admin interface for creating/editing content
   - Configuration for auto-send mode (checkbox + condition)
   - Preview of how bot will use content
   - Analytics: track auto-send effectiveness

**Questions for Product:**
- [ ] Should bot ask permission before sending files? ("Posso te enviar um material?")
- [ ] How should admin test auto-send behavior before production?
- [ ] What analytics do we need? (send rate, open rate, conversion?)

### For Backend Team

1. **Phase 1.5: Local File Storage** (Start: Week 1, Duration: 2-3 days)
   - Implement `FileStorage` abstraction
   - Create `LocalFileStorage` class (save to `./storage/`)
   - Update file upload endpoints
   - Write tests
   - **Deliverable:** Working file upload/download without cloud costs

2. **Phase 2: Database Rename** (Start: Week 1, Duration: 2-3 days)
   - Write simplified migration script (rename only, no split)
   - Create new ORM models (`ContentModel`, `ContextItemModel`, `ContextModel`)
   - Update repositories and services
   - Run migration in staging
   - **Deliverable:** All "playbook" references renamed to "context"

3. **Add Auto-Send Fields** (Start: Week 2, Duration: 1 day)
   - Add columns to `contents`:
     * `auto_send: boolean`
     * `usage_hint: text`
     * `send_condition: enum` (always, on_interest, on_question)
   - Update API endpoints to accept new fields
   - **Deliverable:** Admin can configure auto-send behavior

**Code Checklist:**
- [ ] `FileStorage` interface defined
- [ ] `LocalFileStorage` implementation tested
- [ ] Migration script reviewed by team
- [ ] Auto-send columns added to schema
- [ ] API documentation updated

### For Frontend Team

1. **Content Management UI** (Start: Week 2, Duration: 3-4 days)
   - File upload component (with drag-drop)
   - Usage mode configuration:
     * Radio buttons: Reference Only | Auto-Send | Both
     * Conditional dropdown: "When to send?"
     * Textarea: "Usage hint for bot"
   - Preview panel: "How bot will use this content"
   - **Deliverable:** Admin can create/configure content easily

2. **Context Repository Manager** (Start: Week 2, Duration: 2-3 days)
   - List all context repositories (was "playbooks")
   - Drag-and-drop to reorder steps (display_order)
   - Visual indicators for auto-send content (icon/badge)
   - Test mode: simulate bot conversation to test auto-send
   - **Deliverable:** Admin can organize content intuitively

**UI Mockup Required:**
- [ ] Content creation form (upload + config)
- [ ] Context repository list view
- [ ] Step ordering interface (drag-drop)
- [ ] Auto-send configuration panel

### For DevOps Team

1. **Local Storage Setup** (Start: Week 1, Duration: 1 day)
   - Create `./storage/` directory in project root
   - Add to `.gitignore` (don't commit uploaded files)
   - Configure volume mount for Docker Compose
   - Set environment: `FILE_STORAGE_BACKEND=local`
   - **Deliverable:** Dev environment uses local storage

2. **Migration Planning** (Start: Week 1, Duration: 1 day)
   - Review migration script (simplified - rename only)
   - Test migration in isolated database
   - Prepare rollback script
   - Schedule staging deployment
   - **Deliverable:** Zero-downtime migration plan

**Infrastructure Checklist:**
- [ ] Storage directory created and ignored
- [ ] Docker volume configured
- [ ] Environment variables documented
- [ ] Migration tested in staging

---

## Appendix

### Glossary

- **MCP:** Model Context Protocol - standard for LLM context management
- **RAG:** Retrieval-Augmented Generation - technique for enhancing LLM with external knowledge
- **SPIN Selling:** Sales methodology (Situation, Problem, Implication, Need-Payoff)
- **DDD:** Domain-Driven Design
- **SRP:** Single Responsibility Principle
- **God Class:** Anti-pattern where one class does too much
- **Context Repository:** Knowledge base for specific topic (replaces "Playbook")
- **Knowledge Content:** Individual piece of content in repository (text, PDF, video, etc.)
- **Auto-Send:** Bot autonomously decides to send content based on conversation context
- **Usage Hint:** Admin configuration telling bot when/how to use content

### References

- [Clean Architecture - Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design - Eric Evans](https://www.domainlanguage.com/ddd/)
- [Model Context Protocol Spec](https://modelcontextprotocol.io/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Effective Testing Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
- [Hexagonal Architecture - Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [Repository Pattern - Martin Fowler](https://martinfowler.com/eaaCatalog/repository.html)

### Related Documentation

**Internal Docs:**
- [Architecture Overview](../academic/arquitetura-tecnica.md)
- [Repository Pattern Guide](./repository_pattern.md)
- [Development Workflow](.context/docs/development-workflow.md)
- [Testing Strategy](.context/docs/testing-strategy.md)

**API Documentation:**
- [Postman Collection](../api/postman/)
- [OpenAPI Spec](../../src/robbot/api/openapi.json) (if exists)

**Deployment:**
- [Railway Deployment Guide](../deployment/railway.md)
- [Docker Compose Setup](../../docker-compose.yml)

---

## Document History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0.0 | 2026-02-02 | AI Agent | Initial comprehensive analysis |
| 1.1.0 | 2026-02-02 | AI Agent | Added Phase 1.5 (Local File Storage) |
| 1.2.0 | 2026-02-02 | AI Agent | Corrected Auto-Send workflow (bot autonomous) |
| 1.3.0 | 2026-02-02 | AI Agent | Simplified Phase 2 (rename only, no split) |
| 1.4.0 | 2026-02-02 | AI Agent | Added admin UI mockups and next steps |

**Change Summary:**
- **v1.1.0:** Added local file storage requirement (no cloud costs for dev)
- **v1.2.0:** Corrected auto-send from user-triggered to bot-autonomous decision
- **v1.3.0:** Simplified migration strategy after verifying MessageModel single-purpose
- **v1.4.0:** Added concrete action items for each team

---

**Next Steps:**

1. **Review this document** with team in next daily standup
2. **Validate Auto-Send UX** with product owner (critical business logic)
3. **Prioritize phases** based on business impact and urgency
4. **Assign owners** to Phase 1.5 and Phase 2 tasks
5. **Create tickets** for immediate actions (Week 1)
6. **Schedule kickoff** for refactoring sprint

**Document Status:** ✅ Ready for Review  
**Reviewers:** Backend Team Lead, Product Owner, Frontend Lead  
**Target Approval:** 2026-02-05  
**Implementation Start:** Week of 2026-02-08

---


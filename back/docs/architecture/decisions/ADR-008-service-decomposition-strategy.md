# ADR-004: Service Decomposition Strategy

**Status:** IMPLEMENTED  
**Date:** 2026-01-15  
**Context:** God Object ConversationOrchestrator (Issue #7)  
**Affected Components:** services/conversation_orchestrator.py (529 LOC → 50 LOC)

---

## Problem

**ConversationOrchestrator** was a God Object with 15+ responsibilities:

```
ConversationOrchestrator (529 LOC)
├── Message processing pipeline
├── Intent detection
├── Conversation state management
├── Lead maturity scoring
├── SPIN selling logic
├── Response generation
├── Playbook selection
├── Escalation detection
├── Urgency analysis
├── Name extraction
├── Message persistence
├── Error handling
├── Logging
├── Context building
└── WhatsApp integration
```

**Issues:**
- Hard to test (all-or-nothing)
- Difficult to modify (ripple effects)
- Unclear responsibilities
- Difficult to reuse components
- Single reason to change violated

---

## Decision

**Decompose into 3 Focused Services** + minimal orchestrator:

```
ConversationOrchestrator (SIMPLIFIED - 50 LOC)
├─ MessagePipeline (100 LOC)
│  ├── Validate messages
│  ├── Process media
│  ├── Save to database
│  └── Handle transcription
│
├─ ConversationStateMachine (120 LOC)
│  ├── Update lead maturity
│  ├── Transition lead status
│  ├── Detect escalation triggers
│  └── Close conversation
│
└─ ResponseGenerator (100 LOC)
   ├── Generate AI responses
   ├── Apply playbooks
   ├── Apply SPIN selling
   └── Personalize responses
```

---

## 1. MessagePipeline (100 LOC)

**Single Responsibility:** Process inbound messages

```python
class MessagePipeline:
    def __init__(self, db: Session, message_processor: MessageProcessor):
        self.db = db
        self.message_processor = message_processor
    
    async def validate_message(self, content: str) -> bool:
        # Check length, injection patterns, etc.
        pass
    
    async def process_message(
        self,
        conversation: ConversationModel,
        content: str,
        has_media: bool = False,
    ) -> ConversationMessageModel:
        # 1. Validate
        # 2. Process media if present
        # 3. Store message
        pass
    
    async def save_response(
        self,
        conversation: ConversationModel,
        response_text: str,
    ) -> ConversationMessageModel:
        # Save bot response
        pass
```

**Tests:** `test_message_pipeline.py`
- ✅ Valid messages stored
- ✅ Invalid messages rejected
- ✅ Media transcribed
- ✅ SQL injection blocked

---

## 2. ConversationStateMachine (120 LOC)

**Single Responsibility:** Manage conversation state transitions

```python
class ConversationStateMachine:
    def __init__(self, db: Session):
        self.db = db
    
    async def update_lead_maturity(
        self,
        conversation: ConversationModel,
        detected_intent: IntentType,
        is_urgent: bool,
    ) -> Tuple[int, LeadStatus]:
        # 1. Get intent score
        # 2. Add urgency bonus
        # 3. Update lead (capped at 100)
        # 4. Transition status
        return new_score, new_status
    
    async def check_escalation_needed(
        self,
        conversation: ConversationModel,
        maturity_score: int,
        detected_intent: IntentType,
    ) -> bool:
        # Triggers:
        # - Score > 70 (ready to schedule)
        # - Urgent medical concern
        # - Customer frustration
        # - Explicit request
        pass
    
    async def close_conversation(
        self,
        conversation: ConversationModel,
        reason: str,
    ) -> ConversationModel:
        # Close with reason tracking
        pass
```

**Tests:** `test_state_machine.py`
- ✅ Score increments correctly
- ✅ Status transitions appropriate
- ✅ Escalation detected properly
- ✅ SPIN phases managed

---

## 3. ResponseGenerator (100 LOC)

**Single Responsibility:** Generate contextual responses

```python
class ResponseGenerator:
    def __init__(
        self,
        llm_provider: LLMProvider,
        prompt_loader: PromptLoader,
        playbook_service: PlaybookService,
    ):
        self.llm = llm_provider
        self.prompt_loader = prompt_loader
        self.playbook_service = playbook_service
    
    async def generate_response(
        self,
        user_message: str,
        context: str,
        detected_intent: IntentType,
        maturity_score: int,
        clinic_info: Optional[Dict],
    ) -> str:
        # 1. Try playbook (fast path)
        # 2. Generate with Gemini (AI path)
        # 3. Personalize with clinic info
        return response_text
```

**Tests:** `test_response_generator.py`
- ✅ Playbooks applied
- ✅ Gemini responses generated
- ✅ SPIN methodology followed
- ✅ Clinic info personalized

---

## 4. Simplified ConversationOrchestrator (50 LOC)

**Responsibility:** Orchestrate the pipeline

```python
class ConversationOrchestrator:
    def __init__(
        self,
        db: Session,
        message_pipeline: MessagePipeline,
        state_machine: ConversationStateMachine,
        response_generator: ResponseGenerator,
        intent_detector: IntentDetector,
    ):
        self.db = db
        self.pipeline = message_pipeline
        self.state_machine = state_machine
        self.generator = response_generator
        self.intent_detector = intent_detector
    
    async def process_message(
        self,
        conversation: ConversationModel,
        user_message: str,
    ) -> Optional[str]:
        # 1. Validate and store message
        await self.pipeline.process_message(
            conversation=conversation,
            content=user_message,
        )
        
        # 2. Detect intent
        intent = await self.intent_detector.detect_intent(
            message=user_message,
            context=conversation.context,
        )
        
        # 3. Update state
        score, status = await self.state_machine.update_lead_maturity(
            conversation=conversation,
            detected_intent=intent,
        )
        
        # 4. Check escalation
        if await self.state_machine.check_escalation_needed(
            conversation=conversation,
            maturity_score=score,
            detected_intent=intent,
        ):
            return None  # Escalate to human
        
        # 5. Generate response
        response = await self.generator.generate_response(
            user_message=user_message,
            context=conversation.context,
            detected_intent=intent,
            maturity_score=score,
        )
        
        # 6. Save response
        await self.pipeline.save_response(
            conversation=conversation,
            response_text=response,
        )
        
        return response
```

---

## Dependency Injection

Update DIContainer to instantiate all components:

```python
# config/container.py
class DIContainer:
    async def initialize(self):
        # Individual components
        self._message_pipeline = MessagePipeline(
            db=self.db,
            message_processor=self._message_processor,
        )
        
        self._state_machine = ConversationStateMachine(db=self.db)
        
        self._response_generator = ResponseGenerator(
            llm_provider=self._llm,
            prompt_loader=self._prompt_loader,
            playbook_service=self._playbook_service,
        )
        
        # Orchestrator
        self._orchestrator = ConversationOrchestrator(
            db=self.db,
            message_pipeline=self._message_pipeline,
            state_machine=self._state_machine,
            response_generator=self._response_generator,
            intent_detector=self._intent_detector,
        )
    
    def get_orchestrator(self) -> ConversationOrchestrator:
        return self._orchestrator
```

---

## Testing Strategy

### Unit Tests (Fast, No DB)
```
test_message_pipeline.py        (8 tests)
test_state_machine.py           (10 tests)
test_response_generator.py      (7 tests)
```

### Integration Tests (Real Flow)
```
test_conversation_orchestrator_new.py (4 tests)
├── Test full message → state → response flow
├── Test escalation triggers
├── Test error handling
└── Test message persistence
```

### Coverage Target
- MessagePipeline: 85%+
- ConversationStateMachine: 90%+
- ResponseGenerator: 80%+
- ConversationOrchestrator: 85%+

---

## Benefits

✅ **Single Responsibility:** Each component has one reason to change  
✅ **Testable:** Each component tested independently  
✅ **Reusable:** Components used in other workflows  
✅ **Maintainable:** Clear responsibilities  
✅ **Composable:** Mix and match components  
✅ **Scalable:** Replace components as needed  

---

## Migration Path

**Phase 1 (Done):**
- Create 3 new services
- Keep old orchestrator
- New code uses new services

**Phase 2:**
- Update controllers to use new services
- Add integration tests
- Run in parallel

**Phase 3:**
- Replace orchestrator calls with new services
- Remove old orchestrator logic
- Archive old code

---

## Related ADRs

- ADR-001: Dependency Injection Pattern
- ADR-003: Session Dependency Injection

---

## References

- [Single Responsibility Principle](https://en.wikipedia.org/wiki/Single_responsibility_principle)
- [Service Decomposition Pattern](https://microservices.io/patterns/decomposition/service-per-team.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)

# ADR-003: Session Dependency Injection

**Status:** IMPLEMENTED  
**Date:** 2026-01-15  
**Context:** Session Management Anti-Pattern (Issue #4)  
**Affected Components:** services/*, config/container.py, api/v1/dependencies.py

---

## Problem

Original codebase had **temporal coupling** with session management:

```python
# BAD: Implicit session creation
class LeadService:
    def __init__(self):
        self.db = get_sync_session()  # IMPLICIT - hard to test
    
    def create_lead(self, name: str):
        lead = LeadModel(name=name)
        self.db.add(lead)  # Which session? Unclear!
        self.db.commit()
```

**Issues:**
1. **Hard to Test:** Can't inject mock session
2. **Implicit Dependency:** Constructor doesn't show session need
3. **Transaction Control:** Caller can't manage transaction boundaries
4. **Temporal Coupling:** Session lifecycle unclear
5. **Testing:** Database tests can't rollback per test

---

## Decision

Implement **Session Dependency Injection** pattern:

1. **Session Passed to Constructor**
   - Services receive session as parameter
   - Explicit dependency in code
   - Caller controls session lifecycle

2. **Caller Manages Transactions**
   - FastAPI endpoint creates/manages session
   - Service doesn't create or commit
   - Endpoint handles rollback on error

3. **Mock Session in Tests**
   - Unit tests inject `MagicMock(spec=Session)`
   - No database access in tests
   - Fast test execution

4. **Dependency Injection Chain**
   - DIContainer provides session
   - FastAPI Depends() injects into endpoints
   - Endpoint passes to services

---

## Implementation

### 1. Service Constructor DI
```python
# services/lead_service.py (NEW)
class LeadService:
    def __init__(self, db: Session):  # EXPLICIT
        self.db = db
        self.repo = LeadRepository(db)
    
    def create_lead(self, name: str) -> LeadModel:
        lead = LeadModel(name=name)
        return self.repo.create(lead)
        # Note: NO commit() - caller decides
```

### 2. Endpoint Manages Transaction
```python
# adapters/controllers/lead_controller.py
@app.post("/leads")
async def create_lead(
    payload: CreateLeadDTO,
    db: Session = Depends(get_db),  # Session injected
):
    try:
        service = LeadService(db=db)  # Pass session
        lead = service.create_lead(payload.name)
        db.commit()  # Endpoint commits
        return lead
    except Exception:
        db.rollback()  # Endpoint rollbacks
        raise
```

### 3. Unit Test with Mock Session
```python
# tests/unit/services/test_lead_service.py
def test_create_lead():
    mock_session = MagicMock(spec=Session)
    service = LeadService(db=mock_session)
    
    # Mock repository
    with patch("robbot.services.lead_service.LeadRepository") as MockRepo:
        mock_repo = MagicMock()
        mock_repo.create.return_value = LeadModel(id="1", name="João")
        MockRepo.return_value = mock_repo
        
        result = service.create_lead(name="João")
        
        # No database was hit!
        assert mock_session.commit.not_called
        assert result.name == "João"
```

### 4. Integration Test with Real Session
```python
# tests/integration/test_lead_creation.py
@pytest.mark.asyncio
async def test_create_lead_full_flow(db: Session):
    service = LeadService(db=db)
    
    lead = service.create_lead(name="João")
    db.commit()  # Integration test commits
    
    # Verify in database
    retrieved = db.query(LeadModel).filter_by(id=lead.id).first()
    assert retrieved.name == "João"
```

---

## Session Lifecycle

```
FastAPI Request
    ↓
Depends(get_db) → Create session
    ↓
Pass session to LeadService
    ↓
Service uses session for CRUD
    ↓
Endpoint decides: commit() or rollback()
    ↓
Session closed automatically
```

---

## Benefits

✅ **Testable:** Inject mock session in unit tests  
✅ **Explicit:** Constructor shows session dependency  
✅ **Transactional:** Caller controls commit/rollback  
✅ **Flexible:** Different session strategies per endpoint  
✅ **No Globals:** No global session state  

---

## Guidelines

### ✅ DO:
- Pass `db: Session` to service constructors
- Let endpoint manage `commit()` and `rollback()`
- Use `db.flush()` in service only when needed
- Mock session in unit tests

### ❌ DON'T:
- Call `get_sync_session()` inside service constructors
- Service should not call `db.commit()`
- Don't access session in service class variables
- Service should not manage session lifecycle

---

## Example: Before vs After

### BEFORE (Bad)
```python
class ConversationService:
    def __init__(self):
        self.db = get_sync_session()  # IMPLICIT
    
    def close_conversation(self, id: str):
        conv = self.db.query(ConversationModel).get(id)
        conv.status = "CLOSED"
        self.db.commit()  # Service commits!
```

### AFTER (Good)
```python
class ConversationService:
    def __init__(self, db: Session):  # EXPLICIT
        self.db = db
        self.repo = ConversationRepository(db)
    
    def close_conversation(self, id: str) -> ConversationModel:
        conv = self.repo.get_by_id(id)
        conv.status = ConversationStatus.CLOSED
        return self.repo.update(conv)
        # Note: Endpoint commits
```

---

## Related ADRs

- ADR-001: Dependency Injection Pattern
- ADR-002: Repository Interface Pattern

---

## References

- [SQLAlchemy Session Basics](https://docs.sqlalchemy.org/en/14/orm/session_basics.html)
- [Dependency Injection](https://en.wikipedia.org/wiki/Dependency_injection)
- [Transactional Testing](https://en.wikipedia.org/wiki/Transaction_(database))

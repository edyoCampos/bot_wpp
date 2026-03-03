# ADR-002: Repository Interface Pattern

**Status:** IMPLEMENTED  
**Date:** 2026-01-15  
**Context:** No Repository Interface (Issue #5)  
**Affected Components:** adapters/repositories/base_repository.py, core/interfaces.py

---

## Problem

The original codebase had:
1. **Concrete Repository Classes:** Services depended directly on `LeadRepository`, `ConversationRepository`
2. **No Abstraction:** Couldn't swap implementations without changing code
3. **Hard to Mock:** Unit tests had to mock concrete classes with all their methods
4. **Tight Coupling:** Business logic coupled to specific repository implementation

---

## Decision

Implement **Generic Repository Interface** (`IRepository[T]`):

```python
# core/interfaces.py
class IRepository(ABC, Generic[T]):
    @abstractmethod
    def create(self, entity: T) -> T:
        pass
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[T]:
        pass
    
    @abstractmethod
    def update(self, entity: T) -> T:
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        pass
```

---

## Implementation

### 1. BaseRepository Implements Interface
```python
# adapters/repositories/base_repository.py
class BaseRepository(IRepository[ModelType]):
    def create(self, entity: ModelType) -> ModelType:
        # Standard CRUD operation
        pass
```

### 2. Service Accepts Interface
```python
# services/lead_service.py
class LeadService:
    def __init__(
        self,
        db: Session,
        lead_repo: IRepository[LeadModel],
    ):
        self.repo = lead_repo
```

### 3. MockRepository for Testing
```python
# core/interfaces.py
class MockRepository(IRepository[T]):
    def __init__(self):
        self.data = {}
    
    def create(self, entity: T) -> T:
        self.data[entity.id] = entity
        return entity
```

### 4. Dependency Injection
```python
# config/container.py
class DIContainer:
    def get_lead_repository(self) -> IRepository[LeadModel]:
        return LeadRepository(self.session)
```

---

## Type Safety

The generic `IRepository[T]` provides strong typing:

```python
# Mypy knows this returns LeadModel or None
lead_repo: IRepository[LeadModel] = ...
lead: Optional[LeadModel] = lead_repo.get_by_id("id-123")

# This would be a type error:
# user: UserModel = lead_repo.get_by_id("id-123")  # Type mismatch!
```

---

## Benefits

✅ **Polymorphism:** Swap implementations (SQL → NoSQL, in-memory)  
✅ **Testability:** MockRepository eliminates database dependency  
✅ **Type Safe:** Generic `IRepository[T]` prevents type errors  
✅ **Decoupling:** Business logic doesn't know about database  
✅ **Reusable:** Same interface for all domain models  

---

## CRUD Interface

All repositories implement these methods:

| Method | Signature | Returns |
|--------|-----------|---------|
| `create` | `create(entity: T) -> T` | Created entity |
| `get_by_id` | `get_by_id(id: str) -> Optional[T]` | Entity or None |
| `update` | `update(entity: T) -> T` | Updated entity |
| `delete` | `delete(id: str) -> bool` | Success flag |
| `list_all` | `list_all(skip: int, take: int) -> List[T]` | List of entities |
| `exists` | `exists(id: str) -> bool` | True/False |
| `count` | `count() -> int` | Total count |

---

## Testing Example

```python
# tests/unit/services/test_lead_service.py
def test_lead_creation():
    mock_repo = MockRepository[LeadModel]()
    service = LeadService(db=mock_session, lead_repo=mock_repo)
    
    result = service.create_from_conversation(
        phone_number="+5511999999999",
        name="João",
    )
    
    # Verify stored in mock
    assert mock_repo.get_by_id(result.id) == result
```

---

## Related ADRs

- ADR-001: Dependency Injection Pattern
- ADR-003: Session Dependency Injection

---

## References

- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Generic Types in Python](https://docs.python.org/3/library/typing.html#generics)
- [Testing with Mock Objects](https://en.wikipedia.org/wiki/Mock_object)
